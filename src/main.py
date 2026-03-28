"""
InvisibilityCloakProcessor
Main processor that orchestrates all modules for the invisibility cloak effect.
"""

import cv2
import numpy as np
import time
from src.background_capture import BackgroundCapture
from src.color_detection import ColorDetector
from src.blending import BackgroundBlender
from config.settings import (
    FRAME_WIDTH,
    FRAME_HEIGHT,
    FPS,
    DISPLAY_FPS,
    DISPLAY_INFO,
    WINDOW_NAME,
    INFO_COLOR,
    INFO_FONT,
    INFO_FONT_SCALE,
    INFO_THICKNESS,
    DEBUG_MODE,
    SHOW_MASK,
    SHOW_BACKGROUND,
    RESIZE_FOR_PROCESSING,
    PROCESSING_WIDTH,
    PROCESSING_HEIGHT,
    COLOR_PRESETS
)


class InvisibilityCloakProcessor:
    """
    Main processor for the invisibility cloak effect.

    Workflow:
    1. Capture background frames
    2. For each video frame:
       a. Detect cloak color
       b. Apply morphological operations
       c. Blend background with detected region
       d. Display result
    """

    def __init__(self, cloak_color='red', blend_method='gaussian'):
        """
        Initialize the invisibility cloak processor.

        Args:
            cloak_color (str): Color of the cloak ('red', 'blue', 'green', 'yellow')
            blend_method (str): Blending method ('simple', 'gaussian', 'alpha')
        """
        print("[InvisibilityCloakProcessor] Initializing...")

        # Initialize components
        self.background_capture = BackgroundCapture()
        self.color_detector = ColorDetector()
        self.blender = BackgroundBlender(blend_method=blend_method)

        # Set cloak color
        if cloak_color in COLOR_PRESETS:
            preset = COLOR_PRESETS[cloak_color]
            self.color_detector.set_color_range(preset['lower'], preset['upper'])
            self.cloak_color = cloak_color
            self.cloak_color_lower_alt = preset.get('lower_alt')
            self.cloak_color_upper_alt = preset.get('upper_alt')
        else:
            print(f"[InvisibilityCloakProcessor] Color '{cloak_color}' not found, using red")
            self.cloak_color = 'red'
            self.cloak_color_lower_alt = None
            self.cloak_color_upper_alt = None

        # State tracking
        self.background_ready = False
        self.is_running = False
        self.frame_count = 0
        self.fps_counter = 0
        self.start_time = time.time()
        self.frame_times = []

        # Camera
        self.camera = None
        self.frame = None
        self.frame_resized = None

        print(f"[InvisibilityCloakProcessor] Cloak color: {cloak_color}")
        print(f"[InvisibilityCloakProcessor] Blend method: {blend_method}")

    def initialize_camera(self, camera_index=0, width=FRAME_WIDTH, height=FRAME_HEIGHT, fps=FPS):
        """
        Initialize and configure the camera.

        Args:
            camera_index (int): Index of the camera device
            width (int): Frame width
            height (int): Frame height
            fps (int): Frames per second

        Returns:
            bool: True if camera initialized successfully, False otherwise
        """
        print(f"[InvisibilityCloakProcessor] Initializing camera {camera_index}...")

        self.camera = cv2.VideoCapture(camera_index)

        if not self.camera.isOpened():
            print("[InvisibilityCloakProcessor] Error: Could not open camera")
            return False

        # Set camera properties
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.camera.set(cv2.CAP_PROP_FPS, fps)

        # Reduce camera latency
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        print(f"[InvisibilityCloakProcessor] Camera initialized: {width}x{height} @ {fps} FPS")
        return True

    def capture_background(self):
        """
        Capture background frames.

        Returns:
            bool: True if background captured successfully
        """
        print("[InvisibilityCloakProcessor] Starting background capture...")
        return self.background_capture.capture_frames(self.camera)

    def process_frame(self, frame):
        """
        Process a single frame with the invisibility cloak effect.

        Args:
            frame (np.ndarray): Input frame in BGR format

        Returns:
            np.ndarray: Processed frame with invisibility cloak effect
        """
        # Resize for processing if needed
        if RESIZE_FOR_PROCESSING:
            frame_proc = cv2.resize(frame, (PROCESSING_WIDTH, PROCESSING_HEIGHT))
        else:
            frame_proc = frame

        # Detect cloak color
        if self.cloak_color_lower_alt is not None:
            mask = self.color_detector.detect_with_wraparound(
                frame_proc,
                self.cloak_color_lower_alt,
                self.cloak_color_upper_alt
            )
        else:
            mask = self.color_detector.detect(frame_proc)

        # Apply morphological operations for noise reduction
        mask = self.color_detector.apply_morphological_operations(mask)

        # Resize mask back to original frame size if needed
        if RESIZE_FOR_PROCESSING:
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

        # Get background
        background = self.background_capture.get_background()
        if background is None:
            return frame, mask

        # Blend background with detected cloak region
        result = self.blender.blend(frame, background, mask)

        return result, mask

    def draw_info(self, frame, mask=None, detected_pixels=None):
        """
        Draw information overlay on the frame.

        Args:
            frame (np.ndarray): Frame to draw on
            mask (np.ndarray): Mask for additional info
            detected_pixels (int): Number of detected pixels

        Returns:
            np.ndarray: Frame with overlay
        """
        if not DISPLAY_INFO:
            return frame

        frame_copy = frame.copy()
        y_offset = 30

        # FPS counter
        if DISPLAY_FPS:
            fps = self.get_fps()
            cv2.putText(
                frame_copy,
                f"FPS: {fps:.1f}",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                INFO_FONT_SCALE,
                INFO_COLOR,
                INFO_THICKNESS
            )
            y_offset += 30

        # Background status
        status = "BG: Ready" if self.background_ready else "BG: Capturing..."
        color = (0, 255, 0) if self.background_ready else (0, 0, 255)
        cv2.putText(
            frame_copy,
            status,
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            INFO_FONT_SCALE,
            color,
            INFO_THICKNESS
        )
        y_offset += 30

        # Cloak color info
        cv2.putText(
            frame_copy,
            f"Cloak Color: {self.cloak_color.upper()}",
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            INFO_FONT_SCALE,
            INFO_COLOR,
            INFO_THICKNESS
        )
        y_offset += 30

        # Detected pixels
        if detected_pixels is not None:
            cv2.putText(
                frame_copy,
                f"Detected Pixels: {detected_pixels}",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                INFO_FONT_SCALE,
                INFO_COLOR,
                INFO_THICKNESS
            )

        # Instructions
        y_offset = frame_copy.shape[0] - 60
        cv2.putText(
            frame_copy,
            "Press SPACE to capture BG | R to reset | Q to quit",
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            INFO_COLOR,
            1
        )

        return frame_copy

    def get_fps(self):
        """
        Calculate and return current FPS.

        Returns:
            float: Frames per second
        """
        if len(self.frame_times) == 0:
            return 0.0

        recent_times = self.frame_times[-30:]  # Last 30 frames
        if len(recent_times) > 1:
            avg_time = np.mean(np.diff(recent_times))
            return 1.0 / avg_time if avg_time > 0 else 0.0

        return 0.0

    def display_debug_info(self, frame, mask):
        """
        Display debug information (mask, background, etc.).

        Args:
            frame (np.ndarray): Original frame
            mask (np.ndarray): Detection mask
        """
        if SHOW_MASK:
            cv2.imshow("Mask", mask)

        if SHOW_BACKGROUND:
            background = self.background_capture.get_background()
            if background is not None:
                cv2.imshow("Background", background)

    def run(self):
        """
        Main loop for the invisibility cloak effect.

        This method:
        1. Initializes the camera
        2. Captures background
        3. Processes video frames in real-time
        4. Displays results
        """
        # Initialize camera
        if not self.initialize_camera():
            return

        self.is_running = True

        print("[InvisibilityCloakProcessor] Waiting for background capture...")
        print("[InvisibilityCloakProcessor] Press SPACE to start background capture")

        background_captured = False

        try:
            while self.is_running:
                frame_start = time.time()

                # Read frame
                ret, self.frame = self.camera.read()
                if not ret:
                    print("[InvisibilityCloakProcessor] Error: Could not read frame")
                    break

                # Draw info before background capture
                display_frame = self.frame.copy()
                display_frame = self.draw_info(display_frame)

                # Show waiting message
                if not background_captured:
                    cv2.putText(
                        display_frame,
                        "Press SPACE to capture background",
                        (self.frame.shape[1] // 2 - 200, self.frame.shape[0] // 2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 0, 255),
                        2
                    )

                cv2.imshow(WINDOW_NAME, display_frame)

                # Handle key presses
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):  # Quit
                    self.is_running = False

                elif key == ord(' '):  # Space - capture background
                    if not background_captured:
                        if self.capture_background():
                            self.background_ready = True
                            background_captured = True
                            print("[InvisibilityCloakProcessor] Background captured successfully!")

                elif key == ord('r'):  # Reset
                    self.background_capture.reset()
                    self.background_ready = False
                    background_captured = False
                    print("[InvisibilityCloakProcessor] Reset - background cleared")

                # Process frame if background is ready
                if background_captured:
                    result_frame, mask = self.process_frame(self.frame)
                    detected_pixels = self.color_detector.get_detected_pixel_count(mask)

                    result_frame = self.draw_info(result_frame, mask, detected_pixels)

                    if DEBUG_MODE:
                        self.display_debug_info(result_frame, mask)

                    cv2.imshow(WINDOW_NAME, result_frame)

                # Update FPS counter
                frame_time = time.time() - frame_start
                self.frame_times.append(time.time())
                self.frame_count += 1

        except KeyboardInterrupt:
            print("[InvisibilityCloakProcessor] Interrupted by user")

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        print("[InvisibilityCloakProcessor] Cleaning up...")

        if self.camera is not None:
            self.camera.release()

        cv2.destroyAllWindows()

        self.is_running = False
        print("[InvisibilityCloakProcessor] Cleanup complete")

    def set_cloak_color(self, color_name):
        """
        Change the cloak color.

        Args:
            color_name (str): Name of the color ('red', 'blue', 'green', 'yellow')

        Returns:
            bool: True if color changed successfully
        """
        if color_name in COLOR_PRESETS:
            preset = COLOR_PRESETS[color_name]
            self.color_detector.set_color_range(preset['lower'], preset['upper'])
            self.cloak_color = color_name
            self.cloak_color_lower_alt = preset.get('lower_alt')
            self.cloak_color_upper_alt = preset.get('upper_alt')
            print(f"[InvisibilityCloakProcessor] Cloak color changed to: {color_name}")
            return True

        print(f"[InvisibilityCloakProcessor] Color '{color_name}' not found")
        return False