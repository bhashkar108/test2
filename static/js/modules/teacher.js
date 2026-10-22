/**
 * TECH AI | Smart Way - AI Teacher & Smart Notesbook Module
 * Features:
 * - Web Speech API (TTS & SpeechRecognition)
 * - Karaoke-style word & sentence highlighting with synchronized scrolling
 * - Reactive visual glowing orb & audio waves (animates only when speech is active)
 * - Speech rate controls (0.75x, 1x, 1.25x, 1.5x), repeat, pause, resume
 * - Voice commands: 'stop', 'ruko', 'repeat', 'aage bolo', 'continue', 'done'
 * - Difficult word pronunciation & 1-3 word chunk explanations
 * - Smart Notesbook persistence
 */

const TeacherModule = {
  synth: window.speechSynthesis,
  recognition: null,
  currentUtterance: null,
  isPlaying: false,
  isPaused: false,
  currentSentenceIdx: 0,
  currentWordIdx: 0,
  sentences: [],
  currentLessonData: null,
  speechRate: 1.0,
  isListeningCommands: false,

  init() {
    this.bindEvents();
    this.setupSpeechRecognition();
  },

  bindEvents() {
    // Start Learning Button
    const startBtn = document.getElementById("startLearningBtn");
    if (startBtn) {
      startBtn.addEventListener("click", () => this.startLesson());
    }

    // Sample Topic Loader
    const sampleBtn = document.getElementById("loadSampleStudyBtn");
    if (sampleBtn) {
      sampleBtn.addEventListener("click", () => this.loadSampleMaterial());
    }

    // PDF / Text File Upload for AI Teacher
    const uploadInput = document.getElementById("teacherDocUpload");
    if (uploadInput) {
      uploadInput.addEventListener("change", (e) => this.handleFileUpload(e));
    }

    // Playback Controls
    document.getElementById("speechPlayPauseBtn")?.addEventListener("click", () => this.togglePlayPause());
    document.getElementById("speechStopBtn")?.addEventListener("click", () => this.stopSpeech());
    document.getElementById("speechRepeatBtn")?.addEventListener("click", () => this.repeatCurrentSentence());
    document.getElementById("speechNextBtn")?.addEventListener("click", () => this.nextSentence());
    document.getElementById("speechPrevBtn")?.addEventListener("click", () => this.prevSentence());

    // Speed Rate Selector
    const speedSelect = document.getElementById("speechRateSelect");
    if (speedSelect) {
      speedSelect.addEventListener("change", (e) => {
        this.speechRate = parseFloat(e.target.value);
        if (this.isPlaying) {
          this.speakCurrentSentence();
        }
      });
    }

    // Persistent Voice Command Mic Toggle
    document.getElementById("voiceCommandToggle")?.addEventListener("click", () => this.toggleVoiceCommands());

    // Save Note Button
    document.getElementById("saveCurrentNoteBtn")?.addEventListener("click", () => this.saveCurrentNote());
  },

  loadSampleMaterial() {
    const sampleText = `Photosynthesis is the biological process by which green plants, algae, and certain bacteria convert sunlight energy into chemical energy stored in glucose. 
Chlorophyll, the green pigment located inside plant chloroplasts, absorbs blue and red wavelengths of light while reflecting green. 
During the light-dependent reactions in the thylakoid membrane, water molecules (H2O) are split into oxygen and protons, releasing ATP energy. 
Then, in the light-independent Calvin cycle within the stroma, carbon dioxide (CO2) is fixed and reduced to synthesize high-energy carbohydrates like glucose.`;
    
    document.getElementById("teacherStudyText").value = sampleText;
    App.toast("Sample physics/biology lesson loaded!", "info");
  },

  async handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    App.toast(`Extracting text from ${file.name}...`, "info");
    try {
      const res = await App.api("/api/teacher/upload-study-material", {
        method: "POST",
        body: formData
      });
      document.getElementById("teacherStudyText").value = res.text;
      App.toast(`Extracted ${res.length} characters from ${file.name}!`, "success");
    } catch (err) {
      App.toast(err.message, "error");
    }
  },

  async startLesson() {
    const text = document.getElementById("teacherStudyText").value.trim();
    if (!text) {
      App.toast("Please enter or upload study notes first.", "error");
      return;
    }

    const difficulty = document.getElementById("teacherDifficulty")?.value || "medium";
    const language = App.state.language || "hinglish";

    App.toast("AI Teacher is analyzing and preparing your lesson...", "info");
    document.getElementById("lessonStatusDisplay").innerText = "AI Teacher is preparing explanation...";

    try {
      const data = await App.api("/api/teacher/explain", {
        method: "POST",
        body: JSON.stringify({
          text: text,
          language: language,
          difficulty: difficulty,
          title: "Study Lesson"
        })
      });

      this.currentLessonData = data;
      this.renderLesson(data);
      this.prepareKaraoke(data.teacher_narration);
      this.playSpeech();
    } catch (err) {
      App.toast(err.message, "error");
    }
  },

  renderLesson(data) {
    document.getElementById("lessonTitleDisplay").innerText = data.title || "Lesson in Progress";
    document.getElementById("lessonStatusDisplay").innerText = "Speaking: Step-by-Step Lesson";

    // Render Steps
    const stepsContainer = document.getElementById("stepsContainer");
    if (stepsContainer && data.steps) {
      stepsContainer.innerHTML = data.steps.map(step => `
        <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem;">
            <span style="width: 24px; height: 24px; border-radius: 50%; background: var(--accent-cyan); color: #0a0f1d; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 800;">
              ${step.step_number}
            </span>
            <h4 style="font-size: 0.95rem; font-weight: 700; color: var(--text-primary);">${step.title}</h4>
          </div>
          <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">${step.explanation}</p>
        </div>
      `).join("");
    }

    // Render Difficult Words
    const wordsContainer = document.getElementById("difficultWordsTags");
    if (wordsContainer && data.difficult_words) {
      wordsContainer.innerHTML = data.difficult_words.map(w => `
        <div class="ctrl-btn" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;" onclick="TeacherModule.pronounceWord('${w.word}', '${w.chunk_meaning}')">
          <i data-lucide="volume-2" style="width: 14px; height: 14px;"></i>
          <strong>${w.word}</strong>: ${w.chunk_meaning} (${w.pronunciation})
        </div>
      `).join("");
      if (window.lucide) lucide.createIcons();
    }
  },

  // Prepare text into sentences and clickable words for karaoke
  prepareKaraoke(narration) {
    const container = document.getElementById("karaokeContainer");
    if (!container) return;

    // Remove pause markers for cleaner visual reading while retaining audio pacing
    const cleanNarration = narration.replace(/\[pause\]/gi, " ... ");
    
    // Split into sentences
    const rawSentences = cleanNarration.match(/[^.!?]+[.!?]+(\s|$)|[^.!?]+$/g) || [cleanNarration];
    this.sentences = rawSentences.map(s => s.trim()).filter(s => s.length > 0);
    this.currentSentenceIdx = 0;

    let html = "";
    this.sentences.forEach((sentence, sIdx) => {
      const words = sentence.split(/\s+/);
      const wordsHtml = words.map((w, wIdx) => `
        <span class="karaoke-word" id="word-${sIdx}-${wIdx}">${w}</span>
      `).join(" ");

      html += `<p class="karaoke-sentence" id="sentence-${sIdx}" style="margin-bottom: 0.75rem;">${wordsHtml}</p>`;
    });

    container.innerHTML = html;
  },

  // Play Speech via Web Speech API
  playSpeech() {
    if (!this.synth) {
      App.toast("Speech synthesis not supported in this browser.", "error");
      return;
    }

    this.isPlaying = true;
    this.isPaused = false;
    this.updateOrbAndWaves(true);
    this.updatePlayBtn(true);
    this.speakCurrentSentence();
  },

  speakCurrentSentence() {
    if (this.currentSentenceIdx >= this.sentences.length) {
      this.stopSpeech();
      App.toast("Lesson explanation completed!", "success");
      return;
    }

    this.synth.cancel();

    const sentence = this.sentences[this.currentSentenceIdx];
    this.highlightActiveSentence(this.currentSentenceIdx);

    const utterance = new SpeechSynthesisUtterance(sentence);
    utterance.rate = this.speechRate;
    utterance.pitch = 1.0;

    // Pick best voice (Hindi or Indian English or English)
    const voices = this.synth.getVoices();
    const langMode = App.state.language;
    let selectedVoice = null;

    if (langMode === "hi") {
      selectedVoice = voices.find(v => v.lang.includes("hi") || v.lang.includes("IN"));
    } else {
      selectedVoice = voices.find(v => v.lang === "en-IN") || voices.find(v => v.lang.startsWith("en"));
    }
    if (selectedVoice) utterance.voice = selectedVoice;

    // Karaoke word boundary tracking
    utterance.onboundary = (event) => {
      if (event.name === "word") {
        const textBefore = sentence.substring(0, event.charIndex);
        const wordIndex = textBefore.trim().split(/\s+/).filter(Boolean).length;
        this.highlightActiveWord(this.currentSentenceIdx, wordIndex);
      }
    };

    utterance.onend = () => {
      if (this.isPlaying && !this.isPaused) {
        this.currentSentenceIdx++;
        // Small pause between sentences for teacher pacing
        setTimeout(() => this.speakCurrentSentence(), 400);
      }
    };

    utterance.onerror = (e) => {
      console.warn("Speech error:", e);
      this.updateOrbAndWaves(false);
    };

    this.currentUtterance = utterance;
    this.synth.speak(utterance);
    this.updateProgressLabel();
  },

  highlightActiveSentence(sIdx) {
    document.querySelectorAll(".karaoke-sentence").forEach(el => el.classList.remove("active-sentence"));
    const activeEl = document.getElementById(`sentence-${sIdx}`);
    if (activeEl) {
      activeEl.classList.add("active-sentence");
      activeEl.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  },

  highlightActiveWord(sIdx, wIdx) {
    document.querySelectorAll(".karaoke-word").forEach(el => el.classList.remove("active-word"));
    const wordEl = document.getElementById(`word-${sIdx}-${wIdx}`);
    if (wordEl) {
      wordEl.classList.add("active-word");
    }
  },

  updateProgressLabel() {
    const total = this.sentences.length;
    const current = this.currentSentenceIdx + 1;
    const pct = total > 0 ? Math.min(100, Math.round((current / total) * 100)) : 0;
    const label = document.getElementById("readingProgressLabel");
    if (label) label.innerText = `${pct}%`;
  },

  togglePlayPause() {
    if (!this.isPlaying) {
      if (this.sentences.length > 0) {
        this.playSpeech();
      } else {
        this.startLesson();
      }
      return;
    }

    if (this.isPaused) {
      this.synth.resume();
      this.isPaused = false;
      this.updateOrbAndWaves(true);
      this.updatePlayBtn(true);
    } else {
      this.synth.pause();
      this.isPaused = true;
      this.updateOrbAndWaves(false);
      this.updatePlayBtn(false);
    }
  },

  stopSpeech() {
    if (this.synth) this.synth.cancel();
    this.isPlaying = false;
    this.isPaused = false;
    this.updateOrbAndWaves(false);
    this.updatePlayBtn(false);
    document.querySelectorAll(".karaoke-word").forEach(el => el.classList.remove("active-word"));
  },

  repeatCurrentSentence() {
    this.speakCurrentSentence();
  },

  nextSentence() {
    if (this.currentSentenceIdx < this.sentences.length - 1) {
      this.currentSentenceIdx++;
      this.speakCurrentSentence();
    }
  },

  prevSentence() {
    if (this.currentSentenceIdx > 0) {
      this.currentSentenceIdx--;
      this.speakCurrentSentence();
    }
  },

  pronounceWord(word, meaning) {
    if (!this.synth) return;
    this.synth.cancel();
    const utterance = new SpeechSynthesisUtterance(`${word}. It means: ${meaning}`);
    utterance.rate = 0.85; // Slower for clarity
    this.synth.speak(utterance);
    App.toast(`Pronouncing "${word}": ${meaning}`, "info");
  },

  updateOrbAndWaves(active) {
    const orb = document.getElementById("teacherVoiceOrb");
    const waves = document.getElementById("audioWaveVisualizer");
    if (active) {
      orb?.classList.add("speaking");
      waves?.classList.add("speaking");
    } else {
      orb?.classList.remove("speaking");
      waves?.classList.remove("speaking");
    }
  },

  updatePlayBtn(isPlaying) {
    const icon = document.getElementById("playPauseIcon");
    const label = document.getElementById("playPauseLabel");
    if (isPlaying) {
      icon?.setAttribute("data-lucide", "pause");
      if (label) label.innerText = "Pause";
    } else {
      icon?.setAttribute("data-lucide", "play");
      if (label) label.innerText = "Play";
    }
    if (window.lucide) lucide.createIcons();
  },

  // Setup Browser Web Speech Recognition for Voice Commands
  setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("Speech recognition not supported in this browser.");
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = false;
    this.recognition.lang = "en-IN"; // English + Indian accent commands

    this.recognition.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
      console.log("Voice Command Recognized:", transcript);
      this.handleVoiceCommand(transcript);
    };

    this.recognition.onerror = (e) => {
      console.warn("Recognition error:", e);
    };
  },

  toggleVoiceCommands() {
    const micBtn = document.getElementById("voiceCommandToggle");
    const micLabel = document.getElementById("voiceMicStatus");

    if (!this.recognition) {
      App.toast("Voice recognition not supported in your browser.", "error");
      return;
    }

    if (this.isListeningCommands) {
      this.recognition.stop();
      this.isListeningCommands = false;
      micBtn?.classList.remove("active");
      if (micLabel) micLabel.innerText = "Voice Cmds";
      App.toast("Voice commands deactivated", "info");
    } else {
      try {
        this.recognition.start();
        this.isListeningCommands = true;
        micBtn?.classList.add("active");
        if (micLabel) micLabel.innerText = "Listening...";
        App.toast("Listening for commands: 'stop', 'ruko', 'repeat', 'continue', 'aage bolo', 'done'", "success");
      } catch (err) {
        console.error("Recognition start err:", err);
      }
    }
  },

  handleVoiceCommand(cmd) {
    App.toast(`Voice Command: "${cmd}"`, "info");

    if (cmd.includes("stop") || cmd.includes("ruko") || cmd.includes("ruk")) {
      this.togglePlayPause();
    } else if (cmd.includes("repeat") || cmd.includes("fir se") || cmd.includes("dobara")) {
      this.repeatCurrentSentence();
    } else if (cmd.includes("continue") || cmd.includes("chalo") || cmd.includes("play")) {
      if (this.isPaused) this.togglePlayPause();
    } else if (cmd.includes("aage bolo") || cmd.includes("next") || cmd.includes("aage")) {
      this.nextSentence();
    } else if (cmd.includes("done") || cmd.includes("khatam") || cmd.includes("finish")) {
      this.stopSpeech();
    }
  },

  // Smart Notesbook
  async saveCurrentNote() {
    if (!this.currentLessonData) {
      App.toast("Please start or generate a lesson before saving notes.", "error");
      return;
    }

    const title = this.currentLessonData.title || "Lesson Summary";
    const summary = this.currentLessonData.quick_summary || "";
    const explanation = this.currentLessonData.teacher_narration || "";
    const keyPoints = this.currentLessonData.steps?.map(s => s.explanation) || [];

    try {
      await App.api("/api/teacher/notes", {
        method: "POST",
        body: JSON.stringify({
          title: title,
          summary: summary,
          teacher_explanation: explanation.substring(0, 500),
          key_points: keyPoints,
          tags: "AI Teacher"
        })
      });
      App.toast("Note saved to Smart Notesbook!", "success");
      this.loadNotes();
    } catch (err) {
      App.toast(err.message, "error");
    }
  },

  async loadNotes() {
    try {
      const notes = await App.api("/api/teacher/notes");
      const listEl = document.getElementById("notesbookList");
      if (!listEl) return;

      if (notes.length === 0) {
        listEl.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 1.5rem 0;">No notes saved yet. Click "Save Lesson Note" to persist your notes!</div>`;
        return;
      }

      listEl.innerHTML = notes.map(n => `
        <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 0.75rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
            <h5 style="font-size: 0.85rem; font-weight: 700; color: var(--accent-cyan);">${n.title}</h5>
            <button class="icon-btn" style="width: 24px; height: 24px;" onclick="TeacherModule.deleteNote(${n.id})" title="Delete Note">
              <i data-lucide="trash-2" style="width: 13px; height: 13px;"></i>
            </button>
          </div>
          <p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4;">${n.summary || n.teacher_explanation || ""}</p>
        </div>
      `).join("");

      if (window.lucide) lucide.createIcons();
    } catch (err) {
      console.warn("Failed to load notes:", err);
    }
  },

  async deleteNote(id) {
    try {
      await App.api(`/api/teacher/notes/${id}`, { method: "DELETE" });
      App.toast("Note removed", "info");
      this.loadNotes();
    } catch (err) {
      App.toast(err.message, "error");
    }
  }
};

document.addEventListener("DOMContentLoaded", () => TeacherModule.init());
