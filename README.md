# Real-Time Conversational AI Avatar System

🎯 **Production-ready system for real-time AI avatar with lip synchronization**

A fully local, GPU-accelerated conversational AI avatar that maintains natural lip sync with sub-2 second latency.

---

## 🏗️ System Architecture

```
Microphone → Whisper STT → Llama 3.1 LLM → Edge-TTS → Wav2Lip → OpenCV Renderer
                ↓              ↓              ↓          ↓            ↓
          [audio_queue] [transcript_q] [token_q] [tts_q] [lip_q] [frame_q]
```

**Complete async streaming pipeline with:**
- Voice Activity Detection (VAD)
- Streaming Speech-to-Text (Faster-Whisper)
- Streaming LLM responses (Llama.cpp)
- Chunked Text-to-Speech (Edge-TTS)
- Real-time lip synchronization (Wav2Lip)
- Optimized frame rendering (OpenCV)

---

## 📋 Requirements

### Hardware
- **GPU**: NVIDIA RTX 4070 or better (16GB VRAM minimum)
- **RAM**: 32GB recommended
- **Microphone**: Any USB/built-in microphone
- **OS**: Windows/Linux with CUDA support

### Software
- Python 3.9+
- CUDA 11.8+ / CUDA 12.x
- PyTorch with CUDA support
- NVIDIA drivers (latest recommended)

---

## 📂 Project Structure

```
inter_view/
├── src/
│   ├── main.py                # Entry point
│   ├── config.py              # Configuration
│   ├── pipeline.py            # Main orchestrator
│   │
│   ├── preprocessing/         # Source media & face detection
│   │   ├── source_loader.py
│   │   └── face_detector.py
│   │
│   ├── audio/                 # Audio capture
│   │   ├── microphone.py
│   │   └── audio_utils.py
│   │
│   ├── stt/                   # Speech-to-Text
│   │   └── whisper_stream.py
│   │
│   ├── llm/                   # Language Model
│   │   └── llama_stream.py
│   │
│   ├── tts/                   # Text-to-Speech
│   │   └── edge_tts_stream.py
│   │
│   ├── lipsync/               # Lip Synchronization
│   │   └── wav2lip_processor.py
│   │
│   └── renderer/              # Frame Rendering
│       └── frame_renderer.py
│
├── models/                    # ⚠️ PLACE YOUR MODELS HERE
│   ├── whisper/
│   │   └── small.en/          # Faster-Whisper model
│   │
│   ├── llama/
│   │   └── llama-3.1-8b-instruct-q4_k_m.gguf  # Llama GGUF model
│   │
│   └── wav2lip/
│       ├── wav2lip_gan.pth    # Wav2Lip checkpoint
│       └── face_detection.pth # Face detection model (optional)
│
├── input/                     # ⚠️ PLACE YOUR SOURCE MEDIA HERE
│   ├── images/
│   │   └── avatar.jpg         # Source image
│   │
│   └── videos/
│       └── avatar.mp4         # Source video (recommended)
│
├── output/                    # Output videos (if enabled)
│
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### 1. Clone & Setup Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux)
source venv/bin/activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Download Models

#### **Faster-Whisper** (Speech-to-Text)
```powershell
# The model will auto-download on first run
# Or download manually and place in: models/whisper/small.en/
```

#### **Llama 3.1 8B** (LLM)
Download GGUF quantized model:
- **Source**: [HuggingFace - Llama-3.1-8B-Instruct-GGUF](https://huggingface.co/models?search=llama-3.1-8b-instruct-gguf)
- **Recommended**: Q4_K_M quantization (~4.9GB)
- **Place in**: `models/llama/llama-3.1-8b-instruct-q4_k_m.gguf`

#### **Wav2Lip** (Lip Sync)
Download checkpoint:
- **Source**: [Wav2Lip GitHub - Checkpoints](https://github.com/Rudrabha/Wav2Lip#getting-the-weights)
- **Download**: `wav2lip_gan.pth` (official checkpoint)
- **Place in**: `models/wav2lip/wav2lip_gan.pth`

**Important**: Also clone/download the Wav2Lip repository code:
```powershell
git clone https://github.com/Rudrabha/Wav2Lip.git
# Add Wav2Lip to Python path or copy models/ folder to your project
```

### 4. Prepare Source Media

**Option A: Static Image**
- Place avatar image in `input/images/avatar.jpg`
- Set `SOURCE_TYPE = "image"` in config.py

**Option B: Video (RECOMMENDED)**
- Place short video (3-10 seconds) in `input/videos/avatar.mp4`
- Set `SOURCE_TYPE = "video"` in config.py
- Video provides more realistic results with natural head movements

---

## ⚙️ Configuration

Edit `src/config.py` to customize:

### Key Settings

```python
# Source Media
SOURCE_TYPE = "video"  # or "image"
SOURCE_VIDEO_PATH = INPUT_VIDEOS_DIR / "avatar.mp4"
SOURCE_IMAGE_PATH = INPUT_IMAGES_DIR / "avatar.jpg"

# Model Paths
WHISPER_MODEL_SIZE = "small.en"  # tiny.en / base.en / small.en
LLAMA_MODEL_PATH = LLAMA_MODEL_DIR / "llama-3.1-8b-instruct-q4_k_m.gguf"
WAV2LIP_CHECKPOINT = WAV2LIP_MODEL_DIR / "wav2lip_gan.pth"

# GPU Settings
LLAMA_N_GPU_LAYERS = -1  # -1 = all layers to GPU
WHISPER_DEVICE = "cuda"
WAV2LIP_DEVICE = "cuda"

# Performance
TOKEN_BUFFER_SIZE = 15  # Buffer tokens before TTS
TTS_CHUNK_DURATION = 0.5  # seconds
RENDER_FPS = 25

# TTS Voice
TTS_VOICE = "en-US-AriaNeural"  # en-US-JennyNeural, en-US-GuyNeural, etc.
```

---

## 🎬 Usage

### Run the System

```powershell
cd src
python main.py
```

### What Happens:
1. ✅ All models load into memory
2. ✅ Face detected and cached from source media
3. ✅ Microphone activated with VAD
4. ✅ OpenCV window opens showing avatar
5. 🎤 **Start speaking!**
   - System listens continuously
   - Detects speech and silence
   - Transcribes with Whisper
   - Generates response with Llama
   - Synthesizes speech with Edge-TTS
   - Lip syncs with Wav2Lip
   - Renders in real-time

### Controls:
- **Speak** into microphone to interact
- **Press 'q' or ESC** to quit
- System processes speech after detecting silence (default: 1 second)

---

## 🔧 Optimization Tips

### For RTX 4070 (16GB VRAM):

**Optimal Settings:**
```python
# Use Q4 quantization for Llama
LLAMA_MODEL = "llama-3.1-8b-instruct-q4_k_m.gguf"

# Use small Whisper model
WHISPER_MODEL_SIZE = "small.en"

# Enable FP16 for Wav2Lip
WAV2LIP_USE_FP16 = True
WAV2LIP_FACE_SIZE = 256  # 256 is faster, 384 is higher quality

# Preload video frames
VIDEO_PRELOAD_ALL_FRAMES = True  # Loads entire video into RAM
```

### Memory Management:
- **Total VRAM usage**: ~10-12GB
- **RAM usage**: ~8-10GB (with preloaded video frames)
- **Latency**: 1.5-2.5 seconds from speech end to first lip movement

### If VRAM is limited:
```python
# Use smaller models
WHISPER_MODEL_SIZE = "base.en"  # Instead of small.en
LLAMA_MODEL = "llama-3.1-8b-instruct-q5_k_m.gguf"  # Less compressed

# Reduce face resolution
WAV2LIP_FACE_SIZE = 192  # Instead of 256

# Disable video preloading
VIDEO_PRELOAD_ALL_FRAMES = False  # Streams from disk instead
```

---

## 🐛 Troubleshooting

### Models Not Found
**Error**: `FileNotFoundError: Model not found`

**Solution**:
1. Verify model files exist in `models/` directory
2. Check file names match config.py exactly
3. Ensure models are not corrupted (re-download if needed)

### CUDA Out of Memory
**Error**: `RuntimeError: CUDA out of memory`

**Solution**:
1. Close other GPU applications
2. Reduce `WAV2LIP_FACE_SIZE` to 192 or 128
3. Use smaller Whisper model: `tiny.en` or `base.en`
4. Reduce `LLAMA_N_CTX` to 2048

### Poor Lip Sync Quality
**Issue**: Lips don't match speech well

**Solution**:
1. Ensure source media has clear face visibility
2. Use video instead of static image
3. Increase `WAV2LIP_FACE_SIZE` to 384
4. Adjust `WAV2LIP_BOX_EXPANSION` (default: 0.1)
5. Verify face detection is accurate (check logs)

### Audio Issues
**Issue**: Microphone not working / No transcription

**Solution**:
1. Check microphone permissions
2. Adjust `SILENCE_THRESHOLD` in config.py
3. Test microphone: `python -c "import pyaudio; print(pyaudio.PyAudio().get_default_input_device_info())"`
4. Increase `SILENCE_DURATION` if speech cuts off early

### Slow Response Time
**Issue**: Avatar takes too long to respond

**Solution**:
1. Reduce `TOKEN_BUFFER_SIZE` (try 10 instead of 15)
2. Decrease `TTS_CHUNK_DURATION` to 0.3
3. Use `WHISPER_BEAM_SIZE = 1` (greedy decoding)
4. Ensure GPU is being used (check logs)
5. Close background applications

---

## 📊 Performance Metrics

**Expected performance on RTX 4070:**

| Component | Processing Time | Notes |
|-----------|----------------|-------|
| **STT** (Whisper) | 200-400ms | For 3-5 sec audio |
| **LLM** (Llama) | 800-1200ms | First 15 tokens |
| **TTS** (Edge-TTS) | 300-500ms | Per chunk |
| **Lip Sync** (Wav2Lip) | 100-200ms | Per 0.5s chunk |
| **End-to-End** | **1.5-2.5s** | Speech end → first lip movement |

---

## 🎯 Advanced Features

### Custom System Prompt

Edit in `config.py`:
```python
SYSTEM_PROMPT = """You are a professional interviewer. 
Ask insightful questions and provide thoughtful feedback."""
```

### Save Output Video

Enable in `config.py`:
```python
SAVE_OUTPUT_VIDEO = True
OUTPUT_VIDEO_PATH = OUTPUT_DIR / "session.mp4"
```

### Change Voice

Available voices:
- `en-US-AriaNeural` (Female, friendly)
- `en-US-JennyNeural` (Female, professional)
- `en-US-GuyNeural` (Male, casual)
- `en-US-DavisNeural` (Male, professional)

Get full list:
```python
import asyncio
from tts import EdgeTTSStream
asyncio.run(EdgeTTSStream.get_available_voices())
```

---

## 📝 Notes

### Wav2Lip Integration
This codebase expects Wav2Lip repository to be available. Either:
1. Clone Wav2Lip repo and add to Python path
2. Copy required files from Wav2Lip repo
3. Install as package: `pip install git+https://github.com/Rudrabha/Wav2Lip.git`

### Edge-TTS
- Requires internet connection for TTS synthesis
- For fully offline operation, replace with local TTS (e.g., Coqui TTS, Piper TTS)

### Face Detection
- Face is detected once at startup and cached
- For videos with camera movement, disable caching:
  ```python
  CACHE_FACE_DETECTION = False
  ```

---

## 🚧 Future Enhancements

**Potential improvements:**
- [ ] Emotion detection and expression mapping
- [ ] Multi-language support
- [ ] Real-time face tracking (not cached)
- [ ] Voice cloning for personalized TTS
- [ ] WebRTC streaming for remote access
- [ ] Fine-tuned Wav2Lip for specific faces
- [ ] Gesture synthesis from text
- [ ] Interactive UI controls

---

## 📄 License

This project structure and code is provided as-is. Make sure to comply with licenses of:
- Faster-Whisper (MIT)
- Llama models (Meta license)
- Wav2Lip (Non-commercial license)
- Edge-TTS (Custom license)

---

## 🙏 Acknowledgments

Built with:
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Optimized Whisper implementation
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Efficient LLM inference
- [Wav2Lip](https://github.com/Rudrabha/Wav2Lip) - Lip synchronization
- [Edge-TTS](https://github.com/rany2/edge-tts) - Microsoft Edge TTS
- PyTorch, OpenCV, asyncio

---

## 💬 Support

For issues specific to individual components:
- Wav2Lip: https://github.com/Rudrabha/Wav2Lip/issues
- Faster-Whisper: https://github.com/guillaumekln/faster-whisper/issues
- Llama.cpp: https://github.com/ggerganov/llama.cpp/issues

---

**Happy building! 🎉**
