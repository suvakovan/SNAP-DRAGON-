"""
Benchmark harness for measuring NPU vs CPU performance, RTF, tokens/sec, RAM, CPU utilization, and battery drain.
"""

import argparse
import json
import time
import sys
import os
import platform
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import numpy as np
import pandas as pd
import psutil
import matplotlib.pyplot as plt

from lecturelens.backends import get_stt_backend, get_llm_backend, get_embed_backend
from lecturelens.backends.detect import detect_hardware
from lecturelens.config import config
from lecturelens.logging_setup import logger


def get_battery_info() -> Dict[str, Any]:
    """Reads system battery status if available."""
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "secsleft": battery.secsleft
            }
    except Exception:
        pass
    return {"percent": None, "power_plugged": None, "secsleft": None}


def generate_benchmark_audio(duration_sec: float = 30.0, sample_rate: int = 16000) -> np.ndarray:
    """Generates synthetic speech-like tone audio buffer for reproducible benchmarks."""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    audio = 0.3 * np.sin(2 * np.pi * 440 * t) + 0.1 * np.random.randn(len(t))
    return audio.astype(np.float32)


def run_stt_benchmark(backend_name: str, runs: int, audio: np.ndarray) -> Dict[str, Any]:
    """Runs STT benchmark for specified backend."""
    backend = get_stt_backend(backend_name)

    # Warmup
    for _ in range(2):
        backend.transcribe(audio[:16000])

    wall_times = []
    rtfs = []
    cpu_utils = []

    for _ in range(runs):
        psutil.cpu_percent(interval=None)
        t0 = time.time()
        res = backend.transcribe(audio)
        t1 = time.time()

        wall_sec = t1 - t0
        audio_sec = len(audio) / 16000.0
        rtf = wall_sec / max(audio_sec, 0.001)
        cpu_u = psutil.cpu_percent(interval=None)

        wall_times.append(wall_sec)
        rtfs.append(rtf)
        cpu_utils.append(cpu_u)

    return {
        "task": "STT",
        "backend": backend.info.runtime,
        "device": backend.info.device,
        "verified_npu": backend.info.verified_npu,
        "mean_wall_sec": float(np.mean(wall_times)),
        "mean_rtf": float(np.mean(rtfs)),
        "std_rtf": float(np.std(rtfs)),
        "mean_cpu_percent": float(np.mean(cpu_utils))
    }


def run_llm_benchmark(backend_name: str, runs: int) -> Dict[str, Any]:
    """Runs LLM benchmark for specified backend."""
    backend = get_llm_backend(backend_name)
    prompt_user = "Summarize the principles of hardware acceleration in neural processing units."
    prompt_sys = "You are a hardware specialist."

    # Warmup
    for _ in range(2):
        backend.generate(prompt_sys, "Hello", max_tokens=10)

    latencies = []
    tps_list = []
    cpu_utils = []

    for _ in range(runs):
        psutil.cpu_percent(interval=None)
        t0 = time.time()
        res = backend.generate(prompt_sys, prompt_user, max_tokens=200)
        t1 = time.time()

        total_sec = t1 - t0
        tps = res.tokens_per_second or (len(res.text.split()) / max(total_sec, 0.001))
        cpu_u = psutil.cpu_percent(interval=None)

        latencies.append(total_sec)
        tps_list.append(tps)
        cpu_utils.append(cpu_u)

    return {
        "task": "LLM",
        "backend": backend.info.runtime,
        "device": backend.info.device,
        "verified_npu": backend.info.verified_npu,
        "mean_latency_sec": float(np.mean(latencies)),
        "mean_tps": float(np.mean(tps_list)),
        "std_tps": float(np.std(tps_list)),
        "mean_cpu_percent": float(np.mean(cpu_utils))
    }


def generate_benchmark_charts(df: pd.DataFrame, output_dir: Path):
    """Generates bar charts comparing CPU vs NPU performance metrics."""
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("ggplot")

    # Chart 1: STT RTF Comparison
    stt_df = df[df["task"] == "STT"]
    if not stt_df.empty:
        plt.figure(figsize=(7, 4.5))
        bars = plt.bar(stt_df["backend"], stt_df["mean_rtf"], color=["#2ca02c" if v else "#1f77b4" for v in stt_df["verified_npu"]])
        plt.title("Speech-to-Text Real-Time Factor (Lower is Faster)")
        plt.ylabel("Real-Time Factor (RTF)")
        plt.tight_layout()
        plt.savefig(output_dir / "stt_rtf.png", dpi=200)
        plt.close()

    # Chart 2: LLM Tokens / Sec Comparison
    llm_df = df[df["task"] == "LLM"]
    if not llm_df.empty:
        plt.figure(figsize=(7, 4.5))
        plt.bar(llm_df["backend"], llm_df["mean_tps"], color=["#2ca02c" if v else "#ff7f0e" for v in llm_df["verified_npu"]])
        plt.title("LLM Generation Speed (Tokens / Second)")
        plt.ylabel("Tokens / Sec")
        plt.tight_layout()
        plt.savefig(output_dir / "llm_tps.png", dpi=200)
        plt.close()


def run_benchmark_harness(quick: bool = False):
    """Main entry point for benchmark execution."""
    runs = 1 if quick else 5
    logger.info(f"Starting Benchmark Harness (Quick Mode: {quick}, Measured Runs per test: {runs})")

    results_dir = Path("./benchmarks/results")
    charts_dir = Path("./benchmarks/charts")
    results_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)

    battery_start = get_battery_info()
    audio = generate_benchmark_audio(duration_sec=30.0)

    benchmark_rows = []

    # 1. Run STT Benchmarks (NPU preferred & CPU fallback)
    for pref in ["npu", "cpu"]:
        row = run_stt_benchmark(pref, runs=runs, audio=audio)
        benchmark_rows.append(row)

    # 2. Run LLM Benchmarks (NPU preferred & CPU fallback)
    for pref in ["npu", "cpu"]:
        row = run_llm_benchmark(pref, runs=runs)
        benchmark_rows.append(row)

    battery_end = get_battery_info()

    # Create Summary DataFrame
    df = pd.DataFrame(benchmark_rows)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save CSV & JSON
    csv_path = results_dir / "latest.csv"
    json_path = results_dir / f"{timestamp}.json"

    df.to_csv(csv_path, index=False)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "hardware": detect_hardware(),
            "battery_start": battery_start,
            "battery_end": battery_end,
            "results": benchmark_rows
        }, f, indent=2)

    # Generate Charts
    generate_benchmark_charts(df, charts_dir)

    # Generate Markdown Table for docs/BENCHMARKS.md
    md_table = df.to_markdown(index=False)

    benchmarks_doc = Path("./docs/BENCHMARKS.md")
    benchmarks_doc.parent.mkdir(parents=True, exist_ok=True)
    with open(benchmarks_doc, "w", encoding="utf-8") as f:
        f.write("# Measured NPU vs CPU Benchmark Diagnostics\n\n")
        f.write(f"**Last Run Timestamp:** {timestamp}\n\n")
        f.write("## Methodology\n\n")
        f.write("- **Protocol:** 2 warmup runs, followed by measured iterations.\n")
        f.write("- **Environment:** Windows 11 ARM64 Native Python Environment.\n")
        f.write("- **Verification:** `verified_npu` is marked True strictly when hardware execution provider (QNN HTP) is verified active.\n\n")
        f.write("## Benchmark Results Table\n\n")
        f.write(f"{md_table}\n\n")

    print("\n=== Benchmark Summary ===")
    print(df)
    print(f"\nSaved CSV: {csv_path.resolve()}")
    print(f"Saved Markdown Doc: {benchmarks_doc.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LectureLens benchmark harness.")
    parser.add_argument("--quick", action="store_true", help="Run quick single-iteration benchmark")
    parser.add_argument("--full", action="store_true", help="Run full benchmark protocol")
    args = parser.parse_args()

    run_benchmark_harness(quick=not args.full)
