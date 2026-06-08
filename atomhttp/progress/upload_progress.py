"""
Progress Tracker Module
-----------------------
Provides progress tracking functionality for upload and download operations.

This module contains the ProgressTracker class which monitors data transfer
progress and notifies callbacks as data is transmitted. It is used by the
HTTP adapter to provide real-time progress updates for large uploads and
downloads.
"""

from typing import Callable, Optional


class ProgressTracker:
    """
    Track upload and download progress for HTTP operations.
    
    This class maintains progress state for data transfer operations and
    invokes a callback function whenever progress is updated. It is designed
    to work with both upload and download scenarios, tracking bytes transferred
    against the total expected size (when known).
    
    The progress callback receives two arguments:
        - loaded (int): Number of bytes transferred so far
        - total (int): Total bytes expected (0 if unknown)
    
    Attributes:
        callback (Optional[Callable]): Function called on each progress update.
                                      Signature: callback(loaded: int, total: int)
        total (int): Total bytes expected to transfer (0 if unknown)
        loaded (int): Number of bytes transferred so far
    """
    
    def __init__(self, callback: Optional[Callable] = None):
        """
        Initialize a new progress tracker.
        
        Args:
            callback (Optional[Callable]): Function to call on progress updates.
                                         Receives (loaded, total) arguments.
                                         If None, progress is tracked but no
                                         notifications are sent.
        """
        self.callback = callback
        self.total = 0
        self.loaded = 0
    
    def update(self, loaded: int, total: Optional[int] = None) -> None:
        """
        Update the current progress and notify callback if present.
        
        This method updates the amount of data transferred and optionally
        sets the total expected size. After updating internal state, it
        invokes the callback function (if provided) with the current
        progress values.
        
        Args:
            loaded (int): Current number of bytes transferred
            total (Optional[int]): Total bytes expected to transfer.
                                  If provided, updates self.total.
                                  If None, self.total remains unchanged.
        
        Example:
            >>> tracker = ProgressTracker(lambda l, t: print(f"{l}/{t}"))
            >>> tracker.update(0, 100)   # Start: 0/100 bytes
            >>> tracker.update(50)        # Halfway: 50/100 bytes
            >>> tracker.update(100)       # Complete: 100/100 bytes
        """
        self.loaded = loaded
        if total is not None:
            self.total = total
        
        if self.callback:
            self.callback(self.loaded, self.total)
    
    def reset(self) -> None:
        """
        Reset the progress tracker to initial state.
        
        This method resets both loaded and total counters to zero.
        Useful when reusing the same tracker for multiple operations.
        
        Note:
            This does not call the callback function. The callback will
            be called on the next update() call with the reset values.
        """
        self.loaded = 0
        self.total = 0