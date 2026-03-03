"""
Real-Time Conversational AI Avatar System
Main entry point
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline import main

if __name__ == "__main__":
    """
    Run the real-time AI avatar system
    
    Requirements:
    - Models must be placed in models/ directory
    - Source media (image or video) in input/ directory
    - Microphone connected
    - GPU with CUDA support (RTX 4070 recommended)
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nSystem stopped by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
