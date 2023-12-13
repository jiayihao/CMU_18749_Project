import psutil
import time
import statistics
from utilities import print_color, COLOR_ORANGE, COLOR_RED

def collect():
    print("Collecting Regular Memory Usage...")
    cnt = 5
    usage = []
    memory_usage = psutil.virtual_memory()
    while cnt:
        usage.append(memory_usage.percent)
        time.sleep(2)
        cnt -= 1
    reference = statistics.mean(usage)
    print(f"Regular Memory Usage: {reference}%")
    return reference


def usage_validation(reference: float):
    memory_usage = psutil.virtual_memory()
    if memory_usage.percent > reference:
        print_color(f"[Abnormal] Memory Usage: {memory_usage.percent}%", COLOR_RED)
    else:
        print(f"Memory Usage: {memory_usage.percent}%")


if __name__ == "__main__":
    reference = collect()
    print("Start Memory Usage Monitoring...")
    threshold = reference * 1.05
    print_color(f"Memory Usage Threashold: {threshold}%", COLOR_ORANGE)
    while True:
        usage_validation(threshold)
        time.sleep(3)
