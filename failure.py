import time
ROOM = 20000

def consume_memory(size_in_mb):
    print(f"failure injecting...")
    bytes_per_mb = 1024 * 1024
    big_data = ' ' * (size_in_mb * bytes_per_mb)
    print(f"failure injected...")
    time.sleep(15)
    print(f"failure restored...")

if __name__ == "__main__":
    try:
        consume_memory(ROOM)
    except MemoryError:
        print("No Enough Memory...")
