"""
Wav2Lip Processor - Real-time lip synchronization
Optimized for low-latency streaming with GPU acceleration
"""
import asyncio
import cv2
import numpy as np
import torch
from typing import Optional, Tuple, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Wav2LipProcessor:
    """Real-time lip sync using Wav2Lip"""
    
    def __init__(self,
                 checkpoint_path: str,
                 device: str = "cuda",
                 face_size: int = 256,
                 fps: int = 25,
                 batch_size: int = 1,
                 use_fp16: bool = True,
                 window_overlap: float = 0.2):
        """
        Initialize Wav2Lip processor
        
        Args:
            checkpoint_path: Path to wav2lip_gan.pth
            device: Device (cuda, cpu)
            face_size: Face resolution (256 recommended for speed)
            fps: Target FPS
            batch_size: Batch size (keep 1 for real-time)
            use_fp16: Use FP16 for faster inference
            window_overlap: Overlap between audio windows (seconds)
        """
        self.checkpoint_path = Path(checkpoint_path)
        self.device = device
        self.face_size = face_size
        self.fps = fps
        self.batch_size = batch_size
        self.use_fp16 = use_fp16
        self.window_overlap = window_overlap
        
        self.model = None
        self.mel_step_size = 16
        self.audio_buffer = []
        
    def load_model(self):
        """Load Wav2Lip model"""
        try:
            logger.info(f"Loading Wav2Lip model from: {self.checkpoint_path}")
            
            # Import Wav2Lip inference
            # Note: This assumes you have Wav2Lip repository code available
            # You'll need to add Wav2Lip to your Python path
            try:
                from models import Wav2Lip
            except ImportError:
                logger.error("Wav2Lip models not found. Please add Wav2Lip repo to Python path")
                raise
            
            # Load checkpoint
            checkpoint = torch.load(
                str(self.checkpoint_path),
                map_location=self.device
            )
            
            # Initialize model
            self.model = Wav2Lip()
            self.model.load_state_dict(checkpoint["state_dict"])
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # Use FP16 if enabled
            if self.use_fp16 and self.device == "cuda":
                self.model = self.model.half()
                logger.info("Using FP16 inference")
            
            logger.info("Wav2Lip model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Wav2Lip model: {e}")
            raise
    
    def preprocess_audio(self, audio: np.ndarray, sample_rate: int = 16000) -> np.ndarray:
        """
        Preprocess audio to mel spectrogram
        
        Args:
            audio: Audio array (int16)
            sample_rate: Sample rate
            
        Returns:
            Mel spectrogram
        """
        try:
            # Import audio processing from Wav2Lip
            from audio import melspectrogram
            
            # Normalize audio
            audio_float = audio.astype(np.float32) / 32768.0
            
            # Generate mel spectrogram
            mel = melspectrogram(audio_float, sample_rate)
            
            return mel
            
        except ImportError:
            logger.error("Wav2Lip audio module not found")
            return np.zeros((80, 16))
        except Exception as e:
            logger.error(f"Audio preprocessing error: {e}")
            return np.zeros((80, 16))
    
    def preprocess_frame(self, frame: np.ndarray) -> torch.Tensor:
        """
        Preprocess frame for Wav2Lip
        
        Args:
            frame: Input frame (BGR, 256x256)
            
        Returns:
            Preprocessed tensor
        """
        # Resize if needed
        if frame.shape[0] != self.face_size or frame.shape[1] != self.face_size:
            frame = cv2.resize(frame, (self.face_size, self.face_size))
        
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Normalize to [-1, 1]
        frame = frame.astype(np.float32) / 255.0
        frame = (frame - 0.5) / 0.5
        
        # Convert to tensor (C, H, W)
        frame_tensor = torch.FloatTensor(frame.transpose(2, 0, 1))
        
        return frame_tensor
    
    def generate_lip_sync(self,
                         face_frame: np.ndarray,
                         audio: np.ndarray,
                         sample_rate: int = 16000) -> List[np.ndarray]:
        """
        Generate lip-synced frames
        
        Args:
            face_frame: Face image (256x256, BGR)
            audio: Audio array (int16)
            sample_rate: Audio sample rate
            
        Returns:
            List of lip-synced frames
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first")
        
        try:
            # Preprocess audio to mel spectrogram
            mel = self.preprocess_audio(audio, sample_rate)
            
            # Calculate number of frames needed
            mel_chunks = mel.shape[1]
            num_frames = mel_chunks
            
            # Preprocess face frame
            face_tensor = self.preprocess_frame(face_frame)
            
            # Prepare frame sequence (repeat same frame for all mel chunks)
            faces = face_tensor.unsqueeze(0).repeat(num_frames, 1, 1, 1)
            faces = faces.to(self.device)
            
            if self.use_fp16 and self.device == "cuda":
                faces = faces.half()
            
            # Prepare mel spectrogram
            mel_tensor = torch.FloatTensor(mel.T).unsqueeze(0).unsqueeze(0)
            mel_tensor = mel_tensor.to(self.device)
            
            if self.use_fp16 and self.device == "cuda":
                mel_tensor = mel_tensor.half()
            
            # Generate in batches
            generated_frames = []
            
            with torch.no_grad():
                for i in range(0, num_frames, self.batch_size):
                    batch_end = min(i + self.batch_size, num_frames)
                    
                    face_batch = faces[i:batch_end]
                    mel_batch = mel_tensor[:, :, i:batch_end, :]
                    
                    # Generate
                    pred = self.model(mel_batch, face_batch)
                    
                    # Postprocess
                    pred = pred.cpu().float().numpy()
                    pred = pred.transpose(0, 2, 3, 1)  # (B, C, H, W) -> (B, H, W, C)
                    
                    # Denormalize
                    pred = (pred * 0.5 + 0.5) * 255.0
                    pred = pred.astype(np.uint8)
                    
                    # Convert RGB to BGR
                    for frame in pred:
                        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        generated_frames.append(frame_bgr)
            
            return generated_frames
            
        except Exception as e:
            logger.error(f"Lip sync generation error: {e}")
            # Return original frame as fallback
            return [face_frame]
    
    async def process_audio_stream(self,
                                  audio_queue: asyncio.Queue,
                                  frame_queue: asyncio.Queue,
                                  source_frame_provider,
                                  face_coords: Tuple[int, int, int, int]):
        """
        Process streaming audio and generate lip-synced frames
        
        Args:
            audio_queue: Input audio queue (MP3 bytes from TTS)
            frame_queue: Output frame queue
            source_frame_provider: Function to get source frames
            face_coords: Face coordinates (x, y, w, h)
        """
        logger.info("Started Wav2Lip streaming")
        
        try:
            while True:
                # Get audio chunk
                audio_bytes = await audio_queue.get()
                
                if audio_bytes is None:
                    # End signal
                    await frame_queue.put(None)
                    continue
                
                # Convert audio bytes to numpy array
                from pydub import AudioSegment
                import io
                
                audio_segment = AudioSegment.from_file(
                    io.BytesIO(audio_bytes),
                    format="mp3"
                )
                
                # Convert to 16kHz mono
                audio_segment = audio_segment.set_frame_rate(16000)
                audio_segment = audio_segment.set_channels(1)
                
                # Get numpy array
                audio_array = np.array(audio_segment.get_array_of_samples()).astype(np.int16)
                
                # Get source frame
                full_frame = source_frame_provider()
                
                # Extract face region
                x, y, w, h = face_coords
                face_frame = full_frame[y:y+h, x:x+w]
                face_frame = cv2.resize(face_frame, (self.face_size, self.face_size))
                
                # Generate lip-synced frames
                synced_frames = await asyncio.to_thread(
                    self.generate_lip_sync,
                    face_frame,
                    audio_array
                )
                
                # Paste back to full frames and send to queue
                for synced_face in synced_frames:
                    # Resize face back
                    synced_face_resized = cv2.resize(synced_face, (w, h))
                    
                    # Get fresh source frame
                    output_frame = source_frame_provider()
                    
                    # Paste face
                    output_frame[y:y+h, x:x+w] = synced_face_resized
                    
                    # Send to render queue
                    await frame_queue.put(output_frame)
                
        except asyncio.CancelledError:
            logger.info("Wav2Lip processing cancelled")
        except Exception as e:
            logger.error(f"Error in Wav2Lip streaming: {e}")
            await frame_queue.put(None)
    
    def unload_model(self):
        """Unload model to free memory"""
        if self.model:
            del self.model
            self.model = None
            torch.cuda.empty_cache()
            logger.info("Wav2Lip model unloaded")
