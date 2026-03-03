"""
Quick Setup Script for Target PC
Automates installation of dependencies
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description, shell=True):
    """Run command and report status"""
    print(f"\n{'='*70}")
    print(f"⚙️  {description}")
    print(f"{'='*70}")
    print(f"Command: {cmd}\n")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=shell, 
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        return False

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"\n📌 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 9:
        print("✅ Python version OK (>= 3.9)")
        return True
    else:
        print("❌ Python version must be >= 3.9")
        return False

def check_gpu():
    """Check if NVIDIA GPU is available"""
    try:
        result = subprocess.run(
            "nvidia-smi",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ NVIDIA GPU detected")
            return True
        else:
            print("⚠️  NVIDIA GPU not detected or drivers not installed")
            return False
    except:
        print("⚠️  nvidia-smi command not found")
        return False

def main():
    """Main setup script"""
    print("="*70)
    print("🚀 AI AVATAR SYSTEM - AUTOMATED SETUP")
    print("="*70)
    print("\nThis script will install all required dependencies.")
    print("This may take 10-20 minutes depending on your internet speed.\n")
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    # Check prerequisites
    print("\n" + "="*70)
    print("1️⃣  CHECKING PREREQUISITES")
    print("="*70)
    
    if not check_python_version():
        print("\n❌ Please install Python 3.9 or higher and try again")
        return 1
    
    check_gpu()  # Warning only, not required
    
    # Create virtual environment
    print("\n" + "="*70)
    print("2️⃣  CREATING VIRTUAL ENVIRONMENT")
    print("="*70)
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("⚠️  Virtual environment already exists")
        response = input("Recreate? (y/n): ")
        if response.lower() == 'y':
            import shutil
            shutil.rmtree(venv_path)
        else:
            print("Using existing virtual environment")
    
    if not venv_path.exists():
        if not run_command(
            f"{sys.executable} -m venv venv",
            "Creating virtual environment"
        ):
            return 1
    
    # Determine pip path
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip.exe"
        python_path = "venv\\Scripts\\python.exe"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Upgrade pip
    run_command(
        f"{python_path} -m pip install --upgrade pip",
        "Upgrading pip"
    )
    
    # Install PyTorch with CUDA
    print("\n" + "="*70)
    print("3️⃣  INSTALLING PYTORCH WITH CUDA")
    print("="*70)
    
    print("\nSelect CUDA version:")
    print("1. CUDA 11.8 (recommended for most systems)")
    print("2. CUDA 12.1 (for newer GPUs)")
    print("3. CPU only (not recommended - very slow)")
    
    cuda_choice = input("\nEnter choice (1-3) [default: 1]: ").strip() or "1"
    
    if cuda_choice == "1":
        torch_cmd = f"{pip_path} install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
    elif cuda_choice == "2":
        torch_cmd = f"{pip_path} install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
    else:
        torch_cmd = f"{pip_path} install torch torchvision torchaudio"
    
    if not run_command(torch_cmd, "Installing PyTorch"):
        print("\n⚠️  PyTorch installation failed. Continuing with other packages...")
    
    # Install llama-cpp-python with CUDA
    print("\n" + "="*70)
    print("4️⃣  INSTALLING LLAMA-CPP-PYTHON WITH CUDA SUPPORT")
    print("="*70)
    
    if cuda_choice in ["1", "2"]:
        print("This will compile llama-cpp-python with CUDA support (takes 5-10 minutes)")
        if sys.platform == "win32":
            os.environ["CMAKE_ARGS"] = "-DLLAMA_CUBLAS=on"
        else:
            os.environ["CMAKE_ARGS"] = "-DLLAMA_CUBLAS=on"
        
        run_command(
            f"{pip_path} install llama-cpp-python --force-reinstall --no-cache-dir",
            "Installing llama-cpp-python with CUDA"
        )
    else:
        run_command(
            f"{pip_path} install llama-cpp-python",
            "Installing llama-cpp-python (CPU only)"
        )
    
    # Install other dependencies
    print("\n" + "="*70)
    print("5️⃣  INSTALLING OTHER DEPENDENCIES")
    print("="*70)
    
    if not run_command(
        f"{pip_path} install -r requirements.txt",
        "Installing requirements.txt"
    ):
        print("\n⚠️  Some packages failed to install")
    
    # Install PyAudio (Windows special handling)
    if sys.platform == "win32":
        print("\n" + "="*70)
        print("6️⃣  INSTALLING PYAUDIO (WINDOWS)")
        print("="*70)
        
        # Try pipwin first
        if run_command(f"{pip_path} install pipwin", "Installing pipwin"):
            run_command(f"venv\\Scripts\\pipwin.exe install pyaudio", "Installing PyAudio via pipwin")
        else:
            print("\n⚠️  PyAudio installation may fail. If it does, download wheel from:")
            print("https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
    
    # Verify installation
    print("\n" + "="*70)
    print("7️⃣  VERIFYING INSTALLATION")
    print("="*70)
    
    verification_script = """
import sys
print("Python:", sys.version)

try:
    import torch
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
except Exception as e:
    print(f"PyTorch: FAILED - {e}")

try:
    import faster_whisper
    print(f"Faster-Whisper: OK")
except Exception as e:
    print(f"Faster-Whisper: FAILED - {e}")

try:
    import llama_cpp
    print(f"Llama-cpp-python: OK")
except Exception as e:
    print(f"Llama-cpp-python: FAILED - {e}")

try:
    import edge_tts
    print(f"Edge-TTS: OK")
except Exception as e:
    print(f"Edge-TTS: FAILED - {e}")

try:
    import cv2
    print(f"OpenCV: OK")
except Exception as e:
    print(f"OpenCV: FAILED - {e}")

try:
    import pyaudio
    print(f"PyAudio: OK")
except Exception as e:
    print(f"PyAudio: FAILED - {e}")
"""
    
    with open("_verify_temp.py", "w") as f:
        f.write(verification_script)
    
    run_command(
        f"{python_path} _verify_temp.py",
        "Verifying packages"
    )
    
    os.remove("_verify_temp.py")
    
    # Final instructions
    print("\n" + "="*70)
    print("✅ SETUP COMPLETE!")
    print("="*70)
    
    print("\n📋 NEXT STEPS:")
    print("\n1. Download models:")
    print("   - Llama GGUF model (~5GB)")
    print("   - Wav2Lip checkpoint (~150MB)")
    print("   See: MODEL_DOWNLOAD_LINKS.md")
    
    print("\n2. Clone Wav2Lip repository:")
    print("   git clone https://github.com/Rudrabha/Wav2Lip.git")
    
    print("\n3. Add source media (image or video) to input/ folder")
    
    print("\n4. Run verification:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\python.exe verify_setup.py")
    else:
        print("   venv/bin/python verify_setup.py")
    
    print("\n5. Run the system:")
    if sys.platform == "win32":
        print("   cd src")
        print("   ..\\venv\\Scripts\\python.exe main.py")
    else:
        print("   cd src")
        print("   ../venv/bin/python main.py")
    
    print("\n" + "="*70)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        sys.exit(1)
