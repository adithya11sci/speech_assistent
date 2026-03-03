# 📑 Complete File Index - AI Avatar System

## 🎯 Quick Navigation

**New to the project?** → Start with [START_HERE.txt](START_HERE.txt)  
**Quick commands?** → See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)  
**Setting up?** → Follow [QUICKSTART.md](QUICKSTART.md)  
**Transferring?** → Use [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 📂 Complete Directory Structure

```
inter_view/
│
├── 📄 Documentation Files (Read These!)
│   ├── START_HERE.txt              ← Read this FIRST!
│   ├── QUICK_REFERENCE.md          ← Commands & quick help
│   ├── README.md                   ← Complete system documentation
│   ├── QUICKSTART.md               ← Step-by-step setup guide
│   ├── DEPLOYMENT_GUIDE.md         ← How to transfer to another PC
│   ├── TRANSFER_CHECKLIST.md       ← Transfer checklist
│   ├── MODEL_DOWNLOAD_LINKS.md     ← Where to get AI models
│   ├── PROJECT_SUMMARY.md          ← Architecture overview
│   └── FILE_INDEX.md               ← This file
│
├── 🛠️ Setup & Utility Scripts
│   ├── setup_target_pc.py          ← Automated setup (run this first!)
│   ├── verify_setup.py             ← Check if everything works
│   ├── package_creator.py          ← Create deployment package
│   ├── requirements.txt            ← Python dependencies list
│   └── .gitignore                  ← Git ignore rules
│
├── 📦 Source Code (src/)
│   ├── __init__.py                 ← Package initializer
│   ├── config.py                   ← ⭐ All settings (EDIT THIS!)
│   ├── main.py                     ← ⭐ Entry point (RUN THIS!)
│   ├── pipeline.py                 ← Main orchestrator
│   │
│   ├── preprocessing/              ← Source media handling
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── source_loader.py        ← Load image/video
│   │   └── face_detector.py        ← Detect face in media
│   │
│   ├── audio/                      ← Audio capture & processing
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── microphone.py           ← Mic capture with VAD
│   │   └── audio_utils.py          ← Audio utilities
│   │
│   ├── stt/                        ← Speech-to-Text
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── whisper_stream.py       ← Whisper streaming STT
│   │
│   ├── llm/                        ← Language Model
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── llama_stream.py         ← Llama streaming LLM
│   │
│   ├── tts/                        ← Text-to-Speech
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── edge_tts_stream.py      ← Edge-TTS streaming
│   │
│   ├── lipsync/                    ← Lip Synchronization
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── wav2lip_processor.py    ← Wav2Lip lip sync
│   │
│   └── renderer/                   ← Frame Rendering
│       ├── __init__.py
│       ├── README.md
│       └── frame_renderer.py       ← Display frames
│
├── 🤖 AI Models (models/) - Add downloaded models here
│   ├── llama/
│   │   ├── .gitkeep
│   │   ├── README.md
│   │   └── [Place Llama GGUF model here]
│   │       → Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf (~5GB)
│   │
│   └── wav2lip/
│       ├── .gitkeep
│       ├── README.md
│       └── [Place Wav2Lip checkpoint here]
│           → wav2lip_gan.pth (~150MB)
│
├── 🎬 Input Media (input/) - Add your avatar here
│   ├── .gitkeep
│   ├── README.md
│   └── [Place avatar.jpg or avatar.mp4 here]
│
├── 📹 Output Recordings (output/) - Auto-created
│   ├── .gitkeep
│   └── README.md
│
├── 📊 Logs (logs/) - Auto-created
│   ├── .gitkeep
│   └── README.md
│
├── 🔬 Wav2Lip Repository (Wav2Lip/) - Clone from GitHub
│   └── git clone https://github.com/Rudrabha/Wav2Lip.git
│
└── 🐍 Virtual Environment (venv/) - Auto-created by setup
    └── Created by: python -m venv venv

```

---

## 📄 File Descriptions

### Documentation Files

| File | Lines | Purpose | When to Read |
|------|-------|---------|--------------|
| **START_HERE.txt** | 250 | First file to read | Before anything else |
| **QUICK_REFERENCE.md** | 300 | Quick commands & settings | Need fast answer |
| **README.md** | 800 | Complete documentation | Understanding system |
| **QUICKSTART.md** | 600 | Setup instructions | First-time setup |
| **DEPLOYMENT_GUIDE.md** | 600 | Transfer guide | Moving to new PC |
| **TRANSFER_CHECKLIST.md** | 400 | Transfer checklist | During deployment |
| **MODEL_DOWNLOAD_LINKS.md** | 400 | Model download info | Getting AI models |
| **PROJECT_SUMMARY.md** | 500 | Architecture details | Technical understanding |
| **FILE_INDEX.md** | 400 | This file | Finding files |

**Total Documentation**: ~4,250 lines

---

### Setup Scripts

| File | Lines | Purpose | Usage |
|------|-------|---------|-------|
| **setup_target_pc.py** | 350 | Automated setup | `python setup_target_pc.py` |
| **verify_setup.py** | 200 | Verify installation | `python verify_setup.py` |
| **package_creator.py** | 250 | Create deployment ZIP | `python package_creator.py` |
| **requirements.txt** | 20 | Python dependencies | Used by pip |
| **.gitignore** | 50 | Git ignore rules | Used by git |

**Total Setup Code**: ~870 lines

---

### Core Source Code (src/)

#### Main Files

| File | Lines | Purpose | Key Features |
|------|-------|---------|--------------|
| **config.py** | 200 | Configuration | 50+ parameters |
| **main.py** | 50 | Entry point | Error handling |
| **pipeline.py** | 250 | Orchestrator | 6 async tasks, queue management |

#### Preprocessing Module

| File | Lines | Purpose |
|------|-------|---------|
| **source_loader.py** | 150 | Load image/video, frame extraction |
| **face_detector.py** | 120 | Face detection with caching |

#### Audio Module

| File | Lines | Purpose |
|------|-------|---------|
| **microphone.py** | 150 | Async mic capture, VAD |
| **audio_utils.py** | 100 | Normalization, resampling |

#### STT Module

| File | Lines | Purpose |
|------|-------|---------|
| **whisper_stream.py** | 120 | Streaming speech-to-text |

#### LLM Module

| File | Lines | Purpose |
|------|-------|---------|
| **llama_stream.py** | 180 | Streaming LLM responses |

#### TTS Module

| File | Lines | Purpose |
|------|-------|---------|
| **edge_tts_stream.py** | 150 | Streaming text-to-speech |

#### Lip Sync Module

| File | Lines | Purpose |
|------|-------|---------|
| **wav2lip_processor.py** | 200 | Lip synchronization |

#### Renderer Module

| File | Lines | Purpose |
|------|-------|---------|
| **frame_renderer.py** | 130 | Display frames, FPS control |

**Total Source Code**: ~1,800 lines  
**Total with README files**: ~2,000+ lines

---

## 📊 Project Statistics

| Metric | Count |
|--------|-------|
| **Total Files** | 45+ |
| **Python Files** | 22 |
| **Documentation Files** | 9 |
| **README Files** | 8 |
| **Source Code Lines** | ~2,000 |
| **Documentation Lines** | ~4,250 |
| **Total Project Lines** | ~7,000+ |
| **Modules** | 8 |
| **Configuration Parameters** | 50+ |
| **Async Queues** | 6 |
| **Dependencies** | 15+ |

---

## 🔄 Data Flow

```
Microphone → Audio Queue → Whisper → Transcript Queue
                                           ↓
Frame Queue ← Wav2Lip ← TTS Queue ← Token Queue ← Llama
     ↓
Renderer → Display
```

---

## 🎯 File Categories by Purpose

### 🚀 Getting Started
1. START_HERE.txt
2. QUICK_REFERENCE.md
3. setup_target_pc.py

### 📖 Learning the System
1. README.md
2. PROJECT_SUMMARY.md
3. src/config.py (to see all options)

### 🔧 Installation
1. QUICKSTART.md
2. setup_target_pc.py
3. requirements.txt
4. verify_setup.py

### 📦 Deployment
1. DEPLOYMENT_GUIDE.md
2. TRANSFER_CHECKLIST.md
3. package_creator.py

### 🤖 AI Models
1. MODEL_DOWNLOAD_LINKS.md
2. models/llama/README.md
3. models/wav2lip/README.md

### 💻 Development
1. src/ (all source files)
2. config.py (all settings)
3. PROJECT_SUMMARY.md (architecture)

---

## 🔍 Finding What You Need

### "How do I start the system?"
→ START_HERE.txt → setup_target_pc.py → cd src && python main.py

### "What models do I need?"
→ MODEL_DOWNLOAD_LINKS.md

### "How do I configure settings?"
→ src/config.py (edit this file)

### "System not working, what's wrong?"
→ python verify_setup.py → QUICK_REFERENCE.md (troubleshooting)

### "How to transfer to another PC?"
→ DEPLOYMENT_GUIDE.md + TRANSFER_CHECKLIST.md

### "How does it work internally?"
→ PROJECT_SUMMARY.md → src/pipeline.py

### "Quick command reference?"
→ QUICK_REFERENCE.md

---

## 📝 Modification Guide

### To Change Avatar
Edit: `src/config.py` → `SOURCE_IMAGE` or `SOURCE_VIDEO`  
Place file in: `input/` folder

### To Adjust Performance
Edit: `src/config.py`
- `LLAMA_N_GPU_LAYERS` (GPU usage)
- `TOKEN_BUFFER_SIZE` (response speed)
- `WAV2LIP_USE_FP16` (speed vs quality)

### To Change Voice
Edit: `src/config.py` → `VOICE_NAME`  
Options: "en-US-AriaNeural", "en-US-GuyNeural", etc.

### To Adjust Microphone Sensitivity
Edit: `src/config.py` → `RMS_THRESHOLD`  
Lower = more sensitive, Higher = less sensitive

### To Add New Features
Modify: `src/pipeline.py` (add new tasks)  
Create: New modules in `src/your_module/`

---

## ✅ Completeness Check

- [x] All core modules implemented
- [x] Configuration system complete
- [x] Documentation comprehensive
- [x] Setup scripts automated
- [x] Verification tools included
- [x] Transfer guides complete
- [x] Quick reference available
- [x] Troubleshooting documented
- [x] All README files present
- [x] Project structure finalized

---

## 🎓 Learning Path

### Beginner (Just want to use it)
1. START_HERE.txt
2. Run setup_target_pc.py
3. QUICK_REFERENCE.md (as needed)

### Intermediate (Want to customize)
1. README.md (full read)
2. src/config.py (understand all settings)
3. QUICK_REFERENCE.md (performance tuning)

### Advanced (Want to modify code)
1. PROJECT_SUMMARY.md (architecture)
2. src/pipeline.py (understand flow)
3. Individual module files (deep dive)

---

## 📅 Version History

**Version 1.0.0** (Current)
- Complete async pipeline implementation
- 8 main modules (preprocessing, audio, STT, LLM, TTS, lipsync, renderer)
- Comprehensive documentation (9 files)
- Automated setup scripts
- Deployment tools
- ~7,000 lines total

---

## 🔗 External Dependencies

The system requires these to be downloaded separately:

1. **Llama 3.1 8B Model** (~5GB)
   - See: MODEL_DOWNLOAD_LINKS.md
   
2. **Wav2Lip Checkpoint** (~150MB)
   - See: MODEL_DOWNLOAD_LINKS.md
   
3. **Wav2Lip Repository**
   - Clone: https://github.com/Rudrabha/Wav2Lip.git

4. **Whisper Model** (auto-downloads on first run)
   - Stored in: ~/.cache/huggingface/

---

**Last Updated**: 2024  
**Version**: 1.0.0  
**Total Project Size**: ~15GB (with models)
