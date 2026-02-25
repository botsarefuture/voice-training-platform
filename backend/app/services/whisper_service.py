try:
    import whisper
except Exception:
    whisper = None

from config import Config

_model = None


def get_model():
    global _model
    if whisper is None:
        return None
    if _model is None:
        _model = whisper.load_model(Config.WHISPER_MODEL)
    return _model


def transcribe(audio_path: str) -> dict:
    model = get_model()
    if model is None:
        return {"text": ""}
    return model.transcribe(audio_path)
