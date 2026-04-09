import cv2
import numpy as np
from config.settings import CLOAK_COLOR_LOWER, CLOAK_COLOR_UPPER

print("\n" + "=" * 80)
print("COLOR DETECTION DIAGNOSTIC")
print("=" * 80)

print("\nCurrent Settings:")
print(f"  CLOAK_COLOR_LOWER: {CLOAK_COLOR_LOWER}")
print(f"  CLOAK_COLOR_UPPER: {CLOAK_COLOR_UPPER}")

print("\nStarting camera diagnostic...")
print("Position your RED CLOTH in center of frame")
print("The window will show detection results")
print("Press Q to quit\n")

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Cannot open camera!")
    exit(1)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

try:
    while True:
        ret, frame = camera.read()
        if not ret:
            break

        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        
        h, w = frame.shape[:2]
        center_h_val, center_s_val, center_v_val = hsv[h // 2, w // 2]

        
        lower = np.array(CLOAK_COLOR_LOWER, dtype=np.uint8)
        upper = np.array(CLOAK_COLOR_UPPER, dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)

        # Count detected pixels
        detected = cv2.countNonZero(mask)

        # Create result display
        result = frame.copy()
        result[mask > 0] = [0, 255, 0]  # Green where detected

        # Add info
        cv2.putText(result, f"Center HSV: H={int(center_h_val)}, S={int(center_s_val)}, V={int(center_v_val)}",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(result, f"Detected Pixels: {detected}",
                    (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(result, f"H Range: {CLOAK_COLOR_LOWER[0]}-{CLOAK_COLOR_UPPER[0]}",
                    (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(result, f"S Range: {CLOAK_COLOR_LOWER[1]}-{CLOAK_COLOR_UPPER[1]}",
                    (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(result, f"V Range: {CLOAK_COLOR_LOWER[2]}-{CLOAK_COLOR_UPPER[2]}",
                    (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Show mask
        mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        combined = np.hstack([result, mask_colored])

        cv2.imshow("Color Detection Diagnostic", combined)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()

    print("\n" + "=" * 80)
    print("DIAGNOSTIC RESULTS")
    print("=" * 80)
    print(f"\nYour cloth's center color (HSV):")
    print(f"  H (Hue):        {int(center_h_val)}")
    print(f"  S (Saturation): {int(center_s_val)}")
    print(f"  V (Value):      {int(center_v_val)}")

    print(f"\nCurrent detection range:")
    print(f"  H: {CLOAK_COLOR_LOWER[0]} - {CLOAK_COLOR_UPPER[0]}")
    print(f"  S: {CLOAK_COLOR_LOWER[1]} - {CLOAK_COLOR_UPPER[1]}")
    print(f"  V: {CLOAK_COLOR_LOWER[2]} - {CLOAK_COLOR_UPPER[2]}")

    print(f"\nDetected pixels in last frame: {detected}")

    if detected < 100:
        print("\n⚠️  PROBLEM: Very few or no pixels detected!")
        print("\nSOLUTION:")
        print("1. Run: python calibrate_hsv.py")
        print("2. Hold cloth in CENTER")
        print("3. Press SPACE to auto-detect")
        print("4. Copy the printed HSV values")
        print("5. Update config/settings.py")
        print("6. Try again!")
    else:
        print(f"\n✅ Good! {detected} pixels detected")
        print("If invisibility still doesn't work, check blending settings")

    print("\n" + "=" * 80)
