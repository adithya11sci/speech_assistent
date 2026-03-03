# 📋 Transfer Checklist - Moving to Another PC

## ✅ Pre-Transfer (Source PC)

### 1. Package Creation
- [ ] Run `python package_creator.py`
- [ ] Choose packaging option (code only / code+models / complete)
- [ ] Verify ZIP file created successfully
- [ ] Note ZIP file size and location

### 2. Model Files (if not packaged)
- [ ] Confirm Llama model location: `models/llama/*.gguf`
- [ ] Confirm Wav2Lip model: `models/wav2lip/wav2lip_gan.pth`
- [ ] Note model file sizes (for transfer speed estimation)

### 3. Source Media
- [ ] Have avatar image or video ready
- [ ] File format: JPG/PNG for image, MP4/AVI for video
- [ ] Resolution: Recommended 512x512 or higher
- [ ] Face clearly visible in media

### 4. Documentation
- [ ] Verify all .md files present
- [ ] Check README.md opens correctly
- [ ] Review any custom config changes made

### 5. Transfer Method Selection
Choose ONE method:
- [ ] **USB Drive**: Need 12-15GB space (with models)
- [ ] **Network Transfer**: Both PCs on same network
- [ ] **Cloud Upload**: Google Drive / OneDrive / Dropbox
- [ ] **Git Repository**: For code-only transfers

---

## 🚚 During Transfer

### Option A: USB/External Drive
- [ ] Insert USB drive (12-15GB free)
- [ ] Copy ZIP file to USB
- [ ] Verify file integrity (check size matches)
- [ ] Safely eject USB

### Option B: Network Transfer
- [ ] Both PCs connected to same network
- [ ] Share folder or use transfer tool (e.g., LocalSend)
- [ ] Start transfer
- [ ] Wait for completion
- [ ] Verify file on target PC

### Option C: Cloud Upload
- [ ] Upload ZIP to cloud service
- [ ] Wait for upload to complete (can take 30min-2hrs for 7GB)
- [ ] Verify upload success
- [ ] Get shareable link if needed

### Option D: Git Repository (Code Only)
```bash
# On source PC
git init
git add .
git commit -m "AI Avatar System"
git remote add origin <your-repo-url>
git push -u origin main
```

---

## 📥 Post-Transfer (Target PC)

### 1. Extract Package
- [ ] Create destination folder (e.g., `C:\AI_Avatar`)
- [ ] Extract ZIP to folder
- [ ] Verify all files extracted
- [ ] Check folder structure matches original

### 2. Prerequisites Check
- [ ] Python 3.9+ installed: `python --version`
- [ ] NVIDIA GPU present: `nvidia-smi`
- [ ] 15GB free disk space available
- [ ] Internet connection active (for dependency downloads)

### 3. Automated Setup (RECOMMENDED)
```bash
cd C:\AI_Avatar
python setup_target_pc.py
```
- [ ] Script starts successfully
- [ ] Virtual environment created
- [ ] PyTorch installed with CUDA
- [ ] llama-cpp-python compiled with GPU
- [ ] All dependencies installed
- [ ] Verification passes

### 4. Manual Steps (if needed)
- [ ] Create venv: `python -m venv venv`
- [ ] Activate: `venv\Scripts\activate`
- [ ] Install PyTorch: See QUICKSTART.md
- [ ] Install llama-cpp-python: See QUICKSTART.md
- [ ] Install requirements: `pip install -r requirements.txt`

### 5. Model Setup
If models not included in package:
- [ ] Download Llama model from Hugging Face
- [ ] Place in `models/llama/` folder
- [ ] Download Wav2Lip checkpoint
- [ ] Place in `models/wav2lip/` folder
- [ ] Clone Wav2Lip repo: `git clone https://github.com/Rudrabha/Wav2Lip.git`

### 6. Configuration
- [ ] Open `src/config.py`
- [ ] Verify model paths correct
- [ ] Verify Wav2Lip repo path
- [ ] Adjust settings if needed (GPU layers, etc.)
- [ ] Add source media to `input/` folder

### 7. Verification
```bash
python verify_setup.py
```
- [ ] Python version check passes
- [ ] GPU detected
- [ ] PyTorch CUDA available
- [ ] All models found
- [ ] Dependencies OK

### 8. First Run
```bash
cd src
python main.py
```
- [ ] All components initialize
- [ ] No error messages
- [ ] Microphone detected
- [ ] Idle frame displays
- [ ] Ready for speech input

### 9. Test Functionality
- [ ] Speak into microphone
- [ ] Speech transcribed (shows in console)
- [ ] LLM generates response
- [ ] TTS produces audio
- [ ] Lips sync to audio
- [ ] Display shows animated avatar
- [ ] End-to-end latency acceptable (<3 seconds)

---

## 🔧 Troubleshooting Checklist

### Installation Issues
- [ ] Python version >= 3.9: `python --version`
- [ ] Pip updated: `python -m pip install --upgrade pip`
- [ ] Visual Studio Build Tools installed (Windows)
- [ ] CUDA Toolkit installed: `nvcc --version`

### CUDA Issues
- [ ] NVIDIA drivers updated
- [ ] `nvidia-smi` shows GPU
- [ ] PyTorch sees GPU: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] CUDA version matches PyTorch (11.8 or 12.1)

### Model Issues
- [ ] Model files exist at specified paths
- [ ] Model filenames match config.py exactly
- [ ] Wav2Lip repo cloned to project root
- [ ] Model files not corrupted (check file sizes)

### Runtime Issues
- [ ] Config.py paths use correct slashes (\ for Windows)
- [ ] Microphone permissions granted
- [ ] No other app using microphone
- [ ] Sufficient VRAM available (close other GPU apps)
- [ ] Check logs/ folder for error details

---

## 📊 Verification Matrix

| Component | Check Command | Expected Result |
|-----------|---------------|-----------------|
| Python | `python --version` | 3.9.0 or higher |
| GPU | `nvidia-smi` | Shows GPU name & CUDA version |
| PyTorch | `python -c "import torch; print(torch.__version__)"` | 2.0.0+ |
| CUDA | `python -c "import torch; print(torch.cuda.is_available())"` | True |
| Faster-Whisper | `python -c "import faster_whisper; print('OK')"` | OK |
| Llama | `python -c "import llama_cpp; print('OK')"` | OK |
| EdgeTTS | `python -c "import edge_tts; print('OK')"` | OK |
| OpenCV | `python -c "import cv2; print('OK')"` | OK |
| PyAudio | `python -c "import pyaudio; print('OK')"` | OK |

---

## ⏱️ Time Estimates

| Task | Estimated Time |
|------|----------------|
| Package creation | 2-5 minutes |
| USB transfer (7GB) | 10-15 minutes |
| Network transfer (7GB) | 5-30 minutes |
| Cloud upload (7GB) | 30min-2 hours |
| Extract files | 2-5 minutes |
| Automated setup | 15-25 minutes |
| Model downloads | 10-20 minutes |
| Verification & testing | 5-10 minutes |
| **Total (USB)** | **45-80 minutes** |
| **Total (Cloud)** | **1-3 hours** |

---

## 🆘 Quick Support

**If setup script fails:**
1. Read error message carefully
2. Check Prerequisites section in DEPLOYMENT_GUIDE.md
3. Run manual installation steps
4. Use verify_setup.py to check each component

**If models not found:**
1. Check MODEL_DOWNLOAD_LINKS.md
2. Verify file paths in config.py
3. Ensure filenames match exactly
4. Place files in correct folders

**If GPU not detected:**
1. Update NVIDIA drivers
2. Install CUDA Toolkit matching PyTorch
3. Reinstall PyTorch with CUDA
4. Recompile llama-cpp-python with CMAKE_ARGS

**Still stuck?**
- Review all .md documentation files
- Check verify_setup.py output
- Review console error messages
- Check logs/ folder for details

---

## ✅ Success Indicators

You're ready when:
- ✅ `verify_setup.py` passes all checks
- ✅ `python src/main.py` starts without errors
- ✅ Microphone captures your voice
- ✅ Avatar face displays correctly
- ✅ Speech → response → lip sync works end-to-end
- ✅ Latency is acceptable (under 3 seconds)
- ✅ GPU utilization visible in nvidia-smi

---

## 📝 Notes Section

Use this space to track custom settings or issues:

**Custom Configuration Changes:**
```
[Write your custom settings here]
```

**Issues Encountered:**
```
[Document problems and solutions]
```

**Performance Metrics:**
```
End-to-end latency: _____ seconds
GPU VRAM usage: _____ GB
FPS: _____ 
```

---

**Checklist Version**: 1.0
**Last Updated**: 2024
