"""
AI Avatar — Web Application with Lip Sync
Flask backend: Groq LLM + Edge-TTS + Wav2Lip pipeline
"""
import sys
import os
import io
import json
import uuid
import time
import asyncio
import logging
import threading
import subprocess
import tempfile
import cv2
import numpy as np
from pathlib import Path
from flask import Flask, render_template, request, Response, stream_with_context, send_file, jsonify

# Setup path for project imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

import config
from llm.groq_stream import GroqStream
from tts.edge_tts_stream import EdgeTTSStream
from lipsync.wav2lip_processor import Wav2LipProcessor
from preprocessing.face_detector import FaceDetector

# ============ Logging ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ Flask App ============
app = Flask(__name__)

# ============ Global State for Avatar ============
class AvatarState:
    """Manages the avatar frame state for MJPEG streaming"""
    def __init__(self):
        self.idle_frame = None       # Static avatar image (full frame)
        self.face_frame = None       # Cropped face (256x256)
        self.face_coords = None      # (x, y, w, h)
        self.synced_frames = []      # Lip-synced full frames
        self.frame_index = 0
        self.is_speaking = False
        self.lock = threading.Lock()

    def get_current_frame(self):
        with self.lock:
            if self.is_speaking and self.synced_frames:
                if self.frame_index < len(self.synced_frames):
                    frame = self.synced_frames[self.frame_index]
                    self.frame_index += 1
                    return frame
                else:
                    # Finished speaking
                    self.is_speaking = False
                    self.synced_frames = []
                    self.frame_index = 0
            return self.idle_frame

    def start_speaking(self, frames):
        with self.lock:
            self.synced_frames = frames
            self.frame_index = 0
            self.is_speaking = True

    def stop_speaking(self):
        with self.lock:
            self.is_speaking = False
            self.synced_frames = []
            self.frame_index = 0


avatar_state = AvatarState()

# ============ Temp directory for generated videos ============
TEMP_DIR = Path(__file__).parent / "output" / "web_temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# ============ Initialize Components ============
print("\n" + "=" * 60)
print("  AI AVATAR - Web Interface with Lip Sync")
print("=" * 60)

# 1. Load avatar source (IMAGE or VIDEO)
if config.SOURCE_TYPE == "video":
    logger.info("Loading avatar from video...")
    avatar_video_path = config.SOURCE_VIDEO_PATH
    if not avatar_video_path.exists():
        logger.error(f"Avatar video not found: {avatar_video_path}")
        sys.exit(1)
    
    # Open video and extract first frame
    video_cap = cv2.VideoCapture(str(avatar_video_path))
    if not video_cap.isOpened():
        logger.error(f"Failed to open video: {avatar_video_path}")
        sys.exit(1)
    
    ret, avatar_image = video_cap.read()
    video_cap.release()
    
    if not ret or avatar_image is None:
        logger.error(f"Failed to read frame from video: {avatar_video_path}")
        sys.exit(1)
    
    avatar_state.idle_frame = avatar_image.copy()
    logger.info(f"Avatar video loaded, frame shape: {avatar_image.shape}")
else:
    logger.info("Loading avatar from image...")
    avatar_img_path = config.SOURCE_IMAGE_PATH
    if not avatar_img_path.exists():
        logger.error(f"Avatar image not found: {avatar_img_path}")
        sys.exit(1)
    
    avatar_image = cv2.imread(str(avatar_img_path))
    if avatar_image is None:
        logger.error(f"Failed to read avatar image: {avatar_img_path}")
        sys.exit(1)
    
    avatar_state.idle_frame = avatar_image.copy()
    logger.info(f"Avatar image loaded: {avatar_image.shape}")

# 2. Detect face
logger.info("Detecting face in avatar...")
face_detector = FaceDetector(
    face_size=config.WAV2LIP_FACE_SIZE,
    box_expansion=config.WAV2LIP_BOX_EXPANSION
)
face_coords = face_detector.detect_face(avatar_image)
if face_coords is None:
    logger.error("No face detected in avatar image!")
    sys.exit(1)

avatar_state.face_coords = face_coords
x, y, w, h = face_coords
face_crop = avatar_image[y:y+h, x:x+w]
avatar_state.face_frame = cv2.resize(face_crop, (config.WAV2LIP_FACE_SIZE, config.WAV2LIP_FACE_SIZE))
logger.info(f"Face detected at: x={x}, y={y}, w={w}, h={h}")

# 3. Load Groq LLM
logger.info("Initializing Groq LLM...")
llm = GroqStream(
    api_key=config.GROQ_API_KEY,
    model=config.GROQ_MODEL,
    temperature=config.LLM_TEMPERATURE,
    top_p=config.LLM_TOP_P,
    max_tokens=config.LLM_MAX_TOKENS,
    system_prompt=config.SYSTEM_PROMPT
)
llm.load_model()
logger.info("Groq LLM ready!")

# 4. Initialize TTS
logger.info("Initializing Edge-TTS...")
tts = EdgeTTSStream(
    voice=config.TTS_VOICE,
    rate=config.TTS_RATE,
    pitch=config.TTS_PITCH
)
logger.info("Edge-TTS ready!")

# 5. Load Wav2Lip
logger.info("Loading Wav2Lip model...")
wav2lip = Wav2LipProcessor(
    checkpoint_path=str(config.WAV2LIP_CHECKPOINT),
    device=config.WAV2LIP_DEVICE,
    face_size=config.WAV2LIP_FACE_SIZE,
    fps=config.WAV2LIP_FPS,
    batch_size=config.WAV2LIP_BATCH_SIZE,
    use_fp16=config.WAV2LIP_USE_FP16,
    window_overlap=config.WAV2LIP_WINDOW_OVERLAP
)
wav2lip.load_model()
logger.info("Wav2Lip ready!")

print(f"  Model   : {config.GROQ_MODEL}")
print(f"  Voice   : {config.TTS_VOICE}")
if config.SOURCE_TYPE == "video":
    print(f"  Source  : VIDEO - {config.SOURCE_VIDEO_PATH.name} ({avatar_image.shape[1]}x{avatar_image.shape[0]})")
else:
    print(f"  Source  : IMAGE - {config.SOURCE_IMAGE_PATH.name} ({avatar_image.shape[1]}x{avatar_image.shape[0]})")
print(f"  Face    : ({x},{y}) {w}x{h}")
print("=" * 60)
print(f"\n  Open in browser: http://localhost:5000\n")
print("=" * 60 + "\n")


# ============ Helper: Run async in sync context ============
def run_async(coro):
    """Run an async coroutine in a new event loop (for calling from sync Flask)"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ============ Helper: Generate lip-synced video ============
def generate_lipsync_video(text: str) -> tuple:
    """
    Complete pipeline: Text -> TTS -> Wav2Lip -> MP4 video
    Returns: (video_path, audio_path) or (None, None) on error
    """
    session_id = str(uuid.uuid4())[:8]

    try:
        # Step 1: Generate TTS audio
        logger.info(f"[{session_id}] Generating TTS audio...")
        t0 = time.time()
        audio_bytes = run_async(tts.text_to_audio(text))
        if not audio_bytes:
            logger.error(f"[{session_id}] TTS returned empty audio")
            return None, None
        t1 = time.time()
        logger.info(f"[{session_id}] TTS done in {t1-t0:.1f}s ({len(audio_bytes)} bytes)")

        # Step 2: Convert MP3 to numpy for Wav2Lip
        from pydub import AudioSegment
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
        audio_array = np.array(audio_segment.get_array_of_samples()).astype(np.int16)
        audio_duration = len(audio_array) / 16000.0
        logger.info(f"[{session_id}] Audio: {audio_duration:.1f}s, {len(audio_array)} samples")

        # Step 3: Run Wav2Lip
        logger.info(f"[{session_id}] Running Wav2Lip lip sync...")
        t2 = time.time()
        face_frame = avatar_state.face_frame.copy()
        synced_face_frames = wav2lip.generate_lip_sync(face_frame, audio_array, 16000)
        t3 = time.time()
        logger.info(f"[{session_id}] Wav2Lip done in {t3-t2:.1f}s, {len(synced_face_frames)} frames")

        # Step 4: Paste faces back into full avatar image using fast NumPy broadcasting
        x, y, w, h = avatar_state.face_coords
        n_frames = len(synced_face_frames)
        
        logger.info(f"[{session_id}] Fast-joining {n_frames} frames...")
        t_join_start = time.time()

        # Pre-allocate frames tensor and broadcast the background (much faster than looping copies)
        base_img = avatar_state.idle_frame
        full_frames = np.empty((n_frames, *base_img.shape), dtype=base_img.dtype)
        full_frames[:] = base_img
        
        for i, synced_face in enumerate(synced_face_frames):
            # INTER_LINEAR is faster than INTER_CUBIC with minimal quality difference
            synced_resized = cv2.resize(synced_face, (w, h), interpolation=cv2.INTER_LINEAR)
            full_frames[i, y:y+h, x:x+w] = synced_resized

        t_join_end = time.time()
        logger.info(f"[{session_id}] Frame joining took {t_join_end - t_join_start:.3f}s")

        if len(full_frames) == 0:
            logger.error(f"[{session_id}] No frames generated")
            return None, None

        # Step 5: Create MP4 with ffmpeg (pipe raw frames + mux with audio)
        logger.info(f"[{session_id}] Encoding MP4 video...")
        t4 = time.time()

        # Save audio to temp file
        audio_path = str(TEMP_DIR / f"audio_{session_id}.mp3")
        with open(audio_path, 'wb') as f:
            f.write(audio_bytes)

        # Saving frames to temporary video file using OpenCV
        temp_video_path = str(TEMP_DIR / f"temp_{session_id}.mp4")
        
        # Get frame dimensions
        frame_h, frame_w = full_frames[0].shape[:2]
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video_path, fourcc, 25.0, (frame_w, frame_h))
        
        for frame in full_frames:
            out.write(frame)
        out.release()

        # Generate filename with timestamp and processing time
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Calculate initial processing time estimate (before ffmpeg)
        t_pre_ffmpeg = time.time()
        estimated_time = t_pre_ffmpeg - t0
        
        # Output video path with timing info
        video_path = str(TEMP_DIR / f"lipsync_{timestamp}_{estimated_time:.1f}s_{session_id}.mp4")

        # Use ffmpeg to mux video and audio
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', temp_video_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-shortest',
            '-movflags', '+faststart',
            video_path
        ]

        logger.info(f"[{session_id}] Running FFmpeg muxing...")
        process = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

        # Clean up temp video file
        try:
            os.remove(temp_video_path)
        except Exception:
            pass

        if process.returncode != 0:
            logger.error(f"[{session_id}] FFmpeg error: {process.stderr[-500:]}")
            return None, None

        t5 = time.time()
        total_time = t5 - t0
        logger.info(f"[{session_id}] MP4 encoded in {t5-t4:.1f}s")
        logger.info(f"[{session_id}] Total pipeline: {total_time:.1f}s for {audio_duration:.1f}s of speech")
        logger.info(f"[{session_id}] Saved as: {Path(video_path).name}")

        # Also push frames to MJPEG stream
        avatar_state.start_speaking(full_frames)

        return video_path, audio_path

    except Exception as e:
        logger.error(f"[{session_id}] Lip sync pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


# ============ Routes ============

@app.route('/')
def index():
    """Serve the main chat page"""
    return render_template('index.html')


@app.route('/avatar-image')
def avatar_image_route():
    """Serve the avatar idle frame (from image or video)"""
    try:
        # Encode the current idle frame as JPEG and serve it
        _, buffer = cv2.imencode('.jpg', avatar_state.idle_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return Response(buffer.tobytes(), mimetype='image/jpeg', headers={'Cache-Control': 'max-age=0'})
    except Exception as e:
        logger.error(f"Error serving avatar image: {e}")
        return str(e), 500


@app.route('/video-feed')
def video_feed():
    """MJPEG stream of avatar (idle = static, speaking = lip-synced frames)"""
    def generate():
        while True:
            frame = avatar_state.get_current_frame()
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            # 25 FPS when speaking, 5 FPS when idle
            if avatar_state.is_speaking:
                time.sleep(1.0 / 25)
            else:
                time.sleep(1.0 / 5)

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/chat', methods=['POST'])
def chat():
    """Stream chat response + generate lip-synced video"""
    data = request.get_json()
    if not data or 'message' not in data:
        return Response(
            f"data: {json.dumps({'error': 'No message provided'})}\n\n",
            mimetype='text/event-stream'
        )

    user_message = data['message'].strip()
    if not user_message:
        return Response(
            f"data: {json.dumps({'error': 'Empty message'})}\n\n",
            mimetype='text/event-stream'
        )

    logger.info(f"User: {user_message}")

    def generate():
        try:
            # Phase 1: Stream text tokens
            messages = llm.format_messages(user_message)
            stream = llm.client.chat.completions.create(
                model=llm.model,
                messages=messages,
                temperature=llm.temperature,
                top_p=llm.top_p,
                max_tokens=llm.max_tokens,
                stream=True
            )

            full_response = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    yield f"data: {json.dumps({'token': token})}\n\n"

            # Save conversation history
            llm.conversation_history.append({"role": "user", "content": user_message})
            llm.conversation_history.append({"role": "assistant", "content": full_response})

            logger.info(f"AI response: {full_response[:80]}...")

            # Phase 2: Generate lip-synced video
            logger.info("Sending status: generating_speech")
            yield f"data: {json.dumps({'status': 'generating_speech'})}\n\n"
            time.sleep(0.2)
            
            logger.info("Sending status: generating_lipsync")
            yield f"data: {json.dumps({'status': 'generating_lipsync'})}\n\n"
            time.sleep(0.2)

            logger.info("Starting video generation...")
            video_path, audio_path = generate_lipsync_video(full_response)

            if video_path and os.path.exists(video_path):
                video_name = Path(video_path).name
                video_url = f'/lipsync-video/{video_name}'
                logger.info(f"Sending video URL: {video_url}")
                yield f"data: {json.dumps({'video': video_url})}\n\n"
                time.sleep(0.2)
            else:
                logger.error("Video generation failed!")
                yield f"data: {json.dumps({'status': 'speech_error'})}\n\n"
                time.sleep(0.2)

            logger.info("Sending [DONE]")
            yield f"data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Chat error: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


from flask import send_from_directory

@app.route('/lipsync-video/<filename>')
def lipsync_video(filename):
    """Serve a generated lip-sync video"""
    video_path = TEMP_DIR / filename
    if video_path.exists():
        response = send_from_directory(str(TEMP_DIR), filename, mimetype='video/mp4')
        response.headers['Accept-Ranges'] = 'bytes'
        # Prevent browser caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    return "Video not found", 404


@app.route('/clear', methods=['POST'])
def clear():
    """Clear conversation history"""
    llm.clear_history()
    avatar_state.stop_speaking()
    logger.info("Conversation history cleared")
    return {'status': 'ok'}


# ============ Cleanup old temp files on start ============
def cleanup_temp():
    for f in TEMP_DIR.glob("*"):
        try:
            f.unlink()
        except Exception:
            pass

cleanup_temp()


# ============ Main ============
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
