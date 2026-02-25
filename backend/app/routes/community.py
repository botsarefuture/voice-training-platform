from flask import Blueprint, request, jsonify
from ..db import db
from ..models import CommunityPost

community_bp = Blueprint("community", __name__)


@community_bp.get("")
def list_posts():
    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
    return jsonify([
        {
            "id": p.id,
            "user_id": p.user_id if not p.is_anonymous else None,
            "created_at": p.created_at.isoformat(),
            "title": p.title,
            "body": p.body,
            "audio_session_id": p.audio_session_id,
            "is_anonymous": p.is_anonymous,
        }
        for p in posts
    ])


@community_bp.post("")
def create_post():
    data = request.get_json(force=True)
    post = CommunityPost(
        user_id=data.get("user_id"),
        title=data.get("title"),
        body=data.get("body"),
        audio_session_id=data.get("audio_session_id"),
        is_anonymous=data.get("is_anonymous", True),
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({"id": post.id}), 201
