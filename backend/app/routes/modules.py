from flask import Blueprint, request, jsonify
from ..db import db
from ..models import TrainingModule

modules_bp = Blueprint("modules", __name__)

DEFAULT_MODULES = [
    {
        "title": "Warm‑Up & Vocal Health",
        "description": "Prepare gently and reduce strain (short, frequent practice is safer).",
        "level": "beginner",
        "steps": [
            "Hydrate and take 3 slow breaths",
            "Gentle lip trills for 10–15 seconds",
            "Soft humming on a comfortable pitch",
        ],
    },
    {
        "title": "Pitch Fundamentals",
        "description": "Establish a comfortable baseline pitch and glide safely (neutral ~155–185 Hz).",
        "level": "beginner",
        "steps": [
            "Sustain a gentle 'mmm' for 5 seconds",
            "Slide up in pitch slowly and return",
            "Repeat with vowels: ee, ah, oo",
        ],
    },
    {
        "title": "Resonance & Brightness",
        "description": "Shift resonance forward and brighten tone without strain.",
        "level": "intermediate",
        "steps": [
            "Say 'nee' with a forward, light resonance",
            "Alternate 'nee' and 'nah'",
            "Record and compare",
        ],
    },
    {
        "title": "Intonation & Prosody",
        "description": "Practice melodic contours and expressive variation.",
        "level": "intermediate",
        "steps": [
            "Read a short phrase with rising intonation",
            "Repeat with falling intonation",
            "Record both and compare the contour",
        ],
    },
    {
        "title": "Communication Style & Pragmatics",
        "description": "Explore phrasing, word choice, and non‑verbal cues.",
        "level": "advanced",
        "steps": [
            "Role‑play a greeting, asking for help, and a phone call",
            "Notice pacing and emphasis",
            "Reflect on comfort and confidence",
        ],
    },
]


def seed_default_modules():
    if TrainingModule.query.count() > 0:
        return
    for m in DEFAULT_MODULES:
        db.session.add(TrainingModule(**m))
    db.session.commit()


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
