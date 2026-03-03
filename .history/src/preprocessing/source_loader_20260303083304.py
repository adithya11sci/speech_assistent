"""
Source Media Loader - Handles image and video loading
Optimized for real-time performance with frame caching
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SourceLoader:
    """Load and manage source media (image or video)"""
    
    def __init__(self, 
                 source_path: Path, 
                 source_type: str = "video",
                 preload_all: bool = True,
                 target_fps: int = 25,
                 loop: bool = True):
        """
        Initialize source loader
        
        Args:
            source_path: Path to source image or video
            source_type: "image" or "video"
            preload_all: Load all frames into memory (recommended for videos < 10 sec)
            target_fps: Target FPS for frame extraction
            loop: Loop video frames continuously
        """
        self.source_path = Path(source_path)
        self.source_type = source_type.lower()
        self.preload_all = preload_all
        self.target_fps = target_fps
        self.loop = loop
        
        self.frames: List[np.ndarray] = []
        self.current_frame_idx = 0
        self.total_frames = 0
        self.original_fps = None
        self.cap = None
        
        # Validate source file exists
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source file not found: {self.source_path}")
        
        # Load source media
        self._load_source()
        
    def _load_source(self):
        """Load source media based on type"""
        if self.source_type == "image":
            self._load_image()
        elif self.source_type == "video":
            self._load_video()
        else:
            raise ValueError(f"Invalid source_type: {self.source_type}. Must be 'image' or 'video'")
        
        logger.info(f"Loaded {self.source_type} from {self.source_path}")
        logger.info(f"Total frames: {self.total_frames}")
        
    def _load_image(self):
        """Load static image"""
        img = cv2.imread(str(self.source_path))
        if img is None:
            raise ValueError(f"Failed to load image: {self.source_path}")
        
        # Store single frame
        self.frames = [img]
        self.total_frames = 1
        self.original_fps = self.target_fps
        
    def _load_video(self):
        """Load video and optionally extract all frames"""
        self.cap = cv2.VideoCapture(str(self.source_path))
        
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video: {self.source_path}")
        
        self.original_fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames_in_video = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Video: {total_frames_in_video} frames at {self.original_fps} FPS")
        
        if self.preload_all:
            # Extract all frames into memory
            logger.info("Preloading all frames into memory...")
            
            # Calculate frame skip for target FPS
            frame_skip = max(1, int(self.original_fps / self.target_fps))
            
            frame_idx = 0
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Only keep frames at target FPS
                if frame_idx % frame_skip == 0:
                    self.frames.append(frame)
                
                frame_idx += 1
            
            self.total_frames = len(self.frames)
            self.cap.release()
            self.cap = None
            
            logger.info(f"Preloaded {self.total_frames} frames (resampled to {self.target_fps} FPS)")
        else:
            self.total_frames = total_frames_in_video
            
    def get_next_frame(self) -> np.ndarray:
        """
        Get next frame from source
        
        Returns:
            Frame as numpy array (BGR format)
        """
        if self.source_type == "image":
            # Return same image every time
            return self.frames[0].copy()
        
        if self.preload_all:
            # Return from preloaded frames
            frame = self.frames[self.current_frame_idx].copy()
            self.current_frame_idx += 1
            
            # Loop if enabled
            if self.current_frame_idx >= self.total_frames:
                if self.loop:
                    self.current_frame_idx = 0
                else:
                    self.current_frame_idx = self.total_frames - 1
                    
            return frame
        else:
            # Read from video capture (slower)
            if self.cap is None or not self.cap.isOpened():
                raise RuntimeError("Video capture not initialized")
            
            ret, frame = self.cap.read()
            
            if not ret:
                if self.loop:
                    # Loop back to start
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.cap.read()
                else:
                    # Return last frame
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.total_frames - 1)
                    ret, frame = self.cap.read()
            
            if not ret:
                raise RuntimeError("Failed to read frame from video")
            
            return frame
    
    def get_frame_at_index(self, idx: int) -> np.ndarray:
        """Get specific frame by index"""
        if self.source_type == "image":
            return self.frames[0].copy()
        
        if self.preload_all:
            idx = idx % self.total_frames if self.loop else min(idx, self.total_frames - 1)
            return self.frames[idx].copy()
        else:
            if self.cap is None:
                raise RuntimeError("Video capture not initialized")
            
            idx = idx % self.total_frames if self.loop else min(idx, self.total_frames - 1)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = self.cap.read()
            
            if not ret:
                raise RuntimeError(f"Failed to read frame at index {idx}")
            
            return frame
    
    def get_frame_dimensions(self) -> Tuple[int, int]:
        """Get frame dimensions (width, height)"""
        frame = self.frames[0] if self.frames else self.get_next_frame()
        return frame.shape[1], frame.shape[0]
    
    def reset(self):
        """Reset frame counter to beginning"""
        self.current_frame_idx = 0
        if self.cap is not None and not self.preload_all:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    def release(self):
        """Release resources"""
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        self.frames.clear()
        logger.info("Source loader released")
    
    def __del__(self):
        """Cleanup"""
        self.release()
