import sys

from simp_os.kernel import SimpKernel


def main() -> int:
    """
    Entry point for SimpOs.

    This runs a text-based "fake OS" inside the terminal.
    """
    kernel = SimpKernel()
    try:
        kernel.boot()
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        print("\n[!] SimpOs interrupted, shutting down...")
    finally:
        kernel.shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

