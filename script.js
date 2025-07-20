let isSpeaking = false;
let currentUtterance = null;
let conceptHistory = [];
let currentConceptIndex = -1;


function askConcept() {
    const concept = document.getElementById('conceptInput').value.trim();
    const language = document.getElementById('languageSelect').value;

    if (!concept) {
        alert("Please enter a concept.");
        return;
    }

    conceptHistory.push(concept);
    currentConceptIndex = conceptHistory.length - 1;

    document.getElementById('userQuestion').innerText = concept;
    document.getElementById('botAnswer').innerHTML = "<em>Loading answer...</em>";
    document.getElementById('quiz-section').innerHTML = "";

    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept, level: currentUserLevel || "Beginner", language })
    })
        .then(res => res.json())
        .then(data => {
            if (!data.answer || data.answer.startsWith("Error:")) {
                document.getElementById('botAnswer').innerHTML = "<em>❌ Concept could not be fetched. Try again.</em>";
                return;
            }

            let html = `
                <div class="answer-box">
                    <h2>📘 <strong>Let's Learn:</strong> ${concept}</h2>
                    <div class="answer-content">
                        ${data.answer.replace(/\n/g, "<br><br>")}
                    </div>`;

            if (data.example && data.example.trim()) {
                html += `
                    <div class="example-box">
                        <strong>🧠 Example:</strong>
                        <div>${data.example.replace(/\n/g, "<br><br>")}</div>
                    </div>`;
            }

            if (data.summary && data.summary.trim()) {
                html += `
                    <div class="summary-section">
                        <h3>📝 Easy Summary</h3>
                        <p>${data.summary.replace(/\n/g, "<br>")}</p>
                    </div>`;
            }

            if (data.suggestions && data.suggestions.length > 0) {
                html += `
                    <div class="suggestion-box">
                        <h3>👉 What to learn next:</h3>
                        <ul>
                            ${data.suggestions.map(s => `
                                <li><a href="#" class="suggestion-link" onclick="learnSuggestion('${s.replace(/'/g, "\\'")}')">${s}</a></li>
                            `).join('')}
                        </ul>
                    </div>`;
            }

            html += `</div>`; // Close answer-box

            document.getElementById('botAnswer').innerHTML = html;
            updateProgressBar(data.new_level, data.new_count);
            currentUserLevel = data.new_level;
            currentUserCount = data.new_count;
            isSpeaking = false;
            document.getElementById('readButton').innerText = "🔊 Read Aloud";
        })
        .catch(err => {
            console.error("Fetch /ask error:", err);
            document.getElementById('botAnswer').innerHTML = "<em>❌ Something went wrong. Check console.</em>";
        });

    fetchYouTubeVideos(concept);
}


//youtube raccomndation

// 🔎 YouTube Recommendation
function fetchYouTubeVideos(concept) {
    fetch('/youtube', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept })
    })
    .then(res => res.json())
    .then(data => {
        const videoBox = document.getElementById('youtubeVideo');
        if (data.videos && data.videos.length > 0) {
            const first = data.videos[0];
            let html = `
                <h3>🎥 Learn by Watching</h3>
                <iframe width="100%" height="315"
                    src="https://www.youtube.com/embed/${first.videoId}"
                    frameborder="0" allowfullscreen></iframe>
                <p><a href="https://www.youtube.com/results?search_query=${encodeURIComponent(concept)}" target="_blank">🔎 More on YouTube</a></p>
            `;

            if (data.videos[1]) {
                html += `<p>▶ <a href="https://www.youtube.com/watch?v=${data.videos[1].videoId}" target="_blank">${data.videos[1].title}</a></p>`;
            }
            if (data.videos[2]) {
                html += `<p>▶ <a href="https://www.youtube.com/watch?v=${data.videos[2].videoId}" target="_blank">${data.videos[2].title}</a></p>`;
            }

            videoBox.innerHTML = html;
        } else {
            videoBox.innerHTML = `<p><em>❌ No YouTube videos found.</em></p>`;
        }
    })
    .catch(err => {
        console.error("YouTube fetch error:", err);
        document.getElementById('youtubeVideo').innerHTML = "<p>⚠️ YouTube video could not be loaded.</p>";
    });
}





function learnSuggestion(suggestion) {
    // Update the input box and concept history correctly
    document.getElementById('conceptInput').value = suggestion;

    // Push to history
    conceptHistory.push(suggestion);
    currentConceptIndex = conceptHistory.length - 1;

    // Trigger concept loading
    askConcept();
}


/*
function askConcept() {
    const concept = document.getElementById('conceptInput').value.trim();
    const language = document.getElementById('languageSelect').value;

    if (!concept) {
        alert("Please enter a concept.");
        return;
    }

    conceptHistory.push(concept);
    currentConceptIndex = conceptHistory.length - 1;

    document.getElementById('userQuestion').innerText = concept;
    document.getElementById('botAnswer').innerHTML = "<em>Loading answer...</em>";
    document.getElementById('quiz-section').innerHTML = "";

    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept, level: currentUserLevel || "Beginner", language })
    })
        .then(res => res.json())
        .then(data => {
            if (!data.answer || data.answer.startsWith("Error:")) {
                document.getElementById('botAnswer').innerHTML = "<em>❌ Concept could not be fetched. Try again.</em>";
                return;
            }

            let rawAnswer = data.answer.trim();
            const exampleMatch = rawAnswer.match(/(?:example|उदाहरण|ઉદાહરણ)[\s:–-]*([\s\S]+?)(?:\n{2,}|\Z)/i);
            let example = "";
            if (exampleMatch) {
                example = exampleMatch[1].trim();
                rawAnswer = rawAnswer.replace(exampleMatch[0], "").trim();
            }

            let html = `
                <div class="answer-box">
                    <h2>📘 <strong>Let's Learn:</strong> ${concept}</h2>
                    <div class="answer-content">
                        ${rawAnswer.replace(/\n/g, "<br><br>")}
                    </div>`;

            if (example) {
                html += `
                    <div class="example-box">
                        <strong>🧠 Example:</strong>
                        <p>${example}</p>
                    </div>`;
            }

            if (data.summary) {
                html += `
                    <div class="summary-section">
                        <h3>📝 Easy Summary</h3>
                        <p>${data.summary.replace(/\n/g, "<br>")}</p>
                    </div>`;
            }

            if (data.suggestions && data.suggestions.length > 0) {
                html += `
                    <div class="suggestion-box">
                        <h3>👉 What to learn next:</h3>
                        <ul>
                            ${data.suggestions.map(s => `
                                <li><a href="#" class="suggestion-link" onclick="learnSuggestion('${s.replace(/'/g, "\\'")}')">${s}</a></li>
                            `).join('')}
                        </ul>
                    </div>`;
            }

            html += `</div>`; // Close answer-box

            document.getElementById('botAnswer').innerHTML = html;
            updateProgressBar(data.new_level, data.new_count);
            currentUserLevel = data.new_level;
            currentUserCount = data.new_count;
            isSpeaking = false;
            document.getElementById('readButton').innerText = "🔊 Read Aloud";
        })
        .catch(err => {
            console.error("Fetch /ask error:", err);
            document.getElementById('botAnswer').innerHTML = "<em>❌ Something went wrong. Check console.</em>";
        });
}


function learnSuggestion(suggestion) {
    document.getElementById('conceptInput').value = suggestion;
    askConcept();  // Treat the clicked suggestion like a new search
}

*/

function updateProgressBar(level, count = 0) {
    const bar = document.getElementById('progress-fill');
    const beginner = document.getElementById('beginner');
    const intermediate = document.getElementById('intermediate');
    const advanced = document.getElementById('advanced');

    if (!bar) return;
    if (count === 0) bar.style.width = "0%";
    else if (level === "Beginner") bar.style.width = "33%";
    else if (level === "Intermediate") bar.style.width = "66%";
    else if (level === "Advanced") bar.style.width = "100%";

    beginner?.classList.remove("active");
    intermediate?.classList.remove("active");
    advanced?.classList.remove("active");

    if (level === "Beginner") beginner?.classList.add("active");
    if (level === "Intermediate") intermediate?.classList.add("active");
    if (level === "Advanced") advanced?.classList.add("active");
}



function previousConcept() {
    fetch('/concept-history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            direction: "previous",
            language: document.getElementById('languageSelect').value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.query) {
            document.getElementById('conceptInput').value = data.query;
            askConcept();  // auto triggers learning of previous concept
        } else {
            alert("No previous concept found.");
        }
    })
    .catch(err => {
        console.error("Error fetching previous concept:", err);
    });
}



function nextConcept() {
    fetch('/concept-history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            direction: "next",
            language: document.getElementById('languageSelect').value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.query) {
            document.getElementById('conceptInput').value = data.query;
            askConcept();  // auto triggers learning of next suggested topic
        } else {
            alert("No next concept suggested.");
        }
    })
    .catch(err => {
        console.error("Error fetching next concept:", err);
    });
}





function speakInput() {
    const language = document.getElementById('languageSelect').value;
    const inputField = document.getElementById('conceptInput');

    let recognitionLang = 'en-IN';
    if (language === "Hindi") recognitionLang = 'hi-IN';
    else if (language === "Gujarati") recognitionLang = 'gu-IN';

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = recognitionLang;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    inputField.placeholder = "🎤 Listening... (" + language + ")";
    inputField.classList.add("listening");

    recognition.start();

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        inputField.value = transcript;
        inputField.placeholder = "Enter concept to learn";
        inputField.classList.remove("listening");
        askConcept();
    };

    recognition.onerror = function (event) {
        console.error("Speech Recognition Error:", event.error);
        inputField.placeholder = "Could not recognize. Try again!";
        inputField.classList.remove("listening");
    };

    recognition.onend = function () {
        if (!inputField.value) {
            inputField.placeholder = "Enter concept to learn";
            inputField.classList.remove("listening");
        }
    };
}

function toggleReadAnswerAloud() {
    const language = document.getElementById('languageSelect').value;
    const answerText = document.getElementById('botAnswer').innerText.trim();
    const readBtn = document.getElementById('readButton');

    if (!answerText) {
        alert("Answer is empty. Please ask a question first.");
        return;
    }

    let langCode = 'en-IN';
    if (language === "Hindi") langCode = 'hi-IN';
    else if (language === "Gujarati") langCode = 'gu-IN';

    if (isSpeaking) {
        window.speechSynthesis.cancel();
        isSpeaking = false;
        readBtn.innerText = "🔊 Read Aloud";
        return;
    }

    currentUtterance = new SpeechSynthesisUtterance(answerText);
    currentUtterance.lang = langCode;
    currentUtterance.rate = 0.95;
    currentUtterance.pitch = 1.05;

    currentUtterance.onstart = () => {
        isSpeaking = true;
        readBtn.innerText = "⏹ Stop Reading";
    };

    currentUtterance.onend = () => {
        isSpeaking = false;
        readBtn.innerText = "🔊 Read Aloud";
    };

    currentUtterance.onerror = () => {
        isSpeaking = false;
        readBtn.innerText = "🔊 Read Aloud";
        console.error("Speech synthesis failed.");
    };

    window.speechSynthesis.speak(currentUtterance);
}

function quizMe() {
    const content = document.getElementById('botAnswer').innerText;
    const quizSection = document.getElementById('quiz-section');
    const language = document.getElementById('languageSelect').value;

    if (!content.trim()) {
        quizSection.innerText = "Learn a concept first!";
        return;
    }

    quizSection.innerHTML = "<em>Generating interactive quiz...</em>";

    fetch('/check-quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: content, language })
    })
        .then(res => res.json())
        .then(data => {

            console.log("🧪 Quiz response:", data);

            if (!data.questions || data.questions.length === 0) {
                quizSection.innerHTML = "<em>Could not load quiz questions.</em>";
                return;
            }

            let quizHTML = '<form id="quizForm">';
            data.questions.forEach((q, idx) => {
                quizHTML += `<div class="quiz-question">
                    <p><strong>Q${idx + 1}. ${q.question}</strong></p>`;
                q.options.forEach(opt => {
                    const optId = `q${idx}_${opt.replace(/\s/g, '')}`;
                    quizHTML += `
                        <label for="${optId}">
                            <input type="radio" name="q${idx}" id="${optId}" value="${opt}"> ${opt}
                        </label><br>`;
                });
                quizHTML += `<div class="feedback" id="feedback${idx}"></div></div><hr>`;
            });

            quizHTML += '<button type="submit" class="btn green">Submit Quiz</button></form>';
            quizSection.innerHTML = quizHTML;

            document.getElementById('quizForm').onsubmit = function (e) {
                e.preventDefault();
                let score = 0;

                data.questions.forEach((q, idx) => {
                    const radios = document.getElementsByName(`q${idx}`);
                    let selected = null;
                    for (let r of radios) {
                        if (r.checked) {
                            selected = r.value;
                            break;
                        }
                    }

                    const feedbackDiv = document.getElementById(`feedback${idx}`);
                    if (!selected) {
                        feedbackDiv.innerHTML = "<span style='color: orange;'>You didn't select an answer.</span>";
                    } else if (selected === q.correct) {
                        feedbackDiv.innerHTML = `<span style='color: green;'>✅ ${q.explanation?.correct || "Correct!"}</span>`;
                        score++;
                    } else {
                        feedbackDiv.innerHTML = `<span style='color: red;'>❌ ${q.explanation?.wrong || "Incorrect."}</span><br><strong>✅ Correct:</strong> ${q.correct}`;

                    }
                });

                quizSection.innerHTML += `<p><strong>You got ${score} out of ${data.questions.length} correct.</strong></p>`;
            };
        })
        .catch(err => {
            console.error(err);
            quizSection.innerText = "Quiz could not be generated.";
        });
}

let currentUserLevel = "Beginner";
let currentUserCount = 0;

window.onload = function () {
    const levelFromServer = document.body.getAttribute('data-level');
    const countFromServer = parseInt(document.body.getAttribute('data-count'), 10);

    if (levelFromServer) currentUserLevel = levelFromServer;
    if (!isNaN(countFromServer)) currentUserCount = countFromServer;

    updateProgressBar(currentUserLevel, currentUserCount);
};
