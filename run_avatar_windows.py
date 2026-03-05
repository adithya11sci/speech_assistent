"""
Interactive AI Avatar - Windows Compatible Version
OpenCV display runs in main thread for proper Windows support
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


class InteractivePipeline:
    """Interactive AI Avatar Pipeline - Windows Compatible"""
    
    def __init__(self):
        self.source_loader = None
        self.face_detector = None
        self.llm = None
        self.tts = None
        self.wav2lip = None
        self.face_coords = None
        self.frame_queue = queue.Queue(maxsize=30)
        self.running = True
        self.window_name = "🤖 AI Avatar - Windows"
        self.fps_counter = []
        self.last_frame_time = time.time()
        
    async def initialize(self):
        """Initialize all components"""
        try:
            print("\n" + "="*70)
            print("🤖 AI AVATAR - WINDOWS COMPATIBLE MODE")
            print("="*70)
            
            # Load source (image or video based on config)
            source_path = config.SOURCE_IMAGE_PATH if config.SOURCE_TYPE == "image" else config.SOURCE_VIDEO_PATH
            logger.info(f"Loading source {config.SOURCE_TYPE}: {source_path}")
            self.source_loader = SourceLoader(source_path)
            
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
            
            # Create OpenCV window in main thread
            logger.info("Creating display window...")
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, 1280, 720)
            
            # Show idle frame
            idle_frame = self.source_loader.get_next_frame()
            self.show_frame(idle_frame)
            
            print("\n✅ System ready!")
            print("="*70)
            
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise
    
    def show_frame(self, frame):
        """Display frame with FPS counter (must be called from main thread)"""
        if not self.running:
            return False
        
        try:
            # Calculate FPS
            current_time = time.time()
            if self.last_frame_time > 0:
                fps = 1.0 / (current_time - self.last_frame_time)
                self.fps_counter.append(fps)
                if len(self.fps_counter) > 30:
                    self.fps_counter.pop(0)
            self.last_frame_time = current_time
            
            # Add overlays
            frame = frame.copy()
            avg_fps = np.mean(self.fps_counter) if self.fps_counter else 0
            cv2.putText(frame, f"FPS: {avg_fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display
            cv2.imshow(self.window_name, frame)
            
            # Handle keyboard (non-blocking)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                logger.info("Quit key pressed")
                self.running = False
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Display error: {e}")
            return False
    
    async def process_text(self, text: str):
        """Process text and display in real-time"""
        try:
            print(f"\n💭 You: {text}")
            print("-"*70)
            
            # Show thinking status
            status_frame = self.source_loader.get_next_frame().copy()
            cv2.putText(status_frame, "Thinking...", (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
            self.show_frame(status_frame)
            
            # Get LLM response
            token_queue = asyncio.Queue()
            llm_task = asyncio.create_task(
                self.llm.stream_response(text, token_queue)
            )
            
            # Stream to TTS
            audio_queue = asyncio.Queue()
            tts_task = asyncio.create_task(
                self.tts.tokens_to_audio_chunks(token_queue, audio_queue)
            )
            
            # Show generating status
            gen_frame = self.source_loader.get_next_frame().copy()
            cv2.putText(gen_frame, "Generating response...", (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            self.show_frame(gen_frame)
            
            # Process audio chunks
            x, y, w, h = self.face_coords
            response_text = ""
            
            while True:
                audio_bytes = await audio_queue.get()
                
                if audio_bytes is None:
                    break
                
                # Convert audio to numpy
                from pydub import AudioSegment
                import io
                
                audio_segment = AudioSegment.from_file(
                    io.BytesIO(audio_bytes),
                    format="mp3"
                )
                audio_segment = audio_segment.set_frame_rate(16000)
                audio_segment = audio_segment.set_channels(1)
                audio_array = np.array(audio_segment.get_array_of_samples()).astype(np.int16)
                
                # Get face frame
                full_frame = self.source_loader.get_next_frame()
                face_frame = full_frame[y:y+h, x:x+w]
                face_frame = cv2.resize(face_frame, (config.WAV2LIP_FACE_SIZE, config.WAV2LIP_FACE_SIZE))
                
                # Generate lip sync (in thread to not block main)
                synced_frames = await asyncio.to_thread(
                    self.wav2lip.generate_lip_sync,
                    face_frame,
                    audio_array
                )
                
                # Display synced frames in main thread
                for synced_face in synced_frames:
                    if not self.running:
                        break
                    
                    synced_face_resized = cv2.resize(synced_face, (w, h))
                    output_frame = self.source_loader.get_next_frame()
                    output_frame[y:y+h, x:x+w] = synced_face_resized
                    
                    # Update display (main thread)
                    self.show_frame(output_frame)
                    await asyncio.sleep(0.001)  # Small delay for smooth playback
            
            # Wait for tasks to complete
            await llm_task
            await tts_task
            
            # Show idle frame
            idle_frame = self.source_loader.get_next_frame()
            self.show_frame(idle_frame)
            
            print("="*70)
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            import traceback
            traceback.print_exc()
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up...")
        self.running = False
        cv2.destroyAllWindows()
        if self.source_loader:
            self.source_loader.release()


async def interactive_mode_async(pipeline):
    """Async input handler"""
    print("\n📝 TEXT INPUT MODE")
    print("Type your messages and press Enter.")
    print("Type 'quit' or 'exit' to stop.")
    print("="*70)
    
    while pipeline.running:
        try:
            # Get user input in thread pool
            user_input = await asyncio.to_thread(
                input, "\n💬 Your message: "
            )
            
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


async def main_async():
    """Main async function"""
    pipeline = InteractivePipeline()
    
    try:
        # Initialize pipeline
        await pipeline.initialize()
        
        # Run interactive mode
        await interactive_mode_async(pipeline)
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pipeline.cleanup()


def main():
    """Main entry point"""
    try:
        # Run async event loop
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
