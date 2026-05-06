import cv2
import numpy as np
import sys


class HSVCalibrator:
    """Interactive HSV range calibrator with real-time visualization."""

    def __init__(self, camera_index=0):
        """Initialize the calibrator."""
        self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            print("ERROR: Could not open camera!")
            sys.exit(1)

        # Set camera properties
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # Initial HSV values (Red)
        self.h_min = 0
        self.h_max = 10
        self.s_min = 100
        self.s_max = 255
        self.v_min = 100
        self.v_max = 255

        # For color picker
        self.selected_color = None
        self.sample_points = []

        print("=" * 80)
        print("HSV COLOR CALIBRATOR - DIAGNOSTIC TOOL")
        print("=" * 80)
        print()
        print("INSTRUCTIONS:")
        print("1. Hold your cloak/fabric in front of the camera")
        print("2. Adjust sliders to detect ONLY your cloak (not background)")
        print("3. Green area = detected pixels | Red area = cloak")
        print("4. Try to make green area cover ONLY the cloak")
        print()
        print("KEYBOARD CONTROLS:")
        print("  SPACE  - Auto-detect color from center of screen")
        print("  P      - Sample color from point (click window first)")
        print("  R      - Reset to default Red preset")
        print("  B      - Reset to Blue preset")
        print("  G      - Reset to Green preset")
        print("  Y      - Reset to Yellow preset")
        print("  Q      - Quit and print detected values")
        print()
        print("=" * 80)

    def on_h_min(self, value):
        self.h_min = value

    def on_h_max(self, value):
        self.h_max = value

    def on_s_min(self, value):
        self.s_min = value

    def on_s_max(self, value):
        self.s_max = value

    def on_v_min(self, value):
        self.v_min = value

    def on_v_max(self, value):
        self.v_max = value

    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks to sample color."""
        if event == cv2.EVENT_LBUTTONDOWN:
            frame = param['frame']
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            h, s, v = hsv[y, x]

            # Update ranges based on sampled color
            self.h_min = max(0, int(h) - 10)
            self.h_max = min(180, int(h) + 10)
            self.s_min = max(0, int(s) - 30)
            self.s_max = 255
            self.v_min = max(0, int(v) - 30)
            self.v_max = 255

            print(f"[SAMPLE] Clicked pixel - H:{int(h)}, S:{int(s)}, V:{int(v)}")
            print(f"[UPDATE] Range set to:")
            print(f"  H: {self.h_min} - {self.h_max}")
            print(f"  S: {self.s_min} - {self.s_max}")
            print(f"  V: {self.v_min} - {self.v_max}")

    def auto_detect_color(self, frame):
        """Auto-detect color from center of frame."""
        h, w = frame.shape[:2]
        center_y, center_x = h // 2, w // 2

        # Get color from center
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h_center, s_center, v_center = hsv[center_y, center_x]

        # Set ranges
        self.h_min = max(0, int(h_center) - 15)
        self.h_max = min(180, int(h_center) + 15)
        self.s_min = max(0, int(s_center) - 50)
        self.s_max = 255
        self.v_min = max(0, int(v_center) - 50)
        self.v_max = 255

        print(f"\n[AUTO-DETECT] Center pixel - H:{int(h_center)}, S:{int(s_center)}, V:{int(v_center)}")
        print(f"[AUTO-DETECT] Range set to:")
        print(f"  H: {self.h_min} - {self.h_max}")
        print(f"  S: {self.s_min} - {self.s_max}")
        print(f"  V: {self.v_min} - {self.v_max}")

    def set_preset(self, preset_name):
        """Set to a preset color."""
        presets = {
            'red': (0, 10, 100, 255, 100, 255),
            'blue': (100, 130, 100, 255, 100, 255),
            'green': (50, 70, 100, 255, 100, 255),
            'yellow': (20, 40, 100, 255, 100, 255),
        }

        if preset_name in presets:
            h_min, h_max, s_min, s_max, v_min, v_max = presets[preset_name]
            self.h_min = h_min
            self.h_max = h_max
            self.s_min = s_min
            self.s_max = s_max
            self.v_min = v_min
            self.v_max = v_max
            print(f"\n[PRESET] Set to {preset_name.upper()}")

    def run(self):
        """Run the calibrator."""
        # Create window
        window_name = "HSV Calibrator - Hold Cloak in Center"
        cv2.namedWindow(window_name)

        # Create trackbars
        cv2.createTrackbar('H_min', window_name, self.h_min, 180, self.on_h_min)
        cv2.createTrackbar('H_max', window_name, self.h_max, 180, self.on_h_max)
        cv2.createTrackbar('S_min', window_name, self.s_min, 255, self.on_s_min)
        cv2.createTrackbar('S_max', window_name, self.s_max, 255, self.on_s_max)
        cv2.createTrackbar('V_min', window_name, self.v_min, 255, self.on_v_min)
        cv2.createTrackbar('V_max', window_name, self.v_max, 255, self.on_v_max)

        # Set mouse callback
        callback_data = {'frame': None}
        cv2.setMouseCallback(window_name, self.mouse_callback, callback_data)

        print("\n✓ Calibrator started! Adjust sliders while holding your cloak in frame.\n")

        try:
            frame_count = 0
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    print("Error: Could not read frame")
                    break

                frame_count += 1
                callback_data['frame'] = frame

                # Convert to HSV
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                # Create mask with current values
                lower = np.array([self.h_min, self.s_min, self.v_min], dtype=np.uint8)
                upper = np.array([self.h_max, self.s_max, self.v_max], dtype=np.uint8)
                mask = cv2.inRange(hsv, lower, upper)

                # Apply morphological operations
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                mask = cv2.erode(mask, kernel, iterations=2)
                mask = cv2.dilate(mask, kernel, iterations=3)

                # Create visualization
                mask_color = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

                # Green = detected, original frame in background
                result = frame.copy()
                result[mask > 0] = [0, 255, 0]  # Green where cloak detected

                # Side-by-side view
                left_side = result
                right_side = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                combined = np.hstack([left_side, right_side])

                # Add text info
                text_y = 30
                cv2.putText(combined, f"H: {self.h_min:3d}-{self.h_max:3d}", (15, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(combined, f"S: {self.s_min:3d}-{self.s_max:3d}", (15, text_y + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(combined, f"V: {self.v_min:3d}-{self.v_max:3d}", (15, text_y + 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Pixel count
                pixel_count = cv2.countNonZero(mask)
                cv2.putText(combined, f"Pixels: {pixel_count}", (15, text_y + 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Instructions
                cv2.putText(combined, "SPACE=Auto  P=Sample  R/B/G/Y=Presets  Q=Quit",
                            (15, combined.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                cv2.imshow(window_name, combined)

                # Handle keyboard
                key = cv2.waitKey(30) & 0xFF

                if key == ord('q'):
                    break
                elif key == ord(' '):
                    self.auto_detect_color(frame)
                elif key == ord('p'):
                    print("\n[SAMPLE] Click on the cloak color in the window to sample it")
                elif key == ord('r'):
                    self.set_preset('red')
                elif key == ord('b'):
                    self.set_preset('blue')
                elif key == ord('g'):
                    self.set_preset('green')
                elif key == ord('y'):
                    self.set_preset('yellow')

        finally:
            self.print_results()
            self.camera.release()
            cv2.destroyAllWindows()

    def print_results(self):
        """Print the found values."""
        print("\n" + "=" * 80)
        print("CALIBRATION COMPLETE!")
        print("=" * 80)
        print("\nAdd these values to config/settings.py:\n")
        print(f"CLOAK_COLOR_LOWER = ({self.h_min}, {self.s_min}, {self.v_min})")
        print(f"CLOAK_COLOR_UPPER = ({self.h_max}, {self.s_max}, {self.v_max})")
        print("\nOr use command line:")
        print(f"python run.py --color custom")
        print("\nThen update config/settings.py with the values above.")
        print("\n" + "=" * 80)


class QuickDiagnostic:
    """Quick diagnostic to check current detection."""

    @staticmethod
    def run():
        """Run quick diagnostic."""
        print("\n" + "=" * 80)
        print("QUICK DIAGNOSTIC - Current Color Detection")
        print("=" * 80)

        from config.settings import CLOAK_COLOR_LOWER, CLOAK_COLOR_UPPER, COLOR_PRESETS

        print("\nCurrent Settings:")
        print(f"  Lower HSV: {CLOAK_COLOR_LOWER}")
        print(f"  Upper HSV: {CLOAK_COLOR_UPPER}")

        print("\nAvailable Presets:")
        for color_name, color_data in COLOR_PRESETS.items():
            print(f"  {color_name.upper()}:")
            print(f"    Lower: {color_data['lower']}")
            print(f"    Upper: {color_data['upper']}")

        print("\nTo calibrate your specific cloak:")
        print("  1. Run: python calibrate_hsv.py")
        print("  2. Adjust sliders until only your cloak is green")
        print("  3. Copy the printed values to config/settings.py")
        print("  4. Run: python run.py")

        print("\n" + "=" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--diagnostic':
        QuickDiagnostic.run()
    else:
        calibrator = HSVCalibrator(camera_index=0)
        calibrator.run()


if __name__ == '__main__':
    main()
