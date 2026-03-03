"""
Microphone Stream - Async audio capture with VAD
"""
import asyncio
import pyaudio
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MicrophoneStream:
    """Async microphone stream with Voice Activity Detection"""
    
    def __init__(self,
                 sample_rate: int = 16000,
                 chunk_size: int = 1024,
                 channels: int = 1,
                 silence_threshold: int = 500,
                 silence_duration: float = 1.0):
        """
        Initialize microphone stream
        
        Args:
            sample_rate: Audio sample rate (Hz)
            chunk_size: Audio chunk size (samples)
            channels: Number of audio channels
            silence_threshold: RMS threshold for silence detection
            silence_duration: Seconds of silence to trigger end of speech
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        
        self.audio = None
        self.stream = None
        self.is_recording = False
        
        # Silence detection
        self.silence_chunks = 0
        self.silence_chunk_threshold = int(
            (sample_rate / chunk_size) * silence_duration
        )
        
    def start(self):
        """Start audio stream"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Find default input device
            device_info = self.audio.get_default_input_device_info()
            logger.info(f"Using audio device: {device_info['name']}")
            
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=None
            )
            
            self.is_recording = True
            logger.info(f"Microphone stream started: {self.sample_rate}Hz, chunk={self.chunk_size}")
            
        except Exception as e:
            logger.error(f"Failed to start microphone: {e}")
            raise
    
    def stop(self):
        """Stop audio stream"""
        self.is_recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        logger.info("Microphone stream stopped")
    
    async def read_chunk(self) -> Optional[np.ndarray]:
        """
        Read single audio chunk asynchronously
        
        Returns:
            Audio chunk as numpy array or None if stream closed
        """
        if not self.is_recording or self.stream is None:
            return None
        
        try:
            # Read from stream (blocking)
            data = await asyncio.to_thread(
                self.stream.read,
                self.chunk_size,
                exception_on_overflow=False
            )
            
            # Convert to numpy array
            audio_chunk = np.frombuffer(data, dtype=np.int16)
            
            return audio_chunk
            
        except Exception as e:
            logger.error(f"Error reading audio chunk: {e}")
            return None
    
    async def stream_audio(self, audio_queue: asyncio.Queue):
        """
        Stream audio chunks to queue with VAD
        
        Args:
            audio_queue: Queue to push audio chunks
        """
        logger.info("Started audio streaming with VAD")
        
        speech_started = False
        audio_buffer = []
        
        try:
            while self.is_recording:
                chunk = await self.read_chunk()
                
                if chunk is None:
                    break
                
                # Calculate RMS for VAD
                rms = np.sqrt(np.mean(chunk.astype(np.float32) ** 2))
                
                # Voice Activity Detection
                if rms > self.silence_threshold:
                    # Speech detected
                    if not speech_started:
                        logger.info("Speech started")
                        speech_started = True
                    
                    self.silence_chunks = 0
                    audio_buffer.append(chunk)
                    
                    # Push to queue
                    await audio_queue.put(chunk)
                    
                else:
                    # Silence detected
                    if speech_started:
                        self.silence_chunks += 1
                        audio_buffer.append(chunk)
                        await audio_queue.put(chunk)
                        
                        # Check if speech ended
                        if self.silence_chunks >= self.silence_chunk_threshold:
                            logger.info(f"Speech ended ({self.silence_duration}s silence)")
                            
                            # Signal end of speech
                            await audio_queue.put(None)
                            
                            # Reset
                            speech_started = False
                            self.silence_chunks = 0
                            audio_buffer.clear()
                
        except asyncio.CancelledError:
            logger.info("Audio streaming cancelled")
        except Exception as e:
            logger.error(f"Error in audio streaming: {e}")
        finally:
            # Signal end
            await audio_queue.put(None)
    
    async def record_until_silence(self) -> np.ndarray:
        """
        Record audio until silence detected
        
        Returns:
            Complete audio recording as numpy array
        """
        audio_buffer = []
        speech_started = False
        silence_chunks = 0
        
        logger.info("Listening...")
        
        while self.is_recording:
            chunk = await self.read_chunk()
            
            if chunk is None:
                break
            
            # Calculate RMS
            rms = np.sqrt(np.mean(chunk.astype(np.float32) ** 2))
            
            if rms > self.silence_threshold:
                if not speech_started:
                    logger.info("Speech detected")
                    speech_started = True
                
                silence_chunks = 0
                audio_buffer.append(chunk)
            else:
                if speech_started:
                    silence_chunks += 1
                    audio_buffer.append(chunk)
                    
                    if silence_chunks >= self.silence_chunk_threshold:
                        logger.info("Recording complete")
                        break
        
        # Concatenate all chunks
        if audio_buffer:
            return np.concatenate(audio_buffer)
        else:
            return np.array([], dtype=np.int16)
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
    
    def __del__(self):
        """Cleanup"""
        self.stop()
