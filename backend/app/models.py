from datetime import datetime
from .db import db


class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    display_name = db.Column(db.String)
    preferences = db.Column(db.JSON, default=dict)


class AudioSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String, nullable=False)
    original_filename = db.Column(db.String, nullable=False)
    transcription = db.Column(db.Text)
    module_id = db.Column(db.Integer, db.ForeignKey("training_module.id"), nullable=True)


class Metrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("audio_session.id"), nullable=False)
    f0_mean = db.Column(db.Float)
    f0_median = db.Column(db.Float)
    f0_min = db.Column(db.Float)
    f0_max = db.Column(db.Float)
    f0_range = db.Column(db.Float)
    f0_std = db.Column(db.Float)
    pitch_band = db.Column(db.String)
    rms_mean = db.Column(db.Float)
    spectral_centroid_mean = db.Column(db.Float)


class TrainingModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    level = db.Column(db.String, default="beginner")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    steps = db.Column(db.JSON, default=list)


class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String)
    body = db.Column(db.Text)
    audio_session_id = db.Column(db.Integer, db.ForeignKey("audio_session.id"), nullable=True)
    is_anonymous = db.Column(db.Boolean, default=True)
