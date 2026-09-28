"""
Background sampler for CPU and NPU utilization during pipeline workloads.
"""

import time
import threading
from typing import List, Dict, Any
import psutil


class NPUSampler:
    def __init__(self, interval_sec: float = 0.5):
        self.interval_sec = interval_sec
        self._stop_event = threading.Event()
        self._thread = None
        self.cpu_samples: List[float] = []
        self.ram_samples_mb: List[float] = []

    def start(self):
        self.cpu_samples.clear()
        self.ram_samples_mb.clear()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def _sample_loop(self):
        while not self._stop_event.is_set():
            cpu_pct = psutil.cpu_percent(interval=None)
            ram_mb = psutil.Process().memory_info().rss / (1024 * 1024)
            self.cpu_samples.append(cpu_pct)
            self.ram_samples_mb.append(ram_mb)
            time.sleep(self.interval_sec)

    def stop() -> Dict[str, Any]:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

        mean_cpu = float(sum(self.cpu_samples) / max(len(self.cpu_samples), 1)) if self.cpu_samples else 0.0
        peak_cpu = float(max(self.cpu_samples)) if self.cpu_samples else 0.0
        mean_ram = float(sum(self.ram_samples_mb) / max(len(self.ram_samples_mb), 1)) if self.ram_samples_mb else 0.0
        peak_ram = float(max(self.ram_samples_mb)) if self.ram_samples_mb else 0.0

        return {
            "mean_cpu_percent": round(mean_cpu, 2),
            "peak_cpu_percent": round(peak_cpu, 2),
            "mean_ram_mb": round(mean_ram, 2),
            "peak_ram_mb": round(peak_ram, 2),
            "num_samples": len(self.cpu_samples)
        }
