# GPU Setup Guide

This guide will help you set up GPU acceleration for the chatbot system to achieve maximum performance.

## Prerequisites

### 1. NVIDIA GPU
- NVIDIA GPU with CUDA Compute Capability 3.5 or higher
- Recommended: RTX 3060 or better (6GB+ VRAM)
- Check your GPU: https://developer.nvidia.com/cuda-gpus

### 2. NVIDIA Drivers
- Install the latest NVIDIA drivers for your GPU
- Verify installation:
  ```bash
  nvidia-smi
  ```

### 3. CUDA Toolkit
- CUDA 11.8 or 12.1 recommended
- Download from: https://developer.nvidia.com/cuda-downloads
- Verify installation:
  ```bash
  nvcc --version
  ```

## Installation Steps

### Step 1: Install PyTorch with CUDA Support

**For CUDA 12.1 (Recommended):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**For CUDA 11.8:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Verify PyTorch CUDA:**
```python
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### Step 2: Install GPU-Optimized Dependencies

```bash
pip install faster-whisper ctranslate2
```

### Step 3: Install Other Requirements

```bash
pip install -r requirements.txt
```

### Step 4: Verify GPU Setup

Run the chatbot server and check the startup output:
```bash
python run.py
```

You should see:
```
============================================================
GPU CONFIGURATION
============================================================
PyTorch: Installed
CUDA: Available ✓
GPU Device: NVIDIA GeForce RTX 4090
GPU Count: 1
CUDA Version: 12.1
...
============================================================
```

## Configuration

The system is configured to use GPU by default. Check `config.yaml`:

```yaml
asr:
  whisper:
    model: "medium"  # Options: tiny, base, small, medium, large, large-v3
    device: "auto"   # Auto-detects GPU
    compute_type: "float16"  # FP16 for GPU acceleration
```

### Model Recommendations by GPU Memory

| GPU Memory | Recommended Model | Speed          | Quality |
|-----------|------------------|----------------|---------|
| 4 GB      | small            | Fast           | Good    |
| 6 GB      | medium           | Medium         | Great   |
| 8 GB      | large            | Medium-Slow    | Excellent |
| 12+ GB    | large-v3         | Slow           | Best    |

### Compute Type Options

| Type     | GPU | Speed  | Accuracy | Memory |
|----------|-----|--------|----------|--------|
| float16  | ✓   | Fastest| Good     | Low    |
| int8     | ✓   | Fast   | Good     | Lower  |
| float32  | ✓   | Slow   | Best     | High   |

**Recommendation:** Use `float16` for best speed/quality balance on GPU.

## Performance Benchmarks

Expected transcription speeds (on RTX 4090):

| Model    | Real-time Factor | 1-minute Audio |
|----------|-----------------|----------------|
| tiny     | 50x             | 1.2s           |
| base     | 40x             | 1.5s           |
| small    | 30x             | 2.0s           |
| medium   | 15x             | 4.0s           |
| large-v3 | 8x              | 7.5s           |

*Real-time factor: How many times faster than real-time*

## Troubleshooting

### CUDA Not Available

**Issue:** System shows "CUDA: Not Available ✗"

**Solutions:**
1. Verify NVIDIA drivers:
   ```bash
   nvidia-smi
   ```

2. Reinstall PyTorch with CUDA:
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

3. Check CUDA installation:
   ```bash
   nvcc --version
   ```

### Out of Memory Errors

**Issue:** CUDA out of memory errors

**Solutions:**
1. Use a smaller model (e.g., `small` instead of `medium`)
2. Use `int8` compute type instead of `float16`
3. Clear GPU cache:
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

### Slow Performance on GPU

**Issue:** GPU is slower than expected

**Solutions:**
1. Ensure you're using `faster-whisper`, not `openai-whisper`
2. Check compute type is `float16` or `int8`
3. Verify GPU utilization:
   ```bash
   nvidia-smi
   ```
   Should show high GPU utilization during transcription

4. Update to latest CUDA drivers

### Mixed Precision Warnings

**Issue:** Warnings about mixed precision

**Solutions:**
- Safe to ignore for most users
- Or use `float32` compute type for pure precision

## Multi-GPU Setup

If you have multiple GPUs, the system will automatically use GPU 0. To use a specific GPU:

```bash
# Use GPU 1
export CUDA_VISIBLE_DEVICES=1
python run.py

# Use GPUs 0 and 1
export CUDA_VISIBLE_DEVICES=0,1
python run.py
```

## CPU Fallback

If GPU is not available, the system automatically falls back to CPU mode with optimizations:
- Uses `int8` compute type for faster CPU inference
- Smaller models recommended (tiny/base)
- Expect 5-10x slower performance

## Optimization Tips

### 1. Model Selection
- Start with `medium` model for best balance
- Use `small` for faster responses
- Use `large-v3` only if you have 12GB+ VRAM and need best accuracy

### 2. Batch Processing
- System processes audio in real-time
- GPU efficiently handles single-stream processing

### 3. Memory Management
- Close other GPU applications
- Monitor GPU memory with `nvidia-smi`
- Restart server if memory leaks occur

### 4. VAD (Voice Activity Detection)
- Enabled by default in faster-whisper
- Skips silent portions for faster processing
- Configurable in code if needed

## Verification Checklist

- [ ] NVIDIA drivers installed (`nvidia-smi` works)
- [ ] CUDA Toolkit installed (`nvcc --version` works)
- [ ] PyTorch with CUDA installed
- [ ] `torch.cuda.is_available()` returns `True`
- [ ] faster-whisper installed
- [ ] Server shows "CUDA: Available ✓" on startup
- [ ] ASR logs show "Using faster-whisper (GPU-optimized)"

## Getting Help

If you encounter issues:

1. Check the logs for detailed error messages
2. Run the verification checklist above
3. Check GPU temperature and utilization with `nvidia-smi`
4. Review the troubleshooting section
5. Open an issue on GitHub with:
   - GPU model and VRAM
   - CUDA version
   - Error messages
   - `nvidia-smi` output

## References

- PyTorch CUDA Installation: https://pytorch.org/get-started/locally/
- NVIDIA CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
- faster-whisper Documentation: https://github.com/guillaumekln/faster-whisper
- CTranslate2: https://github.com/OpenNMT/CTranslate2
