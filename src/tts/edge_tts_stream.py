"""
Streaming Text-to-Speech using Edge-TTS
Converts text tokens to audio chunks with minimal latency
"""
import asyncio
import edge_tts
import numpy as np
import logging
from typing import Optional
import io
import wave

logger = logging.getLogger(__name__)


class EdgeTTSStream:
    """Streaming TTS using Edge-TTS"""
    
    def __init__(self,
                 voice: str = "en-US-AriaNeural",
                 rate: str = "+0%",
                 pitch: str = "+0Hz",
                 chunk_duration: float = 0.5,
                 token_buffer_size: int = 15):
        """
        Initialize Edge-TTS streaming
        
        Args:
            voice: Voice name (e.g., en-US-AriaNeural, en-US-JennyNeural)
            rate: Speech rate (-50% to +100%)
            pitch: Pitch adjustment
            chunk_duration: Target duration for audio chunks (seconds)
            token_buffer_size: Buffer N tokens before starting TTS
        """
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.chunk_duration = chunk_duration
        self.token_buffer_size = token_buffer_size
        
        logger.info(f"Initialized Edge-TTS: voice={voice}, rate={rate}")
    
    async def text_to_audio(self, text: str) -> bytes:
        """
        Convert text to audio using Edge-TTS
        
        Args:
            text: Input text
            
        Returns:
            Audio bytes (MP3 format)
        """
        try:
            communicate = edge_tts.Communicate(
                text,
                voice=self.voice,
                rate=self.rate,
                pitch=self.pitch
            )
            
            # Collect audio chunks
            audio_chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])
            
            # Concatenate all chunks
            audio_bytes = b"".join(audio_chunks)
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return b""
    
    async def tokens_to_audio_chunks(self,
                                    token_queue: asyncio.Queue,
                                    audio_queue: asyncio.Queue):
        """
        Convert streaming tokens to audio chunks
        
        Args:
            token_queue: Input queue with text tokens
            audio_queue: Output queue for audio chunks
        """
        logger.info("Started TTS token processing")
        
        token_buffer = []
        word_buffer = []
        
        try:
            while True:
                # Get token
                token = await token_queue.get()
                
                if token is None:
                    # End of generation - process remaining buffer
                    if word_buffer:
                        text = "".join(word_buffer).strip()
                        if text:
                            audio = await self.text_to_audio(text)
                            if audio:
                                await audio_queue.put(audio)
                        word_buffer.clear()
                    
                    # Signal end
                    await audio_queue.put(None)
                    token_buffer.clear()
                    continue
                
                token_buffer.append(token)
                word_buffer.append(token)
                
                # Check if we have enough tokens to start TTS
                if len(token_buffer) < self.token_buffer_size:
                    continue
                
                # Check for sentence boundaries or sufficient text
                text_so_far = "".join(word_buffer)
                
                # Generate audio when we have:
                # 1. Enough tokens buffered
                # 2. A sentence boundary (., !, ?)
                # 3. Or enough text for a chunk
                
                should_generate = False
                split_point = len(word_buffer)
                
                # Check for sentence boundaries
                for i, tok in enumerate(word_buffer):
                    if any(punc in tok for punc in ['. ', '! ', '? ', '.\n', '!\n', '?\n']):
                        should_generate = True
                        split_point = i + 1
                        break
                
                # Or if buffer is large enough
                if len(token_buffer) >= 30 and not should_generate:
                    should_generate = True
                    # Find last space for clean split
                    for i in range(len(word_buffer) - 1, 0, -1):
                        if ' ' in word_buffer[i]:
                            split_point = i + 1
                            break
                
                if should_generate:
                    # Extract text to convert
                    text_to_convert = "".join(word_buffer[:split_point]).strip()
                    
                    if text_to_convert:
                        logger.info(f"Generating TTS: {text_to_convert[:50]}...")
                        
                        # Generate audio
                        audio = await self.text_to_audio(text_to_convert)
                        
                        if audio:
                            await audio_queue.put(audio)
                    
                    # Keep remaining tokens
                    word_buffer = word_buffer[split_point:]
                    token_buffer.clear()
                    
        except asyncio.CancelledError:
            logger.info("TTS processing cancelled")
        except Exception as e:
            logger.error(f"Error in TTS processing: {e}")
            await audio_queue.put(None)
    
    async def convert_audio_format(self, audio_bytes: bytes, target_sr: int = 16000) -> np.ndarray:
        """
        Convert Edge-TTS audio (MP3) to numpy array
        
        Args:
            audio_bytes: MP3 audio bytes
            target_sr: Target sample rate
            
        Returns:
            Audio as numpy array (int16)
        """
        try:
            # Save to temp file and decode with ffmpeg/pydub
            from pydub import AudioSegment
            
            # Load MP3
            audio_segment = AudioSegment.from_file(
                io.BytesIO(audio_bytes),
                format="mp3"
            )
            
            # Convert to target sample rate
            audio_segment = audio_segment.set_frame_rate(target_sr)
            
            # Convert to mono
            audio_segment = audio_segment.set_channels(1)
            
            # Convert to numpy array
            samples = np.array(audio_segment.get_array_of_samples())
            
            # Convert to int16
            if audio_segment.sample_width == 2:
                samples = samples.astype(np.int16)
            elif audio_segment.sample_width == 4:
                samples = (samples / 65536).astype(np.int16)
            
            return samples
            
        except ImportError:
            logger.error("pydub not installed. Install: pip install pydub")
            return np.array([], dtype=np.int16)
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return np.array([], dtype=np.int16)
    
    @staticmethod
    async def get_available_voices():
        """Get list of available Edge-TTS voices"""
        try:
            voices = await edge_tts.list_voices()
            
            # Filter English voices
            en_voices = [v for v in voices if v["Locale"].startswith("en-")]
            
            logger.info(f"Found {len(en_voices)} English voices")
            
            return en_voices
            
        except Exception as e:
            logger.error(f"Failed to get voices: {e}")
            return []
