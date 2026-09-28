"""
Audio chunker to split long recordings into windowed frames with overlap and low-energy boundary cuts.
"""

from typing import List, Tuple
import numpy as np
from lecturelens.config import config
from lecturelens.audio.vad import compute_frame_energy


def chunk_audio(
    audio: np.ndarray,
    sample_rate: int = config.sample_rate,
    chunk_seconds: float = config.chunk_seconds,
    overlap_seconds: float = config.overlap_seconds,
) -> List[Tuple[float, float, np.ndarray]]:
    """
    Splits audio buffer into chunks of ~chunk_seconds with overlap_seconds overlap.
    Seeks lowest energy frame within search window to make natural cuts.
    Returns list of (start_sec, end_sec, audio_chunk).
    """
    if len(audio) == 0:
        return []

    total_seconds = len(audio) / float(sample_rate)
    if total_seconds <= chunk_seconds:
        return [(0.0, total_seconds, audio)]

    chunk_samples = int(chunk_seconds * sample_rate)
    overlap_samples = int(overlap_seconds * sample_rate)
    step_samples = chunk_samples - overlap_samples

    chunks: List[Tuple[float, float, np.ndarray]] = []
    start_sample = 0

    while start_sample < len(audio):
        end_sample = min(start_sample + chunk_samples, len(audio))

        # If remaining audio is small, append to current chunk or finish
        if len(audio) - start_sample < chunk_samples / 2 and chunks:
            # Merge remaining into last chunk
            last_start, _, last_audio = chunks.pop()
            merged_audio = audio[int(last_start * sample_rate):]
            chunks.append((last_start, total_seconds, merged_audio))
            break

        # Cut at lowest energy near end of window if possible
        actual_end = end_sample
        if end_sample < len(audio):
            search_start = max(start_sample, end_sample - int(2.0 * sample_rate))
            search_region = audio[search_start:end_sample]
            if len(search_region) > 512:
                energies = compute_frame_energy(search_region, frame_length=512)
                min_idx = int(np.argmin(energies))
                actual_end = search_start + (min_idx * 512)

        chunk_data = audio[start_sample:actual_end]
        start_sec = start_sample / float(sample_rate)
        end_sec = actual_end / float(sample_rate)
        chunks.append((start_sec, end_sec, chunk_data))

        # Advance start position considering overlap
        next_start = actual_end - overlap_samples
        if next_start <= start_sample:
            next_start = start_sample + step_samples
        start_sample = next_start

    return chunks
