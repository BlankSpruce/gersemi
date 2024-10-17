import sys


if __name__ == "__main__":
    cache_directory_path = sys.stdin.readline().strip()

    def patched_cache_path():
        return cache_directory_path

    import gersemi.cache as gc

    gc.cache_path = patched_cache_path
    from gersemi.__main__ import main as real_main

    real_main()
