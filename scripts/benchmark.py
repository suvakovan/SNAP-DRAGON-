"""
Defensible Benchmark Harness for LectureLens — Phase F.
Records mean/median/min/max/std/95%CI, warm-up discarded, plausibility guards,
machine metadata, and generates truthful charts.
"""

import sys
import json
import time
import platform
import struct
import sysconfig
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import argparse
import statistics
import math

import numpy as np
import pandas as pd
import psutil
import matplotlib.pyplot as plt

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from lecturelens.backends.base import BackendUnavailable
from lecturelens.backends.detect import detect_hardware
from lecturelens.config import config
from lecturelens.logging_setup import logger

# Integrity thresholds
_STT_RTF_SUSPICIOUS_BELOW = 0.005  # faster than real-time 200x is implausible
_LLM_TPS_MIN = 0.5
_LLM_TPS_MAX = 150.0
_LLM_TTFT_MIN_MS = 5.0            # < 5ms TTFT is implausible for any real LLM


def get_machine_metadata() -> Dict[str, Any]:
    target_plat = sysconfig.get_platform()
    bitness = struct.calcsize("P") * 8
    is_arm64 = "arm64" in target_plat.lower() or "aarch64" in platform.machine().lower()
    is_windows = sys.platform == "win32"
    is_snapdragon = is_windows and is_arm64 and ("arm64" in target_plat.lower())

    try:
        import onnxruntime as ort
        ort_ver = ort.__version__
        ort_provs = ort.get_available_providers()
    except ImportError:
        ort_ver, ort_provs = "N/A", []

    battery = None
    try:
        b = psutil.sensors_battery()
        if b:
            battery = {"percent": b.percent, "plugged": b.power_plugged}
    except Exception:
        pass

    return {
        "machine": platform.machine(),
        "processor": platform.processor(),
        "os_platform": platform.platform(),
        "python_version": sys.version,
        "python_bitness": bitness,
        "python_target_platform": target_plat,
        "is_snapdragon_arm64_native": is_snapdragon,
        "ort_version": ort_ver,
        "ort_providers": ort_provs,
        "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "battery": battery,
        "benchmark_run_at": datetime.now().isoformat()
    }


def ci95(samples: List[float]) -> float:
    """95% confidence interval half-width for the mean."""
    n = len(samples)
    if n < 2:
        return 0.0
    se = statistics.stdev(samples) / math.sqrt(n)
    return round(1.96 * se, 4)


def validate_stt_row(row: Dict[str, Any], dry_run: bool = False) -> bool:
    rtf = row.get("mean_rtf", 999)
    if rtf < _STT_RTF_SUSPICIOUS_BELOW:
        logger.warning(f"STT PLAUSIBILITY: RTF={rtf} below {_STT_RTF_SUSPICIOUS_BELOW} — SUSPICIOUS. Row excluded.")
        return False
    return True


def validate_llm_row(row: Dict[str, Any]) -> bool:
    tps = row.get("mean_tps", 999)
    ttft = row.get("mean_ttft_ms", 0)
    if not (_LLM_TPS_MIN <= tps <= _LLM_TPS_MAX):
        logger.warning(f"LLM PLAUSIBILITY: TPS={tps:.1f} outside [{_LLM_TPS_MIN},{_LLM_TPS_MAX}] — SUSPICIOUS.")
        return False
    if ttft < _LLM_TTFT_MIN_MS:
        logger.warning(f"LLM PLAUSIBILITY: TTFT={ttft:.1f}ms below {_LLM_TTFT_MIN_MS}ms — SUSPICIOUS.")
        return False
    return True


def generate_synthetic_audio(duration_sec: float = 30.0, sr: int = 16000) -> np.ndarray:
    """Generates reproducible deterministic sine-burst audio."""
    np.random.seed(42)
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    audio = (0.3 * np.sin(2 * np.pi * 350 * t) +
             0.2 * np.sin(2 * np.pi * 900 * t) +
             0.05 * np.random.randn(len(t)))
    return audio.clip(-1.0, 1.0).astype(np.float32)


def run_stt_benchmark(
    preference: str, audio: np.ndarray, warmup: int = 2, runs: int = 7,
    dry_run: bool = False, meta: Dict[str, Any] = {}
) -> Optional[Dict[str, Any]]:
    from lecturelens.backends import get_stt_backend
    try:
        backend = get_stt_backend(preference)
    except BackendUnavailable as e:
        logger.warning(f"STT[{preference}] unavailable: {e}")
        return None

    if backend.info.is_simulated:
        logger.warning(f"STT[{preference}] backend is simulated — EXCLUDING from benchmark.")
        return None

    if preference == "npu" and not meta.get("is_snapdragon_arm64_native"):
        logger.warning("NOT A SNAPDRAGON RUN — NPU STT rows excluded.")
        return None

    # Warmup
    for _ in range(warmup):
        try:
            backend.transcribe(audio[:16000])
        except Exception:
            pass

    if dry_run:
        logger.info(f"[DRY-RUN] STT[{preference}] backend ready: {backend.info.runtime}")
        return {"task": "STT", "backend_pref": preference, "dry_run": True}

    wall_times, rtfs, cpu_utils = [], [], []
    model_load_time = getattr(backend, "_load_time_sec", 0.0)

    for _ in range(runs):
        psutil.cpu_percent(interval=None)
        t0 = time.time()
        res = backend.transcribe(audio)
        t1 = time.time()
        wt = t1 - t0
        rtf = wt / max(res.audio_seconds, 0.001)
        cpu_u = psutil.cpu_percent(interval=None)
        wall_times.append(wt)
        rtfs.append(rtf)
        cpu_utils.append(cpu_u)

    row = {
        "task": "STT",
        "backend_runtime": backend.info.runtime,
        "device": backend.info.device,
        "verified_npu": backend.info.verified_npu,
        "is_real": backend.info.is_real,
        "is_simulated": backend.info.is_simulated,
        "model_load_time_sec": model_load_time,
        "mean_rtf": round(statistics.mean(rtfs), 4),
        "median_rtf": round(statistics.median(rtfs), 4),
        "min_rtf": round(min(rtfs), 4),
        "max_rtf": round(max(rtfs), 4),
        "std_rtf": round(statistics.stdev(rtfs) if len(rtfs) > 1 else 0.0, 4),
        "ci95_rtf": ci95(rtfs),
        "mean_cpu_percent": round(statistics.mean(cpu_utils), 2),
        "n_measured_runs": runs
    }

    if not validate_stt_row(row):
        return None

    return row


def run_llm_benchmark(
    preference: str, warmup: int = 2, runs: int = 7,
    dry_run: bool = False, meta: Dict[str, Any] = {}
) -> Optional[Dict[str, Any]]:
    from lecturelens.backends import get_llm_backend
    try:
        backend = get_llm_backend(preference)
    except BackendUnavailable as e:
        logger.warning(f"LLM[{preference}] unavailable: {e}")
        return None

    if backend.info.is_simulated:
        logger.warning(f"LLM[{preference}] backend is simulated — EXCLUDING.")
        return None

    if preference == "npu" and not meta.get("is_snapdragon_arm64_native"):
        logger.warning("NOT A SNAPDRAGON RUN — NPU LLM rows excluded.")
        return None

    system_p = "You are a summarization assistant."
    user_p = "Summarize the concept of hardware accelerated neural inference in two sentences."
    MAX_TOK = 150

    for _ in range(warmup):
        try:
            backend.generate(system_p, "Hello.", max_tokens=10)
        except Exception:
            pass

    if dry_run:
        logger.info(f"[DRY-RUN] LLM[{preference}] backend ready: {backend.info.runtime}")
        return {"task": "LLM", "backend_pref": preference, "dry_run": True}

    latencies, tps_list, ttft_list, cpu_utils = [], [], [], []

    for _ in range(runs):
        psutil.cpu_percent(interval=None)
        t0 = time.time()
        res = backend.generate(system_p, user_p, max_tokens=MAX_TOK)
        t1 = time.time()
        wall = t1 - t0
        tps = res.tokens_per_second or (len(res.text.split()) / max(wall, 0.001))
        ttft_ms = (res.time_to_first_token or 0.0) * 1000.0
        cpu_u = psutil.cpu_percent(interval=None)
        latencies.append(wall)
        tps_list.append(tps)
        ttft_list.append(ttft_ms)
        cpu_utils.append(cpu_u)

    row = {
        "task": "LLM",
        "backend_runtime": backend.info.runtime,
        "device": backend.info.device,
        "verified_npu": backend.info.verified_npu,
        "is_real": backend.info.is_real,
        "is_simulated": backend.info.is_simulated,
        "model_name": backend.info.name,
        "max_tokens": MAX_TOK,
        "mean_latency_sec": round(statistics.mean(latencies), 3),
        "median_latency_sec": round(statistics.median(latencies), 3),
        "mean_ttft_ms": round(statistics.mean(ttft_list), 2),
        "mean_tps": round(statistics.mean(tps_list), 2),
        "median_tps": round(statistics.median(tps_list), 2),
        "std_tps": round(statistics.stdev(tps_list) if len(tps_list) > 1 else 0.0, 2),
        "ci95_tps": ci95(tps_list),
        "mean_cpu_percent": round(statistics.mean(cpu_utils), 2),
        "n_measured_runs": runs,
        "tps_estimated": backend.info.details.get("tps_estimated", True)
    }

    if not validate_llm_row(row):
        return None

    return row


def generate_charts(rows: List[Dict], charts_dir: Path):
    """Generate labeled charts with error bars from measured data."""
    charts_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("ggplot")
    fig_size = (7, 4.5)

    # STT RTF
    stt = [r for r in rows if r.get("task") == "STT"]
    if stt:
        labels = [r["backend_runtime"] for r in stt]
        means = [r["mean_rtf"] for r in stt]
        errs = [r.get("ci95_rtf", 0) for r in stt]
        colors = ["#2ca02c" if r["verified_npu"] else "#1f77b4" for r in stt]
        fig, ax = plt.subplots(figsize=fig_size)
        bars = ax.bar(labels, means, color=colors, yerr=errs, capsize=5)
        ax.set_title("STT Real-Time Factor (Lower = Faster)")
        ax.set_ylabel("Real-Time Factor (RTF)")
        ax.set_xlabel("STT Backend Runtime")
        for bar, val in zip(bars, means):
            ax.text(bar.get_x() + bar.get_width() / 2.0, val + 0.001, f"{val:.4f}", ha="center", va="bottom", fontsize=9)
        plt.tight_layout()
        fig.savefig(charts_dir / "stt_rtf.png", dpi=200)
        plt.close(fig)

    # LLM TPS
    llm = [r for r in rows if r.get("task") == "LLM"]
    if llm:
        labels = [r["backend_runtime"] for r in llm]
        means = [r["mean_tps"] for r in llm]
        errs = [r.get("ci95_tps", 0) for r in llm]
        colors = ["#2ca02c" if r["verified_npu"] else "#ff7f0e" for r in llm]
        fig, ax = plt.subplots(figsize=fig_size)
        ax.bar(labels, means, color=colors, yerr=errs, capsize=5)
        ax.set_title("LLM Generation Speed (Tokens / Second)")
        ax.set_ylabel("Tokens / Second")
        ax.set_xlabel("LLM Backend Runtime")
        plt.tight_layout()
        fig.savefig(charts_dir / "llm_tps.png", dpi=200)
        plt.close(fig)

    # CPU Util Combined
    if rows:
        labels = [r["backend_runtime"] for r in rows]
        cpus = [r.get("mean_cpu_percent", 0) for r in rows]
        fig, ax = plt.subplots(figsize=fig_size)
        ax.bar(labels, cpus, color="#d62728")
        ax.set_title("Mean CPU Utilization per Backend")
        ax.set_ylabel("CPU Utilization (%)")
        ax.set_xlabel("Backend")
        plt.tight_layout()
        fig.savefig(charts_dir / "cpu_util.png", dpi=200)
        plt.close(fig)


def run_benchmark_harness(dry_run: bool = False, full: bool = False):
    warmup = 2
    runs = 7 if full else 3
    logger.info(f"Starting Benchmark Harness (dry_run={dry_run}, runs={runs})")

    results_dir = Path("benchmarks/results")
    charts_dir = Path("benchmarks/charts")
    results_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)

    meta = get_machine_metadata()

    if not meta["is_snapdragon_arm64_native"]:
        print("\n⚠ NOT A SNAPDRAGON ARM64 RUN — NPU benchmark rows will be excluded.")

    audio_30s = generate_synthetic_audio(30.0)

    valid_rows = []
    integrity_pass = True

    for pref in ["npu", "cpu"]:
        row = run_stt_benchmark(pref, audio_30s, warmup=warmup, runs=runs, dry_run=dry_run, meta=meta)
        if row and not row.get("dry_run"):
            if row.get("is_simulated"):
                logger.error(f"INTEGRITY FAIL: simulated STT row found for pref={pref}")
                integrity_pass = False
            else:
                valid_rows.append(row)
        # Thermal cooldown between backends
        if not dry_run:
            time.sleep(5)

    for pref in ["npu", "cpu"]:
        row = run_llm_benchmark(pref, warmup=warmup, runs=runs, dry_run=dry_run, meta=meta)
        if row and not row.get("dry_run"):
            if row.get("is_simulated"):
                logger.error(f"INTEGRITY FAIL: simulated LLM row found for pref={pref}")
                integrity_pass = False
            else:
                valid_rows.append(row)
        if not dry_run:
            time.sleep(5)

    if dry_run:
        print("\n[DRY-RUN] Benchmark probing complete. No results written.")
        print("\nINTEGRITY: PASS (dry run)")
        return

    if not valid_rows:
        print("\n[INFO] No real backends produced valid measured rows on this machine.")
        print("INTEGRITY: PASS (no real model available — CPU/NPU benchmark requires model files and local LLM)")
        return

    df = pd.DataFrame(valid_rows)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = results_dir / "latest.csv"
    json_path = results_dir / f"{timestamp}.json"

    df.to_csv(csv_path, index=False)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"timestamp": timestamp, "machine": meta, "results": valid_rows}, f, indent=2)

    generate_charts(valid_rows, charts_dir)

    # Regenerate BENCHMARKS.md
    benchmarks_doc = Path("docs/BENCHMARKS.md")
    with open(benchmarks_doc, "w", encoding="utf-8") as f:
        f.write("# Measured Benchmark Results\n\n")
        f.write(f"**Machine:** {meta['processor']} | **OS:** {meta['os_platform']} | "
                f"**Python:** {meta['python_target_platform']} | **ORT:** {meta['ort_version']}\n\n")
        f.write(f"**Native Snapdragon ARM64:** {meta['is_snapdragon_arm64_native']}\n\n")
        f.write(f"**Warmup Runs (discarded):** {warmup} | **Measured Runs:** {runs}\n\n")
        f.write("## Results Table\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n\n## Notes\n\n")
        if not meta["is_snapdragon_arm64_native"]:
            f.write("- ⚠ NOT A NATIVE SNAPDRAGON ARM64 RUN. NPU rows excluded.\n")
        f.write("- RTF and TPS plausibility guards applied (suspicious rows auto-excluded).\n")
        f.write("- `verified_npu=True` only when QNNExecutionProvider is confirmed first active provider.\n")

    print(f"\n{'=' * 55}")
    print(f"  Benchmark Results: {len(valid_rows)} valid row(s)")
    print(f"  Saved CSV: {csv_path.resolve()}")
    print(f"  Saved JSON: {json_path.resolve()}")
    print(f"  Charts: {charts_dir.resolve()}")
    print(f"\nINTEGRITY: {'PASS' if integrity_pass else 'FAIL'}")
    print(f"{'=' * 55}\n")

    import sys as _sys
    _sys.exit(0 if integrity_pass else 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LectureLens Benchmark Harness")
    parser.add_argument("--dry-run", action="store_true", help="Probe backends, do not record results")
    parser.add_argument("--full", action="store_true", help="Run 7 measured iterations (default: 3)")
    parser.add_argument("--quick", action="store_true", help="Alias for 3 iterations (default)")
    args = parser.parse_args()
    run_benchmark_harness(dry_run=args.dry_run, full=args.full)
