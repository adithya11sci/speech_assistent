"""
Package Creator - Prepare project for transfer
Creates a clean copy ready for deployment
"""
import shutil
import os
from pathlib import Path
import zipfile
from datetime import datetime

def should_exclude(path, exclude_patterns):
    """Check if path should be excluded"""
    path_str = str(path)
    for pattern in exclude_patterns:
        if pattern in path_str:
            return True
    return False

def create_package():
    """Create deployment package"""
    print("="*70)
    print("📦 AI AVATAR - PACKAGE CREATOR")
    print("="*70)
    
    source_dir = Path(__file__).parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"ai_avatar_package_{timestamp}"
    package_dir = source_dir.parent / package_name
    
    # Patterns to exclude
    exclude_patterns = [
        '__pycache__',
        '.pyc',
        '.pyo',
        'venv',
        'env',
        '.git',
        '.vscode',
        '.idea',
        'output',
        '.DS_Store',
        'Thumbs.db',
        '.history',
    ]
    
    print(f"\n📂 Creating package: {package_name}")
    print(f"Source: {source_dir}")
    print(f"Destination: {package_dir}\n")
    
    # Ask what to include
    print("What to include:")
    print("1. Code only (lightweight, ~10MB)")
    print("2. Code + Models (if downloaded, ~6-7GB)")
    print("3. Code + Models + Input media")
    
    choice = input("\nChoose option (1-3) [default: 1]: ").strip() or "1"
    
    include_models = choice in ["2", "3"]
    include_input = choice == "3"
    
    # Create package directory
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    print("\n📝 Copying files...")
    
    copied_count = 0
    skipped_count = 0
    
    for item in source_dir.rglob("*"):
        if item.is_file():
            # Check exclusions
            if should_exclude(item, exclude_patterns):
                skipped_count += 1
                continue
            
            # Special handling for models and input
            relative_path = item.relative_to(source_dir)
            
            if not include_models and "models" in str(relative_path):
                if item.name != ".gitkeep" and item.name != "README.md":
                    skipped_count += 1
                    continue
            
            if not include_input and "input" in str(relative_path):
                if item.name != ".gitkeep" and item.name != "README.md":
                    skipped_count += 1
                    continue
            
            # Copy file
            dest_file = package_dir / relative_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_file)
            copied_count += 1
            
            if copied_count % 10 == 0:
                print(f"  Copied {copied_count} files...", end="\r")
    
    print(f"\n✅ Copied {copied_count} files (skipped {skipped_count})")
    
    # Create README for package
    readme_content = f"""# AI Avatar System - Deployment Package

Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Package type: {"Code + Models + Input" if choice == "3" else "Code + Models" if choice == "2" else "Code only"}

## Quick Start

1. Extract this package to your desired location
2. Read DEPLOYMENT_GUIDE.md for complete instructions
3. Run: python setup_target_pc.py (automated setup)
4. Follow the setup script prompts

## Manual Setup

See DEPLOYMENT_GUIDE.md for detailed step-by-step instructions.

## What's Included

- Full source code (src/)
- Documentation (*.md files)
- Configuration (config.py)
- Setup scripts
{"- AI Models (models/)" if include_models else ""}
{"- Source media (input/)" if include_input else ""}

## What You Need to Add

{"" if include_models else "- Download AI models (see MODEL_DOWNLOAD_LINKS.md)"}
{"" if include_input else "- Add your avatar image/video to input/"}
- Install Python 3.9+
- Install CUDA toolkit
- Run setup scripts

## Support

Refer to:
- README.md - Main documentation
- QUICKSTART.md - Setup guide
- DEPLOYMENT_GUIDE.md - Transfer instructions
- MODEL_DOWNLOAD_LINKS.md - Model downloads

---
Package created by package_creator.py
"""
    
    with open(package_dir / "PACKAGE_README.txt", "w") as f:
        f.write(readme_content)
    
    # Create ZIP archive
    print("\n📦 Creating ZIP archive...")
    
    zip_path = package_dir.parent / f"{package_name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in package_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(package_dir.parent)
                zipf.write(file, arcname)
                print(f"  Adding: {arcname}", end="\r")
    
    zip_size = zip_path.stat().st_size / (1024*1024)  # MB
    
    print(f"\n✅ ZIP created: {zip_path.name}")
    print(f"   Size: {zip_size:.1f} MB")
    
    # Summary
    print("\n" + "="*70)
    print("📊 PACKAGE SUMMARY")
    print("="*70)
    print(f"Package folder: {package_dir}")
    print(f"ZIP archive: {zip_path}")
    print(f"Archive size: {zip_size:.1f} MB")
    print(f"Files included: {copied_count}")
    
    print("\n✅ Package ready for transfer!")
    print("\n📋 Next steps:")
    print("1. Transfer ZIP to target PC via USB/network/cloud")
    print("2. Extract ZIP on target PC")
    print("3. Follow DEPLOYMENT_GUIDE.md")
    print("4. Run: python setup_target_pc.py")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        create_package()
    except KeyboardInterrupt:
        print("\n\n❌ Packaging cancelled")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
