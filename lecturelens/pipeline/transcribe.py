"""
Audio transcription pipeline with VAD filtering, overlap deduplication, and timing metrics.
"""

import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator, Tuple
import numpy as np

from lecturelens.backends import get_stt_backend
from lecturelens.backends.base import STTBackend, STTResult
from lecturelens.audio.preprocess import load_audio
from lecturelens.audio.chunker import chunk_audio
from lecturelens.audio.vad import is_speech
from lecturelens.config import config
from lecturelens.logging_setup import logger


def deduplicate_overlap_text(prev_text: str, current_text: str) -> str:
    """Removes trailing duplicate words between consecutive overlapping chunks."""
    if not prev_text or not current_text:
        return current_text

    prev_words = prev_text.strip().split()
    curr_words = current_text.strip().split()

    # Find longest overlapping word sequence (up to 5 words)
    max_overlap = min(5, len(prev_words), len(curr_words))
    for k in range(max_overlap, 0, -1):
        if prev_words[-k:] == curr_words[:k]:
            return " ".join(curr_words[k:])

    return current_text


def transcribe_audio_array(
    audio: np.ndarray,
    backend: Optional[STTBackend] = None,
    sample_rate: int = config.sample_rate,
    language: Optional[str] = config.stt_language
) -> STTResult:
    """Transcribes an in-memory 1D float32 audio array."""
    if backend is None:
        backend = get_stt_backend(config.stt_backend_preference)

    start_total = time.time()
    audio_seconds = len(audio) / float(sample_rate) if len(audio) > 0 else 0.0

    if audio_seconds == 0:
        return STTResult(
            text="",
            segments=[],
            language=language,
            audio_seconds=0.0,
            wall_seconds=0.0,
            rtf=0.0
        )

    raw_chunks = chunk_audio(audio, sample_rate=sample_rate)
    segments: List[Dict[str, Any]] = []
    full_text_parts: List[str] = []
    last_text = ""

    for start_sec, end_sec, chunk_data in raw_chunks:
        # VAD filtering: skip silence
        if not is_speech(chunk_data, threshold=config.vad_threshold, sample_rate=sample_rate):
            logger.debug(f"Skipping silent chunk from {start_sec:.2f}s to {end_sec:.2f}s")
            continue

        res = backend.transcribe(chunk_data, sample_rate=sample_rate, language=language)
        if res.text.strip():
            dedup_text = deduplicate_overlap_text(last_text, res.text.strip())
            if dedup_text:
                full_text_parts.append(dedup_text)
                segments.append({"start": round(start_sec, 2), "end": round(end_sec, 2), "text": dedup_text})
                last_text = dedup_text

    full_text = " ".join(full_text_parts)
    wall_seconds = time.time() - start_total
    rtf = wall_seconds / max(audio_seconds, 0.001)

    return STTResult(
        text=full_text,
        segments=segments,
        language=language,
        audio_seconds=audio_seconds,
        wall_seconds=wall_seconds,
        rtf=rtf
    )


def transcribe_file(
    file_path: str, backend_preference: str = "auto", language: Optional[str] = config.stt_language
) -> Tuple[STTResult, STTBackend]:
    """Loads audio file and performs complete transcription."""
    audio = load_audio(file_path, target_sample_rate=config.sample_rate)
    backend = get_stt_backend(backend_preference)
    result = transcribe_audio_array(audio, backend=backend, sample_rate=config.sample_rate, language=language)
    return result, backend


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file with LectureLens STT backend.")
    parser.add_argument("--file", type=str, required=True, help="Path to input audio file")
    parser.add_argument("--backend", type=str, default="auto", choices=["auto", "npu", "cpu"], help="Backend preference")
    args = parser.parse_args()

    res, backend_info = transcribe_file(args.file, backend_preference=args.backend)
    print("\n--- Transcription Result ---")
    print(f"Backend Device: {backend_info.info.device} (Verified NPU: {backend_info.info.verified_npu})")
    print(f"Audio Duration: {res.audio_seconds:.2f}s | Processing Time: {res.wall_seconds:.2f}s | RTF: {res.rtf:.4f}")
    print("\nTranscript:")
    print(res.text)
