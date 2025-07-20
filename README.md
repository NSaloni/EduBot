# 🧠 EduBot: AI-Powered Education Assistant

EduBot is an AI-based learning assistant designed to help school students (Grades 1–10) learn topics progressively in a simple, structured, and engaging way. It provides multi-language support, AI-generated explanations, examples, quizzes, and YouTube video suggestions.

---

## 🚀 Features

- ✅ **AI-powered concept explanations** (Beginner → Advanced)
- 🎤 **Voice input** (Speech Recognition)
- 🔊 **Read aloud support** (Speech Synthesis)
- 🌐 **Multilingual support** (English, Hindi, Gujarati)
- 🧠 **Interactive quizzes** with instant feedback
- 📽️ **YouTube video recommendations**
- 📊 **Progress tracking** and level upgrades
- 🔁 **Previous / Next** concept navigation
- 🧩 **Keyword tracking and concept suggestions**
- 🌟 Designed for underprivileged learners and inclusive education

---

## 🛠️ Technologies Used

| Technology     | Role                                |
|----------------|-------------------------------------|
| **Python**     | Backend logic                       |
| **Flask**      | Web framework (backend server)      |
| **HTML/CSS/JS**| Frontend (UI + logic)               |
| **Together.ai**| LLM API for explanations & quizzes  |
| **YouTube API**| Video suggestions for concepts      |
| **SQLite**     | Database for users & concepts       |
| **Speech APIs**| Voice input & read-aloud support    |
| **dotenv**     | Environment variable handling       |

---

## 🧭 Project Flow

1. **User Login** → Username tracked with level & count
2. **Concept Input** → AI explains with example & questions
3. **YouTube Video Search** → Video embedded if available
4. **Quiz Generation** → AI creates interactive MCQs
5. **Progress Updates** → Learning level increases over time
6. **Next / Previous** → Navigate concepts with AI suggestions

---

## 📂 Folder Structure


EduBot/
├── app.py
├── templates/
│   ├── index.html
│   └── login.html                  ← Your login page
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── login.css              ← Moved to css/ folder
│   ├── js/
│   │   └── script.js
│   └── images/
│       └── logo.png               ← ✅ Place logo here
├── edubot.db                      ← (optional)
├── requirements.txt
├── .env.example
└── README.md



---

## 📄 .env File

Create a `.env` file at the root and include: TOGETHER_API_KEY=your_together_api_key  ,   YOUTUBE_API_KEY=your_youtube_api_key


**⚠️ Don't share your `.env` publicly!**

---

## 💡 Example Prompts

- `"What is Solar System?"`
- `"Explain Photosynthesis in Hindi"`
- `"Loops in Python for Grade 6"`
- `"Generate quiz on Fractions"`

---

## ✅ Future Enhancements

- 📈 User dashboard for progress
- 🧮 Math formula rendering (KaTeX/MathJax)
- 📚 Subject-wise learning flow
- 📱 Mobile-first responsive design

---



## 📜 License

This project is open-source for educational purposes under the **MIT License**.

---

## ✨ Contribute

Pull requests are welcome! Feel free to fork this repository, improve it, and submit a PR.

---

Made with ❤️ for inclusive education.
