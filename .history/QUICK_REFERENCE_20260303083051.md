# 🚀 QUICK REFERENCE - AI Avatar System

## ⚡ Ultra-Quick Start (If Everything is Set Up)

```bash
# Activate environment
venv\Scripts\activate         # Windows
source venv/bin/activate      # Linux/Mac

# Run the system
cd src
python main.py

# Press Ctrl+C to stop
```

---

## 📂 Required Files Checklist

### Must Have:
- ✅ `models/llama/` - Llama 3.1 8B GGUF model (~5GB)
- ✅ `models/wav2lip/` - wav2lip_gan.pth (~150MB)  
- ✅ `Wav2Lip/` - Cloned repository
- ✅ `input/` - Avatar image/video

### Auto-Created:
- `output/` - Recordings (optional)
- `logs/` - System logs

---

## 🔧 Common Commands

### New PC Setup
```bash
# Automated setup (RECOMMENDED)
python setup_target_pc.py

# Manual verification
python verify_setup.py
```

### Package for Transfer
```bash
# Create deployment package
python package_creator.py
```

### Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux/Mac

# Deactivate
deactivate
```

### Install Dependencies
```bash
# PyTorch (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Llama with GPU
set CMAKE_ARGS=-DLLAMA_CUBLAS=on
pip install llama-cpp-python --force-reinstall --no-cache-dir

# All other packages
pip install -r requirements.txt
```

---

## 🎮 Controls

### During Execution:
- **Speak into microphone** - System listens automatically
- **Wait for AI response** - Avatar will lip-sync
- **Ctrl+C** - Stop system gracefully

### Voice Activity Detection:
- **RMS Threshold**: 0.02 (adjust in config.py)
- **Silence Duration**: 1.0s before processing

---

## ⚙️ Key Configuration (config.py)

### Source Media
```python
SOURCE_IMAGE = "input/avatar.jpg"        # OR
SOURCE_VIDEO = "input/avatar.mp4"
```

### Performance Tuning
```python
# GPU layers (-1 = all GPU)
LLAMA_N_GPU_LAYERS = -1

# Response speed
TOKEN_BUFFER_SIZE = 15  # Lower=faster start, choppier
TTS_CHUNK_DURATION = 0.5  # Seconds per audio chunk

# Lip sync quality
WAV2LIP_USE_FP16 = True  # Faster, lower VRAM
WAV2LIP_BATCH_SIZE = 1   # Real-time processing
```

### Audio Settings
```python
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
SILENCE_DURATION = 1.0  # Seconds
RMS_THRESHOLD = 0.02    # Voice detection sensitivity
```

---

## 🔍 Troubleshooting Quick Fixes

### "CUDA out of memory"
```python
# In config.py:
LLAMA_N_CTX = 1024          # Reduce from 2048
WAV2LIP_USE_FP16 = True     # Enable if False
```

### "No face detected"
```python
# In config.py:
FACE_DETECTION_CONFIDENCE = 0.5  # Lower from 0.97
```

### "Audio not detected"
```python
# In config.py:
RMS_THRESHOLD = 0.01  # Lower from 0.02
```

### Slow response time
```python
# In config.py:
TOKEN_BUFFER_SIZE = 10     # Reduce from 15
WHISPER_MODEL_SIZE = "tiny.en"  # From "small.en"
LLAMA_N_GPU_LAYERS = -1    # Max GPU usage
```

---

## 📊 Performance Benchmarks (RTX 4070)

| Component | Latency | VRAM Usage |
|-----------|---------|------------|
| Whisper STT | ~200ms | 1.5GB |
| Llama LLM (first token) | ~300ms | 6GB |
| Llama LLM (streaming) | ~50ms/token | - |
| Edge-TTS | ~100ms/chunk | 0 (CPU) |
| Wav2Lip | ~30ms/frame | 2GB |
| **Total (optimized)** | **1.5-2.5s** | **~10GB** |

---

## 🌐 Model Download Links (Quick)

### Llama 3.1 8B
```
https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF
File: Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
Place in: models/llama/
```

### Wav2Lip
```
https://github.com/Rudrabha/Wav2Lip
Download: wav2lip_gan.pth (from releases)
Place in: models/wav2lip/
```

### Whisper
```
Auto-downloads on first run
Location: ~/.cache/huggingface/
```

---

## 📁 Directory Structure (Minimal)

```
inter_view/
├── src/
│   ├── config.py           # ← Edit this for settings
│   └── main.py             # ← Run this to start
├── models/
│   ├── llama/
│   │   └── *.gguf         # ← Place Llama model here
│   └── wav2lip/
│       └── wav2lip_gan.pth  # ← Place Wav2Lip here
├── input/
│   └── avatar.jpg          # ← Your avatar source
├── Wav2Lip/                # ← Clone from GitHub
├── venv/                   # ← Virtual environment
└── requirements.txt
```

---

## 🆘 Quick Support

1. **Check setup**: `python verify_setup.py`
2. **View logs**: Check console output
3. **GPU status**: `nvidia-smi` in terminal
4. **Python version**: `python --version` (need 3.9+)

---

## 📖 Full Documentation

- **README.md** - Complete system overview
- **QUICKSTART.md** - Detailed setup guide
- **DEPLOYMENT_GUIDE.md** - Transfer to new PC
- **MODEL_DOWNLOAD_LINKS.md** - Model downloads
- **PROJECT_SUMMARY.md** - Architecture details

---

## 🎯 System Requirements

### Minimum:
- NVIDIA GPU with 10GB+ VRAM (RTX 3080 or better)
- 16GB RAM
- 15GB disk space
- Python 3.9+
- CUDA 11.8 or 12.1

### Recommended:
- RTX 4070/4080
- 32GB RAM  
- SSD storage
- Python 3.10/3.11

---

## ⏱️ Time Estimates

- Fresh setup: 20-30 minutes
- Model downloads: 10-20 minutes
- First run (cache building): 2-3 minutes
- Subsequent runs: Instant

---

**Last Updated**: 2024
**Version**: 1.0.0
