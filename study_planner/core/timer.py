"""Timer Engine for countdown timing with callbacks."""

import threading
import time
from typing import Callable, Optional


class TimerEngine:
    """Provides precise countdown timing with callbacks.
    
    Uses time.monotonic() for accuracy and runs in a separate thread
    to keep the UI responsive.
    """
    
    def __init__(self, duration_seconds: int, on_tick: Callable[[int], None], 
                 on_finish: Callable[[], None]):
        """Initialize timer with duration and callbacks.
        
        Args:
            duration_seconds: Total countdown duration in seconds
            on_tick: Callback called every second with remaining seconds
            on_finish: Callback called when countdown reaches zero
        """
        self._duration = duration_seconds
        self._on_tick = on_tick
        self._on_finish = on_finish
        
        self._remaining_seconds = duration_seconds
        self._is_running = False
        self._is_paused = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        
    def start(self) -> None:
        """Start countdown in separate thread."""
        with self._lock:
            if self._is_running:
                return
            
            self._is_running = True
            self._is_paused = False
            self._stop_event.clear()
            self._pause_event.clear()
            
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def pause(self) -> None:
        """Pause countdown and preserve remaining time."""
        with self._lock:
            if not self._is_running or self._is_paused:
                return
            
            self._is_paused = True
            self._pause_event.set()
    
    def resume(self) -> None:
        """Resume countdown from paused state."""
        with self._lock:
            if not self._is_running or not self._is_paused:
                return
            
            self._is_paused = False
            self._pause_event.clear()
    
    def stop(self) -> None:
        """Stop countdown and cleanup."""
        with self._lock:
            if not self._is_running:
                return
            
            self._is_running = False
            self._is_paused = False
            self._stop_event.set()
            self._pause_event.clear()
        
        # Wait for thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
    
    def get_remaining_seconds(self) -> int:
        """Get current remaining time.
        
        Returns:
            Remaining seconds in countdown
        """
        with self._lock:
            return self._remaining_seconds
    
    def is_running(self) -> bool:
        """Check if timer is actively counting.
        
        Returns:
            True if timer is running (not paused or stopped)
        """
        with self._lock:
            return self._is_running and not self._is_paused
    
    def _run(self) -> None:
        """Internal countdown loop running in separate thread."""
        start_time = time.monotonic()
        elapsed = 0.0
        
        while True:
            # Check if stopped
            if self._stop_event.is_set():
                break
            
            # Check if paused
            if self._pause_event.is_set():
                # Wait while paused
                while self._pause_event.is_set() and not self._stop_event.is_set():
                    time.sleep(0.1)
                
                # Adjust start time to account for pause duration
                start_time = time.monotonic() - elapsed
                
                if self._stop_event.is_set():
                    break
            
            # Calculate elapsed time
            current_time = time.monotonic()
            elapsed = current_time - start_time
            
            # Calculate remaining seconds
            remaining = max(0, self._duration - int(elapsed))
            
            with self._lock:
                self._remaining_seconds = remaining
            
            # Call tick callback
            try:
                self._on_tick(remaining)
            except Exception as e:
                # Log error but continue timer operation
                print(f"Error in on_tick callback: {e}")
            
            # Check if finished
            if remaining == 0:
                with self._lock:
                    self._is_running = False
                
                # Call finish callback
                try:
                    self._on_finish()
                except Exception as e:
                    # Log error but don't crash
                    print(f"Error in on_finish callback: {e}")
                
                break
            
            # Sleep until next second
            next_tick = start_time + int(elapsed) + 1
            sleep_time = next_tick - time.monotonic()
            if sleep_time > 0:
                time.sleep(sleep_time)
