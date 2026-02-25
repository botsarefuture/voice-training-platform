#!/usr/bin/env python3
"""
Voice Training Platform for Transwomen
Backend main application
"""

from flask import Flask, request, jsonify, send_file
import os
import whisper
import json
from datetime import datetime
import uuid

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
DATABASE_FILE = 'voice_training_data.json'
ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load existing data
def load_database():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    return {"users": {}, "exercises": {}, "sessions": [], "progress": {}}

# Save data
def save_database(data):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Initialize database
database = load_database()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return jsonify({
        "message": "Voice Training Platform API",
        "version": "1.0.0"
    })

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = database["users"].get(user_id, None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/user/<user_id>', methods=['déf'])
def create_user(user_id):
    if user_id not in database["users"]:
        database["users"][user_id] = {
            "id": user_id,
            "created_at": datetime.now().isoformat(),
            "profile": {}
        }
        save_database(database)
    
    return jsonify(database["users"][user_id])

@app.route('/upload/<user_id>', methods=['POST'])
def upload_audio(user_id):
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400
    
    # Save file
    filename = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{file.filename.rsplit('.', 1)[1].lower()}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Process with Whisper
    try:
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
    
    # Store in database
    session_data = {
        "user_id": user_id,
        "filename": filename,
        "file_path": file_path,
        "timestamp": datetime.now().isoformat(),
        "transcription": result["text"],
        "segments": result["segments"]
    }
    
    database["sessions"].append(session_data)
    save_database(database)
    
    return jsonify({
        "message": "Audio processed successfully", 
        "transcription": result["text"],
        "session_id": len(database["sessions"]) - 1
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)