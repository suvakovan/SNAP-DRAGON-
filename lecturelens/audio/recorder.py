"""
Thread-safe microphone audio recorder using sounddevice.
"""

import argparse
import queue
import time
from typing import List, Dict, Any, Optional
import numpy as np
import sounddevice as sd
import soundfile as sf
from lecturelens.config import config
from lecturelens.logging_setup import logger


def list_devices() -> List[Dict[str, Any]]:
    """List available audio input devices."""
    try:
        devices = sd.query_devices()
        return [
            {"index": i, "name": d["name"], "channels": d["max_input_channels"], "sample_rate": d["default_samplerate"]}
            for i, d in enumerate(devices) if d["max_input_channels"] > 0
        ]
    except Exception as e:
        logger.warning(f"Error querying audio devices: {e}")
        return []


class MicRecorder:
    """
    Microphone recorder running background stream, feeding frame buffers into a queue.
    """

    def __init__(self, sample_rate: int = config.sample_rate, device_index: Optional[int] = None):
        self.sample_rate = sample_rate
        self.device_index = device_index
        self.queue: queue.Queue[np.ndarray] = queue.Queue()
        self.stream: Optional[sd.InputStream] = None
        self._active: bool = False
        self.recorded_buffer: List[np.ndarray] = []

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info: Any, status: Any) -> None:
        """Callback from sounddevice InputStream."""
        if status:
            logger.warning(f"Audio stream status notice: {status}")
        mono_frame = np.mean(indata, axis=1).astype(np.float32)
        self.queue.put(mono_frame)
        self.recorded_buffer.append(mono_frame)

    def start(self) -> None:
        """Start microphone recording stream."""
        if self._active:
            return

        devices = list_devices()
        if not devices:
            raise RuntimeError("No microphone input devices available.")

        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                device=self.device_index,
                callback=self._audio_callback
            )
            self.stream.start()
            self._active = True
            logger.info("Microphone recording started.")
        except Exception as e:
            self._active = False
            logger.error(f"Failed to start microphone stream: {e}")
            raise RuntimeError(f"Microphone permission or hardware error: {e}")

    def stop(self) -> np.ndarray:
        """Stop microphone recording stream and return accumulated full audio array."""
        if not self._active or self.stream is None:
            return np.array([], dtype=np.float32)

        self._active = False
        self.stream.stop()
        self.stream.close()
        self.stream = None
        logger.info("Microphone recording stopped.")

        if self.recorded_buffer:
            full_audio = np.concatenate(self.recorded_buffer, axis=0)
        else:
            full_audio = np.array([], dtype=np.float32)

        return full_audio

    def is_active(self) -> bool:
        """Check if stream is active."""
        return self._active

    def read_chunk(self, seconds: float = 30.0) -> np.ndarray:
        """Read accumulated frames from queue corresponding to `seconds` of audio."""
        target_samples = int(seconds * self.sample_rate)
        chunk_frames = []
        collected = 0

        while collected < target_samples and not self.queue.empty():
            try:
                frame = self.queue.get_nowait()
                chunk_frames.append(frame)
                collected += len(frame)
            except queue.Empty:
                break

        if not chunk_frames:
            return np.array([], dtype=np.float32)

        return np.concatenate(chunk_frames, axis=0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record audio from microphone to WAV file.")
    parser.add_argument("--seconds", type=float, default=5.0, help="Duration to record in seconds")
    parser.add_argument("--out", type=str, default="sample.wav", help="Output file path")
    args = parser.parse_args()

    print(f"Recording {args.seconds} seconds of audio...")
    recorder = MicRecorder()
    try:
        recorder.start()
        time.sleep(args.seconds)
        audio_data = recorder.stop()
        if len(audio_data) > 0:
            sf.write(args.out, audio_data, config.sample_rate)
            print(f"Saved recording to {args.out} ({len(audio_data)} samples)")
        else:
            print("No audio captured.")
    except Exception as err:
        print(f"Recording failed: {err}")
