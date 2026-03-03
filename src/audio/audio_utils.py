"""
Audio Processing Utilities
"""
import numpy as np
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Utility functions for audio processing"""
    
    @staticmethod
    def normalize_audio(audio: np.ndarray, target_level: float = 0.5) -> np.ndarray:
        """
        Normalize audio to target level
        
        Args:
            audio: Input audio array
            target_level: Target RMS level (0.0 to 1.0)
            
        Returns:
            Normalized audio
        """
        if len(audio) == 0:
            return audio
        
        # Calculate current RMS
        rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
        
        if rms > 0:
            # Normalize
            scaling_factor = target_level / rms
            normalized = audio.astype(np.float32) * scaling_factor
            
            # Clip to prevent overflow
            normalized = np.clip(normalized, -32768, 32767)
            
            return normalized.astype(np.int16)
        
        return audio
    
    @staticmethod
    def calculate_rms(audio: np.ndarray) -> float:
        """Calculate RMS (Root Mean Square) of audio"""
        if len(audio) == 0:
            return 0.0
        return float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
    
    @staticmethod
    def is_silence(audio: np.ndarray, threshold: float = 500.0) -> bool:
        """Check if audio chunk is silence"""
        rms = AudioProcessor.calculate_rms(audio)
        return rms < threshold
    
    @staticmethod
    def resample_audio(audio: np.ndarray, 
                      orig_sr: int, 
                      target_sr: int) -> np.ndarray:
        """
        Resample audio to different sample rate
        
        Args:
            audio: Input audio
            orig_sr: Original sample rate
            target_sr: Target sample rate
            
        Returns:
            Resampled audio
        """
        if orig_sr == target_sr:
            return audio
        
        try:
            import scipy.signal
            
            # Calculate resampling ratio
            num_samples = int(len(audio) * target_sr / orig_sr)
            
            # Resample
            resampled = scipy.signal.resample(audio, num_samples)
            
            return resampled.astype(np.int16)
            
        except ImportError:
            logger.warning("scipy not available, using simple resampling")
            # Simple linear interpolation
            indices = np.linspace(0, len(audio) - 1, 
                                int(len(audio) * target_sr / orig_sr))
            resampled = np.interp(indices, np.arange(len(audio)), audio)
            return resampled.astype(np.int16)
    
    @staticmethod
    def convert_to_wav(audio: np.ndarray, 
                      sample_rate: int = 16000) -> bytes:
        """
        Convert numpy audio to WAV bytes
        
        Args:
            audio: Audio array (int16)
            sample_rate: Sample rate
            
        Returns:
            WAV file bytes
        """
        import io
        import wave
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio.tobytes())
        
        return wav_buffer.getvalue()
    
    @staticmethod
    def chunk_audio(audio: np.ndarray, 
                   chunk_duration: float,
                   sample_rate: int,
                   overlap: float = 0.0) -> list:
        """
        Split audio into chunks with optional overlap
        
        Args:
            audio: Input audio
            chunk_duration: Duration of each chunk (seconds)
            sample_rate: Audio sample rate
            overlap: Overlap duration (seconds)
            
        Returns:
            List of audio chunks
        """
        chunk_samples = int(chunk_duration * sample_rate)
        overlap_samples = int(overlap * sample_rate)
        stride = chunk_samples - overlap_samples
        
        chunks = []
        start = 0
        
        while start < len(audio):
            end = min(start + chunk_samples, len(audio))
            chunk = audio[start:end]
            
            # Pad last chunk if needed
            if len(chunk) < chunk_samples:
                chunk = np.pad(chunk, (0, chunk_samples - len(chunk)))
            
            chunks.append(chunk)
            start += stride
        
        return chunks
    
    @staticmethod
    def apply_fade(audio: np.ndarray, 
                  fade_in_ms: int = 50,
                  fade_out_ms: int = 50,
                  sample_rate: int = 16000) -> np.ndarray:
        """
        Apply fade in/out to audio to reduce clicks
        
        Args:
            audio: Input audio
            fade_in_ms: Fade in duration (milliseconds)
            fade_out_ms: Fade out duration (milliseconds)
            sample_rate: Audio sample rate
            
        Returns:
            Audio with fade applied
        """
        audio_float = audio.astype(np.float32)
        
        # Fade in
        fade_in_samples = int(fade_in_ms * sample_rate / 1000)
        if fade_in_samples > 0 and len(audio) > fade_in_samples:
            fade_in_curve = np.linspace(0, 1, fade_in_samples)
            audio_float[:fade_in_samples] *= fade_in_curve
        
        # Fade out
        fade_out_samples = int(fade_out_ms * sample_rate / 1000)
        if fade_out_samples > 0 and len(audio) > fade_out_samples:
            fade_out_curve = np.linspace(1, 0, fade_out_samples)
            audio_float[-fade_out_samples:] *= fade_out_curve
        
        return audio_float.astype(np.int16)
