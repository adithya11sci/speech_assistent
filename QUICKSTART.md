# 🚀 Quick Start Guide

Complete setup guide for the Real-Time Conversational AI Avatar system.

---

## ⚡ Fast Setup (Step-by-Step)

### 1️⃣ Install Python Dependencies

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
pip install -r requirements.txt

# Install llama-cpp-python with CUDA support
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir

# Install PyAudio (Windows)
pip install pipwin
pipwin install pyaudio
```

### 2️⃣ Download Models

#### Faster-Whisper (Auto-downloads)
✅ No action needed - downloads automatically on first run

#### Llama 3.1 8B GGUF
```powershell
# Download from HuggingFace (Q4_K_M quantization recommended)
# Example using wget or browser:
# https://huggingface.co/<username>/llama-3.1-8b-instruct-gguf

# Place in: models/llama/llama-3.1-8b-instruct-q4_k_m.gguf
```

**Direct links (search these on HuggingFace):**
- `TheBloke/Llama-2-7B-Chat-GGUF` (alternative)
- `TheBloke/Meta-Llama-3-8B-Instruct-GGUF`

#### Wav2Lip Checkpoint
```powershell
# Download from official Wav2Lip repository
# URL: https://github.com/Rudrabha/Wav2Lip#getting-the-weights

# Place in: models/wav2lip/wav2lip_gan.pth
```

**Direct download:**
```powershell
# Using curl or wget
curl -L "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1" -o models/wav2lip/wav2lip_gan.pth
```

### 3️⃣ Setup Wav2Lip Code

Wav2Lip inference code needs to be available in Python path:

```powershell
# Clone Wav2Lip repository
git clone https://github.com/Rudrabha/Wav2Lip.git

# Add to Python path (choose one method):

# Method 1: Copy files to project
cp -r Wav2Lip/models src/lipsync/wav2lip_models
cp Wav2Lip/audio.py src/lipsync/

# Method 2: Add to PYTHONPATH
$env:PYTHONPATH="$env:PYTHONPATH;D:\inter_view\Wav2Lip"

# Method 3: Install as package
cd Wav2Lip
pip install -e .
```

### 4️⃣ Add Source Media

**Option A: Use an image**
```powershell
# Place avatar.jpg in input/images/
# Set in config.py: SOURCE_TYPE = "image"
```

**Option B: Use a video (RECOMMENDED)**
```powershell
# Place avatar.mp4 in input/videos/
# Set in config.py: SOURCE_TYPE = "video"
```

**Quick test with sample:**
```powershell
# Download test video/image or use your webcam to record one
```

### 5️⃣ Configure System

Edit `src/config.py`:

```python
# Verify these paths
SOURCE_TYPE = "video"  # or "image"
SOURCE_VIDEO_PATH = INPUT_VIDEOS_DIR / "avatar.mp4"  # Your video name
LLAMA_MODEL_PATH = LLAMA_MODEL_DIR / "llama-3.1-8b-instruct-q4_k_m.gguf"  # Your model name

# GPU settings (already optimized for RTX 4070)
LLAMA_N_GPU_LAYERS = -1  # Offload all to GPU
WHISPER_DEVICE = "cuda"
WAV2LIP_DEVICE = "cuda"
```

### 6️⃣ Run the System

```powershell
cd src
python main.py
```

**Expected startup:**
1. Models load (~30-60 seconds)
2. Face detection runs
3. OpenCV window opens
4. Status shows "Ready - Start speaking..."
5. Speak into microphone!

---

## ✅ Verification Checklist

Before running, ensure:

- [ ] Python 3.9+ installed
- [ ] CUDA 11.8+ or 12.x installed
- [ ] NVIDIA drivers updated
- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip list` shows torch, faster-whisper, llama-cpp-python, etc.)
- [ ] Llama GGUF model in `models/llama/`
- [ ] Wav2Lip checkpoint in `models/wav2lip/`
- [ ] Wav2Lip code accessible (PYTHONPATH or copied)
- [ ] Source media (image/video) in `input/`
- [ ] Microphone connected and working
- [ ] GPU has 12GB+ VRAM free

---

## 🧪 Testing Components Individually

### Test Microphone
```powershell
python -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_default_input_device_info())"
```

### Test CUDA
```powershell
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA device: {torch.cuda.get_device_name(0)}')"
```

### Test Whisper
```powershell
python -c "from faster_whisper import WhisperModel; model = WhisperModel('tiny.en', device='cuda'); print('Whisper OK')"
```

### Test Llama
```powershell
python -c "from llama_cpp import Llama; print('Llama-cpp imported successfully')"
```

---

## 🐛 Common Issues & Fixes

### Issue: PyAudio installation fails
**Fix:**
```powershell
pip install pipwin
pipwin install pyaudio
```

### Issue: CUDA not found
**Fix:**
1. Install NVIDIA CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
2. Add to PATH: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin`
3. Restart terminal

### Issue: Llama-cpp-python not using GPU
**Fix:**
```powershell
# Reinstall with CUDA support
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

### Issue: Wav2Lip model not found
**Fix:**
1. Verify `wav2lip_gan.pth` exists in `models/wav2lip/`
2. Check Wav2Lip code is in Python path
3. Ensure Wav2Lip dependencies installed: `face-alignment`

### Issue: Face not detected
**Fix:**
1. Use image/video with clear frontal face
2. Ensure good lighting in source media
3. Try disabling face detection cache: `CACHE_FACE_DETECTION = False`

---

## 📊 Expected Performance

On RTX 4070:
- **Startup time**: 30-60 seconds
- **End-to-end latency**: 1.5-2.5 seconds
- **VRAM usage**: 10-12GB
- **FPS**: Stable 25 FPS

If performance is poor:
1. Check GPU utilization: `nvidia-smi`
2. Close other GPU applications
3. Reduce model sizes (see README.md optimization section)

---

## 🎯 Next Steps

Once running:
1. Test with short phrases first
2. Adjust `SILENCE_DURATION` if speech cuts off
3. Experiment with different voices in config
4. Try custom system prompts
5. Fine-tune performance settings

---

## 📚 Additional Resources

- **Faster-Whisper**: https://github.com/guillaumekln/faster-whisper
- **Llama.cpp**: https://github.com/ggerganov/llama.cpp
- **Wav2Lip**: https://github.com/Rudrabha/Wav2Lip
- **Edge-TTS**: https://github.com/rany2/edge-tts

---

**Need help? Check README.md for detailed troubleshooting!**
