"""
Streaming Speech-to-Text using Faster-Whisper
Optimized for low-latency real-time transcription
"""
import asyncio
import numpy as np
from faster_whisper import WhisperModel
from typing import Optional
import logging
import tempfile
import wave

logger = logging.getLogger(__name__)


class WhisperStream:
    """Streaming STT using Faster-Whisper"""
    
    def __init__(self,
                 model_size: str = "small.en",
                 model_path: Optional[str] = None,
                 device: str = "cuda",
                 compute_type: str = "float16",
                 beam_size: int = 1,
                 vad_filter: bool = True,
                 vad_threshold: float = 0.5,
                 sample_rate: int = 16000):
        """
        Initialize Whisper streaming
        
        Args:
            model_size: Model size (tiny.en, base.en, small.en, medium.en, large-v2)
            model_path: Path to local model directory
            device: Device (cuda, cpu)
            compute_type: Compute type (float16 for GPU, int8 for CPU)
            beam_size: Beam size for decoding (1 = greedy, 5 = beam search)
            vad_filter: Enable VAD filtering
            vad_threshold: VAD threshold (0.0-1.0)
            sample_rate: Audio sample rate
        """
        self.model_size = model_size
        self.model_path = model_path
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        self.vad_threshold = vad_threshold
        self.sample_rate = sample_rate
        
        self.model = None
        
    def load_model(self):
        """Load Faster-Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            
            # Load model
            if self.model_path:
                # Load from local path
                self.model = WhisperModel(
                    self.model_path,
                    device=self.device,
                    compute_type=self.compute_type
                )
            else:
                # Download if needed
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
            
            logger.info(f"Whisper model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe_audio(self, audio: np.ndarray) -> str:
        """
        Transcribe audio array
        
        Args:
            audio: Audio array (float32, normalized to -1 to 1)
            
        Returns:
            Transcribed text
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first")
        
        if len(audio) == 0:
            return ""
        
        try:
            # Normalize audio to float32 [-1, 1]
            if audio.dtype == np.int16:
                audio = audio.astype(np.float32) / 32768.0
            
            # Transcribe
            segments, info = self.model.transcribe(
                audio,
                beam_size=self.beam_size,
                vad_filter=self.vad_filter,
                vad_parameters={
                    "threshold": self.vad_threshold
                } if self.vad_filter else None,
                language="en"
            )
            
            # Collect segments
            text = " ".join([segment.text.strip() for segment in segments])
            
            logger.info(f"Transcribed: {text}")
            
            return text
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    async def transcribe_stream(self,
                               audio_queue: asyncio.Queue,
                               transcript_queue: asyncio.Queue):
        """
        Stream audio chunks and transcribe
        
        Args:
            audio_queue: Input queue with audio chunks
            transcript_queue: Output queue for transcribed text
        """
        logger.info("Started Whisper streaming")
        
        audio_buffer = []
        
        try:
            while True:
                # Get audio chunk
                chunk = await audio_queue.get()
                
                if chunk is None:
                    # End of speech signal
                    if audio_buffer:
                        # Transcribe accumulated audio
                        audio = np.concatenate(audio_buffer)
                        text = await asyncio.to_thread(
                            self.transcribe_audio,
                            audio
                        )
                        
                        if text:
                            await transcript_queue.put(text)
                        
                        # Clear buffer
                        audio_buffer.clear()
                    
                    # Forward None signal
                    await transcript_queue.put(None)
                    continue
                
                # Add to buffer
                audio_buffer.append(chunk)
                
        except asyncio.CancelledError:
            logger.info("Whisper streaming cancelled")
        except Exception as e:
            logger.error(f"Error in Whisper streaming: {e}")
    
    async def transcribe_continuous(self,
                                   audio_queue: asyncio.Queue,
                                   transcript_queue: asyncio.Queue):
        """
        Continuous transcription with chunking
        Transcribe every N seconds of audio
        
        Args:
            audio_queue: Input audio queue
            transcript_queue: Output transcript queue
        """
        logger.info("Started continuous Whisper transcription")
        
        audio_buffer = []
        chunk_duration = 3.0  # seconds
        chunk_samples = int(chunk_duration * self.sample_rate)
        
        try:
            while True:
                chunk = await audio_queue.get()
                
                if chunk is None:
                    # Process remaining buffer
                    if audio_buffer:
                        audio = np.concatenate(audio_buffer)
                        text = await asyncio.to_thread(
                            self.transcribe_audio,
                            audio
                        )
                        if text:
                            await transcript_queue.put(text)
                        audio_buffer.clear()
                    
                    await transcript_queue.put(None)
                    continue
                
                audio_buffer.append(chunk)
                
                # Check if buffer is full
                total_samples = sum(len(c) for c in audio_buffer)
                
                if total_samples >= chunk_samples:
                    # Transcribe current buffer
                    audio = np.concatenate(audio_buffer)
                    text = await asyncio.to_thread(
                        self.transcribe_audio,
                        audio
                    )
                    
                    if text:
                        await transcript_queue.put(text)
                    
                    audio_buffer.clear()
                    
        except asyncio.CancelledError:
            logger.info("Continuous transcription cancelled")
        except Exception as e:
            logger.error(f"Error in continuous transcription: {e}")
    
    def unload_model(self):
        """Unload model to free memory"""
        if self.model:
            del self.model
            self.model = None
            logger.info("Whisper model unloaded")
