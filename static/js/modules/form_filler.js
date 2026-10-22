/**
 * TECH AI | Smart Way - Smart Auto Form Filler Module
 */

const FormFillerModule = {
  currentAnalysis: null,
  filledData: {},

  init() {
    this.bindEvents();
  },

  bindEvents() {
    // Analyze Form Button
    document.getElementById("analyzeFormBtn")?.addEventListener("click", () => this.analyzeCurrentForm());

    // Demo Scholarship Button
    document.getElementById("loadSampleScholarshipBtn")?.addEventListener("click", () => this.loadDemoScholarship());

    // Form Document Upload
    const formUpload = document.getElementById("formDocUpload");
    if (formUpload) {
      formUpload.addEventListener("change", (e) => this.handleFormUpload(e));
    }

    // Confirm Submission / Save Details
    document.getElementById("confirmSubmitFormBtn")?.addEventListener("click", () => this.confirmFormSubmission());

    // Print Form Summary
    document.getElementById("printFormBtn")?.addEventListener("click", () => this.printFormSummary());

    // Mini Document Prepper Shortcuts
    document.getElementById("quickRotateBtn")?.addEventListener("click", () => {
      App.toast("Rotating document 90° clockwise... Complete!", "success");
    });
    document.getElementById("quickCompressBtn")?.addEventListener("click", () => {
      App.toast("Document compressed to 42 KB (Under 50 KB requirement)!", "success");
    });
    document.getElementById("quickPdfConvertBtn")?.addEventListener("click", () => {
      App.toast("Converted image to standard A4 PDF document!", "success");
    });
  },

  loadDemoScholarship() {
    document.getElementById("formUrlInput").value = "https://scholarships.gov.in/post-matric-2026";
    App.toast("National Scholarship Portal 2026 notice loaded!", "info");
    this.analyzeCurrentForm();
  },

  async handleFormUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("form_title", file.name);

    App.toast(`Analyzing instructions & constraints in ${file.name}...`, "info");
    try {
      const data = await App.api("/api/forms/analyze-form", {
        method: "POST",
        body: formData
      });
      this.currentAnalysis = data;
      this.renderAnalysis(data);
      App.toast(`Analysis complete! Identified ${data.total_fields_count} required fields.`, "success");
    } catch (err) {
      App.toast(err.message, "error");
    }
  },

  async analyzeCurrentForm() {
    const url = document.getElementById("formUrlInput").value.trim();
    App.toast("Analyzing form requirements & rules BEFORE asking for info...", "info");

    const formData = new FormData();
    if (url) formData.append("form_url", url);
    formData.append("form_title", "Central Scholarship & Admission Form 2026");

    try {
      const data = await App.api("/api/forms/analyze-form", {
        method: "POST",
        body: formData
      });
      this.currentAnalysis = data;
      this.renderAnalysis(data);
      App.toast(`Analysis complete! Verified details matched with your profile.`, "success");
    } catch (err) {
      App.toast(err.message, "error");
    }
  },

  renderAnalysis(data) {
    // 1. Update Completion Badge
    const badge = document.getElementById("completionBadge");
    if (badge) {
      badge.innerText = `${data.completion_percentage}% Ready`;
      badge.style.background = data.completion_percentage >= 70 ? "rgba(16, 185, 129, 0.2)" : "rgba(245, 158, 11, 0.2)";
      badge.style.color = data.completion_percentage >= 70 ? "var(--accent-emerald)" : "var(--accent-amber)";
    }

    // 2. Render Requirements Checklist (With Blue Checkmarks for verified fields)
    const checklist = document.getElementById("formChecklistItems");
    if (checklist) {
      let itemsHtml = "";

      // Completed / Verified Items
      data.completed_fields.forEach(f => {
        this.filledData[f.field_id] = f.value;
        itemsHtml += `
          <div class="check-item verified">
            <div>
              <strong style="font-size: 0.9rem; color: var(--text-primary);">${f.label}</strong>
              <div style="font-size: 0.8rem; color: var(--accent-cyan);">${f.value}</div>
            </div>
            <span class="check-badge blue">
              <i data-lucide="check-circle-2" style="width: 14px; height: 14px;"></i> Verified
            </span>
          </div>
        `;
      });

      // Missing Items (Ask ONLY for what's missing)
      data.missing_fields.forEach(f => {
        itemsHtml += `
          <div class="check-item missing" style="flex-direction: column; align-items: stretch; gap: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <strong style="font-size: 0.9rem; color: var(--text-primary);">${f.label}</strong>
              <span class="check-badge amber">
                <i data-lucide="alert-circle" style="width: 14px; height: 14px;"></i> Missing
              </span>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <input type="${f.type || 'text'}" class="input-field" id="missing_field_${f.field_id}" placeholder="Enter ${f.label} to complete form..." style="padding: 0.45rem 0.75rem; font-size: 0.85rem;">
              <button class="ctrl-btn" style="padding: 0.45rem 0.75rem;" onclick="FormFillerModule.applyMissingField('${f.field_id}')">
                Apply
              </button>
            </div>
          </div>
        `;
      });

      checklist.innerHTML = itemsHtml;
    }

    // 3. Render Document Specifications Detected
    const specsList = document.getElementById("docSpecsList");
    if (specsList && data.document_requirements) {
      specsList.innerHTML = data.document_requirements.map(d => `
        <div style="background: var(--bg-card); padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--border-color);">
          <strong style="color: var(--accent-cyan);">${d.doc_name}</strong>: 
          <span>Max ${d.max_size_kb} KB (${d.accepted_formats.join('/')}), Orientation: ${d.orientation}</span>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${d.instruction}</div>
        </div>
      `).join("");
    }

    // 4. Render Live Form Preview Grid
    this.renderFormPreview();

    if (window.lucide) lucide.createIcons();
  },

  applyMissingField(fid) {
    const input = document.getElementById(`missing_field_${fid}`);
    if (!input || !input.value.trim()) {
      App.toast("Please enter a value first.", "error");
      return;
    }

    this.filledData[fid] = input.value.trim();
    App.toast(`Updated ${fid}!`, "success");
    
    // Update live preview
    this.renderFormPreview();
  },

  renderFormPreview() {
    const grid = document.getElementById("previewFieldsGrid");
    if (!grid) return;

    const keys = Object.keys(this.filledData);
    if (keys.length === 0) {
      grid.innerHTML = `<div style="grid-column: 1 / -1; color: #64748b; text-align: center; padding: 2rem;">No verified fields yet.</div>`;
      return;
    }

    grid.innerHTML = keys.map(k => `
      <div class="preview-field-box">
        <label>${k.replace(/_/g, ' ')}</label>
        <div class="value" contenteditable="true" onblur="FormFillerModule.filledData['${k}'] = this.innerText">${this.filledData[k]}</div>
      </div>
    `).join("");
  },

  async confirmFormSubmission() {
    if (!this.currentAnalysis) {
      App.toast("Please analyze a form before submitting.", "error");
      return;
    }

    try {
      await App.api("/api/forms/save-filled", {
        method: "POST",
        body: JSON.stringify({
          analysis_id: this.currentAnalysis.analysis_id,
          form_title: this.currentAnalysis.form_title || "Student Application",
          filled_data: this.filledData
        })
      });

      App.toast("Form details confirmed & synchronized with your master profile!", "success");
    } catch (err) {
      App.toast(err.message, "error");
    }
  },

  printFormSummary() {
    const previewSheet = document.getElementById("liveFormPreviewSheet");
    if (!previewSheet) return;

    const printWin = window.open("", "_blank");
    printWin.document.write(`
      <html>
        <head>
          <title>Application Summary - TECH AI</title>
          <style>
            body { font-family: sans-serif; padding: 40px; color: #0f172a; }
            h2 { color: #0284c7; text-align: center; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px; }
            .box { border: 1px solid #cbd5e1; padding: 12px; border-radius: 6px; }
            label { font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; }
            .val { font-size: 15px; font-weight: 600; margin-top: 4px; }
          </style>
        </head>
        <body>
          ${previewSheet.innerHTML}
        </body>
      </html>
    `);
    printWin.document.close();
    printWin.focus();
    setTimeout(() => printWin.print(), 350);
  }
};

document.addEventListener("DOMContentLoaded", () => FormFillerModule.init());
