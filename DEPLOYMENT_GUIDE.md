# 🚀 DEPLOYMENT GUIDE - Transfer to Another PC

Complete instructions for moving this project to another computer and getting it running.

---

## 📦 Package 1: Transfer All Files

### Option A: Using Git (Recommended)

```powershell
# On SOURCE PC (current machine)
cd d:\inter_view
git init
git add .
git commit -m "Initial commit - AI Avatar System"

# Push to GitHub/GitLab
git remote add origin https://github.com/yourusername/ai-avatar.git
git push -u origin main

# On TARGET PC (new machine)
git clone https://github.com/yourusername/ai-avatar.git
cd ai-avatar
```

### Option B: Using ZIP Archive

```powershell
# On SOURCE PC
# 1. Copy entire 'inter_view' folder to USB/Cloud
# 2. OR compress to ZIP (exclude models/ and input/ if large)

# Compress (Windows)
Compress-Archive -Path d:\inter_view\* -DestinationPath d:\ai-avatar-system.zip

# On TARGET PC
# 1. Extract ZIP to desired location
Expand-Archive -Path ai-avatar-system.zip -DestinationPath C:\Projects\ai-avatar
```

### Option C: Network Transfer

```powershell
# Share folder on network or use cloud storage:
# - OneDrive
# - Google Drive
# - Dropbox
# - Network share
```

---

## 📂 What to Transfer

### ✅ Required Files (ALWAYS transfer)
```
inter_view/
├── src/                    # All source code
├── README.md               # Documentation
├── QUICKSTART.md
├── MODEL_DOWNLOAD_LINKS.md
├── requirements.txt
├── verify_setup.py
├── .gitignore
└── models/                 # Create empty folders or...
    ├── whisper/            # Transfer if already downloaded
    ├── llama/              
    └── wav2lip/            
```

### ⚠️ Optional (Large files - re-download on new PC)
```
models/
├── llama/*.gguf            # ~5GB - Re-download recommended
└── wav2lip/*.pth           # ~150MB - Can transfer or re-download

input/
├── images/*.jpg            # Transfer your avatar media
└── videos/*.mp4            
```

### ❌ Don't Transfer
```
.git/                       # Only if using git
__pycache__/               # Python cache
*.pyc                      # Compiled Python
venv/                      # Virtual environment - recreate on new PC
output/                    # Generated outputs
```

---

## 🖥️ Setup on Target PC (Step-by-Step)

### 1️⃣ Install Prerequisites

#### A. Install Python 3.9+
```powershell
# Download from: https://www.python.org/downloads/
# OR use winget
winget install Python.Python.3.11

# Verify
python --version  # Should show 3.9 or higher
```

#### B. Install NVIDIA CUDA Toolkit
```powershell
# Download from: https://developer.nvidia.com/cuda-downloads
# Required: CUDA 11.8 or 12.x
# Install with default settings

# Verify
nvcc --version
nvidia-smi  # Check GPU is detected
```

#### C. Install Git (Optional but recommended)
```powershell
winget install Git.Git

# Verify
git --version
```

#### D. Install Visual Studio Build Tools (for llama-cpp-python)
```powershell
# Download from: https://visualstudio.microsoft.com/downloads/
# Select "Build Tools for Visual Studio 2022"
# Install "Desktop development with C++" workload
```

---

### 2️⃣ Setup Project

```powershell
# Navigate to project directory
cd C:\Projects\ai-avatar  # Or wherever you extracted

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Verify activation (prompt should show (venv))
```

---

### 3️⃣ Install Python Dependencies

#### A. Install PyTorch with CUDA
```powershell
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# OR for CUDA 12.x
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify CUDA support
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

#### B. Install llama-cpp-python with CUDA
```powershell
# Set environment variable for CUDA support
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"

# Install with force rebuild
pip install llama-cpp-python --force-reinstall --no-cache-dir

# This may take 5-10 minutes to compile
```

#### C. Install remaining dependencies
```powershell
# Install all other packages
pip install -r requirements.txt

# If PyAudio fails on Windows:
pip install pipwin
pipwin install pyaudio

# OR download wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# pip install PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl
```

---

### 4️⃣ Download Models

#### A. Faster-Whisper (Auto-downloads)
```powershell
# Will download automatically on first run
# Or pre-download:
python -c "from faster_whisper import WhisperModel; WhisperModel('small.en', device='cpu', download_root='./models/whisper')"
```

#### B. Llama 3.1 8B GGUF
```powershell
# Method 1: Using huggingface-hub
pip install huggingface-hub
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='TheBloke/Llama-2-7B-Chat-GGUF', filename='llama-2-7b-chat.Q4_K_M.gguf', local_dir='./models/llama')"

# Method 2: Manual download
# Visit: https://huggingface.co/models?search=llama+gguf
# Download Q4_K_M.gguf file (~5GB)
# Place in: models/llama/
```

#### C. Wav2Lip Checkpoint
```powershell
# Download using PowerShell
Invoke-WebRequest -Uri "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1" -OutFile "models/wav2lip/wav2lip_gan.pth"

# OR manually from: https://github.com/Rudrabha/Wav2Lip#getting-the-weights
```

#### D. Wav2Lip Source Code
```powershell
# Clone Wav2Lip repository
git clone https://github.com/Rudrabha/Wav2Lip.git

# Add to Python path (in PowerShell profile or before running)
$env:PYTHONPATH="$PWD\Wav2Lip;$env:PYTHONPATH"

# OR copy required files to project
cp -r Wav2Lip\models src\lipsync\wav2lip_models
cp Wav2Lip\audio.py src\lipsync\
```

---

### 5️⃣ Add Source Media

```powershell
# For image-based avatar
# Copy your avatar image to: input/images/avatar.jpg

# For video-based avatar (RECOMMENDED)
# Copy your avatar video to: input/videos/avatar.mp4

# Ensure filename matches config.py:
# SOURCE_IMAGE_PATH = INPUT_IMAGES_DIR / "avatar.jpg"
# SOURCE_VIDEO_PATH = INPUT_VIDEOS_DIR / "avatar.mp4"
```

---

### 6️⃣ Verify Setup

```powershell
# Run verification script
python verify_setup.py

# Should show all green checkmarks ✅
# If any red ❌, fix the issues before proceeding
```

---

### 7️⃣ Configure System

```powershell
# Edit src/config.py if needed
notepad src\config.py

# Key settings to verify:
# - SOURCE_TYPE = "video" or "image"
# - Model paths match your downloaded files
# - GPU settings correct
```

---

### 8️⃣ Run the System

```powershell
# Navigate to src directory
cd src

# Run main script
python main.py

# Expected output:
# - Models loading... (30-60 seconds)
# - Face detected
# - OpenCV window opens
# - "Ready - Start speaking..."

# Start talking into your microphone!
```

---

## 🔧 Troubleshooting on New PC

### Issue 1: CUDA Not Found
**Error**: `torch.cuda.is_available() = False`

**Fix**:
```powershell
# 1. Verify NVIDIA driver installed
nvidia-smi

# 2. Install/Reinstall CUDA Toolkit
# Download from: https://developer.nvidia.com/cuda-downloads

# 3. Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue 2: llama-cpp-python No GPU Support
**Error**: Model loads but doesn't use GPU

**Fix**:
```powershell
# Reinstall with CUDA support
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

### Issue 3: PyAudio Installation Fails
**Error**: `ERROR: Could not build wheels for pyaudio`

**Fix**:
```powershell
# Windows: Use pipwin
pip install pipwin
pipwin install pyaudio

# OR download precompiled wheel
# Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Download appropriate .whl file for your Python version
pip install PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl
```

### Issue 4: Wav2Lip Import Error
**Error**: `ModuleNotFoundError: No module named 'models'`

**Fix**:
```powershell
# Ensure Wav2Lip is cloned and in Python path
git clone https://github.com/Rudrabha/Wav2Lip.git

# Add to path (before running main.py)
$env:PYTHONPATH="$PWD\Wav2Lip;$env:PYTHONPATH"

# Make permanent: Add to Windows Environment Variables
```

### Issue 5: Out of Memory
**Error**: `RuntimeError: CUDA out of memory`

**Fix** in `src/config.py`:
```python
# Reduce model sizes
WHISPER_MODEL_SIZE = "base.en"  # Instead of small.en
WAV2LIP_FACE_SIZE = 192         # Instead of 256
LLAMA_N_CTX = 2048              # Instead of 4096
```

### Issue 6: Microphone Not Working
**Error**: No transcription happening

**Fix**:
```powershell
# 1. Check microphone permissions in Windows Settings
# Settings > Privacy > Microphone > Allow desktop apps

# 2. Test microphone
python -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_default_input_device_info())"

# 3. Adjust sensitivity in config.py
# SILENCE_THRESHOLD = 300  # Lower value = more sensitive
```

---

## 📋 Pre-Transfer Checklist (Source PC)

- [ ] All code in `src/` directory
- [ ] Configuration file (`config.py`) updated
- [ ] Documentation complete
- [ ] `requirements.txt` up to date
- [ ] Source media prepared (avatar image/video)
- [ ] Models downloaded (optional - can re-download)
- [ ] `.gitignore` configured (if using git)
- [ ] Test run successful on source PC

---

## 📋 Post-Transfer Checklist (Target PC)

- [ ] Python 3.9+ installed
- [ ] CUDA Toolkit installed
- [ ] Virtual environment created and activated
- [ ] PyTorch with CUDA installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Models downloaded and placed correctly
- [ ] Wav2Lip repository cloned and accessible
- [ ] Source media added to `input/`
- [ ] `verify_setup.py` runs successfully (all green ✅)
- [ ] GPU detected: `nvidia-smi` works
- [ ] CUDA available: `torch.cuda.is_available() = True`
- [ ] Test run successful

---

## 🎯 Quick Start Commands (Target PC)

```powershell
# After file transfer, run these commands in order:

# 1. Setup environment
cd C:\path\to\ai-avatar
python -m venv venv
.\venv\Scripts\activate

# 2. Install PyTorch (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 3. Install llama-cpp-python (with CUDA)
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir

# 4. Install other dependencies
pip install -r requirements.txt
pip install pipwin
pipwin install pyaudio

# 5. Clone Wav2Lip
git clone https://github.com/Rudrabha/Wav2Lip.git
$env:PYTHONPATH="$PWD\Wav2Lip;$env:PYTHONPATH"

# 6. Download models (see MODEL_DOWNLOAD_LINKS.md)

# 7. Verify setup
python verify_setup.py

# 8. Run system
cd src
python main.py
```

---

## 💾 Backup Important Files

Before transferring, backup:
1. **Source media** - `input/images/`, `input/videos/`
2. **Downloaded models** - `models/llama/*.gguf`, `models/wav2lip/*.pth`
3. **Configuration** - `src/config.py` (if customized)
4. **Generated outputs** - `output/` (if you want to keep them)

---

## 🌐 Cloud Transfer Options

### Google Drive
```powershell
# Upload ZIP to Google Drive
# Download on target PC
# Extract and follow setup steps
```

### OneDrive
```powershell
# Copy folder to OneDrive sync folder
# Wait for sync
# Access from target PC
```

### GitHub/GitLab (Best for code only)
```powershell
# Initialize git repository
git init
git add .
git commit -m "Initial commit"
git push origin main

# On target PC
git clone <repository-url>
```

---

## 📊 Disk Space Requirements

**Target PC needs:**
- Python + packages: ~2GB
- CUDA Toolkit: ~3GB
- Models: ~6-7GB
- Project code: ~10MB
- **Total**: ~12GB minimum

**Recommended**: 20GB free space

---

## 🔒 Security Notes

- Don't commit models to public GitHub (they're large and some have licenses)
- Use `.gitignore` to exclude models, venv, and outputs
- Keep API keys/credentials out of config (use environment variables)

---

## ✅ Final Verification

On target PC, run:
```powershell
# 1. Check Python
python --version

# 2. Check CUDA
nvidia-smi

# 3. Check PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"

# 4. Check all dependencies
pip list | Select-String "torch|whisper|llama|edge-tts|opencv|pyaudio"

# 5. Run verification
python verify_setup.py

# 6. Test run
cd src
python main.py
```

If all pass ✅ - **You're ready to go!** 🚀

---

## 📞 Need Help?

1. Check README.md for detailed documentation
2. Check QUICKSTART.md for setup steps
3. Check MODEL_DOWNLOAD_LINKS.md for download instructions
4. Check troubleshooting sections above
5. Verify all prerequisites installed

---

**Deployment complete!** 🎉
