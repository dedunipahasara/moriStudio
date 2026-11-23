import torch


class GPUUtils:
    """
    GPU and CUDA utility functions.
    """

    @staticmethod
    def is_available():
        return torch.cuda.is_available()

    @staticmethod
    def get_device():
        if torch.cuda.is_available():
            return torch.device("cuda")

        return torch.device("cpu")

    @staticmethod
    def get_device_name():
        if not torch.cuda.is_available():
            return "CPU"

        return torch.cuda.get_device_name(0)

    @staticmethod
    def get_device_count():
        if not torch.cuda.is_available():
            return 0

        return torch.cuda.device_count()

    @staticmethod
    def get_gpu_info():
        if not torch.cuda.is_available():
            return {
                "available": False,
                "device": "CPU",
                "device_count": 0,
            }

        properties = torch.cuda.get_device_properties(0)

        return {
            "available": True,
            "device": properties.name,
            "device_count": torch.cuda.device_count(),
            "total_memory_gb": round(
                properties.total_memory / (1024 ** 3), 2
            ),
            "compute_capability": (
                f"{properties.major}.{properties.minor}"
            ),
        }

    @staticmethod
    def get_memory_usage():
        if not torch.cuda.is_available():
            return None

        allocated = torch.cuda.memory_allocated(0)
        reserved = torch.cuda.memory_reserved(0)

        return {
            "allocated_mb": round(allocated / (1024 ** 2), 2),
            "reserved_mb": round(reserved / (1024 ** 2), 2),
            "max_allocated_mb": round(
                torch.cuda.max_memory_allocated(0) / (1024 ** 2),
                2,
            ),
        }

    @staticmethod
    def clear_cache():
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            return True

        return False

    @staticmethod
    def reset_memory_stats():
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            return True

        return False

    @staticmethod
    def synchronize():
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            return True

        return False
