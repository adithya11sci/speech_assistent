# Input Media

⚠️ **Place your source media (images or videos) here**

## Directory Structure

```
input/
├── images/           # Static images
│   └── avatar.jpg    # Your avatar face image
│
└── videos/           # Video files (RECOMMENDED)
    └── avatar.mp4    # Short talking video (3-10 seconds)
```

## Recommendations

### For Static Image:
- **Format**: JPG, PNG
- **Resolution**: 720p or higher
- **Requirements**:
  - Clear, well-lit face
  - Frontal view
  - Neutral expression
  - Single person in frame
  
### For Video (RECOMMENDED):
- **Format**: MP4, AVI, MOV
- **Duration**: 3-10 seconds (loops automatically)
- **FPS**: 25-30 FPS
- **Resolution**: 720p or higher
- **Content**:
  - Person facing camera
  - Natural head movements
  - Can include slight mouth movements
  - Good lighting
  - Single person in frame

**Why video is better:**
- More natural appearance
- Realistic head movements
- Better engagement
- Smoother animations

## Creating Source Video

### Quick Tips:
1. Record 5-10 seconds of yourself facing camera
2. Keep head relatively still but natural slight movements are good
3. Maintain neutral to slightly positive expression
4. Ensure consistent lighting
5. Use 1080p or 720p resolution
6. Export as MP4 (H.264 codec)

### Command to loop video (optional):
```bash
ffmpeg -i input.mp4 -filter_complex "loop=3:250:0" -t 10 output.mp4
```

## Current Configuration

Check `src/config.py`:
```python
SOURCE_TYPE = "video"  # or "image"
SOURCE_VIDEO_PATH = INPUT_VIDEOS_DIR / "avatar.mp4"
SOURCE_IMAGE_PATH = INPUT_IMAGES_DIR / "avatar.jpg"
```

## Checklist

- [ ] Source media added to appropriate folder
- [ ] Filename matches config.py
- [ ] Face clearly visible
- [ ] Good lighting and quality
- [ ] Single person in frame
