"""
Streaming LLM using Groq API
Optimized for real-time token streaming with Groq's fast inference
"""
import asyncio
from groq import Groq
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class GroqStream:
    """Streaming LLM using Groq API"""
    
    def __init__(self,
                 api_key: str,
                 model: str = "llama-3.1-8b-instant",
                 temperature: float = 0.7,
                 top_p: float = 0.9,
                 max_tokens: int = 512,
                 system_prompt: Optional[str] = None):
        """
        Initialize Groq streaming
        
        Args:
            api_key: Groq API key
            model: Model name (llama-3.1-8b-instant, mixtral-8x7b-32768, etc.)
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold
            max_tokens: Maximum tokens to generate
            system_prompt: System prompt for the model
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        
        self.client = None
        self.conversation_history: List[Dict[str, str]] = []
        
    def load_model(self):
        """Initialize Groq client"""
        try:
            logger.info(f"Initializing Groq client with model: {self.model}")
            self.client = Groq(api_key=self.api_key)
            logger.info("Groq client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise
    
    def format_messages(self, user_message: str) -> List[Dict[str, str]]:
        """
        Format messages for Groq API
        
        Args:
            user_message: User's message
            
        Returns:
            List of message dictionaries
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history (keep last 10 exchanges)
        for msg in self.conversation_history[-20:]:
            messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def generate_response(self, user_message: str) -> str:
        """
        Generate complete response (non-streaming)
        
        Args:
            user_message: User's input
            
        Returns:
            Generated response
        """
        if self.client is None:
            raise RuntimeError("Client not initialized. Call load_model() first")
        
        messages = self.format_messages(user_message)
        
        try:
            # Generate
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stream=False
            )
            
            text = chat_completion.choices[0].message.content.strip()
            
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
        Stream response tokens asynchronously
        
        Args:
            user_message: User's input
            token_queue: Async queue to put tokens into
            stop_event: Optional event to signal stopping generation
        """
        if self.client is None:
            raise RuntimeError("Client not initialized. Call load_model() first")
        
        messages = self.format_messages(user_message)
        full_response = ""
        
        try:
            # Stream tokens
            stream = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stream=True
            )
            
            for chunk in stream:
                # Check if we should stop
                if stop_event and stop_event.is_set():
                    logger.info("Stopping generation (stop event set)")
                    break
                
                # Extract token
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    
                    # Put token in queue
                    await token_queue.put(token)
                    logger.debug(f"Token: {token}")
            
            # Signal end of response
            await token_queue.put(None)
            
            # Update history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
            logger.info(f"Streaming complete. Generated: {len(full_response)} chars")
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            await token_queue.put(None)  # Signal end even on error
            raise
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def set_system_prompt(self, prompt: str):
        """Update system prompt"""
        self.system_prompt = prompt
        logger.info("System prompt updated")
    
    async def process_transcripts(self,
                                 transcript_queue: asyncio.Queue,
                                 token_queue: asyncio.Queue):
        """
        Process transcripts and generate streaming responses
        
        Args:
            transcript_queue: Input queue with transcribed text
            token_queue: Output queue for tokens
        """
        logger.info("Started Groq transcript processing")
        
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
            logger.info("Groq processing cancelled")
        except Exception as e:
            logger.error(f"Error in Groq processing: {e}")
    
    def unload_model(self):
        """Cleanup (no model to unload for API)"""
        logger.info("Groq client cleanup (no model to unload)")


# Test function
async def test_groq_stream():
    """Test Groq streaming"""
    import os
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Set GROQ_API_KEY environment variable")
        return
    
    # Initialize
    groq = GroqStream(
        api_key=api_key,
        model="llama-3.1-8b-instant",
        system_prompt="You are a helpful assistant. Be concise."
    )
    groq.load_model()
    
    # Test streaming
    token_queue = asyncio.Queue()
    
    async def print_tokens():
        """Print tokens as they arrive"""
        while True:
            token = await token_queue.get()
            if token is None:
                break
            print(token, end="", flush=True)
        print()
    
    # Start printing task
    print_task = asyncio.create_task(print_tokens())
    
    # Stream response
    await groq.stream_response("Tell me a short joke", token_queue)
    
    # Wait for printing to complete
    await print_task


if __name__ == "__main__":
    asyncio.run(test_groq_stream())
