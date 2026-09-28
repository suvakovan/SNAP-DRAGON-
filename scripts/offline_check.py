"""
Offline Network Guard Verification Script.
Monkeypatches socket to intercept and block any external non-loopback network requests.
"""

import os
import sys
import socket
from pathlib import Path

# Set offline environment variables
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from rich.console import Console
console = Console()

_original_connect = socket.socket.connect
_original_getaddrinfo = socket.getaddrinfo

blocked_attempts = []


def _is_loopback(host: str) -> bool:
    """Check if address is localhost / loopback."""
    return host in ("127.0.0.1", "localhost", "::1", "0.0.0.0")


def guarded_connect(self, address):
    host = address[0] if isinstance(address, tuple) else address
    if not _is_loopback(str(host)):
        msg = f"Network Connection Attempt Blocked: {address}"
        blocked_attempts.append(msg)
        raise RuntimeError(f"OFFLINE VIOLATION: {msg}")
    return _original_connect(self, address)


def guarded_getaddrinfo(host, port, *args, **kwargs):
    if not _is_loopback(str(host)):
        msg = f"DNS Lookup Attempt Blocked: {host}"
        blocked_attempts.append(msg)
        raise RuntimeError(f"OFFLINE VIOLATION: {msg}")
    return _original_getaddrinfo(host, port, *args, **kwargs)


def run_offline_check():
    """Applies socket guard and executes end-to-end pipeline."""
    console.print("[bold blue]Enforcing Strict Offline Socket Guard...[/bold blue]")

    # Monkeypatch socket
    socket.socket.connect = guarded_connect
    socket.getaddrinfo = guarded_getaddrinfo

    from lecturelens.audio.preprocess import load_audio
    from lecturelens.pipeline.session import run_full_pipeline
    import numpy as np

    try:
        # Run full pipeline with synthetic audio
        audio = np.random.randn(16000 * 3).astype(np.float32)
        session = run_full_pipeline(audio, title="Offline Verification Lecture", stt_preference="cpu", llm_preference="cpu")

        if len(blocked_attempts) == 0:
            console.print("\n[bold green]PASS: Pipeline ran 100% offline with 0 cloud network attempts.[/bold green]")
            console.print(f"Session ID: {session.metadata.id}")
            return True
        else:
            console.print(f"\n[bold red]FAIL: {len(blocked_attempts)} network requests attempted.[/bold red]")
            for b in blocked_attempts:
                console.print(f"  • {b}")
            return False
    except Exception as e:
        console.print(f"\n[bold red]FAIL: Exception occurred during offline execution: {e}[/bold red]")
        return False


if __name__ == "__main__":
    success = run_offline_check()
    sys.exit(0 if success else 1)
