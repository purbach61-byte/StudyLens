# StudyLens

Snap a photo of a problem or notes. StudyLens (powered by Gemma 4 through the Gemini API) gives
hints one at a time, a simple explanation with a memorable analogy, a 3-question quiz, flashcards,
and a study plan, in English, Bengali or Hindi. Hint-first by design: students try before they peek.

## Run
```
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY and the Gemma 4 model ID
python app.py
```
Open http://127.0.0.1:5000

## How it fits the challenge
- **Multimodal:** photo + text in, structured learning pack out
- **Focused tool:** learning, with creativity (analogies), productivity (plan) and community (share card)
- **Rapid prototype:** one Flask file, one page, one model call

License: MIT
