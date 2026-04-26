# AI Quiz Generator

Python + Flask backend with Anthropic AI for MCQ generation.

## Project Structure

```
quiz_app/
├── app.py                  ← Flask server + API routes
├── requirements.txt        ← Python dependencies
├── templates/
│   └── index.html          ← Main HTML page
└── static/
    ├── css/
    │   └── style.css       ← All styling
    └── js/
        └── quiz.js         ← Frontend logic
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
# Windows
set ANTHROPIC_API_KEY=your_api_key_here

# Mac/Linux
export ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Run the app
```bash
python app.py
```

### 4. Open browser
```
http://localhost:5000
```

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Main page |
| `/api/validate-topic` | POST | AI topic validation |
| `/api/generate-quiz` | POST | AI MCQ generation |

## How It Works

1. User types any topic → Flask sends to Claude API → validates if it's a real educational topic
2. User picks difficulty (Easy/Medium/Hard) and question count (5/10/15/20)
3. Flask calls Claude API → returns MCQs as JSON
4. Frontend renders quiz, tracks answers, shows results
