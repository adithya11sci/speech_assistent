# Dependency Installation Script for Real-Time AI Avatar System
# This script installs all required Python packages

$separator = "======================================================================"
Write-Host $separator -ForegroundColor Cyan
Write-Host "Installing Python Dependencies for AI Avatar System" -ForegroundColor Yellow
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "ERROR: Python not found! Please install Python 3.9+ first" -ForegroundColor Red
    exit 1
}

# Check Python version
$pythonVersion = python --version
Write-Host "Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Upgrade pip first
Write-Host "Step 1: Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install PyTorch with CUDA support
Write-Host ""
Write-Host "Step 2: Installing PyTorch with CUDA 11.8 support..." -ForegroundColor Cyan
Write-Host "  (This may take several minutes)" -ForegroundColor Yellow
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install core dependencies
Write-Host ""
Write-Host "Step 3: Installing core dependencies..." -ForegroundColor Cyan
pip install numpy>=1.24.0
pip install opencv-python>=4.8.0
pip install scipy>=1.11.0

# Install audio processing
Write-Host ""
Write-Host "Step 4: Installing audio processing libraries..." -ForegroundColor Cyan
pip install pyaudio>=0.2.13
pip install pydub>=0.25.1
pip install librosa>=0.10.0

# Install AI models
Write-Host ""
Write-Host "Step 5: Installing AI model libraries..." -ForegroundColor Cyan
pip install faster-whisper>=0.9.0
pip install groq>=0.4.0
pip install edge-tts>=6.1.0

# Install face detection
Write-Host ""
Write-Host "Step 6: Installing face detection libraries..." -ForegroundColor Cyan
pip install face-alignment>=1.3.5

# Install utilities
Write-Host ""
Write-Host "Step 7: Installing utilities..." -ForegroundColor Cyan
pip install einops>=0.7.0
pip install timm>=0.9.0
pip install imageio>=2.31.0
pip install imageio-ffmpeg>=0.4.9
pip install aiofiles>=23.2.0
pip install tqdm>=4.66.0
pip install python-dotenv>=1.0.0
pip install psutil>=5.9.0
pip install flask>=3.0.0

# Verify installations
Write-Host ""
Write-Host $separator -ForegroundColor Cyan
Write-Host "Verifying installations..." -ForegroundColor Green
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

# Run verification script
python verify_setup.py

Write-Host ""
Write-Host $separator -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host $separator -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Set your Groq API key in .env file:" -ForegroundColor White
Write-Host "   GROQ_API_KEY=your_api_key_here" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run verification again:" -ForegroundColor White
Write-Host "   python verify_setup.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Start the system:" -ForegroundColor White
Write-Host "   python run_avatar_windows.py" -ForegroundColor Gray
Write-Host ""
Write-Host $separator -ForegroundColor Cyan
