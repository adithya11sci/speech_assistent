# 📥 Model Download Links & Instructions

Complete guide for downloading all required models.

---

## 🎯 Required Models Summary

| Model | Size | Purpose | Download Location |
|-------|------|---------|------------------|
| Faster-Whisper (small.en) | ~500MB | Speech-to-Text | Auto-downloaded |
| Llama 3.1 8B (Q4_K_M) | ~4.9GB | Language Model | HuggingFace |
| Wav2Lip GAN | ~150MB | Lip Sync | GitHub/SharePoint |

**Total**: ~5.5GB

---

## 1. Faster-Whisper (Speech-to-Text)

### ✅ Auto-Download (Recommended)
The model automatically downloads on first run. No manual action needed!

### Manual Download (Optional)
If you want to pre-download:

```python
from faster_whisper import WhisperModel
model = WhisperModel("small.en", device="cuda", download_root="./models/whisper")
```

**Available sizes:**
- `tiny.en` - ~150MB (fastest, less accurate)
- `base.en` - ~300MB (good balance)
- `small.en` - ~500MB ⭐ **RECOMMENDED**
- `medium.en` - ~1.5GB (more accurate, slower)

---

## 2. Llama 3.1 8B Instruct (LLM)

### HuggingFace Downloads

**Recommended: Q4_K_M quantization (~4.9GB)**

#### Option A: Using HuggingFace Hub
```powershell
# Install huggingface-hub
pip install huggingface-hub

# Download
python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='TheBloke/Llama-2-7B-Chat-GGUF', filename='llama-2-7b-chat.Q4_K_M.gguf', local_dir='./models/llama')"
```

#### Option B: Direct Browser Download

1. Visit: **https://huggingface.co/models?search=llama+gguf**

2. Recommended repositories:
   - `TheBloke/Llama-2-7B-Chat-GGUF`
   - `TheBloke/Llama-2-13B-chat-GGUF` (if you have VRAM)
   - `lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF`

3. Download file ending in `.Q4_K_M.gguf`

4. Place in: `models/llama/`

#### Option C: Using Git LFS
```powershell
# Init git LFS
git lfs install

# Clone repo (only download specific file)
git clone --depth 1 --filter=blob:none --sparse https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF
cd Llama-2-7B-Chat-GGUF
git sparse-checkout set llama-2-7b-chat.Q4_K_M.gguf
git lfs pull

# Move to models folder
mv llama-2-7b-chat.Q4_K_M.gguf ../models/llama/
```

### Quantization Guide

| Quantization | Size | Quality | Speed | VRAM |
|--------------|------|---------|-------|------|
| Q2_K | ~2.5GB | Low | Fastest | ~4GB |
| Q3_K_M | ~3.5GB | Medium | Fast | ~5GB |
| Q4_K_M | ~4.9GB | Good | Balanced | ~6GB ⭐ |
| Q5_K_M | ~5.8GB | High | Slower | ~7GB |
| Q8_0 | ~8.5GB | Highest | Slow | ~10GB |

**For RTX 4070 (16GB)**: Q4_K_M or Q5_K_M recommended

---

## 3. Wav2Lip (Lip Synchronization)

### Official Checkpoint

#### Direct Download Link
```powershell
# Using PowerShell (Windows)
Invoke-WebRequest -Uri "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1" -OutFile "models/wav2lip/wav2lip_gan.pth"

# Using wget (Linux/WSL)
wget --no-check-certificate "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1" -O models/wav2lip/wav2lip_gan.pth

# Using curl
curl -L "https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ?download=1" -o models/wav2lip/wav2lip_gan.pth
```

#### Alternative: Google Drive

1. Visit: **https://github.com/Rudrabha/Wav2Lip#getting-the-weights**
2. Click the Google Drive link for `wav2lip_gan.pth`
3. Download (~150MB)
4. Place in: `models/wav2lip/wav2lip_gan.pth`

### Face Detection Model (Optional)

If using face_detection library:
```powershell
# Download s3fd face detection
wget "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth" -O models/wav2lip/face_detection.pth
```

---

## 4. Wav2Lip Source Code

Wav2Lip inference code is required:

### Method 1: Clone Repository
```powershell
git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip
pip install -r requirements.txt
```

Then add to Python path in your script or environment.

### Method 2: Copy Required Files
```powershell
# From Wav2Lip repo, copy:
# - models/ folder
# - audio.py
# - face_detection/ folder

# To your project:
cp -r Wav2Lip/models src/lipsync/wav2lip_models
cp Wav2Lip/audio.py src/lipsync/
```

### Method 3: Set PYTHONPATH
```powershell
# Windows PowerShell
$env:PYTHONPATH="$env:PYTHONPATH;D:\inter_view\Wav2Lip"

# Linux/Mac
export PYTHONPATH=$PYTHONPATH:/path/to/Wav2Lip
```

---

## 📋 Verification Script

Save as `verify_models.py` and run to check all models:

```python
"""Verify all models are downloaded and accessible"""
import os
from pathlib import Path

def check_file(path, description):
    if Path(path).exists():
        size = Path(path).stat().st_size / (1024**3)  # GB
        print(f"✅ {description}: {size:.2f} GB")
        return True
    else:
        print(f"❌ {description}: NOT FOUND at {path}")
        return False

print("=" * 60)
print("MODEL VERIFICATION")
print("=" * 60)

base = Path("models")

# Whisper
print("\n1. Whisper (STT):")
whisper_path = base / "whisper" / "small.en"
if whisper_path.exists():
    print(f"✅ Whisper model directory exists")
else:
    print(f"⚠️  Will auto-download on first run")

# Llama
print("\n2. Llama (LLM):")
llama_found = False
for file in (base / "llama").glob("*.gguf"):
    check_file(file, f"Llama model: {file.name}")
    llama_found = True
if not llama_found:
    print("❌ No GGUF model found in models/llama/")

# Wav2Lip
print("\n3. Wav2Lip (Lip Sync):")
check_file(base / "wav2lip" / "wav2lip_gan.pth", "Wav2Lip checkpoint")

# Source media
print("\n4. Source Media:")
input_base = Path("input")
images = list((input_base / "images").glob("*.jpg")) + list((input_base / "images").glob("*.png"))
videos = list((input_base / "videos").glob("*.mp4")) + list((input_base / "videos").glob("*.avi"))

if images:
    print(f"✅ Found {len(images)} image(s): {[i.name for i in images]}")
if videos:
    print(f"✅ Found {len(videos)} video(s): {[v.name for v in videos]}")
if not images and not videos:
    print("❌ No source media found in input/")

print("\n" + "=" * 60)
print("Verification complete!")
print("=" * 60)
```

Run:
```powershell
python verify_models.py
```

---

## 🔐 Checksum Verification (Optional)

Verify downloaded files aren't corrupted:

### Wav2Lip Checkpoint
```powershell
# Expected SHA256
# wav2lip_gan.pth: TBD (check official repo)

# Verify
certutil -hashfile models/wav2lip/wav2lip_gan.pth SHA256  # Windows
sha256sum models/wav2lip/wav2lip_gan.pth  # Linux
```

---

## 💡 Tips

1. **Use a download manager** for large files (e.g., Free Download Manager)
2. **Check your internet speed** - 5GB+ downloads take time
3. **Keep models organized** - don't rename files unless updating config
4. **Backup models** - once downloaded, keep a backup copy
5. **Check disk space** - ensure 10GB+ free space

---

## 🆘 Troubleshooting Downloads

### HuggingFace is slow
- Use `hf_transfer` for faster downloads:
  ```powershell
  pip install hf_transfer
  $env:HF_HUB_ENABLE_HF_TRANSFER="1"
  ```

### SharePoint link blocked
- Try using VPN
- Use alternative Google Drive link
- Ask in Wav2Lip GitHub issues

### Git LFS fails
- Increase timeout: `git config --global lfs.activitytimeout 300`
- Use direct download instead

---

## ✅ Final Checklist

After downloading all models:

- [ ] Whisper model ready (auto-downloads or manually placed)
- [ ] Llama GGUF file in `models/llama/` (~5GB)
- [ ] Wav2Lip checkpoint in `models/wav2lip/` (~150MB)
- [ ] Wav2Lip code accessible (cloned or copied)
- [ ] Source media in `input/images/` or `input/videos/`
- [ ] Run `verify_models.py` - all green checks
- [ ] Total disk space used: ~6-7GB

**Ready to run!** 🚀

```powershell
cd src
python main.py
```

---

**Happy building!** 🎉
