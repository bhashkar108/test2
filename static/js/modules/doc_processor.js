/**
 * TECH AI | Smart Way - Smart Document Processor & Camera Capture Module
 */

const DocProcessorModule = {
  canvas: null,
  ctx: null,
  currentImage: null,
  rotationAngle: 0,
  mediaStream: null,

  init() {
    this.canvas = document.getElementById("documentCanvas");
    if (this.canvas) {
      this.ctx = this.canvas.getContext("2d");
    }
    this.bindEvents();
    this.loadDocumentsWorkspace();
  },

  bindEvents() {
    // Document Upload
    const uploadInput = document.getElementById("studioDocUpload");
    if (uploadInput) {
      uploadInput.addEventListener("change", (e) => this.handleImageUpload(e));
    }

    // Camera Capture Modal
    document.getElementById("openCameraCaptureBtn")?.addEventListener("click", () => this.openCamera());
    document.getElementById("closeCameraModalBtn")?.addEventListener("click", () => this.closeCamera());
    document.getElementById("snapPhotoBtn")?.addEventListener("click", () => this.capturePhoto());

    // Transformation Tools
    document.getElementById("canvasRotateRightBtn")?.addEventListener("click", () => this.rotate(90));
    document.getElementById("canvasRotateLeftBtn")?.addEventListener("click", () => this.rotate(-90));
    document.getElementById("canvasGrayscaleBtn")?.addEventListener("click", () => this.applyGrayscale());
    document.getElementById("canvasResetBtn")?.addEventListener("click", () => this.resetCanvas());

    // Quality Slider
    const compRange = document.getElementById("compressionRange");
    const compLabel = document.getElementById("compressionValueLabel");
    if (compRange && compLabel) {
      compRange.addEventListener("input", (e) => {
        compLabel.innerText = `${e.target.value}%`;
      });
    }

    // Download & Export
    document.getElementById("downloadProcessedBtn")?.addEventListener("click", () => this.downloadProcessed());
    document.getElementById("exportPdfBtn")?.addEventListener("click", () => this.exportAsPdf());

    // Mathematical Document Solver
    document.getElementById("solveMathDocBtn")?.addEventListener("click", () => this.solveMathDocument());
    document.getElementById("plotMathDocBtn")?.addEventListener("click", () => this.sendToGrapher());
  },

  handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        this.currentImage = img;
        this.rotationAngle = 0;
        this.renderCanvas();
        document.getElementById("canvasEmptyPlaceholder").style.display = "none";
        App.toast(`Loaded ${file.name} for processing`, "info");
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  },

  async openCamera() {
    const modal = document.getElementById("cameraModal");
    const video = document.getElementById("cameraVideo");
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      App.toast("Camera not supported or blocked in this browser.", "error");
      return;
    }

    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" }
      });
      video.srcObject = this.mediaStream;
      modal.classList.add("open");
    } catch (err) {
      App.toast("Unable to access camera: " + err.message, "error");
    }
  },

  closeCamera() {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
    document.getElementById("cameraModal")?.classList.remove("open");
  },

  capturePhoto() {
    const video = document.getElementById("cameraVideo");
    if (!video || !this.canvas) return;

    const tempCanvas = document.createElement("canvas");
    tempCanvas.width = video.videoWidth || 640;
    tempCanvas.height = video.videoHeight || 480;
    const tempCtx = tempCanvas.getContext("2d");
    tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);

    const img = new Image();
    img.onload = () => {
      this.currentImage = img;
      this.rotationAngle = 0;
      this.renderCanvas();
      document.getElementById("canvasEmptyPlaceholder").style.display = "none";
      this.closeCamera();
      App.toast("Document captured with camera!", "success");
    };
    img.src = tempCanvas.toDataURL("image/jpeg", 0.9);
  },

  renderCanvas() {
    if (!this.currentImage || !this.canvas || !this.ctx) return;

    const img = this.currentImage;
    const isRotated = (this.rotationAngle % 180 !== 0);

    const targetWidth = isRotated ? img.height : img.width;
    const targetHeight = isRotated ? img.width : img.height;

    // Scale down if massive
    const maxDim = 1200;
    let scale = 1;
    if (targetWidth > maxDim || targetHeight > maxDim) {
      scale = Math.min(maxDim / targetWidth, maxDim / targetHeight);
    }

    this.canvas.width = targetWidth * scale;
    this.canvas.height = targetHeight * scale;

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.save();
    this.ctx.translate(this.canvas.width / 2, this.canvas.height / 2);
    this.ctx.rotate((this.rotationAngle * Math.PI) / 180);
    this.ctx.drawImage(
      img,
      (-img.width * scale) / 2,
      (-img.height * scale) / 2,
      img.width * scale,
      img.height * scale
    );
    this.ctx.restore();
  },

  rotate(degrees) {
    if (!this.currentImage) return;
    this.rotationAngle = (this.rotationAngle + degrees) % 360;
    this.renderCanvas();
    App.toast(`Rotated to ${this.rotationAngle}°`, "info");
  },

  applyGrayscale() {
    if (!this.canvas || !this.ctx) return;
    const imgData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
    const data = imgData.data;

    for (let i = 0; i < data.length; i += 4) {
      const avg = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
      // High contrast thresholding
      const contrast = avg > 128 ? 255 : 0;
      data[i] = contrast;
      data[i + 1] = contrast;
      data[i + 2] = contrast;
    }
    this.ctx.putImageData(imgData, 0, 0);
    App.toast("Applied Black & White High Contrast filter!", "info");
  },

  resetCanvas() {
    this.rotationAngle = 0;
    this.renderCanvas();
  },

  downloadProcessed() {
    if (!this.canvas) return;
    const quality = (parseInt(document.getElementById("compressionRange")?.value || "85")) / 100;
    const link = document.createElement("a");
    link.download = "tech_ai_processed_document.jpg";
    link.href = this.canvas.toDataURL("image/jpeg", quality);
    link.click();
    App.toast("Processed document downloaded!", "success");
  },

  exportAsPdf() {
    if (!this.canvas) return;
    const dataUrl = this.canvas.toDataURL("image/jpeg", 0.9);
    const printWin = window.open("", "_blank");
    printWin.document.write(`
      <html>
        <head><title>Document PDF Export</title></head>
        <body style="margin:0; display:flex; justify-content:center; align-items:center; height:100vh; background:#000;">
          <img src="${dataUrl}" style="max-width:100%; max-height:100%;" />
        </body>
      </html>
    `);
    printWin.document.close();
    printWin.focus();
    setTimeout(() => printWin.print(), 350);
  },

  async solveMathDocument() {
    const eq = document.getElementById("mathDocInput").value.trim();
    if (!eq) {
      App.toast("Please enter an equation.", "error");
      return;
    }

    App.toast("AI Math Professor is solving equation...", "info");
    try {
      const res = await App.api("/api/math/solve", {
        method: "POST",
        body: JSON.stringify({ equation: eq })
      });

      document.getElementById("mathEquationStandard").innerText = `Standard Form: ${res.standard_form || eq}`;
      document.getElementById("mathRootsOutput").innerText = `Roots: ${(res.roots || []).join(', ')}`;

      const stepsList = document.getElementById("mathStepsList");
      if (stepsList && res.steps) {
        stepsList.innerHTML = res.steps.map(s => `
          <div><strong>Step ${s.step_num || s.step_number || ''}:</strong> ${s.action || ''} (${s.math || s.explanation || ''})</div>
        `).join("");
      }
      App.toast("Equation solved successfully!", "success");
    } catch (err) {
      App.toast(err.message, "error");
    }
  },

  sendToGrapher() {
    const eq = document.getElementById("mathDocInput").value.trim();
    // Switch to graph tab and set function
    const graphNav = document.querySelector('[data-tab="tab-graph"]');
    if (graphNav) graphNav.click();

    const graphInput = document.getElementById("graphFuncInput");
    if (graphInput) {
      graphInput.value = eq.replace(/=0/g, "").trim();
      if (window.GrapherModule) GrapherModule.plotFunction(graphInput.value);
    }
  },

  async loadDocumentsWorkspace() {
    try {
      const docs = await App.api("/api/docs/list");
      const list = document.getElementById("docsWorkspaceList");
      if (!list) return;

      if (docs.length === 0) {
        list.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 1rem 0;">No documents processed yet.</div>`;
        return;
      }

      list.innerHTML = docs.map(d => `
        <div style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 0.6rem 0.85rem; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-primary);">${d.original_name}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">${d.file_type} • ${d.file_size_kb} KB</div>
          </div>
          <a href="${d.download_url}" target="_blank" class="ctrl-btn" style="padding: 0.35rem 0.65rem; font-size: 0.75rem;">
            <i data-lucide="download"></i>
          </a>
        </div>
      `).join("");

      if (window.lucide) lucide.createIcons();
    } catch (e) {
      console.warn("Could not load docs list:", e);
    }
  }
};

document.addEventListener("DOMContentLoaded", () => DocProcessorModule.init());
