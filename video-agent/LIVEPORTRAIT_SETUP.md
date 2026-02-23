# 🎭 LivePortrait Setup Guide (Real Motion Transfer)

The `video-agent` UI comes with a placeholder engine. To make it actually animate faces using your RTX 5060, follow these steps.

## 1. Prerequisites
- **OS:** Windows 10/11 (WSL2 recommended) or Linux.
- **GPU:** NVIDIA RTX series (6GB+ VRAM).
- **Tools:** Git, Python 3.10, Conda (optional but recommended).

## 2. Install the Core Library
Since `LivePortrait` is not a standard pip package yet, we use the official repository.

```bash
# Go to your project root
cd agent-wrapper/video-agent

# Clone the official LivePortrait repo
git clone https://github.com/KwaiVGI/LivePortrait
cd LivePortrait

# Install dependencies
pip install -r requirements.txt
```

## 3. Download Pre-trained Weights (The Models)
You need the AI models (approx 2GB).

1.  **HuggingFace:** Go to [LivePortrait HuggingFace](https://huggingface.co/KwaiVGI/LivePortrait/tree/main).
2.  **Download:**
    *   `appearance_feature_extractor.pth`
    *   `motion_extractor.pth`
    *   `spade_generator.pth`
    *   `warping_module.pth`
3.  **Place them:** Put these files inside `video-agent/LivePortrait/pretrained_weights/`.

## 4. Connect the UI
Now we update `ui.py` to use the real model instead of the mock.

**Modify `src/video_agent/ui.py`:**

```python
import sys
import os
# Add LivePortrait to path
sys.path.append(os.path.join(os.getcwd(), "LivePortrait"))

from inference import LivePortraitPipeline  # Pseudocode wrapper

# Initialize once
pipeline = LivePortraitPipeline(weights_dir="LivePortrait/pretrained_weights")

def animate_face(source_image, driving_video):
    output_path = "outputs/result.mp4"
    
    # Real Inference Call
    pipeline.execute(
        source_image_path=source_image,
        driving_video_path=driving_video,
        output_path=output_path,
        flag_use_cuda=True  # Use your RTX 5060!
    )
    return output_path
```

## 5. Run It
```bash
# From video-agent directory
python src/video_agent/main.py ui
```

## Troubleshooting
- **CUDA Errors:** Ensure you installed PyTorch with CUDA support:
  `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121`
- **Face not detected:** Use high-quality, front-facing photos.
