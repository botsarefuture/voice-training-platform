import whisper
from config import Config

_model = None


def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model(Config.WHISPER_MODEL)
    return _model


def transcribe(audio_path: str) -> dict:
    model = get_model()
    return model.transcribe(audio_path)
