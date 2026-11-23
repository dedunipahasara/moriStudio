
import torch
import platform
import sys


def check_system():
    print("=" * 50)
    print("       CUTE3D AI ENGINE - SYSTEM CHECK")
    print("=" * 50)

    print(f"Python Version : {sys.version.split()[0]}")
    print(f"Platform       : {platform.platform()}")
    print(f"PyTorch        : {torch.__version__}")
    print(f"CUDA Available : {torch.cuda.is_available()}")
    print(f"CUDA Version   : {torch.version.cuda}")

    if torch.cuda.is_available():
        print(f"GPU Count      : {torch.cuda.device_count()}")

        for index in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(index)

            print(f"\nGPU {index}")
            print(f"GPU Name       : {props.name}")
            print(f"Total VRAM     : {props.total_memory / 1024**3:.2f} GB")
            print(f"Compute Cap.   : {props.major}.{props.minor}")

            allocated = torch.cuda.memory_allocated(index) / 1024**3
            reserved = torch.cuda.memory_reserved(index) / 1024**3

            print(f"Allocated VRAM : {allocated:.2f} GB")
            print(f"Reserved VRAM  : {reserved:.2f} GB")

        print("\nSelected Device: CUDA")
    else:
        print("\nSelected Device: CPU")

    print("=" * 50)


if __name__ == "__main__":
    check_system()

