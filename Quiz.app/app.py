from flask import Flask, render_template, request, jsonify
from groq import Groq
import json
import re
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder='templetes')

# Configure Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=GROQ_API_KEY)

# Rate limiting
last_request_time = 0
MIN_REQUEST_INTERVAL = 0.5 

def clean_json(raw: str) -> str:
    """Remove markdown code fences and strip whitespace."""
    cleaned = re.sub(r"```json|```", "", raw).strip()
    return cleaned


def rate_limit():
    """Apply client-side rate limiting."""
    global last_request_time
    current_time = time.time()
    time_since_last_request = current_time - last_request_time
    
    if time_since_last_request < MIN_REQUEST_INTERVAL:
        wait_time = MIN_REQUEST_INTERVAL - time_since_last_request
        time.sleep(wait_time)
    
    last_request_time = time.time()


def generate_with_retry(prompt, max_retries=3):
    """Generate content with Groq with retry logic."""
    for attempt in range(max_retries):
        try:
            rate_limit()
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for rate limit errors
            if "rate" in error_msg or "429" in str(e) or "quota" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5
                    print(f"Rate limited. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("API rate limit exceeded. Please wait a moment and try again.")
            
            # Other errors
            else:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"API error: {str(e)}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"API error: {str(e)[:150]}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/validate-topic", methods=["POST"])
def validate_topic():
    try:
        data = request.get_json()
        topic = data.get("topic", "").strip()

        if not topic:
            return jsonify({"valid": False, "reason": "Topic khali hai. Kuch likhein!"}), 400

        prompt = f"""Validate this topic: "{topic}"

Is this a valid educational or technical topic for MCQ questions?

Reply with ONLY this JSON format, nothing else:
{{"valid": true, "topic": "topic name", "icon": "emoji"}}
or
{{"valid": false, "reason": "why not"}}"""

        raw = generate_with_retry(prompt)
        result = json.loads(clean_json(raw))
        return jsonify(result)
        
    except json.JSONDecodeError as e:
        return jsonify({"valid": False, "reason": f"Response parse error. Retry karein."}), 500
    except Exception as e:
        print(f"Error in validate_topic: {str(e)}")
        return jsonify({"valid": False, "reason": str(e)}), 500


@app.route("/api/generate-quiz", methods=["POST"])
def generate_quiz():
    try:
        data = request.get_json()
        topic = data.get("topic", "")
        difficulty = data.get("difficulty", "medium")
        count = int(data.get("count", 5))

        if not topic:
            return jsonify({"error": "Topic missing"}), 400

        prompt = f"""Generate exactly {count} multiple choice questions about \"{topic}\" at \"{difficulty}\" difficulty level.

Make questions genuinely educational and specific to this topic.

Reply with ONLY valid JSON array, nothing else:
[{{"id":1,"question":"...?,"options":["A","B","C","D"],"correct_answer":0,"explanation":"..."}}]

Important:
- "correct_answer" is 0-based index (0=A, 1=B, 2=C, 3=D)
- All 4 options must be plausible
- Include educational explanation"""

        raw = generate_with_retry(prompt)
        questions = json.loads(clean_json(raw))
        return jsonify({"questions": questions})
        
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Response parse error. Retry karein."}), 500
    except Exception as e:
        print(f"Error in generate_quiz: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
