"""
Face Detector - Detect and cache face bounding boxes
Uses dlib or face_detection library for optimal performance
"""
import cv2
import numpy as np
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class FaceDetector:
    """Detect faces and cache bounding boxes for real-time performance"""
    
    def __init__(self, 
                 detection_model_path: Optional[str] = None,
                 face_size: int = 256,
                 box_expansion: float = 0.1):
        """
        Initialize face detector
        
        Args:
            detection_model_path: Path to face detection model (optional)
            face_size: Target size for face crop
            box_expansion: Expand bounding box by this ratio (0.1 = 10%)
        """
        self.detection_model_path = detection_model_path
        self.face_size = face_size
        self.box_expansion = box_expansion
        
        # Cached face coordinates
        self.cached_coords: Optional[Tuple[int, int, int, int]] = None
        
        # Try to load face_detection library (used by Wav2Lip)
        try:
            import face_detection
            self.detector = face_detection.FaceAlignment(
                face_detection.LandmarksType._2D, 
                flip_input=False, 
                device='cuda'
            )
            self.detection_method = "face_detection"
            logger.info("Using face_detection library")
        except ImportError:
            logger.warning("face_detection not available, falling back to OpenCV Haar Cascade")
            self.detector = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            self.detection_method = "opencv"
    
    def detect_face(self, frame: np.ndarray, use_cache: bool = True) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect face in frame and return bounding box
        
        Args:
            frame: Input frame (BGR)
            use_cache: Use cached coordinates if available
            
        Returns:
            Tuple of (x, y, width, height) or None if no face detected
        """
        if use_cache and self.cached_coords is not None:
            return self.cached_coords
        
        if self.detection_method == "face_detection":
            coords = self._detect_with_face_detection(frame)
        else:
            coords = self._detect_with_opencv(frame)
        
        if coords is not None and use_cache:
            self.cached_coords = coords
            logger.info(f"Cached face coordinates: {coords}")
        
        return coords
    
    def _detect_with_face_detection(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect using face_detection library"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            predictions = self.detector.get_detections_for_batch(np.array([rgb_frame]))
            
            if predictions is None or len(predictions) == 0 or predictions[0] is None:
                logger.warning("No face detected")
                return None
            
            # Get first face
            face = predictions[0][0]  # First batch, first face
            
            # Extract bounding box
            x1, y1, x2, y2 = map(int, face[:4])
            
            # Expand box
            width = x2 - x1
            height = y2 - y1
            expansion = int(min(width, height) * self.box_expansion)
            
            x1 = max(0, x1 - expansion)
            y1 = max(0, y1 - expansion)
            x2 = min(frame.shape[1], x2 + expansion)
            y2 = min(frame.shape[0], y2 + expansion)
            
            return (x1, y1, x2 - x1, y2 - y1)
            
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return None
    
    def _detect_with_opencv(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect using OpenCV Haar Cascade (fallback)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            logger.warning("No face detected with OpenCV")
            return None
        
        # Get largest face
        face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = face
        
        # Expand box
        expansion = int(min(w, h) * self.box_expansion)
        x = max(0, x - expansion)
        y = max(0, y - expansion)
        w = min(frame.shape[1] - x, w + 2 * expansion)
        h = min(frame.shape[0] - y, h + 2 * expansion)
        
        return (x, y, w, h)
    
    def crop_face(self, frame: np.ndarray, coords: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """
        Crop face from frame
        
        Args:
            frame: Input frame
            coords: Face coordinates (x, y, w, h). If None, detect face
            
        Returns:
            Cropped and resized face image
        """
        if coords is None:
            coords = self.detect_face(frame)
        
        if coords is None:
            return None
        
        x, y, w, h = coords
        
        # Crop face
        face = frame[y:y+h, x:x+w]
        
        if face.size == 0:
            return None
        
        # Resize to target size
        face_resized = cv2.resize(face, (self.face_size, self.face_size))
        
        return face_resized
    
    def get_face_region(self, frame: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
        """
        Get face region and coordinates
        
        Returns:
            Tuple of (face_image, coordinates)
        """
        coords = self.detect_face(frame, use_cache=True)
        
        if coords is None:
            # Return full frame as fallback
            logger.warning("No face detected, using full frame")
            h, w = frame.shape[:2]
            coords = (0, 0, w, h)
        
        face = self.crop_face(frame, coords)
        
        return face, coords
    
    def clear_cache(self):
        """Clear cached face coordinates"""
        self.cached_coords = None
        logger.info("Face detection cache cleared")
    
    def paste_face_back(self, 
                       full_frame: np.ndarray, 
                       face_frame: np.ndarray, 
                       coords: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Paste processed face back into full frame
        
        Args:
            full_frame: Original full frame
            face_frame: Processed face (256x256)
            coords: Original face coordinates (x, y, w, h)
            
        Returns:
            Full frame with face replaced
        """
        x, y, w, h = coords
        
        # Resize face back to original size
        face_resized = cv2.resize(face_frame, (w, h))
        
        # Create copy of full frame
        result = full_frame.copy()
        
        # Paste face back
        result[y:y+h, x:x+w] = face_resized
        
        return result
