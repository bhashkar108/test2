/**
 * TECH AI | Smart Way - Auto Quiz Generator Module
 */

const QuizModule = {
  questions: [],
  currentIdx: 0,
  score: 0,
  currentTopic: "",
  userAnswers: [],

  init() {
    this.bindEvents();
  },

  bindEvents() {
    document.getElementById("generateQuizBtn")?.addEventListener("click", () => this.generateQuiz());
    document.getElementById("quizNextBtn")?.addEventListener("click", () => this.nextQuestion());
    document.getElementById("quizHintBtn")?.addEventListener("click", () => this.showHint());
    document.getElementById("retakeQuizBtn")?.addEventListener("click", () => this.retakeQuiz());
    document.getElementById("reviewAnswersBtn")?.addEventListener("click", () => {
      App.toast("Quiz results saved to your progress dashboard!", "success");
      const progTab = document.querySelector('[data-tab="tab-progress"]');
      if (progTab) progTab.click();
    });
  },

  async generateQuiz() {
    let topic = document.getElementById("quizTopicInput").value.trim();
    if (!topic) {
      // Check if text is present in AI Teacher study input
      const teacherText = document.getElementById("teacherStudyText")?.value.trim();
      topic = teacherText || "General Engineering & Science Fundamentals";
    }

    this.currentTopic = topic;
    App.toast("AI is formulating conceptual MCQs...", "info");

    try {
      const data = await App.api("/api/quiz/generate", {
        method: "POST",
        body: JSON.stringify({
          topic_or_content: topic,
          num_questions: 5,
          language: App.state.language || "en"
        })
      });

      this.questions = data.questions || [];
      if (this.questions.length === 0) {
        App.toast("Could not generate questions. Please try another topic.", "error");
        return;
      }

      this.currentIdx = 0;
      this.score = 0;
      this.userAnswers = [];

      document.getElementById("quizPlayCard").style.display = "block";
      document.getElementById("quizResultCard").style.display = "none";
      this.renderQuestion();
      App.toast("Quiz is ready! Good luck!", "success");
    } catch (err) {
      App.toast(err.message, "error");
    }
  },

  renderQuestion() {
    const q = this.questions[this.currentIdx];
    if (!q) return;

    document.getElementById("quizCounterLabel").innerText = `Question ${this.currentIdx + 1} of ${this.questions.length}`;
    document.getElementById("quizQuestionText").innerText = q.question;
    document.getElementById("quizScoreLabel").innerText = `Score: ${this.score}`;
    document.getElementById("quizExplanationBox").style.display = "none";
    document.getElementById("quizNextBtn").style.display = "none";

    const container = document.getElementById("quizOptionsContainer");
    if (!container) return;

    const letters = ["A", "B", "C", "D"];
    container.innerHTML = q.options.map((opt, idx) => `
      <div class="quiz-option-card" id="q_opt_${idx}" onclick="QuizModule.selectOption(${idx})">
        <div class="quiz-opt-letter">${letters[idx]}</div>
        <div style="flex: 1;">${opt}</div>
      </div>
    `).join("");
  },

  selectOption(chosenIdx) {
    const q = this.questions[this.currentIdx];
    if (!q) return;

    // Prevent re-selection
    const options = document.querySelectorAll(".quiz-option-card");
    options.forEach(opt => opt.onclick = null);

    const isCorrect = (chosenIdx === q.correct_answer_index);
    if (isCorrect) {
      this.score++;
      document.getElementById(`q_opt_${chosenIdx}`)?.classList.add("correct");
      App.toast("Correct answer! +1 point", "success");
    } else {
      document.getElementById(`q_opt_${chosenIdx}`)?.classList.add("wrong");
      document.getElementById(`q_opt_${q.correct_answer_index}`)?.classList.add("correct");
      App.toast("Incorrect. Review the explanation below.", "error");
    }

    document.getElementById("quizScoreLabel").innerText = `Score: ${this.score}`;

    // Show explanation
    const expBox = document.getElementById("quizExplanationBox");
    const expText = document.getElementById("quizExplanationText");
    if (expBox && expText) {
      expBox.style.display = "block";
      expText.innerHTML = `<strong>Explanation:</strong> ${q.explanation || 'Verified conceptual answer.'}`;
    }

    document.getElementById("quizNextBtn").style.display = "inline-flex";

    this.userAnswers.push({
      question_id: q.id,
      chosen: chosenIdx,
      correct: q.correct_answer_index,
      is_correct: isCorrect
    });
  },

  showHint() {
    const q = this.questions[this.currentIdx];
    if (q && q.hint) {
      App.toast(`Hint: ${q.hint}`, "info");
    } else {
      App.toast("Analyze the relationship between the key terms in the question.", "info");
    }
  },

  nextQuestion() {
    this.currentIdx++;
    if (this.currentIdx < this.questions.length) {
      this.renderQuestion();
    } else {
      this.finishQuiz();
    }
  },

  async finishQuiz() {
    document.getElementById("quizPlayCard").style.display = "none";
    const resultCard = document.getElementById("quizResultCard");
    resultCard.style.display = "block";

    const total = this.questions.length;
    const pct = Math.round((this.score / total) * 100);

    const titleEl = document.getElementById("quizFinalTitle");
    const scoreEl = document.getElementById("quizFinalScore");

    if (titleEl) {
      titleEl.innerText = pct >= 80 ? "Mastery Achieved! 🌟" : pct >= 50 ? "Good Effort! 👍" : "Keep Practicing! 💡";
    }
    if (scoreEl) {
      scoreEl.innerText = `You scored ${this.score} out of ${total} (${pct}%)`;
    }

    // Submit to backend
    try {
      await App.api("/api/quiz/submit", {
        method: "POST",
        body: JSON.stringify({
          topic: this.currentTopic || "Quiz Assessment",
          score: this.score,
          total_questions: total,
          questions_data: this.userAnswers
        })
      });
    } catch (e) {
      console.warn("Quiz submit:", e);
    }
  },

  retakeQuiz() {
    this.generateQuiz();
  }
};

document.addEventListener("DOMContentLoaded", () => QuizModule.init());
