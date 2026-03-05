"""
Configuration file for Real-Time Conversational AI Avatar System
All paths and parameters are centralized here
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== PROJECT PATHS ==========
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# Source Media
INPUT_IMAGES_DIR = INPUT_DIR / "images"
INPUT_VIDEOS_DIR = INPUT_DIR / "videos"

# Model Directories
WHISPER_MODEL_DIR = MODELS_DIR / "whisper"
LLAMA_MODEL_DIR = MODELS_DIR / "llama"
WAV2LIP_MODEL_DIR = MODELS_DIR / "wav2lip"

# Create directories if they don't exist
for directory in [MODELS_DIR, INPUT_IMAGES_DIR, INPUT_VIDEOS_DIR, OUTPUT_DIR, 
                  WHISPER_MODEL_DIR, LLAMA_MODEL_DIR, WAV2LIP_MODEL_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ========== MODEL PATHS ==========
# Faster-Whisper
WHISPER_MODEL_SIZE = "small.en"  # Options: tiny.en, base.en, small.en, medium.en, large-v2
WHISPER_MODEL_PATH = WHISPER_MODEL_DIR / WHISPER_MODEL_SIZE

# Llama
LLAMA_MODEL_PATH = LLAMA_MODEL_DIR / "llama-3.1-8b-instruct-q4_k_m.gguf"  # Place your GGUF model here

# Wav2Lip
WAV2LIP_CHECKPOINT = WAV2LIP_MODEL_DIR / "wav2lip_gan.pth"  # Place wav2lip_gan.pth here
WAV2LIP_FACE_DETECTION_MODEL = WAV2LIP_MODEL_DIR / "face_detection.pth"

# ========== AUDIO SETTINGS ==========
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_SIZE = 1024
AUDIO_CHANNELS = 1
AUDIO_FORMAT = "int16"

# Silence detection for VAD
SILENCE_THRESHOLD = 500  # RMS threshold
SILENCE_DURATION = 1.0   # seconds of silence to trigger end of speech

# ========== STT SETTINGS (Faster-Whisper) ==========
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"  # float16 for GPU, int8 for CPU
WHISPER_BEAM_SIZE = 1  # 1 for speed, 5 for accuracy
WHISPER_VAD_FILTER = True
WHISPER_VAD_THRESHOLD = 0.5

# ========== LLM SETTINGS ==========
# Choose LLM backend: "local" (llama.cpp) or "groq" (Groq API)
LLM_BACKEND = "groq"  # "local" or "groq"

# Groq API Settings (when LLM_BACKEND = "groq")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Set your API key in .env file
GROQ_MODEL = "llama-3.1-8b-instant"  # Options: llama-3.1-8b-instant, mixtral-8x7b-32768, etc.

# Local Llama Settings (when LLM_BACKEND = "local")
LLAMA_N_GPU_LAYERS = -1  # -1 = offload all layers to GPU
LLAMA_N_CTX = 4096       # Context window
LLAMA_N_BATCH = 512      # Batch size for prompt processing
LLAMA_N_THREADS = 8      # CPU threads

# Common LLM Settings (applies to both backends)
LLM_TEMPERATURE = 0.7
LLM_TOP_P = 0.9
LLM_TOP_K = 40
LLM_MAX_TOKENS = 512
LLM_STREAM = True

# System prompt for the avatar
SYSTEM_PROMPT = """You are a helpful, friendly AI assistant. Keep your responses concise and conversational. 
Respond naturally as if having a real-time conversation. Keep answers under 3-4 sentences when possible."""

# Token buffering before starting TTS
TOKEN_BUFFER_SIZE = 15  # Buffer 15-20 tokens before starting TTS

# ========== TTS SETTINGS (Edge-TTS) ==========
TTS_VOICE = "en-US-AriaNeural"  # Options: en-US-JennyNeural, en-US-GuyNeural, etc.
TTS_RATE = "+0%"  # Speed: -50% to +100%
TTS_PITCH = "+0Hz"
TTS_CHUNK_DURATION = 0.5  # seconds per audio chunk

# ========== WAV2LIP SETTINGS ==========
WAV2LIP_DEVICE = "cuda"
WAV2LIP_BATCH_SIZE = 128  # Increased for faster GPU batch inference
WAV2LIP_FPS = 25
WAV2LIP_FACE_SIZE = 192  # 192x192 for faster speed (was 256)
WAV2LIP_FACE_DETECTION_BATCH_SIZE = 8
WAV2LIP_BOX_EXPANSION = 0.1  # Expand face box by 10%

# Sliding window for smooth lip sync
WAV2LIP_WINDOW_OVERLAP = 0.2  # seconds
WAV2LIP_USE_FP16 = True

# ========== SOURCE MEDIA SETTINGS ==========
SOURCE_TYPE = "video"  # "image" or "video"
SOURCE_IMAGE_PATH = INPUT_IMAGES_DIR / "avatar.jpg"  # Your source image
SOURCE_VIDEO_PATH = INPUT_VIDEOS_DIR / "avatar.mp4"  # Your source video

# Video preprocessing
VIDEO_FPS = 25
VIDEO_LOOP = True  # Loop video frames continuously
VIDEO_PRELOAD_ALL_FRAMES = True  # Load all frames into memory (faster)

# ========== RENDERING SETTINGS ==========
RENDER_FPS = 25
RENDER_WINDOW_NAME = "AI Avatar"
RENDER_FULLSCREEN = False
RENDER_WIDTH = 720
RENDER_HEIGHT = 1280

# ========== PIPELINE SETTINGS ==========
# Queue sizes for async pipeline
AUDIO_QUEUE_SIZE = 100
TRANSCRIPT_QUEUE_SIZE = 50
TOKEN_QUEUE_SIZE = 200
TTS_QUEUE_SIZE = 50
LIP_QUEUE_SIZE = 50
FRAME_QUEUE_SIZE = 30

# Performance monitoring
ENABLE_FPS_DISPLAY = True
ENABLE_LATENCY_LOGGING = True
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# ========== OPTIMIZATION FLAGS ==========
USE_FLASH_ATTENTION = True  # For Llama
PRELOAD_MODELS = True  # Load all models at startup
CACHE_FACE_DETECTION = True  # Detect face once and cache
USE_MEMORY_POOL = True  # Reuse memory buffers

# ========== DEBUG SETTINGS ==========
SAVE_OUTPUT_VIDEO = False  # Save rendered output to file
OUTPUT_VIDEO_PATH = OUTPUT_DIR / "output.mp4"
ENABLE_PROFILING = False  # Enable performance profiling
