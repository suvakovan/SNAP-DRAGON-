"""
Hardware and runtime environment detection for LectureLens.
"""

import os
import sys
import platform
import subprocess
from typing import Dict, Any, List


def detect_hardware() -> Dict[str, Any]:
    """
    Detects local CPU, RAM, OS, ONNX execution providers, Qualcomm QNN presence,
    Foundry Local status, audio input devices, and returns a detailed report.
    """
    report: Dict[str, Any] = {
        "python_version": sys.version.split()[0],
        "machine": platform.machine(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "cpu_name": platform.processor() or "Unknown CPU",
        "cpu_count": os.cpu_count() or 1,
        "ram_gb": None,
        "onnxruntime_installed": False,
        "onnxruntime_version": None,
        "providers": [],
        "qnn_available": False,
        "foundry_available": False,
        "foundry_models": [],
        "audio_input_available": False,
        "audio_devices": [],
        "verdict": "NOT READY",
        "hints": []
    }

    # RAM Detection
    try:
        import psutil
        report["ram_gb"] = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    except Exception as e:
        report["hints"].append(f"psutil check failed: {e}")

    # ONNX Runtime & Providers Detection
    try:
        import onnxruntime as ort
        report["onnxruntime_installed"] = True
        report["onnxruntime_version"] = ort.__version__
        report["providers"] = ort.get_available_providers()
        if "QNNExecutionProvider" in report["providers"]:
            report["qnn_available"] = True
    except ImportError:
        report["hints"].append("onnxruntime is not installed.")
    except Exception as e:
        report["hints"].append(f"ONNX Runtime query error: {e}")

    # Foundry Local Detection
    try:
        res = subprocess.run(["foundry", "--version"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            report["foundry_available"] = True
            # Attempt to list models
            res_m = subprocess.run(["foundry", "model", "list"], capture_output=True, text=True, timeout=5)
            if res_m.returncode == 0:
                report["foundry_models"] = [line.strip() for line in res_m.stdout.splitlines() if line.strip()]
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        report["hints"].append("Foundry CLI not found or inactive. Local LLM fallback will be used.")

    # Audio Input Detection
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devs = [
            {"index": i, "name": d["name"], "channels": d["max_input_channels"]}
            for i, d in enumerate(devices) if d["max_input_channels"] > 0
        ]
        report["audio_devices"] = input_devs
        if len(input_devs) > 0:
            report["audio_input_available"] = True
        else:
            report["hints"].append("No audio input (microphone) devices detected.")
    except Exception as e:
        report["hints"].append(f"Audio device query notice: {e}")

    # Determine Verdict
    if report["qnn_available"] and report["foundry_available"]:
        report["verdict"] = "NPU READY"
    elif report["onnxruntime_installed"]:
        report["verdict"] = "PARTIAL (CPU fallback available)"
        if not report["qnn_available"]:
            report["hints"].append("QNNExecutionProvider not active; app will run STT/embeddings on CPU.")
        if not report["foundry_available"]:
            report["hints"].append("Foundry Local not active; app will use local CPU LLM endpoint/fallback.")
    else:
        report["verdict"] = "NOT READY"

    return report


if __name__ == "__main__":
    from rich import print as rprint
    rprint(detect_hardware())
