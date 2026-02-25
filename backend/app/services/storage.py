import os
from werkzeug.utils import secure_filename
from config import Config


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_audio_file(user_id: str, file_storage) -> str:
    user_dir = os.path.join(Config.UPLOAD_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    filename = secure_filename(file_storage.filename)
    dest = os.path.join(user_dir, filename)
    file_storage.save(dest)
    os.chmod(dest, 0o600)
    return dest
