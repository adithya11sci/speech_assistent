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
import sys

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

        # Optimization cached properties
        self._cached_mask = None
        self._cached_mask_size = None
        
    def load_model(self):
        """Load Wav2Lip model"""
        try:
            logger.info(f"Loading Wav2Lip model from: {self.checkpoint_path}")
            
            # Add Wav2Lip repository to Python path
            wav2lip_repo = Path(__file__).parent.parent.parent / "Wav2Lip"
            if wav2lip_repo.exists():
                sys.path.insert(0, str(wav2lip_repo))
                logger.info(f"Added Wav2Lip repo to path: {wav2lip_repo}")
            else:
                logger.warning(f"Wav2Lip repo not found at: {wav2lip_repo}")
            
            # Import Wav2Lip inference
            try:
                from models import Wav2Lip
            except ImportError as e:
                logger.error(f"Wav2Lip models not found: {e}")
                logger.error("Please ensure Wav2Lip repository is cloned in project root")
                raise
            
            # Load checkpoint - handle both TorchScript and regular checkpoints
            try:
                # Try loading as TorchScript first
                logger.info("Attempting to load as TorchScript model")
                self.model = torch.jit.load(str(self.checkpoint_path), map_location=self.device)
                logger.info("Loaded as TorchScript model")
            except Exception as e:
                logger.info(f"Not a TorchScript model ({e}), loading as state_dict")
                # Load as regular checkpoint
                checkpoint = torch.load(
                    str(self.checkpoint_path),
                    map_location=self.device,
                    weights_only=False
                )
                
                # Initialize model
                self.model = Wav2Lip()
                self.model.load_state_dict(checkpoint["state_dict"])
                self.model = self.model.to(self.device)
            
            # Set to eval mode
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
            audio: Audio array (int16 or float32)
            sample_rate: Sample rate (Wav2Lip expects 16000)
            
        Returns:
            Mel spectrogram
        """
        try:
            # Ensure Wav2Lip is in path
            wav2lip_repo = Path(__file__).parent.parent.parent / "Wav2Lip"
            if str(wav2lip_repo) not in sys.path and wav2lip_repo.exists():
                sys.path.insert(0, str(wav2lip_repo))
            
            # Import audio processing from Wav2Lip
            import audio as wav2lip_audio
            
            # Normalize audio to float32 in range [-1, 1]
            if audio.dtype == np.int16:
                audio_float = audio.astype(np.float32) / 32768.0
            elif audio.dtype == np.float64:
                audio_float = audio.astype(np.float32)
            else:
                audio_float = audio.astype(np.float32)
                # If audio is already in [0, 1] range, convert to [-1, 1]
                if audio_float.max() <= 1.0 and audio_float.min() >= 0.0:
                    audio_float = audio_float * 2.0 - 1.0
            
            # Ensure audio is in correct range and clip extreme values
            audio_float = np.clip(audio_float, -1.0, 1.0)
            
            # Apply slight normalization for better lip sync (helps with quiet audio)
            if np.abs(audio_float).max() > 0.01:
                audio_float = audio_float * (0.95 / np.abs(audio_float).max())
            
            logger.info(f"Audio shape before mel: {audio_float.shape}, sample_rate: {sample_rate}")
            
            # Generate mel spectrogram (Wav2Lip's melspectrogram takes only 1 argument)
            mel = wav2lip_audio.melspectrogram(audio_float)
            
            logger.info(f"Mel spectrogram shape: {mel.shape}")
            
            return mel
            
        except ImportError as e:
            logger.error(f"Wav2Lip audio module not found: {e}")
            import traceback
            traceback.print_exc()
            return np.zeros((80, 16))
        except Exception as e:
            logger.error(f"Audio preprocessing error: {e}")
            import traceback
            traceback.print_exc()
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
    
    def blend_face(self, original_face: np.ndarray, synced_face: np.ndarray) -> np.ndarray:
        """
        Blend the lip-synced face with original to reduce artifacts
        
        Args:
            original_face: Original face (BGR)
            synced_face: Lip-synced face (BGR)
            
        Returns:
            Blended face
        """
        # Ensure both faces have the same size
        if original_face.shape != synced_face.shape:
            original_face = cv2.resize(original_face, (synced_face.shape[1], synced_face.shape[0]))
        
        h, w = synced_face.shape[:2]
        
        # Use cached mask if size matches
        if self._cached_mask is not None and self._cached_mask_size == (h, w):
            mask = self._cached_mask
        else:
            # Create a mask for blending - focus on lower face (mouth region)
            mask = np.zeros((h, w), dtype=np.float32)
            
            # Create smooth circular/elliptical mask for mouth region
            center_y, center_x = int(h * 0.65), int(w * 0.5)
            radius_y, radius_x = int(h * 0.25), int(w * 0.35)
            
            y_grid, x_grid = np.ogrid[:h, :w]
            mask_region = ((x_grid - center_x) / radius_x) ** 2 + ((y_grid - center_y) / radius_y) ** 2 <= 1
            mask[mask_region] = 1.0
            
            # Apply Gaussian blur for smooth transition
            kernel_size = max(3, int(h * 0.2) | 1)  # Make odd, proportional to face size
            mask = cv2.GaussianBlur(mask, (kernel_size, kernel_size), kernel_size // 3)
            
            # Expand mask to 3 channels
            mask = np.expand_dims(mask, axis=2)
            
            # Cache it
            self._cached_mask = mask
            self._cached_mask_size = (h, w)
        
        # Blend: use synced face for mouth region, original for rest
        blended = (synced_face * mask + original_face * (1 - mask)).astype(np.uint8)
        
        return blended
    
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
            # mel has shape (80, T) where T is total time steps
            
            logger.info(f"Full mel shape: {mel.shape}")
            
            # Wav2Lip uses 80 temporal steps per second (16000 SR / 200 hop_size)
            # To get frames at self.fps, we use an index multiplier of 80.0 / self.fps
            mel_step_size = 16
            mel_idx_multiplier = 80.0 / self.fps
            
            # Calculate total video frames based on audio length
            num_frames = int((mel.shape[1] / 80.0) * self.fps)
            mel_chunks = []
            
            for i in range(num_frames):
                start_idx = int(i * mel_idx_multiplier)
                if start_idx + mel_step_size <= mel.shape[1]:
                    mel_chunks.append(mel[:, start_idx : start_idx + mel_step_size])
                else:
                    # Pad last chunk if needed
                    last_chunk = mel[:, start_idx : ]
                    if last_chunk.shape[1] < mel_step_size:
                        pad_width = mel_step_size - last_chunk.shape[1]
                        last_chunk = np.pad(last_chunk, ((0, 0), (0, pad_width)), mode='edge')
                    mel_chunks.append(last_chunk)
            
            if not mel_chunks:
                logger.warning("No mel chunks generated, returning original frame")
                return [face_frame]
            
            num_frames = len(mel_chunks)
            
            # Preprocess face frame
            face_tensor = self.preprocess_frame(face_frame)
            
            # Prepare face batches (repeat same frame for all mel chunks)
            # Convert to (H, W, C) for Wav2Lip's expected input
            face_np = face_frame.copy()
            
            # CRITICAL: Convert BGR to RGB before processing (fixes blue color issue)
            face_np = cv2.cvtColor(face_np, cv2.COLOR_BGR2RGB)
            
            # Resize to 96x96 (Wav2Lip's expected input size)
            face_np = cv2.resize(face_np, (96, 96))
            
            # Create masked version (mask lower half for better lip sync)
            face_masked = face_np.copy()
            face_masked[48:, :] = 0  # Mask lower half (mouth region)
            
            # Concatenate masked and original (6 channels: 3 for masked + 3 for original)
            face_combined = np.concatenate((face_masked, face_np), axis=2) / 255.0
            
            # Generate in batches
            generated_frames = []
            
            with torch.no_grad():
                for i in range(0, num_frames, self.batch_size):
                    batch_end = min(i + self.batch_size, num_frames)
                    batch_size_actual = batch_end - i
                    
                    # Prepare face batch
                    img_batch = np.repeat(face_combined[np.newaxis, :, :, :], batch_size_actual, axis=0)
                    img_batch = torch.FloatTensor(np.transpose(img_batch, (0, 3, 1, 2)))  # (B, C, H, W)
                    img_batch = img_batch.to(self.device)
                    
                    # Prepare mel batch
                    mel_batch = np.array(mel_chunks[i:batch_end])  # (B, 80, 16)
                    mel_batch = mel_batch.reshape(batch_size_actual, 80, 16, 1)  # (B, 80, 16, 1)
                    mel_batch = torch.FloatTensor(np.transpose(mel_batch, (0, 3, 1, 2)))  # (B, 1, 80, 16)
                    mel_batch = mel_batch.to(self.device)
                    
                    if self.use_fp16 and self.device == "cuda":
                        img_batch = img_batch.half()
                        mel_batch = mel_batch.half()
                    
                    # Generate
                    pred = self.model(mel_batch, img_batch)
                    
                    # Postprocess
                    pred = pred.cpu().float().numpy()
                    pred = pred.transpose(0, 2, 3, 1) * 255.0  # (B, H, W, C)
                    
                    # Clip to valid range to avoid artifacts
                    pred = np.clip(pred, 0, 255)
                    pred = pred.astype(np.uint8)
                    
                    # Resize back to 256x256 and convert RGB to BGR
                    for frame in pred:
                        # Use high-quality resizing for better lip sync quality
                        frame_resized = cv2.resize(frame, (self.face_size, self.face_size), 
                                                  interpolation=cv2.INTER_CUBIC)
                        frame_bgr = cv2.cvtColor(frame_resized, cv2.COLOR_RGB2BGR)
                        
                        # Blend with original face for smoother result (reduces artifacts)
                        blended_frame = self.blend_face(face_frame, frame_bgr)
                        generated_frames.append(blended_frame)
            
            return generated_frames
            
        except Exception as e:
            logger.error(f"Lip sync generation error: {e}")
            import traceback
            traceback.print_exc()
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
