# Configuration parameters for the Invisibility Cloak System

# ============================================================================
# CAMERA SETTINGS
# ============================================================================
CAMERA_INDEX = 0  # Default camera device (0 is usually the built-in camera)
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30

CLOAK_COLOR_LOWER = (10, 95, 140)   # ← Your exact center color - 2
CLOAK_COLOR_UPPER = (14, 255, 255)  # ← Your exact center color + 2

# Alternative color presets (HSV format)
COLOR_PRESETS = {
    'red': {
        'lower': (0, 100, 100),
        'upper': (10, 255, 255),
        'lower_alt': (170, 100, 100),  # Red wraps around HSV circle
        'upper_alt': (180, 255, 255)
    },
    'blue': {
        'lower': (100, 100, 100),
        'upper': (130, 255, 255)
    },
    'green': {
        'lower': (50, 100, 100),
        'upper': (70, 255, 255)
    },
    'yellow': {
        'lower': (20, 100, 100),
        'upper': (40, 255, 255)
    }
}

# ============================================================================
# BACKGROUND CAPTURE SETTINGS
# ============================================================================
BACKGROUND_CAPTURE_FRAMES = 30  # Number of frames to capture for background
BACKGROUND_BLUR_KERNEL = (21, 21)  # Kernel size for averaging background
BACKGROUND_CAPTURE_WAIT_TIME = 3  # Seconds to wait before capturing

# ============================================================================
# MORPHOLOGICAL OPERATIONS
# ============================================================================
MORPH_KERNEL_SIZE = (5, 5)
EROSION_ITERATIONS = 2
DILATION_ITERATIONS = 3

# ============================================================================
# BLENDING SETTINGS
# ============================================================================
BLEND_METHOD = 'gaussian'  # 'simple', 'gaussian', or 'alpha'
GAUSSIAN_BLUR_KERNEL = (15, 15)
GAUSSIAN_BLUR_SIGMA = 0

# ============================================================================
# DISPLAY SETTINGS
# ============================================================================
DISPLAY_FPS = True
DISPLAY_INFO = True
WINDOW_NAME = 'Invisibility Cloak - Real Time'
INFO_COLOR = (0, 255, 0)  # Green color for text (BGR format)
INFO_FONT = 'hershey_simplex'
INFO_FONT_SCALE = 0.7
INFO_THICKNESS = 2

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================
FRAME_SKIP = 1  # Process every Nth frame (1 = process every frame)
USE_THREADING = True  # Use threading for background capture
RESIZE_FOR_PROCESSING = True
PROCESSING_WIDTH = 640  # Resize frame width for faster processing
PROCESSING_HEIGHT = 480

# ============================================================================
# DEBUG MODE
# ============================================================================
DEBUG_MODE = False  # Set to True for debug visualizations
SHOW_MASK = False  # Display the mask during processing
SHOW_BACKGROUND = False  # Display the captured background