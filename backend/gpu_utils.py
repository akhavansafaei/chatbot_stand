"""GPU detection and optimization utilities."""

import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class GPUManager:
    """Manages GPU detection and configuration."""

    def __init__(self):
        """Initialize GPU manager."""
        self.has_cuda = False
        self.cuda_device_count = 0
        self.cuda_device_name = None
        self.torch_available = False

        self._detect_gpu()

    def _detect_gpu(self):
        """Detect available GPU resources."""
        try:
            import torch
            self.torch_available = True
            self.has_cuda = torch.cuda.is_available()

            if self.has_cuda:
                self.cuda_device_count = torch.cuda.device_count()
                self.cuda_device_name = torch.cuda.get_device_name(0)

                logger.info(f"GPU detected: {self.cuda_device_name}")
                logger.info(f"CUDA devices available: {self.cuda_device_count}")
                logger.info(f"CUDA version: {torch.version.cuda}")

                # Log GPU memory
                for i in range(self.cuda_device_count):
                    mem_total = torch.cuda.get_device_properties(i).total_memory / 1e9
                    logger.info(f"GPU {i} memory: {mem_total:.2f} GB")
            else:
                logger.warning("CUDA not available. GPU acceleration disabled.")

        except ImportError:
            logger.warning("PyTorch not installed. GPU detection skipped.")
        except Exception as e:
            logger.error(f"Error detecting GPU: {e}")

    def get_device(self, requested_device: str = "auto") -> str:
        """Get the optimal device based on availability.

        Args:
            requested_device: Requested device ('auto', 'cuda', 'cpu')

        Returns:
            Device string ('cuda' or 'cpu')
        """
        if requested_device == "auto":
            if self.has_cuda:
                logger.info("Auto-detected device: CUDA")
                return "cuda"
            else:
                logger.warning("CUDA not available, falling back to CPU")
                return "cpu"
        elif requested_device == "cuda":
            if self.has_cuda:
                return "cuda"
            else:
                logger.error("CUDA requested but not available! Using CPU instead.")
                logger.error("Please install CUDA-enabled PyTorch or set device to 'auto'")
                return "cpu"
        else:
            return "cpu"

    def get_whisper_device_config(self, requested_device: str = "auto",
                                  compute_type: str = "float16") -> Tuple[str, str]:
        """Get optimized device configuration for Whisper.

        Args:
            requested_device: Requested device
            compute_type: Compute type (float16, int8, float32)

        Returns:
            Tuple of (device, compute_type)
        """
        device = self.get_device(requested_device)

        # Optimize compute type based on device
        if device == "cuda":
            if compute_type == "float16":
                logger.info("Using FP16 precision for GPU acceleration")
                return device, "float16"
            elif compute_type == "int8":
                logger.info("Using INT8 precision for GPU")
                return device, "int8"
            else:
                logger.info("Using FP32 precision on GPU (slower but more accurate)")
                return device, "float32"
        else:
            # CPU optimizations
            if compute_type in ["float16", "int8"]:
                logger.warning(f"{compute_type} requested but running on CPU, using int8")
                return device, "int8"
            else:
                logger.info("Using FP32 precision on CPU")
                return device, "float32"

    def optimize_model_size(self, requested_model: str) -> str:
        """Suggest optimal model size based on GPU memory.

        Args:
            requested_model: Requested model size

        Returns:
            Recommended model size
        """
        if not self.has_cuda:
            # CPU recommendations
            if requested_model in ["large", "large-v2", "large-v3", "medium"]:
                logger.warning(f"Model '{requested_model}' may be slow on CPU")
                logger.warning("Consider using 'base' or 'small' for CPU")
            return requested_model

        try:
            import torch

            # Get available GPU memory in GB
            mem_available = torch.cuda.get_device_properties(0).total_memory / 1e9

            # Model memory requirements (approximate)
            model_memory = {
                "tiny": 1,
                "base": 1,
                "small": 2,
                "medium": 5,
                "large": 10,
                "large-v2": 10,
                "large-v3": 10
            }

            required_mem = model_memory.get(requested_model, 5)

            if required_mem > mem_available * 0.8:  # Leave 20% headroom
                logger.warning(f"GPU memory may be insufficient for {requested_model}")
                logger.warning(f"Available: {mem_available:.1f}GB, Required: ~{required_mem}GB")

                # Suggest smaller model
                if mem_available < 4:
                    logger.warning("Recommend using 'small' model")
                elif mem_available < 8:
                    logger.warning("Recommend using 'medium' model")
            else:
                logger.info(f"GPU memory sufficient for {requested_model} model")

        except Exception as e:
            logger.error(f"Error checking GPU memory: {e}")

        return requested_model

    def print_gpu_info(self):
        """Print detailed GPU information."""
        print("\n" + "=" * 60)
        print("GPU CONFIGURATION")
        print("=" * 60)

        if self.torch_available:
            print(f"PyTorch: Installed")
            if self.has_cuda:
                print(f"CUDA: Available ✓")
                print(f"GPU Device: {self.cuda_device_name}")
                print(f"GPU Count: {self.cuda_device_count}")

                try:
                    import torch
                    print(f"CUDA Version: {torch.version.cuda}")
                    print(f"cuDNN Version: {torch.backends.cudnn.version()}")

                    for i in range(self.cuda_device_count):
                        props = torch.cuda.get_device_properties(i)
                        mem_total = props.total_memory / 1e9
                        mem_allocated = torch.cuda.memory_allocated(i) / 1e9
                        mem_cached = torch.cuda.memory_reserved(i) / 1e9

                        print(f"\nGPU {i}: {torch.cuda.get_device_name(i)}")
                        print(f"  Total Memory: {mem_total:.2f} GB")
                        print(f"  Allocated: {mem_allocated:.2f} GB")
                        print(f"  Cached: {mem_cached:.2f} GB")
                        print(f"  Compute Capability: {props.major}.{props.minor}")
                except Exception as e:
                    logger.error(f"Error getting GPU details: {e}")
            else:
                print(f"CUDA: Not Available ✗")
                print("RECOMMENDATION: Install CUDA-enabled PyTorch for GPU acceleration")
        else:
            print(f"PyTorch: Not Installed")
            print("Please install PyTorch with CUDA support")

        print("=" * 60 + "\n")

    def clear_gpu_cache(self):
        """Clear GPU cache to free memory."""
        if self.has_cuda:
            try:
                import torch
                torch.cuda.empty_cache()
                logger.info("GPU cache cleared")
            except Exception as e:
                logger.error(f"Error clearing GPU cache: {e}")


# Global GPU manager instance
_gpu_manager: Optional[GPUManager] = None


def get_gpu_manager() -> GPUManager:
    """Get the global GPU manager instance.

    Returns:
        GPUManager instance
    """
    global _gpu_manager
    if _gpu_manager is None:
        _gpu_manager = GPUManager()
    return _gpu_manager
