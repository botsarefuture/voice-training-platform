from flask import Blueprint, request, jsonify
from ..db import db
from ..models import TrainingModule

modules_bp = Blueprint("modules", __name__)


@modules_bp.get("")
def list_modules():
    modules = TrainingModule.query.all()
    return jsonify([
        {
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "level": m.level,
            "steps": m.steps,
        }
        for m in modules
    ])


@modules_bp.post("")
def create_module():
    data = request.get_json(force=True)
    module = TrainingModule(
        title=data.get("title"),
        description=data.get("description"),
        level=data.get("level", "beginner"),
        steps=data.get("steps", []),
    )
    db.session.add(module)
    db.session.commit()
    return jsonify({"id": module.id}), 201
