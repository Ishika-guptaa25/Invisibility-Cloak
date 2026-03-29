"""
Configuration parameters for the Invisibility Cloak System
"""

# ============================================================================
# CAMERA SETTINGS
# ============================================================================
CAMERA_INDEX = 0  # Default camera device (0 is usually the built-in camera)
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30

# Red cloth HSV values - ADJUST THESE FOR YOUR SPECIFIC CLOTH!
CLOAK_COLOR_LOWER = (0, 100, 100)
CLOAK_COLOR_UPPER = (10, 255, 255)

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
    },
    'orange': {
        'lower': (10, 100, 100),
        'upper': (25, 255, 255)
    },
    'purple': {
        'lower': (130, 100, 100),
        'upper': (160, 255, 255)
    }
}

# ============================================================================
# BACKGROUND CAPTURE SETTINGS
# ============================================================================
BACKGROUND_CAPTURE_FRAMES = 30  # Number of frames to capture for background averaging
BACKGROUND_BLUR_KERNEL = (21, 21)  # Kernel size for smoothing background
BACKGROUND_CAPTURE_WAIT_TIME = 2  # Seconds to wait before capturing (for stability)

# ============================================================================
# MORPHOLOGICAL OPERATIONS - Remove noise from mask
# ============================================================================
MORPH_KERNEL_SIZE = (5, 5)  # Size of morphological kernel
EROSION_ITERATIONS = 2  # Remove small noise
DILATION_ITERATIONS = 3  # Restore object size and fill holes

# ============================================================================
# BLENDING SETTINGS - How to blend background with current frame
# ============================================================================
BLEND_METHOD = 'gaussian'  # Options: 'simple', 'gaussian', 'alpha', 'pyramid'
GAUSSIAN_BLUR_KERNEL = (15, 15)  # Size of Gaussian kernel for smooth edges
GAUSSIAN_BLUR_SIGMA = 0  # Sigma for Gaussian blur (0 = auto-calculate)

# ============================================================================
# DISPLAY SETTINGS
# ============================================================================
DISPLAY_FPS = True  # Show FPS counter
DISPLAY_INFO = True  # Show status information
WINDOW_NAME = 'Invisibility Cloak - Real Time'
INFO_COLOR = (0, 255, 0)  # Green color for text (BGR format)
INFO_FONT = 'hershey_simplex'
INFO_FONT_SCALE = 0.7
INFO_THICKNESS = 2

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================
FRAME_SKIP = 1  # Process every Nth frame (1 = process every frame)
USE_THREADING = True  # Use threading for background capture (non-blocking)
RESIZE_FOR_PROCESSING = False  # Resize frame for faster processing
PROCESSING_WIDTH = 640  # Resize frame width for faster processing
PROCESSING_HEIGHT = 480  # Resize frame height for faster processing

# ============================================================================
# DEBUG MODE
# ============================================================================
DEBUG_MODE = False  # Set to True for debug visualizations
SHOW_MASK = False  # Display the mask during processing
SHOW_BACKGROUND = False  # Display the captured background