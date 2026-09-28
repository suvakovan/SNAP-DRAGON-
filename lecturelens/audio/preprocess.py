"""
Audio loading, preprocessing, mono conversion, 16 kHz resampling, and peak normalization.
"""

from pathlib import Path
from typing import Union
import numpy as np
import soundfile as sf
from lecturelens.logging_setup import logger


def load_audio(file_path: Union[str, Path], target_sample_rate: int = 16000) -> np.ndarray:
    """
    Loads an audio file, converts to mono, resamples to target_sample_rate (16 kHz),
    and normalizes peak amplitude to [-1, 1]. Returns 1D float32 numpy array.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    data, samplerate = sf.read(str(path), dtype="float32")
    return preprocess_audio(data, original_sample_rate=samplerate, target_sample_rate=target_sample_rate)


def preprocess_audio(
    data: np.ndarray, original_sample_rate: int = 16000, target_sample_rate: int = 16000
) -> np.ndarray:
    """
    Processes audio data array: converts stereo to mono, resamples to target_sample_rate,
    and normalizes amplitude to [-1, 1].
    """
    if data.ndim > 1:
        # Average channels to convert to mono
        data = np.mean(data, axis=1)

    data = data.astype(np.float32)

    # Resample if sample rates differ
    if original_sample_rate != target_sample_rate and len(data) > 0:
        data = resample_audio(data, original_sample_rate, target_sample_rate)

    # Peak normalization
    max_val = np.max(np.abs(data))
    if max_val > 0:
        data = data / max_val

    return data


def resample_audio(data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """
    Resamples 1D audio array from orig_sr to target_sr using scipy.signal or linear interpolation fallback.
    """
    if orig_sr == target_sr or len(data) == 0:
        return data

    try:
        from scipy.signal import resample_poly
        import math
        gcd = math.gcd(orig_sr, target_sr)
        up = target_sr // gcd
        down = orig_sr // gcd
        resampled = resample_poly(data, up, down).astype(np.float32)
        return resampled
    except ImportError:
        logger.debug("scipy not available, using linear interpolation resampler.")
        num_samples = int(round(len(data) * target_sr / float(orig_sr)))
        old_indices = np.linspace(0, len(data) - 1, num=len(data))
        new_indices = np.linspace(0, len(data) - 1, num=num_samples)
        return np.interp(new_indices, old_indices, data).astype(np.float32)
