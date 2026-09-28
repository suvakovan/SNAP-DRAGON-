"""
Energy-based Voice Activity Detection (VAD) module.
"""

from typing import List, Tuple
import numpy as np
from lecturelens.config import config


def compute_frame_energy(audio: np.ndarray, frame_length: int = 512) -> np.ndarray:
    """Computes RMS energy per frame."""
    if len(audio) == 0:
        return np.array([], dtype=np.float32)

    num_frames = len(audio) // frame_length
    if num_frames == 0:
        return np.array([np.sqrt(np.mean(audio ** 2))], dtype=np.float32)

    frames = audio[: num_frames * frame_length].reshape(num_frames, frame_length)
    rms = np.sqrt(np.mean(frames ** 2, axis=1))
    return rms.astype(np.float32)


def is_speech(
    audio: np.ndarray, threshold: float = config.vad_threshold, sample_rate: int = config.sample_rate
) -> bool:
    """Quick check whether audio buffer contains voice activity above threshold."""
    if len(audio) == 0:
        return False
    rms = np.sqrt(np.mean(audio ** 2))
    return bool(rms >= threshold)


def detect_speech_spans(
    audio: np.ndarray,
    sample_rate: int = config.sample_rate,
    threshold: float = config.vad_threshold,
    frame_ms: int = 30,
    min_silence_ms: int = 300,
) -> List[Tuple[float, float]]:
    """
    Detects continuous speech time spans [(start_sec, end_sec)] in audio array.
    """
    if len(audio) == 0:
        return []

    frame_length = int(sample_rate * (frame_ms / 1000.0))
    if frame_length <= 0:
        frame_length = 512

    min_silence_frames = max(1, int(min_silence_ms / frame_ms))

    energies = compute_frame_energy(audio, frame_length=frame_length)
    speech_frames = energies >= threshold

    spans: List[Tuple[float, float]] = []
    in_speech = False
    start_frame = 0
    silence_count = 0

    for i, active in enumerate(speech_frames):
        if active:
            if not in_speech:
                in_speech = True
                start_frame = i
            silence_count = 0
        else:
            if in_speech:
                silence_count += 1
                if silence_count >= min_silence_frames:
                    end_frame = i - silence_count + 1
                    start_sec = (start_frame * frame_length) / float(sample_rate)
                    end_sec = (end_frame * frame_length) / float(sample_rate)
                    if end_sec > start_sec:
                        spans.append((start_sec, end_sec))
                    in_speech = False
                    silence_count = 0

    if in_speech:
        end_frame = len(speech_frames)
        start_sec = (start_frame * frame_length) / float(sample_rate)
        end_sec = (end_frame * frame_length) / float(sample_rate)
        if end_sec > start_sec:
            spans.append((start_sec, end_sec))

    return spans
