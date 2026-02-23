# 3D Gaussian Splatting Pipeline for DepoSafety V2

This directory contains the ML pipeline for converting video to 3D Gaussian Splatting models.

## Files

- `colab_3dgs.ipynb` - Google Colab notebook for cloud processing (recommended for large videos)
- `local_3dgs.py` - Local fallback script for small videos
- `api_client.py` - Backend webhook client
- `requirements.txt` - Python dependencies

## Quick Start

### Option 1: Google Colab (Recommended)

1. Open `colab_3dgs.ipynb` in Google Colab
2. Mount your Google Drive
3. Set your Cloudflare R2 credentials
4. Run all cells

### Option 2: Local Processing (Small Videos Only)

```bash
# Install dependencies
pip install -r requirements.txt

# Install COLMAP (Ubuntu/Debian)
sudo apt-get install colmap

# Install gaussian-splatting submodule
git clone --recursive https://github.com/graphdeco-inria/gaussian-splatting.git
cd gaussian-splatting
pip install submodules/diff-gaussian-rasterization
pip install submodules/simple-knn

# Run local pipeline
python local_3dgs.py --video input.mp4 --output ./output
```

## Architecture

```
Video Input
    ↓
Frame Extraction (ffmpeg)
    ↓
COLMAP (Camera Pose Estimation)
    ↓
3D Gaussian Splatting Training
    ↓
Export (.ply + .splat)
    ↓
Upload to Cloudflare R2
    ↓
Webhook to Backend
```

## API Integration

The pipeline calls the backend webhook with processing status:

```python
from api_client import notify_processing_complete

notify_processing_complete(
    job_id="uuid",
    status="completed",
    model_url="https://r2.example.com/model.splat"
)
```

## Model Compression

The pipeline includes automatic compression:
- PLY to SPLAT conversion (10-20x smaller)
- Quantization for web viewing
- Optional: Draco compression for PLY

## Requirements

- CUDA-capable GPU (8GB+ VRAM recommended)
- Python 3.8+
- COLMAP
- ffmpeg

## Troubleshooting

### Out of Memory
- Reduce `resolution` in training config
- Use Colab with V100/A100 GPU
- Process shorter video segments

### COLMAP fails
- Ensure sufficient texture in video
- Check camera intrinsics if known
- Try sequential matcher for ordered frames

## License

Same as DepoSafety V2 project.
