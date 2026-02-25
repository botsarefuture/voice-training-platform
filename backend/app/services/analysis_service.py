import numpy as np
import librosa


def classify_pitch_band(f0_mean: float) -> str:
    if f0_mean is None:
        return "unknown"
    if f0_mean < 155:
        return "lower"
    if 155 <= f0_mean <= 185:
        return "neutral"
    if 185 < f0_mean <= 300:
        return "feminine"
    return "high"


def analyze_audio(audio_path: str) -> dict:
    y, sr = librosa.load(audio_path, sr=None)
    f0 = librosa.yin(y, fmin=80, fmax=400, sr=sr)
    f0 = f0[np.isfinite(f0)]
    if f0.size == 0:
        f0_stats = {
            "f0_mean": None,
            "f0_median": None,
            "f0_min": None,
            "f0_max": None,
            "f0_range": None,
            "f0_std": None,
            "pitch_band": None,
        }
    else:
        f0_mean = float(np.mean(f0))
        f0_stats = {
            "f0_mean": f0_mean,
            "f0_median": float(np.median(f0)),
            "f0_min": float(np.min(f0)),
            "f0_max": float(np.max(f0)),
            "f0_range": float(np.max(f0) - np.min(f0)),
            "f0_std": float(np.std(f0)),
            "pitch_band": classify_pitch_band(f0_mean),
        }

    rms = librosa.feature.rms(y=y)[0]
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    return {
        **f0_stats,
        "rms_mean": float(np.mean(rms)),
        "spectral_centroid_mean": float(np.mean(spectral_centroid)),
    }
