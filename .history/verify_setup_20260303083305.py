"""
Model and Setup Verification Script
Run this to verify all components are ready before starting the system
"""
import os
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def check_file(path, description, required=True):
    """Check if file exists and return status"""
    if Path(path).exists():
        size = Path(path).stat().st_size / (1024**3)  # GB
        print_success(f"{description}: {size:.2f} GB at {path}")
        return True
    else:
        if required:
            print_error(f"{description}: NOT FOUND at {path}")
        else:
            print_warning(f"{description}: Not found (optional)")
        return False

def check_directory(path, description):
    """Check if directory exists"""
    if Path(path).exists() and Path(path).is_dir():
        print_success(f"{description}: {path}")
        return True
    else:
        print_error(f"{description}: NOT FOUND at {path}")
        return False

def check_python_package(package_name, import_name=None):
    """Check if Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print_success(f"Python package '{package_name}' installed")
        return True
    except ImportError:
        print_error(f"Python package '{package_name}' NOT installed")
        return False

def main():
    print("=" * 70)
    print("🔍 REAL-TIME AI AVATAR - SYSTEM VERIFICATION")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    models_dir = base_dir / "models"
    input_dir = base_dir / "input"
    src_dir = base_dir / "src"
    
    all_checks_passed = True
    
    # 1. Python Version
    print("\n📌 1. Python Environment")
    print("-" * 70)
    python_version = sys.version_info
    print_info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major >= 3 and python_version.minor >= 9:
        print_success("Python version >= 3.9")
    else:
        print_error("Python version must be >= 3.9")
        all_checks_passed = False
    
    # 2. Critical Python Packages
    print("\n📌 2. Required Python Packages")
    print("-" * 70)
    
    packages = [
        ("torch", "torch"),
        ("faster-whisper", "faster_whisper"),
        ("llama-cpp-python", "llama_cpp"),
        ("edge-tts", "edge_tts"),
        ("opencv-python", "cv2"),
        ("numpy", "numpy"),
        ("pyaudio", "pyaudio"),
        ("pydub", "pydub"),
    ]
    
    for package_name, import_name in packages:
        if not check_python_package(package_name, import_name):
            all_checks_passed = False
    
    # 3. CUDA/GPU Check
    print("\n📌 3. GPU & CUDA Support")
    print("-" * 70)
    
    try:
        import torch
        if torch.cuda.is_available():
            print_success(f"CUDA available: {torch.version.cuda}")
            print_success(f"GPU: {torch.cuda.get_device_name(0)}")
            print_info(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
        else:
            print_error("CUDA not available - GPU acceleration disabled")
            print_warning("System will run on CPU (very slow)")
            all_checks_passed = False
    except Exception as e:
        print_error(f"PyTorch check failed: {e}")
        all_checks_passed = False
    
    # 4. Models
    print("\n📌 4. AI Models")
    print("-" * 70)
    
    # Whisper
    whisper_dir = models_dir / "whisper"
    if whisper_dir.exists():
        print_success(f"Whisper model directory exists")
    else:
        print_warning("Whisper will auto-download on first run")
    
    # Llama
    llama_dir = models_dir / "llama"
    llama_found = False
    if llama_dir.exists():
        for file in llama_dir.glob("*.gguf"):
            if check_file(file, f"Llama model ({file.name})"):
                llama_found = True
                break
    
    if not llama_found:
        print_error("No Llama GGUF model found in models/llama/")
        print_info("Download from: https://huggingface.co/models?search=llama+gguf")
        all_checks_passed = False
    
    # Wav2Lip
    wav2lip_checkpoint = models_dir / "wav2lip" / "wav2lip_gan.pth"
    if not check_file(wav2lip_checkpoint, "Wav2Lip checkpoint"):
        print_info("Download from: https://github.com/Rudrabha/Wav2Lip#getting-the-weights")
        all_checks_passed = False
    
    # 5. Source Media
    print("\n📌 5. Source Media (Image or Video)")
    print("-" * 70)
    
    images_dir = input_dir / "images"
    videos_dir = input_dir / "videos"
    
    images = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpeg"))
    videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.avi")) + list(videos_dir.glob("*.mov"))
    
    media_found = False
    
    if images:
        print_success(f"Found {len(images)} image(s): {[i.name for i in images]}")
        media_found = True
    
    if videos:
        print_success(f"Found {len(videos)} video(s): {[v.name for v in videos]}")
        media_found = True
    
    if not media_found:
        print_error("No source media found in input/images/ or input/videos/")
        print_info("Add avatar.jpg (image) or avatar.mp4 (video)")
        all_checks_passed = False
    
    # 6. Configuration
    print("\n📌 6. Configuration")
    print("-" * 70)
    
    config_file = src_dir / "config.py"
    if check_file(config_file, "Configuration file"):
        print_info("Edit src/config.py to customize settings")
    else:
        print_error("config.py not found!")
        all_checks_passed = False
    
    # 7. Source Code
    print("\n📌 7. Source Code Modules")
    print("-" * 70)
    
    required_modules = [
        "preprocessing",
        "audio",
        "stt",
        "llm",
        "tts",
        "lipsync",
        "renderer"
    ]
    
    for module in required_modules:
        module_path = src_dir / module
        if not check_directory(module_path, f"Module: {module}"):
            all_checks_passed = False
    
    # 8. Wav2Lip Code Access
    print("\n📌 8. Wav2Lip Source Code")
    print("-" * 70)
    
    try:
        # Try importing Wav2Lip modules
        import sys
        # Check if Wav2Lip is in path
        wav2lip_check = False
        
        # Check common locations
        possible_paths = [
            base_dir / "Wav2Lip",
            base_dir.parent / "Wav2Lip",
            Path.cwd() / "Wav2Lip"
        ]
        
        for path in possible_paths:
            if path.exists():
                print_success(f"Wav2Lip repository found at: {path}")
                wav2lip_check = True
                break
        
        if not wav2lip_check:
            print_warning("Wav2Lip repository not found in expected locations")
            print_info("Clone: git clone https://github.com/Rudrabha/Wav2Lip.git")
            print_info("Or add to PYTHONPATH")
        
    except Exception as e:
        print_warning(f"Wav2Lip check issue: {e}")
    
    # Final Summary
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    if all_checks_passed:
        print_success("🎉 ALL CRITICAL CHECKS PASSED!")
        print_success("System is ready to run!")
        print("\n🚀 To start:")
        print(f"   cd {src_dir}")
        print("   python main.py")
    else:
        print_error("⚠️ SOME CHECKS FAILED")
        print_warning("Please resolve the issues above before running")
        print("\n📖 Refer to:")
        print("   - README.md for detailed instructions")
        print("   - QUICKSTART.md for step-by-step setup")
        print("   - MODEL_DOWNLOAD_LINKS.md for model downloads")
    
    print("=" * 70)
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
