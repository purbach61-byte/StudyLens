import os
import json

from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = os.getenv(
    "GEMMA_MODEL",
    "gemma-4-31b-it"
)


# =========================================================
# FAST STUDYLENS PROMPT
# =========================================================

PROMPT = """
You are StudyLens, a fast and friendly tutor.

Student level: {level}
Subject: {subject}
Language: {language}

Student question:
"{question}"

Analyze the photo if provided.

Return ONLY valid JSON.

Keep every answer concise so the response is fast.

JSON format:
{{
  "topic": "short topic name",

  "hints": [
    "short hint 1",
    "short hint 2",
    "short hint 3"
  ],

  "solution": "short step-by-step solution",

  "explain": "simple explanation in 3 short sentences",

  "analogy": "one short everyday analogy",

  "quiz": [
    {{
      "q": "question",
      "options": ["A", "B", "C", "D"],
      "answer": 0,
      "why": "short reason"
    }},
    {{
      "q": "question",
      "options": ["A", "B", "C", "D"],
      "answer": 0,
      "why": "short reason"
    }},
    {{
      "q": "question",
      "options": ["A", "B", "C", "D"],
      "answer": 0,
      "why": "short reason"
    }}
  ],

  "flashcards": [
    {{
      "front": "short question",
      "back": "short answer"
    }},
    {{
      "front": "short question",
      "back": "short answer"
    }},
    {{
      "front": "short question",
      "back": "short answer"
    }}
  ],

  "plan": [
    "short next step",
    "short next step",
    "short next step"
  ]
}}

Rules:
- Be concise.
- Do not write long paragraphs.
- Exactly 3 quiz questions.
- Exactly 3 flashcards.
- Answer must be the zero-based index of the correct option.
- If the image is unreadable, say so briefly.
"""


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# STUDY API
# =========================================================

@app.route("/study", methods=["POST"])
def study():

    question = request.form.get("question", "").strip()

    subject = request.form.get(
        "subject",
        "General"
    ).strip()

    language = request.form.get(
        "language",
        "English"
    ).strip()

    level = request.form.get(
        "level",
        "Class 9-10"
    ).strip()

    img = request.files.get("image")

    if not img and not question:
        return jsonify(
            error="Add a photo or type a question."
        ), 400

    prompt = PROMPT.format(
        level=level,
        subject=subject,
        language=language,
        question=question or "(No typed question. Use the image.)"
    )

    parts = [prompt]

    # Add image if supplied
    if img:
        image_data = img.read()

        parts.insert(
            0,
            types.Part.from_bytes(
                data=image_data,
                mime_type=img.mimetype
            )
        )

    try:

        # Faster generation settings
        config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=1200,
            response_mime_type="application/json"
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=parts,
            config=config
        )

        raw = response.text.strip()

        # Remove accidental markdown fences if model adds them
        if raw.startswith("```"):
            raw = raw.replace("```json", "")
            raw = raw.replace("```", "")
            raw = raw.strip()

        data = json.loads(raw)

        return jsonify(data)

    except json.JSONDecodeError:
        app.logger.error("Model returned invalid JSON")
        return jsonify(
            error="The AI response was incomplete. Please try again."
        ), 502

    except Exception as e:
     app.logger.exception("GEMMA ERROR")
    return jsonify(error=f"Gemma error: {str(e)}"), 502
# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)