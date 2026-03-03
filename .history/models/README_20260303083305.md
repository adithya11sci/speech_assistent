# Models Directory

⚠️ **Place your trained models here**

This directory should contain all the AI models required for the system:

## Directory Structure

```
models/
├── whisper/              # Faster-Whisper models
│   └── small.en/         # Model files (auto-downloaded on first run)
│
├── llama/                # Llama LLM models
│   └── llama-3.1-8b-instruct-q4_k_m.gguf  # ~4.9GB
│
└── wav2lip/              # Wav2Lip checkpoints
    ├── wav2lip_gan.pth   # Main checkpoint (~150MB)
    └── face_detection.pth # Optional face detection model
```

## Where to Download

### 1. Faster-Whisper
- **Auto-downloads** on first run
- Or manually download from: https://huggingface.co/models?search=whisper

### 2. Llama 3.1 8B (GGUF)
- HuggingFace: Search "llama-3.1-8b-instruct gguf"
- Recommended: Q4_K_M quantization (~4.9GB)
- Direct: https://huggingface.co/models?search=llama-3.1-8b-instruct-gguf

### 3. Wav2Lip
- Official checkpoint: https://github.com/Rudrabha/Wav2Lip#getting-the-weights
- Download `wav2lip_gan.pth`
- Face detection (optional): Download from Wav2Lip repo

## Important Notes

- **Do not commit** large model files to git (already in .gitignore)
- Total size: ~6-7GB for all models
- Ensure sufficient disk space
- Models load into GPU VRAM during initialization

## Model Placement Checklist

- [ ] Whisper model downloaded/auto-configured
- [ ] Llama GGUF model in `models/llama/`
- [ ] Wav2Lip checkpoint in `models/wav2lip/`
- [ ] Paths in `config.py` match your filenames
