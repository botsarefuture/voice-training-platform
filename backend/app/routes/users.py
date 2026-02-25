import uuid
from flask import Blueprint, request, jsonify, send_file
from ..db import db
from ..models import User, AudioSession, Metrics, TrainingModule, CommunityPost

users_bp = Blueprint("users", __name__)


@users_bp.post("")
def create_user():
    data = request.get_json(force=True, silent=True) or {}
    user_id = data.get("id") or str(uuid.uuid4())
    user = User(id=user_id, display_name=data.get("display_name"))
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "created_at": user.created_at.isoformat()}), 201


@users_bp.get("/<user_id>")
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"id": user.id, "display_name": user.display_name, "created_at": user.created_at.isoformat()})


@users_bp.delete("/<user_id>")
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    AudioSession.query.filter_by(user_id=user_id).delete()
    CommunityPost.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"status": "deleted"})


@users_bp.get("/<user_id>/export")
def export_user_data(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    sessions = AudioSession.query.filter_by(user_id=user_id).all()
    metrics = Metrics.query.join(AudioSession, Metrics.session_id == AudioSession.id).filter(AudioSession.user_id == user_id).all()
    posts = CommunityPost.query.filter_by(user_id=user_id).all()

    export = {
        "user": {"id": user.id, "display_name": user.display_name, "created_at": user.created_at.isoformat()},
        "sessions": [
            {
                "id": s.id,
                "created_at": s.created_at.isoformat(),
                "filename": s.filename,
                "transcription": s.transcription,
                "module_id": s.module_id,
            }
            for s in sessions
        ],
        "metrics": [
            {
                "session_id": m.session_id,
                "f0_mean": m.f0_mean,
                "f0_median": m.f0_median,
                "f0_min": m.f0_min,
                "f0_max": m.f0_max,
                "f0_range": m.f0_range,
                "f0_std": m.f0_std,
                "pitch_band": m.pitch_band,
                "rms_mean": m.rms_mean,
                "spectral_centroid_mean": m.spectral_centroid_mean,
            }
            for m in metrics
        ],
        "community_posts": [
            {
                "id": p.id,
                "created_at": p.created_at.isoformat(),
                "title": p.title,
                "body": p.body,
                "audio_session_id": p.audio_session_id,
                "is_anonymous": p.is_anonymous,
            }
            for p in posts
        ],
    }

    return jsonify(export)
