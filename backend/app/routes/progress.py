from flask import Blueprint, jsonify
from ..models import AudioSession, Metrics

progress_bp = Blueprint("progress", __name__)


@progress_bp.get("/<user_id>")
def user_progress(user_id):
    sessions = AudioSession.query.filter_by(user_id=user_id).order_by(AudioSession.created_at).all()
    payload = []
    for s in sessions:
        m = Metrics.query.filter_by(session_id=s.id).first()
        payload.append({
            "session_id": s.id,
            "created_at": s.created_at.isoformat(),
            "transcription": s.transcription,
            "metrics": {
                "f0_mean": m.f0_mean if m else None,
                "f0_median": m.f0_median if m else None,
                "f0_min": m.f0_min if m else None,
                "f0_max": m.f0_max if m else None,
                "f0_range": m.f0_range if m else None,
                "f0_std": m.f0_std if m else None,
                "pitch_band": m.pitch_band if m else None,
                "rms_mean": m.rms_mean if m else None,
                "spectral_centroid_mean": m.spectral_centroid_mean if m else None,
            }
        })
    return jsonify({"sessions": payload})
