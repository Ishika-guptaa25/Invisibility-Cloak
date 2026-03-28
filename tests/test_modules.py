"""
Test Suite
Unit tests and integration tests for the invisibility cloak system.
"""

import cv2
import numpy as np
import unittest
from src.background_capture import BackgroundCapture
from src.color_detection import ColorDetector
from src.blending import BackgroundBlender


class TestColorDetector(unittest.TestCase):
    """Test cases for ColorDetector."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = ColorDetector()

    def test_color_detection_basic(self):
        """Test basic color detection."""
        # Create a test frame with red region
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[25:75, 25:75] = (0, 0, 255)  # Red in BGR

        mask = self.detector.detect(frame)

        # Check that red region is detected
        self.assertGreater(cv2.countNonZero(mask), 0)

    def test_morphological_operations(self):
        """Test morphological operations."""
        # Create mask with noise
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[25:75, 25:75] = 255

        # Add noise
        mask[40:45, 40:45] = 0

        cleaned = self.detector.apply_morphological_operations(mask)

        # Check that noise is removed
        self.assertLessEqual(
            cv2.countNonZero(cv2.bitwise_xor(mask, cleaned)),
            cv2.countNonZero(mask)
        )

    def test_color_range_setting(self):
        """Test setting color range."""
        self.detector.set_color_range((100, 100, 100), (130, 255, 255))

        self.assertTrue(np.array_equal(
            self.detector.color_lower,
            np.array([100, 100, 100], dtype=np.uint8)
        ))

    def test_color_preset(self):
        """Test color preset loading."""
        result = self.detector.set_color_preset('blue')
        self.assertTrue(result)


class TestBackgroundBlender(unittest.TestCase):
    """Test cases for BackgroundBlender."""

    def setUp(self):
        """Set up test fixtures."""
        self.blender = BackgroundBlender(blend_method='gaussian')
        self.frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        self.background = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        self.mask = np.zeros((100, 100), dtype=np.uint8)
        self.mask[25:75, 25:75] = 255

    def test_simple_blending(self):
        """Test simple blending method."""
        result = self.blender.blend_simple(self.frame, self.background, self.mask)

        self.assertEqual(result.shape, self.frame.shape)
        self.assertEqual(result.dtype, np.uint8)

    def test_gaussian_blending(self):
        """Test Gaussian blending method."""
        result = self.blender.blend_gaussian(self.frame, self.background, self.mask)

        self.assertEqual(result.shape, self.frame.shape)
        self.assertEqual(result.dtype, np.uint8)

    def test_alpha_blending(self):
        """Test alpha blending method."""
        result = self.blender.blend_alpha(self.frame, self.background, self.mask)

        self.assertEqual(result.shape, self.frame.shape)
        self.assertEqual(result.dtype, np.uint8)

    def test_blend_method_switching(self):
        """Test switching blend methods."""
        methods = ['simple', 'gaussian', 'alpha']

        for method in methods:
            self.blender.set_blend_method(method)
            result = self.blender.blend(self.frame, self.background, self.mask)
            self.assertEqual(result.shape, self.frame.shape)

    def test_feathered_mask(self):
        """Test feathered mask creation."""
        feathered = self.blender.create_feathered_mask(self.mask)

        self.assertEqual(feathered.shape, self.mask.shape)
        # Feathered mask should have gradient values
        self.assertGreater(np.max(feathered), 0)
        self.assertLess(np.max(feathered), 255)


class TestBackgroundCapture(unittest.TestCase):
    """Test cases for BackgroundCapture."""

    def setUp(self):
        """Set up test fixtures."""
        self.capture = BackgroundCapture(num_frames=5)

    def test_initialization(self):
        """Test BackgroundCapture initialization."""
        self.assertEqual(self.capture.num_frames, 5)
        self.assertIsNone(self.capture.background)
        self.assertFalse(self.capture.capture_complete)

    def test_frame_storage(self):
        """Test frame storage in deque."""
        # Create dummy frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 128

        self.capture.frames.append(frame1)
        self.capture.frames.append(frame2)

        self.assertEqual(len(self.capture.frames), 2)

    def test_background_processing(self):
        """Test background processing."""
        # Create dummy frames
        frames = [np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
                  for _ in range(5)]

        for frame in frames:
            self.capture.frames.append(frame)

        result = self.capture.process_background()

        self.assertTrue(result)
        self.assertIsNotNone(self.capture.background)
        self.assertEqual(self.capture.background.shape, (100, 100, 3))

    def test_reset(self):
        """Test reset functionality."""
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        self.capture.frames.append(frame)

        self.capture.reset()

        self.assertEqual(len(self.capture.frames), 0)
        self.assertIsNone(self.capture.background)
        self.assertFalse(self.capture.capture_complete)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestColorDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestBackgroundBlender))
    suite.addTests(loader.loadTestsFromTestCase(TestBackgroundCapture))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)