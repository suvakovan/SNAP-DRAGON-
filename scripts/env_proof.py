"""
Environment Truth & Hardware Verification Script.
Proves python architecture, OS build, CPU model, ORT execution providers,
NPU availability, and battery state, writing docs/env_proof.json.
"""

import json
import os
import platform
import struct
import sys
import sysconfig
import subprocess
from pathlib import Path
from typing import Dict, Any

import psutil

# Windows registry access
if sys.platform == "win32":
    import winreg
else:
    winreg = None


def get_registry_value(key_path: str, value_name: str) -> str:
    """Reads a string value from Windows registry."""
    if not winreg:
        return "N/A"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            val, _ = winreg.QueryValueEx(key, value_name)
            return str(val)
    except Exception as e:
        return f"Error: {e}"


def run_command_safe(cmd: list) -> str:
    """Safely executes shell command and captures stdout."""
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return res.stdout.strip() or res.stderr.strip() or "No output"
    except Exception as e:
        return f"Execution error: {e}"


def generate_env_proof() -> Dict[str, Any]:
    """Collects comprehensive environment metadata."""
    machine = platform.machine()
    processor = platform.processor()
    plat_str = platform.platform()
    sys_version = sys.version
    bitness = struct.calcsize("P") * 8
    target_platform = sysconfig.get_platform()

    is_arm64_python = "arm64" in target_platform.lower() or "aarch64" in machine.lower()
    is_windows = sys.platform == "win32"
    is_snapdragon_arm64_native = is_windows and ("arm64" in machine.lower() or "aarch64" in machine.lower()) and is_arm64_python

    # Windows OS metadata
    win_product_name = get_registry_value(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "ProductName")
    win_display_version = get_registry_value(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "DisplayVersion")
    cpu_name = get_registry_value(r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "ProcessorNameString")

    # Memory
    mem = psutil.virtual_memory()

    # ONNX Runtime Providers
    ort_version = "Not Installed"
    ort_providers = []
    try:
        import onnxruntime as ort
        ort_version = ort.__version__
        ort_providers = ort.get_available_providers()
    except ImportError:
        pass

    # Qualcomm AI Hub Models
    qai_hub_version = "Not Installed"
    try:
        import qai_hub_models
        qai_hub_version = getattr(qai_hub_models, "__version__", "Installed")
    except ImportError:
        pass

    # Foundry Local status
    foundry_ver = run_command_safe(["foundry", "--version"])
    foundry_status = run_command_safe(["foundry", "service", "status"])

    # Ollama / llama.cpp status
    ollama_ver = run_command_safe(["ollama", "--version"])
    llama_ver = run_command_safe(["llama-server", "--version"])

    # Power plan
    power_plan = run_command_safe(["powercfg", "/getactivescheme"])

    # Battery State
    battery_info = {"percent": None, "power_plugged": None, "secsleft": None}
    try:
        b = psutil.sensors_battery()
        if b:
            battery_info = {
                "percent": b.percent,
                "power_plugged": b.power_plugged,
                "secsleft": b.secsleft
            }
    except Exception:
        pass

    # Typeperf NPU counters check
    npu_counters = run_command_safe(["cmd", "/c", "typeperf -q | findstr /i npu"])

    proof_data = {
        "timestamp": platform.node(),
        "is_snapdragon_arm64_native": is_snapdragon_arm64_native,
        "platform": {
            "machine": machine,
            "processor": processor,
            "platform_string": plat_str,
            "os_product_name": win_product_name,
            "os_display_version": win_display_version,
            "cpu_name": cpu_name,
        },
        "python": {
            "version": sys_version,
            "bitness": bitness,
            "target_platform": target_platform,
            "is_arm64_build": is_arm64_python
        },
        "hardware_resources": {
            "ram_total_gb": round(mem.total / (1024 ** 3), 2),
            "ram_available_gb": round(mem.available / (1024 ** 3), 2),
            "battery": battery_info,
            "power_plan": power_plan
        },
        "runtimes": {
            "onnxruntime_version": ort_version,
            "onnxruntime_providers": ort_providers,
            "qai_hub_models_version": qai_hub_version,
            "foundry_version": foundry_ver,
            "foundry_status": foundry_status,
            "ollama_version": ollama_ver,
            "llama_server_version": llama_ver
        },
        "npu_performance_counters": npu_counters
    }

    return proof_data


def print_and_save_proof():
    proof = generate_env_proof()
    docs_dir = Path("docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    out_file = docs_dir / "env_proof.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(proof, f, indent=2)

    print("\n" + "=" * 60)
    print("      LECTURELENS ENVIRONMENT TRUTH PROOF")
    print("=" * 60)
    print(f"Native Snapdragon ARM64: {proof['is_snapdragon_arm64_native']}")
    print(f"Machine:                {proof['platform']['machine']} ({proof['platform']['cpu_name']})")
    print(f"OS Build:               {proof['platform']['os_product_name']} ({proof['platform']['os_display_version']})")
    print(f"Python Platform:        {proof['python']['target_platform']} ({proof['python']['bitness']}-bit)")
    print(f"RAM Total / Available:  {proof['hardware_resources']['ram_total_gb']} GB / {proof['hardware_resources']['ram_available_gb']} GB")
    print(f"ORT Providers:          {proof['runtimes']['onnxruntime_providers']}")
    print(f"Foundry Service:        {proof['runtimes']['foundry_status']}")
    print(f"Ollama Version:         {proof['runtimes']['ollama_version']}")
    print(f"Saved JSON Proof:       {out_file.resolve()}")
    print("=" * 60)

    if not proof['is_snapdragon_arm64_native']:
        print("\n [WARNING] NOT A NATIVE SNAPDRAGON ARM64 RUN.")
        print("  NPU benchmarks will be marked UNVERIFIED / CPU fallback.\n")


if __name__ == "__main__":
    print_and_save_proof()
