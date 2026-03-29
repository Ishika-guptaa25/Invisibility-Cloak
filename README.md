# Invisibility Cloak - Real-Time Video Processing

A real-time system that detects colored cloth in video and replaces it with a previously captured background.

## Installation

```bash
pip install opencv-python numpy scipy pillow
```

## Quick Start

Replace fixed files:
```bash
cp main_fixed.py src/main.py
cp blending_fixed.py src/blending.py
cp settings_fixed.py config/settings.py
```

Run:
```bash
python run.py
```

## Usage

1. Position cloth in frame
2. Press SPACE to capture background
3. Hold cloth - it becomes invisible

Controls: SPACE (capture), R (reset), Q (quit)

## Configuration

Edit `config/settings.py`:
- `CLOAK_COLOR_LOWER/UPPER`: HSV color range
- `BLEND_METHOD`: simple, gaussian, alpha, pyramid
- `CAMERA_INDEX`: Camera device number

## Options

```bash
python run.py --color blue              # Blue cloth
python run.py --blend simple            # Faster blending
python run.py --camera 1                # Different camera
```

## Troubleshooting

**Cloth not detected:**
```bash
python calibrate_hsv.py
```
Position cloth in center, press SPACE, copy values to settings.

**Slow performance:**
```python
# In config/settings.py
RESIZE_FOR_PROCESSING = True
BLEND_METHOD = 'simple'
```

**Camera not working:**
```bash
python run.py --camera 1
```

## Technical Details

**Fixes applied:**
1. Fixed display pipeline (single frame rendering)
2. Clarified mask blending logic
3. Added error feedback messages

**Performance:** 30+ FPS on modern hardware (gaussian), 45+ FPS (simple)

**Algorithm:** HSV detection → Morphological operations → Background blending

## Requirements

- Python 3.7+
- OpenCV 4.0+
- NumPy, SciPy, Pillow