"""
Main Pipeline Orchestrator
Coordinates all components in async streaming pipeline
"""
import asyncio
import logging
from pathlib import Path
import time

# Import all modules
from preprocessing import SourceLoader, FaceDetector
from audio import MicrophoneStream, AudioProcessor
from stt import WhisperStream
from llm import LlamaStream, GroqStream
from tts import EdgeTTSStream
from lipsync import Wav2LipProcessor
from renderer import FrameRenderer

# Import config
import config

logger = logging.getLogger(__name__)


class AvatarPipeline:
    """Main pipeline orchestrator for real-time AI avatar"""
    
    def __init__(self):
        """Initialize pipeline components"""
        logger.info("Initializing Avatar Pipeline...")
        
        # Components
        self.source_loader = None
        self.face_detector = None
        self.microphone = None
        self.whisper = None
        self.llama = None
        self.tts = None
        self.wav2lip = None
        self.renderer = None
        
        # Async queues
        self.audio_queue = asyncio.Queue(maxsize=config.AUDIO_QUEUE_SIZE)
        self.transcript_queue = asyncio.Queue(maxsize=config.TRANSCRIPT_QUEUE_SIZE)
        self.token_queue = asyncio.Queue(maxsize=config.TOKEN_QUEUE_SIZE)
        self.tts_queue = asyncio.Queue(maxsize=config.TTS_QUEUE_SIZE)
        self.lip_queue = asyncio.Queue(maxsize=config.LIP_QUEUE_SIZE)
        self.frame_queue = asyncio.Queue(maxsize=config.FRAME_QUEUE_SIZE)
        
        # State
        self.face_coords = None
        self.is_running = False
        self.tasks = []
        
    def initialize_components(self):
        """Initialize all pipeline components"""
        try:
            # 1. Source Media Loader
            logger.info("Loading source media...")
            source_path = config.SOURCE_VIDEO_PATH if config.SOURCE_TYPE == "video" else config.SOURCE_IMAGE_PATH
            
            self.source_loader = SourceLoader(
                source_path=source_path,
                source_type=config.SOURCE_TYPE,
                preload_all=config.VIDEO_PRELOAD_ALL_FRAMES,
                target_fps=config.VIDEO_FPS,
                loop=config.VIDEO_LOOP
            )
            
            # 2. Face Detector
            logger.info("Initializing face detector...")
            self.face_detector = FaceDetector(
                face_size=config.WAV2LIP_FACE_SIZE,
                box_expansion=config.WAV2LIP_BOX_EXPANSION
            )
            
            # Detect face once and cache
            first_frame = self.source_loader.get_next_frame()
            self.face_coords = self.face_detector.detect_face(first_frame, use_cache=True)
            
            if self.face_coords is None:
                logger.warning("No face detected, using full frame")
                h, w = first_frame.shape[:2]
                self.face_coords = (0, 0, w, h)
            
            logger.info(f"Face detected at: {self.face_coords}")
            
            # 3. Microphone
            logger.info("Initializing microphone...")
            self.microphone = MicrophoneStream(
                sample_rate=config.AUDIO_SAMPLE_RATE,
                chunk_size=config.AUDIO_CHUNK_SIZE,
                channels=config.AUDIO_CHANNELS,
                silence_threshold=config.SILENCE_THRESHOLD,
                silence_duration=config.SILENCE_DURATION
            )
            
            # 4. Whisper STT
            logger.info("Loading Whisper model...")
            self.whisper = WhisperStream(
                model_size=config.WHISPER_MODEL_SIZE,
                model_path=str(config.WHISPER_MODEL_PATH) if config.WHISPER_MODEL_PATH.exists() else None,
                device=config.WHISPER_DEVICE,
                compute_type=config.WHISPER_COMPUTE_TYPE,
                beam_size=config.WHISPER_BEAM_SIZE,
                vad_filter=config.WHISPER_VAD_FILTER,
                vad_threshold=config.WHISPER_VAD_THRESHOLD,
                sample_rate=config.AUDIO_SAMPLE_RATE
            )
            self.whisper.load_model()
            
            # 5. LLM (Groq or Llama)
            if config.LLM_BACKEND == "groq":
                logger.info("Initializing Groq API...")
                self.llama = GroqStream(
                    api_key=config.GROQ_API_KEY,
                    model=config.GROQ_MODEL,
                    temperature=config.LLM_TEMPERATURE,
                    top_p=config.LLM_TOP_P,
                    max_tokens=config.LLM_MAX_TOKENS,
                    system_prompt=config.SYSTEM_PROMPT
                )
                self.llama.load_model()
            else:
                logger.info("Loading local Llama model...")
                self.llama = LlamaStream(
                    model_path=str(config.LLAMA_MODEL_PATH),
                    n_gpu_layers=config.LLAMA_N_GPU_LAYERS,
                    n_ctx=config.LLAMA_N_CTX,
                    n_batch=config.LLAMA_N_BATCH,
                    n_threads=config.LLAMA_N_THREADS,
                    temperature=config.LLM_TEMPERATURE,
                    top_p=config.LLM_TOP_P,
                    top_k=config.LLM_TOP_K,
                    max_tokens=config.LLM_MAX_TOKENS,
                    system_prompt=config.SYSTEM_PROMPT,
                    use_flash_attention=config.USE_FLASH_ATTENTION
                )
                self.llama.load_model()
            
            # 6. Edge-TTS
            logger.info("Initializing TTS...")
            self.tts = EdgeTTSStream(
                voice=config.TTS_VOICE,
                rate=config.TTS_RATE,
                pitch=config.TTS_PITCH,
                chunk_duration=config.TTS_CHUNK_DURATION,
                token_buffer_size=config.TOKEN_BUFFER_SIZE
            )
            
            # 7. Wav2Lip
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
            
            # 8. Renderer
            logger.info("Initializing renderer...")
            self.renderer = FrameRenderer(
                window_name=config.RENDER_WINDOW_NAME,
                target_fps=config.RENDER_FPS,
                width=config.RENDER_WIDTH,
                height=config.RENDER_HEIGHT,
                fullscreen=config.RENDER_FULLSCREEN,
                show_fps=config.ENABLE_FPS_DISPLAY,
                save_output=config.SAVE_OUTPUT_VIDEO,
                output_path=str(config.OUTPUT_VIDEO_PATH) if config.SAVE_OUTPUT_VIDEO else None
            )
            
            logger.info("All components initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def run(self):
        """Run the complete pipeline"""
        try:
            self.is_running = True
            
            # Start microphone
            self.microphone.start()
            
            # Start renderer
            self.renderer.start()
            
            # Show idle frame
            idle_frame = self.source_loader.get_next_frame()
            self.renderer.display_idle_frame(idle_frame, "Ready - Start speaking...")
            
            logger.info("Pipeline running! Speak into the microphone...")
            logger.info("Press 'q' or ESC to quit")
            
            # Create all pipeline tasks
            self.tasks = [
                # Audio capture
                asyncio.create_task(
                    self.microphone.stream_audio(self.audio_queue),
                    name="audio_capture"
                ),
                
                # Speech-to-Text
                asyncio.create_task(
                    self.whisper.transcribe_stream(self.audio_queue, self.transcript_queue),
                    name="stt"
                ),
                
                # LLM processing
                asyncio.create_task(
                    self.llama.process_transcripts(self.transcript_queue, self.token_queue),
                    name="llm"
                ),
                
                # Text-to-Speech
                asyncio.create_task(
                    self.tts.tokens_to_audio_chunks(self.token_queue, self.tts_queue),
                    name="tts"
                ),
                
                # Lip sync
                asyncio.create_task(
                    self.wav2lip.process_audio_stream(
                        self.tts_queue,
                        self.frame_queue,
                        self.source_loader.get_next_frame,
                        self.face_coords
                    ),
                    name="lipsync"
                ),
                
                # Rendering
                asyncio.create_task(
                    self.renderer.render_stream(self.frame_queue),
                    name="renderer"
                )
            ]
            
            # Wait for all tasks or until renderer stops
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Cleanup and shutdown pipeline"""
        logger.info("Shutting down pipeline...")
        
        self.is_running = False
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Cleanup components
        if self.microphone:
            self.microphone.stop()
        
        if self.renderer:
            self.renderer.stop()
        
        if self.source_loader:
            self.source_loader.release()
        
        if self.whisper:
            self.whisper.unload_model()
        
        if self.llama:
            self.llama.unload_model()
        
        if self.wav2lip:
            self.wav2lip.unload_model()
        
        logger.info("Pipeline shutdown complete")


async def main():
    """Main entry point"""
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("=" * 80)
    logger.info("Real-Time Conversational AI Avatar System")
    logger.info("=" * 80)
    
    # Create and run pipeline
    pipeline = AvatarPipeline()
    pipeline.initialize_components()
    await pipeline.run()


if __name__ == "__main__":
    asyncio.run(main())
