# LectureLens Offline Execution Proof & Security Guarantee

## 1. Socket Guard Verification Mechanism

LectureLens enforces a strict network isolation policy at runtime after initial setup and model caching.
The validation script `scripts/offline_check.py` monkeypatches Python standard library sockets (`socket.socket.connect` and `socket.getaddrinfo`) to block any non-loopback network calls.

### Verification Command

```powershell
python scripts/offline_check.py
```

Expected Output:

```
Enforcing Strict Offline Socket Guard...
PASS: Pipeline ran 100% offline with 0 cloud network attempts.
```

## 2. Airplane-Mode Demonstration Protocol

To perform a physical airplane-mode demo for judges or video presentation:

1. Download model assets once using `python scripts/download_models.py`.
2. Disable all Wi-Fi and network adapters on your Snapdragon X laptop.
3. Launch LectureLens using `powershell -ExecutionPolicy Bypass -File scripts/run.ps1`.
4. Observe the green **OFFLINE MODE** badge in the sidebar header.
5. Record or process a lecture recording file.
6. Verify transcription, summary, quiz, and flashcards are generated completely on-device.
