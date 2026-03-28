"""
Utility Functions
Helper functions for color conversion, HSV range adjustments, and other utilities.
"""

import cv2
import numpy as np


class ColorUtils:
    """Utilities for color space conversion and manipulation."""

    @staticmethod
    def bgr_to_hsv(bgr_color):
        """
        Convert BGR color to HSV.

        Args:
            bgr_color (tuple): BGR color (B, G, R)

        Returns:
            tuple: HSV color (H, S, V)
        """
        bgr_array = np.uint8([[[bgr_color[0], bgr_color[1], bgr_color[2]]]])
        hsv_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2HSV)
        return tuple(hsv_array[0][0])

    @staticmethod
    def hsv_to_bgr(hsv_color):
        """
        Convert HSV color to BGR.

        Args:
            hsv_color (tuple): HSV color (H, S, V)

        Returns:
            tuple: BGR color (B, G, R)
        """
        hsv_array = np.uint8([[[hsv_color[0], hsv_color[1], hsv_color[2]]]])
        bgr_array = cv2.cvtColor(hsv_array, cv2.COLOR_HSV2BGR)
        return tuple(bgr_array[0][0])

    @staticmethod
    def create_hsv_range(center_h, s_range=(100, 255), v_range=(100, 255), h_tolerance=10):
        """
        Create HSV range from center hue.

        Args:
            center_h (int): Center hue value (0-180 in OpenCV)
            s_range (tuple): Saturation range (min, max)
            v_range (tuple): Value range (min, max)
            h_tolerance (int): Hue tolerance (range will be ±h_tolerance)

        Returns:
            tuple: (lower, upper) HSV bounds
        """
        lower = (max(0, center_h - h_tolerance), s_range[0], v_range[0])
        upper = (min(180, center_h + h_tolerance), s_range[1], v_range[1])
        return lower, upper


class ImageUtils:
    """Utilities for image processing."""

    @staticmethod
    def resize_frame(frame, width=None, height=None, inter=cv2.INTER_AREA):
        """
        Resize frame while maintaining aspect ratio.

        Args:
            frame (np.ndarray): Input frame
            width (int): Target width (None to maintain aspect ratio)
            height (int): Target height (None to maintain aspect ratio)
            inter: Interpolation method

        Returns:
            np.ndarray: Resized frame
        """
        (h, w) = frame.shape[:2]

        if width is None and height is None:
            return frame

        if width is None:
            ratio = height / float(h)
            width = int(w * ratio)

        if height is None:
            ratio = width / float(w)
            height = int(h * ratio)

        return cv2.resize(frame, (width, height), interpolation=inter)

    @staticmethod
    def create_gradient_mask(mask, gradient_size=20):
        """
        Create a gradient mask for smooth transitions.

        Args:
            mask (np.ndarray): Input binary mask
            gradient_size (int): Size of gradient transition

        Returns:
            np.ndarray: Gradient mask (0-255)
        """
        # Dilate the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (gradient_size, gradient_size))
        dilated = cv2.dilate(mask, kernel, iterations=1)

        # Apply Gaussian blur for smooth gradient
        gradient = cv2.GaussianBlur(dilated, (gradient_size, gradient_size), 0)

        return gradient

    @staticmethod
    def apply_clahe(frame, clip_limit=2.0, grid_size=(8, 8)):
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).

        Args:
            frame (np.ndarray): Input BGR frame
            clip_limit (float): Contrast limiting threshold
            grid_size (tuple): Size of grid cells

        Returns:
            np.ndarray: Enhanced frame
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]

        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
        l_enhanced = clahe.apply(l_channel)

        # Merge channels
        lab[:, :, 0] = l_enhanced

        # Convert back to BGR
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    @staticmethod
    def draw_hsv_histogram(frame, mask=None):
        """
        Draw HSV histogram of the frame.

        Args:
            frame (np.ndarray): Input BGR frame
            mask (np.ndarray): Optional mask to restrict histogram to masked region

        Returns:
            np.ndarray: Histogram visualization
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Calculate histogram
        hist = cv2.calcHist([hsv], [0], mask, [180], [0, 180])

        # Draw histogram
        hist_img = np.ones((256, 180)) * 255
        cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)

        for i in range(len(hist) - 1):
            cv2.line(hist_img, (i, int(256 - hist[i])),
                     (i + 1, int(256 - hist[i + 1])), (0, 0, 0), 2)

        return hist_img


class PerformanceUtils:
    """Utilities for performance monitoring."""

    @staticmethod
    def calculate_fps(frame_times, window_size=30):
        """
        Calculate FPS from frame times.

        Args:
            frame_times (list): List of frame timestamps
            window_size (int): Number of frames to average

        Returns:
            float: Calculated FPS
        """
        if len(frame_times) < 2:
            return 0.0

        recent_times = frame_times[-window_size:]
        if len(recent_times) > 1:
            avg_time = np.mean(np.diff(recent_times))
            return 1.0 / avg_time if avg_time > 0 else 0.0

        return 0.0

    @staticmethod
    def measure_time(func):
        """
        Decorator to measure function execution time.

        Args:
            func: Function to measure

        Returns:
            Wrapper function
        """
        import time

        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"[{func.__name__}] Execution time: {(end - start) * 1000:.2f}ms")
            return result

        return wrapper


class FileUtils:
    """Utilities for file operations."""

    @staticmethod
    def save_background(background, filepath):
        """
        Save captured background to file.

        Args:
            background (np.ndarray): Background image
            filepath (str): Output file path

        Returns:
            bool: True if saved successfully
        """
        try:
            cv2.imwrite(filepath, background)
            print(f"[FileUtils] Background saved to {filepath}")
            return True
        except Exception as e:
            print(f"[FileUtils] Error saving background: {e}")
            return False

    @staticmethod
    def load_background(filepath):
        """
        Load background from file.

        Args:
            filepath (str): Input file path

        Returns:
            np.ndarray: Background image, or None if load failed
        """
        try:
            background = cv2.imread(filepath)
            if background is None:
                print(f"[FileUtils] Error: Could not load image from {filepath}")
                return None
            print(f"[FileUtils] Background loaded from {filepath}")
            return background
        except Exception as e:
            print(f"[FileUtils] Error loading background: {e}")
            return None

    @staticmethod
    def save_frame(frame, filepath):
        """
        Save a single frame to file.

        Args:
            frame (np.ndarray): Frame to save
            filepath (str): Output file path

        Returns:
            bool: True if saved successfully
        """
        try:
            cv2.imwrite(filepath, frame)
            print(f"[FileUtils] Frame saved to {filepath}")
            return True
        except Exception as e:
            print(f"[FileUtils] Error saving frame: {e}")
            return False