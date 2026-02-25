from flask import Blueprint, request, jsonify
from ..db import db
from ..models import AudioSession, Metrics
from ..services.storage import allowed_file, save_audio_file
from ..services.whisper_service import transcribe
from ..services.analysis_service import analyze_audio


audio_bp = Blueprint("audio", __name__)


@audio_bp.post("/upload")
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    user_id = request.form.get("user_id")
    module_id = request.form.get("module_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    file = request.files["audio"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    file_path = save_audio_file(user_id, file)

    transcription = None
    try:
        result = transcribe(file_path)
        transcription = result.get("text", "")
    except Exception:
        transcription = ""

    metrics = analyze_audio(file_path)

    session = AudioSession(
        user_id=user_id,
        filename=file_path,
        original_filename=file.filename,
        transcription=transcription,
        module_id=int(module_id) if module_id else None,
    )
    db.session.add(session)
    db.session.commit()

    metric_row = Metrics(session_id=session.id, **metrics)
    db.session.add(metric_row)
    db.session.commit()

    return jsonify({
        "session_id": session.id,
        "transcription": transcription,
        "metrics": metrics,
    }), 201
