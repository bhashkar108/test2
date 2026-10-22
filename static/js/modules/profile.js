/**
 * TECH AI | Smart Way - Student Profile & Progress Analytics Module
 */

const ProfileModule = {
  chartInstance: null,

  init() {
    this.bindEvents();
  },

  bindEvents() {
    const profileForm = document.getElementById("studentProfileForm");
    if (profileForm) {
      profileForm.addEventListener("submit", (e) => this.saveProfile(e));
    }
  },

  async loadProfile() {
    try {
      const data = await App.api("/api/auth/me");
      const p = data.profile || {};
      const u = data.user || {};

      document.getElementById("profFullName").value = u.full_name || "";
      document.getElementById("profRollNumber").value = p.roll_number || "";
      document.getElementById("profFatherName").value = p.father_name || "";
      document.getElementById("profMotherName").value = p.mother_name || "";
      document.getElementById("profDob").value = p.dob || "";
      document.getElementById("profCategory").value = p.category || "General";
      document.getElementById("profCollege").value = p.college || "";
      document.getElementById("profBranch").value = p.branch || "";
      document.getElementById("profAcademicYear").value = p.academic_year || "";
      document.getElementById("profPhone").value = p.phone_number || "";
      document.getElementById("profVillage").value = p.village || "";
      document.getElementById("profDistrict").value = p.district || "";
      document.getElementById("profState").value = p.state || "";
      document.getElementById("profPinCode").value = p.pin_code || "";
      document.getElementById("profIncome").value = p.annual_income || "";
      document.getElementById("profAadhar").value = p.aadhar_last4 || "";
      document.getElementById("profBankAccount").value = p.bank_account || "";
      document.getElementById("profIfsc").value = p.ifsc_code || "";

      App.updateUserUI(u);
    } catch (err) {
      console.warn("Could not load profile:", err);
    }
  },

  async saveProfile(e) {
    e.preventDefault();

    const profileData = {
      roll_number: document.getElementById("profRollNumber").value.trim(),
      father_name: document.getElementById("profFatherName").value.trim(),
      mother_name: document.getElementById("profMotherName").value.trim(),
      dob: document.getElementById("profDob").value,
      category: document.getElementById("profCategory").value,
      college: document.getElementById("profCollege").value.trim(),
      branch: document.getElementById("profBranch").value.trim(),
      academic_year: document.getElementById("profAcademicYear").value.trim(),
      phone_number: document.getElementById("profPhone").value.trim(),
      village: document.getElementById("profVillage").value.trim(),
      district: document.getElementById("profDistrict").value.trim(),
      state: document.getElementById("profState").value.trim(),
      pin_code: document.getElementById("profPinCode").value.trim(),
      annual_income: document.getElementById("profIncome").value.trim(),
      aadhar_last4: document.getElementById("profAadhar").value.trim(),
      bank_account: document.getElementById("profBankAccount").value.trim(),
      ifsc_code: document.getElementById("profIfsc").value.trim(),
    };

    try {
      await App.api("/api/auth/profile", {
        method: "PUT",
        body: JSON.stringify(profileData)
      });
      App.toast("Student profile saved! Auto Form Filler will now use these verified details.", "success");
    } catch (err) {
      App.toast(err.message, "error");
    }
  },

  async loadProgress() {
    try {
      const summary = await App.api("/api/progress/summary");

      document.getElementById("statStreakDays").innerText = `${summary.streak_days} Days`;
      document.getElementById("statHoursLearned").innerText = `${summary.total_hours_learned} hrs`;
      document.getElementById("statQuizAccuracy").innerText = `${summary.quiz_accuracy}%`;
      document.getElementById("statFormsDone").innerText = summary.forms_count;

      this.renderProgressChart(summary.weekly_activity);
      this.loadRecentSessions();
    } catch (err) {
      console.warn("Could not load progress:", err);
    }
  },

  renderProgressChart(weeklyActivity) {
    const canvas = document.getElementById("progressActivityChart");
    if (!canvas || !window.Chart) return;

    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    const labels = weeklyActivity.map(a => a.day);
    const data = weeklyActivity.map(a => a.minutes);

    const isDark = (App.state.theme === "dark");
    const gridColor = isDark ? "#1e293b" : "#e2e8f0";
    const textColor = isDark ? "#94a3b8" : "#475569";

    this.chartInstance = new Chart(canvas, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Study Minutes",
          data: data,
          backgroundColor: "#38bdf8",
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: textColor }
          },
          y: {
            grid: { color: gridColor },
            ticks: { color: textColor }
          }
        }
      }
    });
  },

  async loadRecentSessions() {
    try {
      const sessions = await App.api("/api/teacher/sessions");
      const list = document.getElementById("progressSessionsList");
      if (!list) return;

      if (sessions.length === 0) {
        list.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 1.5rem 0;">No learning sessions yet.</div>`;
        return;
      }

      list.innerHTML = sessions.map(s => `
        <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 0.75rem;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <strong style="font-size: 0.85rem; color: var(--text-primary);">${s.title}</strong>
            <span class="nav-badge" style="font-size: 0.65rem;">${s.difficulty}</span>
          </div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">Speed: ${s.speed}x • ${new Date(s.updated_at).toLocaleDateString()}</div>
        </div>
      `).join("");
    } catch (e) {
      console.warn("Could not load sessions:", e);
    }
  }
};

document.addEventListener("DOMContentLoaded", () => ProfileModule.init());
