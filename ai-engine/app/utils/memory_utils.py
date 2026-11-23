import gc
import os
import torch
import psutil


class MemoryUtils:
    """
    System RAM and GPU memory management utilities.
    """

    @staticmethod
    def get_system_memory():
        memory = psutil.virtual_memory()

        return {
            "total_gb": round(memory.total / (1024 ** 3), 2),
            "available_gb": round(memory.available / (1024 ** 3), 2),
            "used_gb": round(memory.used / (1024 ** 3), 2),
            "usage_percent": memory.percent,
        }

    @staticmethod
    def get_process_memory():
        process = psutil.Process(os.getpid())
        memory = process.memory_info()

        return {
            "rss_mb": round(memory.rss / (1024 ** 2), 2),
            "vms_mb": round(memory.vms / (1024 ** 2), 2),
        }

    @staticmethod
    def get_gpu_memory():
        if not torch.cuda.is_available():
            return {
                "available": False,
            }

        return {
            "available": True,
            "allocated_mb": round(
                torch.cuda.memory_allocated() / (1024 ** 2), 2
            ),
            "reserved_mb": round(
                torch.cuda.memory_reserved() / (1024 ** 2), 2
            ),
            "max_allocated_mb": round(
                torch.cuda.max_memory_allocated() / (1024 ** 2), 2
            ),
        }

    @staticmethod
    def clear_python_memory():
        collected = gc.collect()

        return {
            "success": True,
            "objects_collected": collected,
        }

    @staticmethod
    def clear_gpu_memory():
        if not torch.cuda.is_available():
            return False

        gc.collect()
        torch.cuda.empty_cache()

        return True

    @staticmethod
    def get_memory_summary():
        return {
            "system": MemoryUtils.get_system_memory(),
            "process": MemoryUtils.get_process_memory(),
            "gpu": MemoryUtils.get_gpu_memory(),
        }
