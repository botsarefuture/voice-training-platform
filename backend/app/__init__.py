from flask import Flask, jsonify
from flask_cors import CORS
from .db import db
from .routes.users import users_bp
from .routes.audio import audio_bp
from .routes.modules import modules_bp, seed_default_modules
from .routes.progress import progress_bp
from .routes.community import community_bp
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_default_modules()

    @app.route("/")
    def index():
        return jsonify({"name": "Voice Training Platform API", "version": "0.1.0"})

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(audio_bp, url_prefix="/api/audio")
    app.register_blueprint(modules_bp, url_prefix="/api/modules")
    app.register_blueprint(progress_bp, url_prefix="/api/progress")
    app.register_blueprint(community_bp, url_prefix="/api/community")

    return app
