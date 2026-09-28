"""
Script to check system environment, ONNX providers, hardware, and save report to docs/env_report.json.
"""

import json
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from rich.console import Console
from rich.table import Table

from lecturelens.backends.detect import detect_hardware

console = Console()


def run_check() -> dict:
    console.print("[bold blue]Checking LectureLens Target Environment...[/bold blue]\n")
    report = detect_hardware()

    table = Table(title="LectureLens Environment Diagnostics")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Detected Value", style="magenta")

    table.add_row("Python Version", report["python_version"])
    table.add_row("Architecture", report["machine"])
    table.add_row("OS System / Release", f"{report['system']} {report['release']} (Build: {report['version']})")
    table.add_row("CPU Model", str(report["cpu_name"]))
    table.add_row("CPU Cores / RAM", f"{report['cpu_count']} cores / {report['ram_gb']} GB")
    table.add_row("ONNX Runtime", f"{report['onnxruntime_version'] if report['onnxruntime_installed'] else 'Not Installed'}")
    table.add_row("ORT Providers", ", ".join(report["providers"]) if report["providers"] else "None")
    table.add_row("QNN (NPU) Execution Provider", "[green]PRESENT[/green]" if report["qnn_available"] else "[yellow]ABSENT (CPU fallback will be used)[/yellow]")
    table.add_row("Foundry Local Service", "[green]AVAILABLE[/green]" if report["foundry_available"] else "[yellow]NOT DETECTED (CPU LLM fallback active)[/yellow]")
    table.add_row("Audio Input Devices", f"{len(report['audio_devices'])} device(s) found")

    verdict_color = "green" if report["verdict"] == "NPU READY" else "yellow" if "PARTIAL" in report["verdict"] else "red"
    table.add_row("Overall Verdict", f"[{verdict_color}]{report['verdict']}[/{verdict_color}]")

    console.print(table)

    if report["hints"]:
        console.print("\n[bold yellow]System Notes & Recommendations:[/bold yellow]")
        for hint in report["hints"]:
            console.print(f"  • {hint}")

    # Ensure docs directory exists
    docs_dir = Path("./docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    report_file = docs_dir / "env_report.json"

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    console.print(f"\n[green]Saved report to {report_file.resolve()}[/green]")
    return report


if __name__ == "__main__":
    run_check()
