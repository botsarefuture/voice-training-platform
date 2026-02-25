import requests

API = "http://localhost:5000/api/modules"

modules = [
    {
        "title": "Warm‑Up & Vocal Health",
        "description": "Prepare gently and reduce strain (short, frequent practice is safer).",
        "level": "beginner",
        "steps": [
            "Hydrate and take 3 slow breaths",
            "Gentle lip trills for 10–15 seconds",
            "Soft humming on a comfortable pitch"
        ]
    },
    {
        "title": "Pitch Fundamentals",
        "description": "Establish a comfortable baseline pitch and glide safely (neutral ~155–185 Hz).",
        "level": "beginner",
        "steps": [
            "Sustain a gentle 'mmm' for 5 seconds",
            "Slide up in pitch slowly and return",
            "Repeat with vowels: ee, ah, oo"
        ]
    },
    {
        "title": "Resonance & Brightness",
        "description": "Shift resonance forward and brighten tone without strain.",
        "level": "intermediate",
        "steps": [
            "Say 'nee' with a forward, light resonance",
            "Alternate 'nee' and 'nah'",
            "Record and compare"
        ]
    },
    {
        "title": "Intonation & Prosody",
        "description": "Practice melodic contours and expressive variation.",
        "level": "intermediate",
        "steps": [
            "Read a short phrase with rising intonation",
            "Repeat with falling intonation",
            "Record both and compare the contour"
        ]
    },
    {
        "title": "Communication Style & Pragmatics",
        "description": "Explore phrasing, word choice, and non‑verbal cues.",
        "level": "advanced",
        "steps": [
            "Role‑play a greeting, asking for help, and a phone call",
            "Notice pacing and emphasis",
            "Reflect on comfort and confidence"
        ]
    }
]

for m in modules:
    r = requests.post(API, json=m)
    print(r.status_code, r.json())
