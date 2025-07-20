from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, os, json, re
from datetime import datetime
import requests
from dotenv import load_dotenv
load_dotenv()  # Will read from `.env`

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")





app = Flask(__name__)
app.secret_key = 'd1c5af7b8f6e4723a6e14c739e57c9b3'

#openai.api_key = os.getenv("TOGETHER_API_KEY")

#openai.api_base = "https://api.together.xyz/v1"
TOGETHER_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

DB_PATH = os.path.join('instance', 'edubot.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 🔹 Ask AI
def ask_together_ai(prompt):
    try:
        res = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                #"Authorization": f"Bearer {openai.api_key}",
                "Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}",

                "Content-Type": "application/json"
            },
            json={
                "model": TOGETHER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ AI Error:", e)
        return None

# 🔹 Ensure table exists
def ensure_history_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS learned_concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            concept TEXT NOT NULL,
            level TEXT NOT NULL,
            query TEXT,
            previous TEXT,
            suggestion TEXT,
            count INTEGER,
            keywords TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


ensure_history_table()

# 🔹 Home/Login Routes
@app.route('/')
def home():
    if 'username' not in session:
        return redirect('/login')

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (session['username'],)).fetchone()
    conn.close()

    if not user:
        # If the user no longer exists in DB but session still has it, log them out
        session.pop('username', None)
        return redirect('/login')

    return render_template("index.html", username=session['username'], level=user["progress_level"], count=user["learning_count"])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            user = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                cur.execute("INSERT INTO users (username) VALUES (?)", (username,))
                conn.commit()
            session['username'] = username
            return redirect('/')
        finally:
            conn.close()  # ✅ always close connection in finally block
    return render_template("login.html")


@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    concept = data.get("concept", "").strip()
    level = data.get("level", "Beginner")
    language = data.get("language", "English")
    username = session.get("username")

    if not concept or not username:
        return jsonify({
            "answer": "❌ Concept missing or user not logged in.",
            "summary": "", "example": "", "suggestions": [],
            "new_level": level, "new_count": 0
        })

    # 🧠 Structured Prompt
    explain_prompt = f"""
Explain the concept '{concept}' in simple language for students in grades 1 to 10 at {level} level.
Respond in the following format:

1. Explanation:
(Write a clear paragraph explanation.)

2. Example:
(Give one real-world code-based or relatable example.)

3. Two Simple Questions with Answers:
Q1: ...
A1: ...
Q2: ...
A2: ...
    """

    if language == "Hindi":
        explain_prompt = f"""
'{concept}' को कक्षा 1 से 10 तक के छात्रों के लिए {level} स्तर पर सरल भाषा में समझाइए।
उत्तर इस संरचना में दें:

1. Explanation:
(सरल भाषा में स्पष्ट व्याख्या)

2. Example:
(एक व्यावहारिक उदाहरण)

3. Two Simple Questions with Answers:
Q1: ...
A1: ...
Q2: ...
A2: ...
        """
    elif language == "Gujarati":
        explain_prompt = f"""
'{concept}' ને ધોરણ 1 થી 10 ના વિદ્યાર્થીઓ માટે {level} સ્તરે સરળ ભાષામાં સમજાવો.
આરંભ નીચેના ફોર્મેટમાં આપો:

1. Explanation:
(સારી રીતે સમજાવટ આપો)

2. Example:
(એક ઉદાહરણ આપો)

3. Two Simple Questions with Answers:
Q1: ...
A1: ...
Q2: ...
A2: ...
        """

    full_answer = ask_together_ai(explain_prompt)
    if not full_answer:
        return jsonify({
            "answer": "❌ Something went wrong.",
            "summary": "", "example": "", "suggestions": [],
            "new_level": level, "new_count": 0
        })

    # ✂️ Extract parts: explanation, example, questions
    explanation = example = questions = ""

    try:
        explanation_match = re.search(r'1\.\s*Explanation:\s*(.*?)(?:2\.|$)', full_answer, re.DOTALL)
        example_match = re.search(r'2\.\s*Example:\s*(.*?)(?:3\.|$)', full_answer, re.DOTALL)
        questions_match = re.search(r'3\.\s*(Two\s+)?Simple\s+Questions\s+with\s+Answers:\s*(.*)', full_answer, re.DOTALL)

        if explanation_match:
            explanation = explanation_match.group(1).strip()
        if example_match:
            example = example_match.group(1).strip()
        if questions_match:
            questions = questions_match.group(2).strip()
    except Exception as e:
        print("❌ Parsing error:", e)

    # 📝 Summary
    summary = ask_together_ai(f"Summarize this in 3 short lines:\n\n{full_answer}") or ""

    # 🌐 Translate (if needed)
    if language == "Hindi":
        explanation = ask_together_ai(f"Translate to Hindi:\n{explanation}") or explanation
        summary = ask_together_ai(f"Translate to Hindi:\n{summary}") or summary
        example = ask_together_ai(f"Translate to Hindi:\n{example}") or example
        questions = ask_together_ai(f"Translate to Hindi:\n{questions}") or questions
    elif language == "Gujarati":
        explanation = ask_together_ai(f"Translate to Gujarati:\n{explanation}") or explanation
        summary = ask_together_ai(f"Translate to Gujarati:\n{summary}") or summary
        example = ask_together_ai(f"Translate to Gujarati:\n{example}") or example
        questions = ask_together_ai(f"Translate to Gujarati:\n{questions}") or questions

    # 🔑 Keywords
    keywords_prompt = f"List 5 important keywords from this explanation:\n\n{explanation}\n\nRespond only as comma-separated values."
    keywords_raw = ask_together_ai(keywords_prompt)
    keywords = keywords_raw if keywords_raw else ""

    # 🔮 Topic Suggestions
    suggestion_prompt = (
    f"Based on this {level} explanation of '{concept}', suggest 2 short and clear topic titles "
    f"(max 6 words each) the student should learn next. Return only the list like:\n1. Topic A\n2. Topic B"
)

    raw_suggestions = ask_together_ai(suggestion_prompt) or ""

# 🔹 Clean and filter suggestions to keep only short ones (no paragraphs)
    # 🔹 Clean and filter suggestions to keep only short ones (no paragraphs)
    suggestions = []
    for line in raw_suggestions.splitlines():
            line = line.strip("•➡👉- 1234567890.").strip()
            if 1 <= len(line.split()) <= 6:
                suggestions.append(line)

    suggestions = suggestions[:2]  # Keep max 2



    # 🔁 DB: Get count
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(count) FROM learned_concepts WHERE username=? AND concept=?", (username, concept))
    last_count = cur.fetchone()[0]
    current_count = (last_count + 1) if last_count is not None else 0

    # 🔁 Previous Query
    previous_query = ""
    if current_count > 0:
        cur.execute("SELECT query FROM learned_concepts WHERE username=? AND concept=? AND count=?",
                    (username, concept, current_count - 1))
        row = cur.fetchone()
        previous_query = row["query"] if row else ""

    # 🧠 Save concept
    first_suggestion = suggestions[0] if suggestions else ""
    cur.execute("""INSERT INTO learned_concepts (username, concept, level, query, previous, suggestion, count, keywords)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (username, concept, level, concept, previous_query, first_suggestion, current_count, keywords))

    # 🔄 Update user level
    user = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    new_user_count = user["learning_count"] + 1
    new_user_level = user["progress_level"]

    if new_user_count >= 5 and new_user_level == "Beginner":
        new_user_level = "Intermediate"
    elif new_user_count >= 10 and new_user_level == "Intermediate":
        new_user_level = "Advanced"

    cur.execute("UPDATE users SET learning_count = ?, progress_level = ? WHERE username = ?",
                (new_user_count, new_user_level, username))

    conn.commit()
    conn.close()

    return jsonify({
        "answer": explanation,
        "summary": summary,
        "example": example + "\n\n" + questions,
        "suggestions": suggestions,
        "new_level": new_user_level,
        "new_count": new_user_count
    })


@app.route('/youtube', methods=['POST'])
def youtube_search():
    data = request.json
    concept = data.get("concept", "").strip()

    if not concept:
        return jsonify({"videos": [], "error": "No concept provided."})

    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "q": f"{concept} tutorial for kids",
        "part": "snippet",
        "type": "video",
        "maxResults": 3
    }

    try:
        res = requests.get(search_url, params=params)
        res.raise_for_status()
        items = res.json().get("items", [])
        
        videos = [{
            "title": item["snippet"]["title"],
            "videoId": item["id"]["videoId"],
            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"]
        } for item in items]

        return jsonify({ "videos": videos })
    
    except Exception as e:
        print("❌ YouTube API error:", str(e))
        return jsonify({ "videos": [], "error": str(e) })


@app.route('/concept-history', methods=['POST'])
def concept_history():
    data = request.json
    direction = data.get("direction")  # "next" or "previous"
    username = session.get("username")

    if not username:
        return jsonify({ "status": "error", "message": "User not logged in." })

    conn = get_db_connection()
    cur = conn.cursor()

    # Get all learned concepts for this user (sorted by time)
    cur.execute("""
        SELECT * FROM learned_concepts 
        WHERE username = ? 
        ORDER BY timestamp ASC
    """, (username,))
    rows = cur.fetchall()

    if not rows:
        conn.close()
        return jsonify({ "status": "error", "message": "No learning history." })

    # Find current (latest) index
    last_concept = rows[-1]
    current_index = len(rows) - 1

    if direction == "previous":
        if current_index == 0:
            conn.close()
            return jsonify({ "status": "error", "message": "No previous concept found." })
        prev_row = rows[current_index - 1]
        conn.close()
        return jsonify({
            "status": "ok",
            "query": prev_row["query"],
            "level": prev_row["level"]
        })

    elif direction == "next":
        suggestion = last_concept["suggestion"]
        if not suggestion:
            conn.close()
            return jsonify({ "status": "error", "message": "No next concept suggested." })
        # Check if already learned
        cur.execute("""
            SELECT * FROM learned_concepts 
            WHERE username = ? AND concept = ? 
            ORDER BY timestamp ASC LIMIT 1
        """, (username, suggestion))
        row = cur.fetchone()
        conn.close()
        return jsonify({
            "status": "ok",
            "query": suggestion,
            "level": row["level"] if row else "Beginner"
        })

    conn.close()
    return jsonify({ "status": "error", "message": "Invalid direction." })





# 🔹 Quiz Generation
@app.route('/check-quiz', methods=['POST'])
def check_quiz():
    data = request.json
    text = data.get("text", "")
    language = data.get("language", "English")

    try:
        # 🔹 Generate MCQs
        quiz_prompt = (
            "Create 5 multiple-choice questions (MCQs) with 3 options each. "
            "Each must include 'question', 'options' (list), 'correct', and 'explanation' with 'correct' and 'wrong'. "
            "Return ONLY valid JSON array. No headings, no intro. Format:\n\n"
            '[{"question": "...", "options": ["...","...","..."], "correct": "...", '
            '"explanation": {"correct": "...", "wrong": "..."}}]'
        )

        raw = ask_together_ai(f"{quiz_prompt}\n\nTopic:\n{text}")
        print("🧪 RAW QUIZ:", raw[:500])

        # Try strict JSON match
        match = re.search(r'(\[.*\])', raw, re.DOTALL)
        if not match:
            raise ValueError("❌ AI did not return a valid JSON list.")

        raw_json = match.group(1)

        # Fix unescaped backslashes, if any
        cleaned_json = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', raw_json)

        try:
            quiz_data = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            print("⚠️ Attempting partial recovery due to JSON error:", e)
            # Attempt to fix missing commas or broken entries
            fixed = "[" + ",".join(line.strip().rstrip(',') for line in raw_json.splitlines() if line.strip().startswith("{")) + "]"
            quiz_data = json.loads(fixed)

        # 🔁 Translate if needed
        if language != "English":
            trans_prompt = (
                f"Translate only the values of 'question', 'options', and 'explanation' into {language}. "
                "DO NOT change JSON structure or keys.\n\n"
                f"{json.dumps(quiz_data, ensure_ascii=False)}"
            )
            translated_raw = ask_together_ai(trans_prompt)
            match_trans = re.search(r'(\[.*?\])', translated_raw, re.DOTALL)
            if not match_trans:
                raise ValueError("❌ Translated version is not valid JSON.")

            translated_json = match_trans.group(1)
            translated_cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', translated_json)
            quiz_data = json.loads(translated_cleaned)

        return jsonify({ "questions": quiz_data })

    except Exception as e:
        print("❌ Quiz error:", str(e))
        return jsonify({ "questions": [], "error": str(e) })






"""@app.route('/test-quiz')
@app.route('/test-quiz', methods=['GET'])
def test_quiz():
    example_text = "Newton's Laws of Motion explained simply for 10-year-olds."
    language = "English"

    try:
        quiz_prompt = (
            "Create 5 multiple-choice questions (MCQs) with 3 options each. "
            "Return only valid JSON list:\n"
            "[{\"question\": \"...\", \"options\": [\"...\", \"...\", \"...\"], \"correct\": \"...\", "
            "\"explanation\": {\"correct\": \"...\", \"wrong\": \"...\"}}, ...]\n\n"
            f"Topic:\n{example_text}"
        )
        raw = ask_together_ai(quiz_prompt)
        print("🧪 TRANSLATED AI RESPONSE:", translated_raw)


        match = re.search(r'(\[.*\])', raw, re.DOTALL)
        if not match:
            return "❌ JSON not found in response."

        cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', match.group(1))
        quiz_data = json.loads(cleaned)
        return jsonify({ "questions": quiz_data })

    except Exception as e:
        return f"❌ Error: {str(e)}"

"""""

if __name__ == '__main__':
    app.run(debug=True)
