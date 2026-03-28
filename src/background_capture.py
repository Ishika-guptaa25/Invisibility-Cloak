"""
BackgroundCapture Module
Handles capturing and processing the background for the invisibility cloak effect.
"""

import cv2
import numpy as np
from collections import deque
import threading
import time
from config.settings import (
    BACKGROUND_CAPTURE_FRAMES,
    BACKGROUND_BLUR_KERNEL,
    BACKGROUND_CAPTURE_WAIT_TIME,
    USE_THREADING
)


class BackgroundCapture:
    """
    Captures and processes background frames for the invisibility cloak.

    This module:
    - Captures multiple frames from the video feed
    - Averages them to reduce noise
    - Stores the processed background for later use
    - Handles threading for non-blocking capture
    """

    def __init__(self, num_frames=BACKGROUND_CAPTURE_FRAMES):
        """
        Initialize the background capture system.

        Args:
            num_frames (int): Number of frames to capture and average
        """
        self.num_frames = num_frames
        self.frames = deque(maxlen=num_frames)
        self.background = None
        self.is_capturing = False
        self.capture_complete = False
        self.capture_thread = None

    def capture_frames(self, video_capture, num_frames_to_capture=None):
        """
        Capture frames from the video feed.

        Args:
            video_capture: OpenCV VideoCapture object
            num_frames_to_capture (int): Override number of frames to capture

        Returns:
            bool: True if capture was successful, False otherwise
        """
        if num_frames_to_capture is None:
            num_frames_to_capture = self.num_frames

        self.frames.clear()
        self.is_capturing = True
        frames_captured = 0

        print(f"[BackgroundCapture] Capturing {num_frames_to_capture} background frames...")
        print(f"[BackgroundCapture] Waiting {BACKGROUND_CAPTURE_WAIT_TIME} seconds...")
        time.sleep(BACKGROUND_CAPTURE_WAIT_TIME)

        while frames_captured < num_frames_to_capture:
            ret, frame = video_capture.read()

            if not ret:
                print("[BackgroundCapture] Error: Could not read frame from video capture")
                self.is_capturing = False
                return False

            self.frames.append(frame)
            frames_captured += 1

            # Display progress
            if frames_captured % 10 == 0 or frames_captured == num_frames_to_capture:
                print(f"[BackgroundCapture] Captured {frames_captured}/{num_frames_to_capture} frames")

        self.is_capturing = False
        self.process_background()
        return True

    def process_background(self):
        """
        Average the captured frames and apply smoothing.

        This method:
        1. Converts all frames to float32 for precise averaging
        2. Computes the mean across all captured frames
        3. Applies Gaussian blur to reduce noise
        4. Converts back to uint8
        """
        if len(self.frames) == 0:
            print("[BackgroundCapture] Error: No frames captured")
            return False

        print(f"[BackgroundCapture] Processing {len(self.frames)} frames...")

        # Convert frames to float for averaging
        frames_float = np.array([frame.astype(np.float32) for frame in self.frames])

        # Compute average across all frames
        self.background = np.mean(frames_float, axis=0).astype(np.uint8)

        # Apply Gaussian blur to smooth the background
        self.background = cv2.GaussianBlur(
            self.background,
            BACKGROUND_BLUR_KERNEL,
            0
        )

        self.capture_complete = True
        print("[BackgroundCapture] Background processing complete")
        return True

    def capture_frames_threaded(self, video_capture):
        """
        Capture frames in a separate thread (non-blocking).

        Args:
            video_capture: OpenCV VideoCapture object

        Returns:
            threading.Thread: The thread object (already started)
        """
        self.capture_thread = threading.Thread(
            target=self.capture_frames,
            args=(video_capture,),
            daemon=True
        )
        self.capture_thread.start()
        return self.capture_thread

    def get_background(self):
        """
        Get the processed background image.

        Returns:
            np.ndarray: The background image, or None if not yet processed
        """
        return self.background

    def is_ready(self):
        """
        Check if background capture is complete and ready for use.

        Returns:
            bool: True if background is ready, False otherwise
        """
        return self.capture_complete and self.background is not None

    def reset(self):
        """Reset the background capture state."""
        self.frames.clear()
        self.background = None
        self.capture_complete = False
        self.is_capturing = False

    def get_capture_progress(self):
        """
        Get the current capture progress.

        Returns:
            tuple: (frames_captured, total_frames)
        """
        return (len(self.frames), self.num_frames)