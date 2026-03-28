#!/usr/bin/env python3
"""
Advanced Examples
Demonstrating custom configurations and HSV color tuning.

Examples:
    python examples_advanced.py --example hsv_tuner
    python examples_advanced.py --example custom_config
    python examples_advanced.py --example performance_test
"""

import cv2
import numpy as np
import sys
from src.main import InvisibilityCloakProcessor
from src.color_detection import ColorDetector
from config.settings import COLOR_PRESETS
from utils.utilities import ColorUtils


class HSVTuner:
    """Interactive HSV color range tuner."""

    def __init__(self):
        """Initialize the HSV tuner."""
        self.frame = None
        self.h_min = 0
        self.h_max = 10
        self.s_min = 100
        self.s_max = 255
        self.v_min = 100
        self.v_max = 255

    def on_trackbar_h_min(self, value):
        """Trackbar callback for hue min."""
        self.h_min = value

    def on_trackbar_h_max(self, value):
        """Trackbar callback for hue max."""
        self.h_max = value

    def on_trackbar_s_min(self, value):
        """Trackbar callback for saturation min."""
        self.s_min = value

    def on_trackbar_s_max(self, value):
        """Trackbar callback for saturation max."""
        self.s_max = value

    def on_trackbar_v_min(self, value):
        """Trackbar callback for value min."""
        self.v_min = value

    def on_trackbar_v_max(self, value):
        """Trackbar callback for value max."""
        self.v_max = value

    def run(self):
        """Run the HSV tuner."""
        print("HSV Tuner - Adjust sliders to find your cloak color")
        print("Press 'q' to quit")

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            print("Error: Could not open camera")
            return

        # Create window and trackbars
        cv2.namedWindow('HSV Tuner')

        cv2.createTrackbar('H min', 'HSV Tuner', self.h_min, 180, self.on_trackbar_h_min)
        cv2.createTrackbar('H max', 'HSV Tuner', self.h_max, 180, self.on_trackbar_h_max)
        cv2.createTrackbar('S min', 'HSV Tuner', self.s_min, 255, self.on_trackbar_s_min)
        cv2.createTrackbar('S max', 'HSV Tuner', self.s_max, 255, self.on_trackbar_s_max)
        cv2.createTrackbar('V min', 'HSV Tuner', self.v_min, 255, self.on_trackbar_v_min)
        cv2.createTrackbar('V max', 'HSV Tuner', self.v_max, 255, self.on_trackbar_v_max)

        try:
            while True:
                ret, frame = camera.read()
                if not ret:
                    break

                # Convert to HSV
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                # Create mask with current values
                lower = np.array([self.h_min, self.s_min, self.v_min])
                upper = np.array([self.h_max, self.s_max, self.v_max])
                mask = cv2.inRange(hsv, lower, upper)

                # Apply morphological operations
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                mask = cv2.erode(mask, kernel, iterations=2)
                mask = cv2.dilate(mask, kernel, iterations=3)

                # Create result showing original and mask
                result = np.hstack([frame, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)])

                # Add text info
                cv2.putText(result, f'H: {self.h_min}-{self.h_max}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(result, f'S: {self.s_min}-{self.s_max}', (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(result, f'V: {self.v_min}-{self.v_max}', (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Show pixel count
                pixel_count = cv2.countNonZero(mask)
                cv2.putText(result, f'Pixels: {pixel_count}', (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                cv2.imshow('HSV Tuner', result)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Print the found values
            print("\nFound HSV Range:")
            print(f"Lower: ({self.h_min}, {self.s_min}, {self.v_min})")
            print(f"Upper: ({self.h_max}, {self.s_max}, {self.v_max})")
            print("\nAdd to config/settings.py:")
            print(f"CLOAK_COLOR_LOWER = ({self.h_min}, {self.s_min}, {self.v_min})")
            print(f"CLOAK_COLOR_UPPER = ({self.h_max}, {self.s_max}, {self.v_max})")

        finally:
            camera.release()
            cv2.destroyAllWindows()


class CustomConfigExample:
    """Example with custom configuration."""

    @staticmethod
    def run():
        """Run with custom configuration."""
        print("Custom Configuration Example")

        # Create processor with custom settings
        processor = InvisibilityCloakProcessor(
            cloak_color='red',
            blend_method='gaussian'
        )

        # Customize detector
        print("Setting custom HSV range...")
        processor.color_detector.set_color_range(
            color_lower=(0, 80, 80),
            color_upper=(15, 255, 255)
        )

        # Customize blender
        print("Setting Gaussian blur kernel...")
        processor.blender.feather_kernel = (25, 25)

        print("Running with custom configuration...")
        processor.run()


class PerformanceTest:
    """Performance benchmarking."""

    @staticmethod
    def benchmark_color_detection():
        """Benchmark color detection."""
        print("Benchmarking Color Detection...")

        detector = ColorDetector()

        # Create test frames
        test_frames = [
            np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
            for _ in range(100)
        ]

        import time
        start = time.time()

        for frame in test_frames:
            detector.detect(frame)

        end = time.time()
        total_time = end - start
        fps = len(test_frames) / total_time

        print(f"Total time: {total_time:.2f}s")
        print(f"Average per frame: {(total_time / len(test_frames)) * 1000:.2f}ms")
        print(f"FPS: {fps:.2f}")

    @staticmethod
    def benchmark_blending():
        """Benchmark blending algorithms."""
        print("\nBenchmarking Blending Methods...")

        from src.blending import BackgroundBlender

        # Create test data
        frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        background = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
        mask = np.zeros((720, 1280), dtype=np.uint8)
        mask[200:520, 400:880] = 255

        methods = ['simple', 'gaussian', 'alpha']

        import time

        for method in methods:
            blender = BackgroundBlender(blend_method=method)

            start = time.time()
            for _ in range(100):
                blender.blend(frame, background, mask)
            end = time.time()

            total_time = end - start
            avg_time = (total_time / 100) * 1000

            print(f"\n{method.upper()}:")
            print(f"  100 frames: {total_time:.2f}s")
            print(f"  Per frame: {avg_time:.2f}ms")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        example = sys.argv[1]

        if example == '--example':
            if len(sys.argv) > 2:
                example_type = sys.argv[2]

                if example_type == 'hsv_tuner':
                    tuner = HSVTuner()
                    tuner.run()

                elif example_type == 'custom_config':
                    CustomConfigExample.run()

                elif example_type == 'performance_test':
                    PerformanceTest.benchmark_color_detection()
                    PerformanceTest.benchmark_blending()

                else:
                    print(f"Unknown example: {example_type}")
                    print("Available: hsv_tuner, custom_config, performance_test")
            else:
                print("Available examples:")
                print("  python examples_advanced.py --example hsv_tuner")
                print("  python examples_advanced.py --example custom_config")
                print("  python examples_advanced.py --example performance_test")
        else:
            print("Usage: python examples_advanced.py --example [hsv_tuner|custom_config|performance_test]")
    else:
        print("Usage: python examples_advanced.py --example [example_name]")
        print("\nAvailable examples:")
        print("  hsv_tuner      - Interactive HSV color range tuner")
        print("  custom_config  - Custom configuration example")
        print("  performance_test - Performance benchmarking")


if __name__ == '__main__':
    main()