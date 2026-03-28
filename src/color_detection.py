"""
ColorDetection Module
Handles color-based segmentation for detecting the invisibility cloak.
"""

import cv2
import numpy as np
from config.settings import (
    CLOAK_COLOR_LOWER,
    CLOAK_COLOR_UPPER,
    COLOR_PRESETS,
    MORPH_KERNEL_SIZE,
    EROSION_ITERATIONS,
    DILATION_ITERATIONS
)


class ColorDetector:
    """
    Detects and segments pixels matching a specific color range.

    This module:
    - Converts BGR frames to HSV color space
    - Creates masks based on color range
    - Applies morphological operations for noise reduction
    - Handles HSV color range boundaries
    """

    def __init__(self, color_lower=CLOAK_COLOR_LOWER, color_upper=CLOAK_COLOR_UPPER):
        """
        Initialize the color detector.

        Args:
            color_lower (tuple): Lower HSV bound (H, S, V)
            color_upper (tuple): Upper HSV bound (H, S, V)
        """
        self.color_lower = np.array(color_lower, dtype=np.uint8)
        self.color_upper = np.array(color_upper, dtype=np.uint8)
        self.morph_kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            MORPH_KERNEL_SIZE
        )
        self.detected_pixels = 0

    def detect(self, frame):
        """
        Detect pixels matching the configured color range.

        Args:
            frame (np.ndarray): Input frame in BGR format

        Returns:
            np.ndarray: Binary mask where detected color = 255, others = 0
        """
        # Convert BGR to HSV color space
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create mask for the color range
        mask = cv2.inRange(hsv_frame, self.color_lower, self.color_upper)

        return mask

    def detect_with_wraparound(self, frame, color_lower_alt=None, color_upper_alt=None):
        """
        Detect color with HSV wraparound support (for colors like red that wrap).

        Args:
            frame (np.ndarray): Input frame in BGR format
            color_lower_alt (tuple): Alternative lower HSV bound for wraparound
            color_upper_alt (tuple): Alternative upper HSV bound for wraparound

        Returns:
            np.ndarray: Binary mask combining both color ranges
        """
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Primary color range
        mask1 = cv2.inRange(hsv_frame, self.color_lower, self.color_upper)

        # Alternative color range (for wraparound)
        if color_lower_alt is not None and color_upper_alt is not None:
            color_lower_alt = np.array(color_lower_alt, dtype=np.uint8)
            color_upper_alt = np.array(color_upper_alt, dtype=np.uint8)
            mask2 = cv2.inRange(hsv_frame, color_lower_alt, color_upper_alt)
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            mask = mask1

        return mask

    def apply_morphological_operations(self, mask):
        """
        Apply morphological operations to clean up the mask.

        Operations performed:
        1. Erosion: Removes small noise
        2. Dilation: Restores object size and fills small holes

        Args:
            mask (np.ndarray): Input binary mask

        Returns:
            np.ndarray: Cleaned binary mask
        """
        # Erosion: remove small noise
        eroded = cv2.erode(mask, self.morph_kernel, iterations=EROSION_ITERATIONS)

        # Dilation: restore size and fill holes
        dilated = cv2.dilate(eroded, self.morph_kernel, iterations=DILATION_ITERATIONS)

        return dilated

    def get_contours(self, mask):
        """
        Extract contours from the binary mask.

        Args:
            mask (np.ndarray): Input binary mask

        Returns:
            list: List of contours detected in the mask
        """
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        return contours

    def get_largest_contour(self, mask):
        """
        Get the largest contour from the mask.

        Args:
            mask (np.ndarray): Input binary mask

        Returns:
            tuple: (contour, area) or (None, 0) if no contour found
        """
        contours = self.get_contours(mask)

        if len(contours) == 0:
            return None, 0

        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        return largest_contour, area

    def set_color_range(self, color_lower, color_upper):
        """
        Update the color range for detection.

        Args:
            color_lower (tuple): Lower HSV bound (H, S, V)
            color_upper (tuple): Upper HSV bound (H, S, V)
        """
        self.color_lower = np.array(color_lower, dtype=np.uint8)
        self.color_upper = np.array(color_upper, dtype=np.uint8)
        print(f"[ColorDetector] Updated color range: {color_lower} - {color_upper}")

    def set_color_preset(self, preset_name):
        """
        Set color range from a preset.

        Args:
            preset_name (str): Name of the color preset ('red', 'blue', 'green', 'yellow')

        Returns:
            bool: True if preset found, False otherwise
        """
        if preset_name not in COLOR_PRESETS:
            print(f"[ColorDetector] Preset '{preset_name}' not found")
            return False

        preset = COLOR_PRESETS[preset_name]
        self.set_color_range(preset['lower'], preset['upper'])
        return True

    def get_detected_pixel_count(self, mask):
        """
        Count the number of detected pixels in the mask.

        Args:
            mask (np.ndarray): Binary mask

        Returns:
            int: Number of white pixels (detected pixels)
        """
        self.detected_pixels = cv2.countNonZero(mask)
        return self.detected_pixels