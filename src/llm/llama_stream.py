"""
Streaming LLM using llama-cpp-python
Optimized for real-time token streaming with GPU acceleration
"""
import asyncio
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

# Conditional import - only import if needed
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    logger.warning("llama-cpp-python not installed. Install it to use local LLM: pip install llama-cpp-python")


class LlamaStream:
    """Streaming LLM using llama.cpp"""
    
    def __init__(self,
                 model_path: str,
                 n_gpu_layers: int = -1,
                 n_ctx: int = 4096,
                 n_batch: int = 512,
                 n_threads: int = 8,
                 temperature: float = 0.7,
                 top_p: float = 0.9,
                 top_k: int = 40,
                 max_tokens: int = 512,
                 system_prompt: Optional[str] = None,
                 use_flash_attention: bool = True):
        """
        Initialize Llama streaming
        
        Args:
            model_path: Path to GGUF model file
            n_gpu_layers: Number of layers to offload to GPU (-1 = all)
            n_ctx: Context window size
            n_batch: Batch size for prompt processing
            n_threads: Number of CPU threads
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling
            max_tokens: Maximum tokens to generate
            system_prompt: System prompt for the model
            use_flash_attention: Use flash attention (if supported)
        """
        self.model_path = model_path
        self.n_gpu_layers = n_gpu_layers
        self.n_ctx = n_ctx
        self.n_batch = n_batch
        self.n_threads = n_threads
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.use_flash_attention = use_flash_attention
        
        self.model = None
        self.conversation_history: List[Dict[str, str]] = []
        
    def load_model(self):
        """Load Llama model"""
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError(
                "llama-cpp-python is not installed. "
                "Install it with: pip install llama-cpp-python "
                "Or use Groq API instead by setting LLM_BACKEND='groq' in config.py"
            )
        
        try:
            logger.info(f"Loading Llama model from: {self.model_path}")
            
            # Load model with llama.cpp
            self.model = Llama(
                model_path=str(self.model_path),
                n_gpu_layers=self.n_gpu_layers,
                n_ctx=self.n_ctx,
                n_batch=self.n_batch,
                n_threads=self.n_threads,
                verbose=False,
                # Flash attention is automatically used if available in llama.cpp
            )
            
            logger.info(f"Llama model loaded: {self.n_gpu_layers} GPU layers")
            
        except Exception as e:
            logger.error(f"Failed to load Llama model: {e}")
            raise
    
    def format_prompt(self, user_message: str) -> str:
        """
        Format prompt with conversation history
        
        Args:
            user_message: User's message
            
        Returns:
            Formatted prompt string
        """
        # Llama 3.1 Instruct format
        prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{self.system_prompt}<|eot_id|>"
        
        # Add conversation history
        for msg in self.conversation_history[-10:]:  # Keep last 10 messages
            role = msg["role"]
            content = msg["content"]
            prompt += f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>"
        
        # Add current user message
        prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{user_message}<|eot_id|>"
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
        
        return prompt
    
    def generate_response(self, user_message: str) -> str:
        """
        Generate complete response (non-streaming)
        
        Args:
            user_message: User's input
            
        Returns:
            Generated response
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first")
        
        prompt = self.format_prompt(user_message)
        
        try:
            # Generate
            response = self.model(
                prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                stop=["<|eot_id|>", "<|end_of_text|>"],
                echo=False
            )
            
            text = response["choices"][0]["text"].strip()
            
            # Update history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": text})
            
            logger.info(f"Generated: {text[:100]}...")
            
            return text
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return "I apologize, but I encountered an error generating a response."
    
    async def stream_response(self,
                             user_message: str,
                             token_queue: asyncio.Queue,
                             stop_event: Optional[asyncio.Event] = None):
        """
        Stream response tokens
        
        Args:
            user_message: User's input
            token_queue: Queue to put tokens
            stop_event: Event to stop generation early
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first")
        
        prompt = self.format_prompt(user_message)
        
        try:
            logger.info(f"Generating response for: {user_message[:50]}...")
            
            # Stream generation
            full_response = ""
            
            stream = await asyncio.to_thread(
                self.model,
                prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                stop=["<|eot_id|>", "<|end_of_text|>"],
                stream=True,
                echo=False
            )
            
            for output in stream:
                # Check stop event
                if stop_event and stop_event.is_set():
                    logger.info("Generation stopped by event")
                    break
                
                # Extract token
                token = output["choices"][0]["text"]
                full_response += token
                
                # Put token in queue
                await token_queue.put(token)
            
            # Signal end of generation
            await token_queue.put(None)
            
            # Update history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
            logger.info(f"Generation complete: {len(full_response)} chars")
            
        except asyncio.CancelledError:
            logger.info("Token streaming cancelled")
            await token_queue.put(None)
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            await token_queue.put(None)
    
    async def process_transcripts(self,
                                 transcript_queue: asyncio.Queue,
                                 token_queue: asyncio.Queue):
        """
        Process transcripts and generate streaming responses
        
        Args:
            transcript_queue: Input queue with transcribed text
            token_queue: Output queue for tokens
        """
        logger.info("Started LLM transcript processing")
        
        try:
            while True:
                # Get transcript
                transcript = await transcript_queue.get()
                
                if transcript is None:
                    # End signal - wait for next transcript
                    continue
                
                if not transcript.strip():
                    continue
                
                logger.info(f"Processing transcript: {transcript}")
                
                # Generate streaming response
                await self.stream_response(transcript, token_queue)
                
        except asyncio.CancelledError:
            logger.info("LLM processing cancelled")
        except Exception as e:
            logger.error(f"Error in LLM processing: {e}")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def unload_model(self):
        """Unload model to free memory"""
        if self.model:
            del self.model
            self.model = None
            logger.info("Llama model unloaded")
