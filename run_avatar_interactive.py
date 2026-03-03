"""
Interactive AI Avatar - Real-time with Display Window
Choose between text input or microphone input
"""
import sys
import os
import asyncio
import numpy as np
import cv2
import logging
from pathlib import Path
import threading
import queue
import time

# Setup path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

import config
from preprocessing.source_loader import SourceLoader
from preprocessing.face_detector import FaceDetector
from llm.groq_stream import GroqStream
from tts.edge_tts_stream import EdgeTTSStream
from lipsync.wav2lip_processor import Wav2LipProcessor


class DisplayThread(threading.Thread):
    """Separate thread for OpenCV display operations"""
    
    def __init__(self, window_name="AI Avatar", target_fps=25):
        super().__init__(daemon=True)
        self.window_name = window_name
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.frame_queue = queue.Queue(maxsize=30)
        self.running = True
        self.fps_counter = []
        self.last_frame_time = 0
        
    def run(self):
        """Display loop - runs in separate thread"""
        try:
            # Create window
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, 1280, 720)
            
            logger.info(f"✅ Display window opened at {self.target_fps} FPS")
            
            while self.running:
                try:
                    frame = self.frame_queue.get(timeout=0.1)
                    
                    if frame is None:
                        continue
                    
                    # Calculate FPS
                    current_time = time.time()
                    if self.last_frame_time > 0:
                        fps = 1.0 / (current_time - self.last_frame_time)
                        self.fps_counter.append(fps)
                        if len(self.fps_counter) > 30:
                            self.fps_counter.pop(0)
                    self.last_frame_time = current_time
                    
                    # Add FPS overlay
                    frame = frame.copy()
                    avg_fps = np.mean(self.fps_counter) if self.fps_counter else 0
                    cv2.putText(frame, f"FPS: {avg_fps:.1f}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, "Press 'q' to quit", (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Display
                    cv2.imshow(self.window_name, frame)
                    
                    # Handle keyboard
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:
                        logger.info("Quit key pressed")
                        self.running = False
                        break
                    
                    # FPS control
                    elapsed = time.time() - current_time
                    if elapsed < self.frame_time:
                        time.sleep(self.frame_time - elapsed)
                        
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Display error: {e}")
                    break
                    
        finally:
            cv2.destroyAllWindows()
            logger.info("Display window closed")
    
    def show_frame(self, frame):
        """Add frame to display queue"""
        if not self.running:
            return False
        try:
            self.frame_queue.put(frame, block=False)
            return True
        except queue.Full:
            return False
    
    def stop(self):
        """Stop display thread"""
        self.running = False


class InteractivePipeline:
    """Interactive AI Avatar Pipeline"""
    
    def __init__(self):
        self.source_loader = None
        self.face_detector = None
        self.llm = None
        self.tts = None
        self.wav2lip = None
        self.face_coords = None
        self.display = None
        
    async def initialize(self):
        """Initialize all components"""
        try:
            print("\n" + "="*70)
            print("🤖 AI AVATAR - INTERACTIVE MODE")
            print("="*70)
            
            logger.info("Loading source video...")
            self.source_loader = SourceLoader(config.SOURCE_VIDEO_PATH)
            
            logger.info("Detecting face...")
            self.face_detector = FaceDetector()
            first_frame = self.source_loader.get_next_frame()
            self.face_coords = self.face_detector.detect_face(first_frame)
            
            logger.info("Initializing Groq API...")
            self.llm = GroqStream(api_key=config.GROQ_API_KEY, model=config.GROQ_MODEL)
            self.llm.load_model()
            
            logger.info("Initializing Edge-TTS...")
            self.tts = EdgeTTSStream(
                voice=config.TTS_VOICE,
                rate=config.TTS_RATE,
                pitch=config.TTS_PITCH,
                chunk_duration=config.TTS_CHUNK_DURATION,
                token_buffer_size=config.TOKEN_BUFFER_SIZE
            )
            
            logger.info("Loading Wav2Lip model...")
            self.wav2lip = Wav2LipProcessor(
                checkpoint_path=str(config.WAV2LIP_CHECKPOINT),
                device=config.WAV2LIP_DEVICE,
                face_size=config.WAV2LIP_FACE_SIZE,
                fps=config.WAV2LIP_FPS,
                batch_size=config.WAV2LIP_BATCH_SIZE,
                use_fp16=config.WAV2LIP_USE_FP16,
                window_overlap=config.WAV2LIP_WINDOW_OVERLAP
            )
            self.wav2lip.load_model()
            
            logger.info("Starting display window...")
            self.display = DisplayThread(window_name="🤖 AI Avatar", target_fps=25)
            self.display.start()
            time.sleep(0.5)  # Let window initialize
            
            # Show idle frame
            idle_frame = self.source_loader.get_next_frame()
            self.display.show_frame(idle_frame)
            
            print("\n✅ System ready!")
            print("="*70)
            
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise
    
    async def process_text(self, text: str):
        """Process text and display in real-time"""
        try:
            print(f"\n💭 You: {text}")
            print("-"*70)
            
            # Show thinking status
            status_frame = self.source_loader.get_next_frame().copy()
            cv2.putText(status_frame, "Thinking...", (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
            self.display.show_frame(status_frame)
            
            # Generate response
            token_queue = asyncio.Queue()
            full_response = ""
            
            stream_task = asyncio.create_task(self.llm.stream_response(text, token_queue))
            
            while True:
                try:
                    token = await asyncio.wait_for(token_queue.get(), timeout=0.1)
                    if token is None:
                        break
                    full_response += token
                except asyncio.TimeoutError:
                    if stream_task.done():
                        while not token_queue.empty():
                            token = await token_queue.get()
                            if token:
                                full_response += token
                        break
            
            await stream_task
            print(f"🤖 AI: {full_response}")
            print("-"*70)
            
            # Show speaking status
            status_frame = self.source_loader.get_next_frame().copy()
            cv2.putText(status_frame, "Speaking...", (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            self.display.show_frame(status_frame)
            
            # Generate TTS
            audio_bytes = await self.tts.text_to_audio(full_response)
            
            # Generate lip-sync
            from pydub import AudioSegment
            import io
            
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
            audio_array = np.array(audio_segment.get_array_of_samples()).astype(np.int16)
            
            x, y, w, h = self.face_coords
            face_frame = self.source_loader.get_next_frame()[y:y+h, x:x+w]
            face_frame = cv2.resize(face_frame, (96, 96))
            
            synced_frames = self.wav2lip.generate_lip_sync(face_frame, audio_array)
            
            # Display frames
            for synced_face in synced_frames:
                if not self.display.running:
                    break
                    
                synced_face_resized = cv2.resize(synced_face, (w, h))
                output_frame = self.source_loader.get_next_frame()
                output_frame[y:y+h, x:x+w] = synced_face_resized
                
                self.display.show_frame(output_frame)
                await asyncio.sleep(0.04)
            
            # Show idle frame
            idle_frame = self.source_loader.get_next_frame()
            self.display.show_frame(idle_frame)
            
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.display:
            self.display.stop()
            self.display.join(timeout=2)
        if self.source_loader:
            self.source_loader.release()


async def interactive_mode():
    """Interactive text input mode"""
    pipeline = InteractivePipeline()
    
    try:
        await pipeline.initialize()
        
        print("\n📝 TEXT INPUT MODE")
        print("Type your messages and press Enter.")
        print("Type 'quit' or 'exit' to stop.")
        print("="*70)
        
        while pipeline.display.running:
            try:
                # Get user input (run in thread to not block async)
                user_input = await asyncio.to_thread(input, "\n💬 Your message: ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.strip():
                    await pipeline.process_text(user_input)
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
        
    finally:
        pipeline.cleanup()


def main():
    """Main entry point"""
    try:
        asyncio.run(interactive_mode())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
