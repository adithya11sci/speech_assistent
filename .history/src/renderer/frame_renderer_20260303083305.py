"""
Frame Renderer - Display lip-synced frames in real-time
Optimized for consistent FPS and low latency
"""
import asyncio
import cv2
import numpy as np
from typing import Optional
import time
import logging

logger = logging.getLogger(__name__)


class FrameRenderer:
    """Real-time frame renderer with FPS control"""
    
    def __init__(self,
                 window_name: str = "AI Avatar",
                 target_fps: int = 25,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 fullscreen: bool = False,
                 show_fps: bool = True,
                 save_output: bool = False,
                 output_path: Optional[str] = None):
        """
        Initialize frame renderer
        
        Args:
            window_name: OpenCV window name
            target_fps: Target FPS for rendering
            width: Display width (None = auto)
            height: Display height (None = auto)
            fullscreen: Display in fullscreen mode
            show_fps: Show FPS counter on frames
            save_output: Save output to video file
            output_path: Path to save output video
        """
        self.window_name = window_name
        self.target_fps = target_fps
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        self.show_fps = show_fps
        self.save_output = save_output
        self.output_path = output_path
        
        self.frame_time = 1.0 / target_fps
        self.is_running = False
        self.video_writer = None
        
        # FPS tracking
        self.fps_counter = []
        self.last_frame_time = time.time()
        
    def start(self):
        """Initialize renderer window"""
        try:
            # Create window
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            
            if self.fullscreen:
                cv2.setWindowProperty(
                    self.window_name,
                    cv2.WND_PROP_FULLSCREEN,
                    cv2.WINDOW_FULLSCREEN
                )
            elif self.width and self.height:
                cv2.resizeWindow(self.window_name, self.width, self.height)
            
            self.is_running = True
            logger.info(f"Renderer started: {self.target_fps} FPS")
            
        except Exception as e:
            logger.error(f"Failed to start renderer: {e}")
            raise
    
    def stop(self):
        """Stop renderer and cleanup"""
        self.is_running = False
        
        if self.video_writer:
            self.video_writer.release()
        
        cv2.destroyAllWindows()
        logger.info("Renderer stopped")
    
    def render_frame(self, frame: np.ndarray):
        """
        Render single frame
        
        Args:
            frame: Frame to display (BGR)
        """
        if not self.is_running:
            return
        
        # Calculate FPS
        current_time = time.time()
        fps = 1.0 / (current_time - self.last_frame_time) if self.last_frame_time else 0
        self.last_frame_time = current_time
        
        self.fps_counter.append(fps)
        if len(self.fps_counter) > 30:
            self.fps_counter.pop(0)
        
        avg_fps = np.mean(self.fps_counter) if self.fps_counter else 0
        
        # Add FPS overlay
        if self.show_fps:
            frame = frame.copy()
            cv2.putText(
                frame,
                f"FPS: {avg_fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
        
        # Display frame
        cv2.imshow(self.window_name, frame)
        
        # Save to video if enabled
        if self.save_output and self.video_writer:
            self.video_writer.write(frame)
        
        # Handle key press (1ms wait for responsiveness)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC
            logger.info("Quit key pressed")
            self.is_running = False
    
    async def render_stream(self, frame_queue: asyncio.Queue):
        """
        Render frames from queue with FPS control
        
        Args:
            frame_queue: Queue containing frames to render
        """
        logger.info("Started frame rendering stream")
        
        try:
            while self.is_running:
                try:
                    # Get frame with timeout
                    frame = await asyncio.wait_for(
                        frame_queue.get(),
                        timeout=1.0
                    )
                    
                    if frame is None:
                        # End signal or placeholder
                        continue
                    
                    # Initialize video writer on first frame
                    if self.save_output and self.video_writer is None:
                        self._init_video_writer(frame)
                    
                    # Render frame
                    await asyncio.to_thread(self.render_frame, frame)
                    
                    # FPS control - wait if processing too fast
                    elapsed = time.time() - self.last_frame_time
                    if elapsed < self.frame_time:
                        await asyncio.sleep(self.frame_time - elapsed)
                    
                except asyncio.TimeoutError:
                    # No frame available, continue
                    continue
                
        except asyncio.CancelledError:
            logger.info("Frame rendering cancelled")
        except Exception as e:
            logger.error(f"Error in frame rendering: {e}")
        finally:
            self.stop()
    
    def _init_video_writer(self, frame: np.ndarray):
        """Initialize video writer"""
        if self.output_path:
            try:
                h, w = frame.shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(
                    self.output_path,
                    fourcc,
                    self.target_fps,
                    (w, h)
                )
                logger.info(f"Saving output to: {self.output_path}")
            except Exception as e:
                logger.error(f"Failed to initialize video writer: {e}")
                self.save_output = False
    
    def display_idle_frame(self, frame: np.ndarray, text: str = "Listening..."):
        """
        Display idle frame with status text
        
        Args:
            frame: Frame to display
            text: Status text to overlay
        """
        frame = frame.copy()
        
        # Add status text
        font_scale = 1.5
        thickness = 3
        color = (0, 255, 255)  # Yellow
        
        # Calculate text size for centering
        (text_width, text_height), baseline = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            thickness
        )
        
        # Position at top center
        x = (frame.shape[1] - text_width) // 2
        y = 50
        
        # Add background rectangle
        cv2.rectangle(
            frame,
            (x - 10, y - text_height - 10),
            (x + text_width + 10, y + 10),
            (0, 0, 0),
            -1
        )
        
        # Add text
        cv2.putText(
            frame,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness
        )
        
        self.render_frame(frame)
    
    async def show_status_message(self, frame: np.ndarray, message: str, duration: float = 2.0):
        """
        Show status message for specified duration
        
        Args:
            frame: Base frame
            message: Message to display
            duration: Display duration (seconds)
        """
        start_time = time.time()
        
        while time.time() - start_time < duration:
            self.display_idle_frame(frame, message)
            await asyncio.sleep(0.033)  # ~30 FPS
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
