# Real-Time Conversational AI Avatar System

🎯 **Web-based AI avatar with real-time lip synchronization powered by Groq AI**

A GPU-accelerated conversational AI avatar system with natural lip sync, delivered through a modern web interface. Chat with an AI assistant that responds with synchronized facial animations.

---

## 🏗️ System Architecture

```
Web Interface → Groq API (LLM) → Edge-TTS → Wav2Lip → Video Output
                    ↓                ↓          ↓            ↓
              [Text Response]   [Audio]   [Lip Sync]   [MP4 File]
```

**Streaming pipeline with:**
- Web-based chat interface (Flask + JavaScript)
- Cloud-based LLM (Groq API - llama-3.1-8b-instant)
- Real-time Text-to-Speech (Edge-TTS)
- GPU-accelerated lip synchronization (Wav2Lip)
- Video-based avatar with timing-based outputs

---

## ✨ Features

- 💬 **Web Chat Interface**: Modern, responsive chat UI
- 🎭 **Video Avatar**: Uses video source for realistic animations
- 🗣️ **Natural Voice**: Microsoft Edge-TTS with neural voices
- 👄 **Lip Synchronization**: GPU-accelerated Wav2Lip
- ⚡ **Fast Processing**: Optimized for RTX 4080 (16GB VRAM)
- 📊 **Timing Metrics**: Output files named with processing duration
- 🌐 **Cloud LLM**: No local model required (uses Groq API)

---

## 📋 Requirements

### Hardware
- **GPU**: NVIDIA RTX 4070 or better (16GB VRAM recommended)
- **RAM**: 16GB minimum, 32GB recommended
- **Internet**: Required for Groq API and Edge-TTS
- **OS**: Windows 10/11 with CUDA support

### Software
- **Python**: 3.11+ (tested on 3.13.11)
- **CUDA**: 11.8 or 12.x
- **PyTorch**: 2.7.1+ with CUDA support
- **NVIDIA Drivers**: Latest recommended

---

## 📂 Project Structure

```
real_time_ai_speaker_generator/
├── web_app.py                 # Main Flask web server
├── requirements.txt           # Python dependencies
├── .env                       # Configuration (API keys)
│
├── src/                       # Core modules
│   ├── config.py              # System configuration
│   ├── lipsync/
│   │   └── wav2lip_processor.py  # Wav2Lip integration
│   ├── tts/
│   │   └── edge_tts_stream.py    # Text-to-Speech
│   └── preprocessing/
│       └── face_detector.py      # Face detection
│
├── models/                    # ⚠️ REQUIRED: Place models here
│   └── wav2lip/
│       └── wav2lip_gan.pth    # Wav2Lip checkpoint (REQUIRED)
│
├── input/                     # ⚠️ REQUIRED: Avatar source
│   ├── images/
│   │   └── avatar.jpg         # Static image option
│   └── videos/
│       └── avatar.mp4         # Video source (RECOMMENDED)
│
├── output/                    # Generated lip-sync videos
│   └── web_temp/
│       └── lipsync_*.mp4      # Timing-based output files
│
├── static/                    # Web interface assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── templates/                 # HTML templates
│   └── index.html             # Main chat interface
│
├── Wav2Lip/                   # Wav2Lip repository (cloned)
│   └── ...
│
└── Documentation files
    ├── README.md              # This file
    ├── QUICKSTART.md          # Quick start guide
    ├── SETUP_COMPLETE.txt     # Setup status
    └── MODEL_DOWNLOAD_LINKS.md
```

---

## 🚀 Installation

### 1. Clone & Setup Environment

```powershell
# Create virtual environment
pythonQuick Start

### 1. Clone Repository

```powershell
git clone https://github.com/adithya11sci/speech_assistent.git
cd speech_assistent
```

### 2. Install Dependencies

```powershell
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
pip install -r requirements.txt
```

**Key Dependencies:**
- `torch>=2.0.0` - PyTorch with CUDA
- `flask` - Web framework
- `groq` - Groq API client
- `edge-tts` - Text-to-Speech
- `opencv-python` - Video processing
- `librosa` - Audio processing
- `numpy`, `scipy` - Numerical operations

### 3. Download Wav2Lip Model

**Wav2Lip Checkpoint** (lip synchronization):
- **Download**: [wav2lip_gan.pth](https://github.com/Rudrabha/Wav2Lip#getting-the-weights)
- **Place in**: `models/wav2lip/wav2lip_gan.pth`
- **Size**: ~150MB

**Clone Wav2Lip Repository**:
```powershell
git clone https://github.com/Rudrabha/Wav2Lip.git
```

### 4. Configure API Keys

Create a `.env` file in the project root:

```ini
# Groq API Key (REQUIRED)
GROQ_API_KEY=your_groq_api_key_here

# Get your free API key at: https://console.groq.com/keys
```

**Get Groq API Key:**
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for free account
3. 💬 How to Use

1. **Open Browser**: Navigate to http://localhost:5000
2. **Wait for Avatar**: Video avatar loads automatically
3. **Start Chatting**: Type your message in the chat box
4. **Send Message**: Click "Send" or press Enter
5. **Watch Response**:
   - AI processes your message (Groq API)
   - Voice is synthesized (Edge-TTS)
   - Lip-sync video is generated (Wav2Lip)
   - Avatar speaks with synchronized lip movements
6. **Download Video**: Each response is saved in `output/web_temp/` with timing-based filename

**Example Outputs:**
- `lipsync_3s245ms.mp4` - Response took 3.245 seconds
- `lipsync_5s102ms.mp4` - Response took 5.102 seconds

---

## ⚙️ Configuration

### System Settings

Edit `src/config.py` to customize:

```python
# Wav2Lip Settings (Optimized for RTX 4080)
WAV2LIP_BATCH_SIZE = 128      # Larger = faster processing
WAV2LIP_FACE_SIZE = 192       # Face resolution (96/192/288/384)
WAV2LIP_FP16 = True           # Enable FP16 for faster inference
WAV2LIP_DEVICE = "cuda"       # Use GPU

# TTS Settings
TTS_� System Workflow

**User sends message** → **Processing Pipeline**:

1. **Text Input**: User types message in web interface
2. **Groq API**: Sends message to llama-3.1-8b-instant
3. **Stream Response**: AI response streams back token by token
4. **Edge-TTS**: Converts response text to speech audio
5. **Face Detection**: Detects face in avatar video/image
6. **Wav2Lip**: Generates lip-synchronized video on GPU
7. **Output**: Returns MP4 video with synchronized lip movements
8. **Display**: Automatically plays in browser interface

**Total Processing Time**: 5-15 seconds (depending on response length
**English Voices:**
- `en-US-AriaNeural` - Female, friendly (default)
- `en-US-JennyNeural` - Female, professional
- `en-US-GuyNeural` - Male, casual
- `en-US-DavisNeural` - Male, professional
- `en-US-SaraNeural` - Female, warm

List all available voices:
```python
import edge_tts
import asyncio
asyncio.run(edge_tts.list_voices())

```python
# Source Media
SOURCE_TYPE = "video"  # or "image"
SOURCE_VIDEO_PATH =& Performance

### Current Configuration (RTX 4080)

**Optimized Settings:**
```python
WAV2LIP_BATCH_SIZE = 128      # Maximum batch size for RTX 4080
WAV2LIP_FACE_SIZE = 192       # Balance of quality and speed
WAV2LIP_FP16 = True           # FP16 precision for 2x speedup
```

**Performance Metrics:**

| Component | Processing Time | Notes |
|-----------|----------------|-------|
| **Groq API** | 1-3 seconds | Depends on response length |
| **Edge-TTS** | 0.5-1 second | Network dependent |
| **Face Detection** | 50-100ms | Cached after first detection |
| **Wav2Lip** | 2-5 seconds | Depends on audio length |
| **Total Pipeline** | **5-15 seconds** | Full response generation |

### Memory Usage:
- **VRAM**: 4-6GB (Wav2Lip model + processing)
- **RAM**: 2-4GB (video cache + Flask)
- **Disk**: ~200MB per response video

### If You Have Less VRAM:

**For GPUs with 8GB VRAM:**
```python
WAV2LIP_BATCH_SIZE = 64       # Reduce batch size
WAV2LIP_FACE_SIZE = 128       # Smaller face resolution
WAV2LIP_FP16 = True           # Keep FP16 enabled
```

**For GPUs with 4-6GB VRAM:**
```python
WAV2LIP_BATCH_SIZE = 32       # Further reduce batch
WAV2LIP_FACE_SIZE = 96        # Minimum face size
WAV2LIP_FP16 = True           # Essential for low VRAM
```

### Server Won't Start

**Error**: Flask server exits with code 1

**Solutions**:
1. Check if port 5000 is already in use:
   ```powershell
   netstat -ano | findstr :5000
   ```
2. Kill existing Python processes:
   ```powershell
   Get-Process python | Stop-Process -Force
   ```
3. Try a different port:
   ```python
   # In web_app.py
   app.run(host='0.0.0.0', port=8000)
   ```

### Missing Groq API Key

**Error**: `GROQ_API_KEY environment variable is not set`

**Solutions**:
1. Create `.env` file in project root
2. Add your API key:
   ```ini
   GROQ_API_KEY=your_key_here
   ```
3. Get free API key at: https://console.groq.com/keys

### Wav2Lip Model Not Found

**Error**: `FileNotFoundError: wav2lip_gan.pth not found`

**Solutions**:
1. Download model from [Wav2Lip releases](https://github.com/Rudrabha/Wav2Lip#getting-the-weights)
2. Place in: `models/wav2lip/wav2lip_gan.pth`
3. Verify file size is ~150MB

### CUDA Out of Memory

**Error**: `RuntimeError: CUDA out of memory`

**Solutions**:
1. Close other GPU applications (games, browsers with hardware acceleration)
2. Reduce batch size in `src/config.py`:
   ```python
   WAV2LIP_BATCH_SIZE = 64  # or 32
   ```
3. Reduce face size:
   ```python
   WAV2LIP_FACE_SIZE = 128  # or 96
   ```
4. Clear GPU memory:
   ```powershell
   taskkill /F /IM python.exe
   ```

### Poor Lip Sync Quality

**Issue**: Lips don't match speech well

**Solutions**:
1. **Use higher resolution avatar** (720p+)
2. **Ensure clear face visibility** in source video/image
3. **Increase face size** in config:
   ```python
   WAV2LIP_FACE_SIZE = 288  # or 384 for best quality
   ```
4. **Use video instead of static image** for better results
5. **Check face detection** - face should be centered and frontal

### Slow Processing

**Issue**: Takes too long to generate videos

**Solutions**:
1. **Verify GPU is being used**:
   ```powershell
   nvidia-smi
   ```
   Should show python.exe using GPU memory
   
2. **Enable FP16** in config (if not already):
   ```python
   WAV2LIP_FP16 = True
   ```
   
3. **Increase batch size** (if you have VRAM):
   ```python
   WAV2LIP_BATCH_SIZE = 256  # RTX 4080/4090 only
   ```
   
4. **Use shorter responses**:
   ```python
   MAX_TOKENS = 100  # in web_app.py
   ```

### Video Not Playing in Browser

**Issue**: Avatar video doesn't show or play

**Solutions**:
1. **Clear browser cache**: Ctrl+Shift+Delete
2. **Check video codec**: Re-encode avatar.mp4 with H.264:
   ```powershell
   ffmpeg -i input.mp4 -c:v libx264 -c:a aac avatar.mp4
   ```
3. **Try different browser**: Chrome/Edge work best
4. **Check developer console** (F12) for errors

### Face Not Detected

**Error**: `No face detected in source media`

**Solutions**:
1. **Use frontal face photo/video** with clear visibility
2. 🎯 Use Cases

### Perfect For:
- 🎓 **Educational Content**: Create AI tutors with visual presence
- 🎥 **Content Creation**: Generate avatar videos for YouTube/social media
- 💼 **Business**: Virtual assistants and customer service avatars
- 🎮 **Gaming**: NPC characters with natural speech
- 🏥 **Healthcare**: Patient education and virtual consultations
- 📚 **E-Learning**: Interactive course instructors

### Not Suitable For:
- ⚠️ Real-time video calls (5-15s latency)
- ⚠️ High-volume production (single-threaded processing)
- ⚠️ Offline environments (requires internet for API calls)

---

## 🚧 Future Enhancements

**Planned Improvements:**
- [ ] Multi-user support with queue system
- [ ] Real-time streaming instead of file-based output
- [ ] Custom avatar upload via web interface
- [ ] Voice cloning integration
- [ ] Emotion detection and facial expressions
- [ ] Multi-language support (beyond English)
- [ ] WebSocket streaming for lower latency
- [ ] Background music and sound effects
- [ ] Gesture synthesis from text cues
- [ ] Export to multiple formats (GIF, WebM)
- [ ] Cloud deployment (Docker + Kubernetes)
- [ ] Fine-tuned Wav2Lip for specific faces

---

## 📄 License

This project code is provided as-is for educational and research purposes. 

**Component Licenses:**
- **Wav2Lip**: [Non-commercial license](https://github.com/Rudrabha/Wav2Lip#license-and-citation) - Research use only
- **PyTorch**: BSD License
- **Flask**: BSD License
- **Groq API**: Groq Terms of Service
- **Edge-TTS**: Use at your own risk (Microsoft terms apply)

**Important:** If using for commercial purposes, ensure compliance with all component licenses, especially Wav2Lip.

---

## 🙏 Acknowledgments

Built with amazing open-source technologies:

- **[Wav2Lip](https://github.com/Rudrabha/Wav2Lip)** by Rudrabha Mukhopadhyay - Lip synchronization
- **[Groq](https://groq.com/)** - Fast LLM inference API
- **[Edge-TTS](https://github.com/rany2/edge-tts)** by rany2 - Microsoft Edge TTS wrapper
- **[PyTorch](https://pytorch.org/)** - Deep learning framework
- **[Flask](https://flask.palletsprojects.com/)** - Web framework
- **[OpenCV](https://opencv.org/)** - Computer vision library

Special thanks to the AI research community for making these tools accessible.

---

## 📞 Support & Contributing

### Get Help:
- 🐛 **Bug Reports**: [Open an issue](https://github.com/adithya11sci/speech_assistent/issues)
- 💡 **Feature Requests**: [Start a discussion](https://github.com/adithya11sci/speech_assistent/discussions)
- 📧 **Contact**: For commercial inquiries and collaboration

### Contributing:
Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Test thoroughly
5. Submit a pull request

### Component-Specific Issues:
- **Wav2Lip bugs**: https://github.com/Rudrabha/Wav2Lip/issues
- **Groq API issues**: https://console.groq.com/docs
- **Edge-TTS issues**: https://github.com/rany2/edge-tts/issues

---

## 📊 Project Stats

- **Languages**: Python, JavaScript, HTML/CSS
- **Total Files**: 140+
- **Lines of Code**: 5,000+
- **Models**: Wav2Lip (150MB)
- **Dependencies**: 20+ Python packages
- **Tested On**: Windows 10/11, Python 3.13, CUDA 11.8

---

## 🌟 Key Features Summary

✅ **Web-based interface** - No command line needed  
✅ **Cloud LLM** - No local model download required  
✅ **GPU-accelerated** - Fast lip-sync processing  
✅ **Video avatars** - More realistic than static images  
✅ **Timing metrics** - Track processing performance  
✅ **Modern UI** - Clean, responsive design  
✅ **Easy setup** - Just API key + Wav2Lip model  
✅ **Extensible** - Modular code architecture  

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Fast setup guide
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment
- **[FILE_INDEX.md](FILE_INDEX.md)** - File structure reference
- **[MODEL_DOWNLOAD_LINKS.md](MODEL_DOWNLOAD_LINKS.md)** - Model downloads

---

**Made with ❤️ for the AI community**

**Star ⭐ this repo if you find it useful!processing duration: `lipsync_3s245ms.mp4`
- Files are kept for debugging/review
- Manually delete old files to free disk space

### Security Considerations

- **Never commit `.env` file** with API keys to Git
- Add `.env` to `.gitignore`
- Rotate API keys if accidentally exposed
- Use environment variables on production serversution**:
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
