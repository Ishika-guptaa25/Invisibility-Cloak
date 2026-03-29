"""
Blending Module - FIXED VERSION
Handles blending the background image with the cloak region.
"""

import cv2
import numpy as np
from config.settings import (
    BLEND_METHOD,
    GAUSSIAN_BLUR_KERNEL,
    GAUSSIAN_BLUR_SIGMA
)


class BackgroundBlender:
    """
    Blends the background image with the detected cloak region.

    This module:
    - Applies the background to masked regions
    - Creates smooth transitions using various blending techniques
    - Handles edge smoothing and feathering
    """

    def __init__(self, blend_method=BLEND_METHOD):
        """
        Initialize the background blender.

        Args:
            blend_method (str): Blending method ('simple', 'gaussian', 'alpha')
        """
        self.blend_method = blend_method
        self.feather_kernel = GAUSSIAN_BLUR_KERNEL

    def blend_simple(self, frame, background, mask):
        """
        Simple blending: directly replace masked regions with background.

        Args:
            frame (np.ndarray): Input frame
            background (np.ndarray): Background image
            mask (np.ndarray): Binary mask (255 where cloak is detected)

        Returns:
            np.ndarray: Blended result
        """
        # mask has 255 where cloak is detected
        # We want to REPLACE cloak area with background

        # Convert mask to 3 channels
        mask_3channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        mask_inv_3channel = cv2.cvtColor(cv2.bitwise_not(mask), cv2.COLOR_GRAY2BGR)

        # Blend: keep original frame where mask is 0, use background where mask is 255
        result = cv2.bitwise_and(frame, mask_inv_3channel) + \
                 cv2.bitwise_and(background, mask_3channel)

        return result

    def blend_gaussian(self, frame, background, mask):
        """
        Gaussian blending: uses Gaussian blur on mask for smooth transitions.

        Args:
            frame (np.ndarray): Input frame
            background (np.ndarray): Background image
            mask (np.ndarray): Binary mask (255 where cloak is detected)

        Returns:
            np.ndarray: Blended result
        """
        # Create smooth mask using Gaussian blur
        smooth_mask = cv2.GaussianBlur(mask, self.feather_kernel, GAUSSIAN_BLUR_SIGMA)

        # Normalize to 0-1 range
        smooth_mask_normalized = smooth_mask.astype(np.float32) / 255.0

        # Convert to 3 channels
        smooth_mask_3channel = np.dstack([smooth_mask_normalized] * 3)

        # Blend using the smooth mask
        # Where mask=255 (cloak), use more background
        # Where mask=0 (non-cloak), use more frame
        frame_float = frame.astype(np.float32)
        background_float = background.astype(np.float32)

        result = (background_float * smooth_mask_3channel +
                  frame_float * (1 - smooth_mask_3channel)).astype(np.uint8)

        return result

    def blend_alpha(self, frame, background, mask, alpha=0.5):
        """
        Alpha blending: blends frame and background with adjustable opacity.

        Args:
            frame (np.ndarray): Input frame
            background (np.ndarray): Background image
            mask (np.ndarray): Binary mask (255 where cloak is detected)
            alpha (float): Blending ratio (0-1)

        Returns:
            np.ndarray: Blended result
        """
        # Simple alpha blending where mask is detected
        result = frame.copy()

        # Get mask indices
        mask_indices = mask > 0

        # Blend in masked regions using addWeighted
        if np.any(mask_indices):
            blended_region = cv2.addWeighted(
                frame[mask_indices].astype(np.float32), 1 - alpha,
                background[mask_indices].astype(np.float32), alpha, 0
            ).astype(np.uint8)
            result[mask_indices] = blended_region

        return result

    def blend_pyramid(self, frame, background, mask):
        """
        Laplacian pyramid blending: advanced blending for smooth transitions.

        Args:
            frame (np.ndarray): Input frame
            background (np.ndarray): Background image
            mask (np.ndarray): Binary mask (255 where cloak is detected)

        Returns:
            np.ndarray: Blended result
        """
        # Create smooth mask using Gaussian blur
        smooth_mask = cv2.GaussianBlur(mask, (25, 25), 0)

        # Normalize to 0-1 range
        mask_normalized = smooth_mask.astype(np.float32) / 255.0
        mask_3channel = np.dstack([mask_normalized] * 3)

        # Blend with weighted mask
        frame_float = frame.astype(np.float32)
        background_float = background.astype(np.float32)

        result = (background_float * mask_3channel +
                  frame_float * (1 - mask_3channel)).astype(np.uint8)

        return result

    def blend(self, frame, background, mask):
        """
        Apply the selected blending method.

        Args:
            frame (np.ndarray): Input frame
            background (np.ndarray): Background image
            mask (np.ndarray): Binary mask (255 where cloak is detected)

        Returns:
            np.ndarray: Blended result
        """
        if background is None:
            return frame

        # Ensure background is same size as frame
        if background.shape != frame.shape:
            background = cv2.resize(background, (frame.shape[1], frame.shape[0]))

        if self.blend_method == 'simple':
            return self.blend_simple(frame, background, mask)
        elif self.blend_method == 'gaussian':
            return self.blend_gaussian(frame, background, mask)
        elif self.blend_method == 'alpha':
            return self.blend_alpha(frame, background, mask)
        elif self.blend_method == 'pyramid':
            return self.blend_pyramid(frame, background, mask)
        else:
            print(f"[BackgroundBlender] Unknown blend method: {self.blend_method}")
            return self.blend_gaussian(frame, background, mask)

    def set_blend_method(self, method):
        """
        Set the blending method.

        Args:
            method (str): Blending method ('simple', 'gaussian', 'alpha', 'pyramid')
        """
        if method in ['simple', 'gaussian', 'alpha', 'pyramid']:
            self.blend_method = method
            print(f"[BackgroundBlender] Blend method set to: {method}")
        else:
            print(f"[BackgroundBlender] Unknown blend method: {method}")

    def create_feathered_mask(self, mask, feather_size=15):
        """
        Create a feathered mask for smoother transitions.

        Args:
            mask (np.ndarray): Input binary mask
            feather_size (int): Size of feathering

        Returns:
            np.ndarray: Feathered mask (0-255)
        """
        # Apply Gaussian blur to create feathered edges
        feathered = cv2.GaussianBlur(mask, (feather_size * 2 + 1, feather_size * 2 + 1), 0)

        return feathered