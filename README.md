# Voice Training Platform for Transwomen

Local-first voice training platform with live feedback, guided exercises, and progress tracking.

## Features
- **Audio recording + Whisper transcription** (local processing)
- **Multi‑dimensional feedback**: pitch, variability, resonance proxies, loudness
- **Guided training modules** (warm‑ups, pitch, resonance, prosody, pragmatics)
- **Progress dashboard** (session history + multi‑metric trends)
- **Community sharing** (anonymous posts + optional audio linking)
- **Secure audio storage** (local storage with restrictive permissions)
- **Offline-first support** (PWA service worker + local backend)
- **GDPR tools** (data export + deletion endpoints)

## Project Structure
```
voice-training-platform/
├── backend/          # Flask backend API
├── frontend/         # React + Vite frontend
├── docs/             # Documentation
├── scripts/          # Utility scripts
└── README.md
```

## Quick Start

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend connects to `http://localhost:5000` by default. Configure with `VITE_API_BASE` if needed.

## API Summary
- `POST /api/users` → create local user
- `GET /api/users/<id>` → user profile
- `DELETE /api/users/<id>` → GDPR delete
- `GET /api/users/<id>/export` → GDPR export
- `POST /api/audio/upload` → upload + transcription + analysis
- `GET /api/progress/<user_id>` → progress dashboard data
- `GET/POST /api/modules` → training modules
- `GET/POST /api/community` → community posts

## Offline Capability
Run backend locally and use the PWA service worker to cache UI assets. Audio processing stays on-device via the local backend.

## Security & Privacy
- Audio files saved to `backend/data/uploads/<user_id>/` with `0600` permissions.
- No external cloud calls by default.
- GDPR export and delete endpoints included.
- Practice reminders emphasize safe, short sessions and vocal health.

## Next Steps
- Add authentication and per-user access control
- Add advanced formant and resonance analysis
- Enrich training modules with multimedia guidance
- Mobile deployment via PWA or native wrapper
