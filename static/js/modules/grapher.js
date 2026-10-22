/**
 * TECH AI | Smart Way - Equation Graph & Math Studio Module
 * Powered by math.js and HTML5 Canvas
 */

const GrapherModule = {
  canvas: null,
  ctx: null,
  scale: 40, // pixels per unit
  originX: 0,
  originY: 0,
  currentExpression: "x^2 - 4*x + 3",

  init() {
    this.canvas = document.getElementById("equationGraphCanvas");
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext("2d");

    this.resizeCanvas();
    window.addEventListener("resize", () => {
      this.resizeCanvas();
      this.render();
    });

    this.bindEvents();
    this.render();
  },

  resizeCanvas() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height || 420;
    this.originX = this.canvas.width / 2;
    this.originY = this.canvas.height / 2;
  },

  bindEvents() {
    // Plot Function Button
    document.getElementById("plotGraphBtn")?.addEventListener("click", () => {
      const expr = document.getElementById("graphFuncInput")?.value.trim();
      if (expr) this.plotFunction(expr);
    });

    // Preset buttons
    document.querySelectorAll("[data-preset]").forEach(btn => {
      btn.addEventListener("click", () => {
        const p = btn.getAttribute("data-preset");
        document.getElementById("graphFuncInput").value = p;
        this.plotFunction(p);
      });
    });

    // Zoom & Reset
    document.getElementById("graphZoomInBtn")?.addEventListener("click", () => {
      this.scale *= 1.25;
      this.render();
    });
    document.getElementById("graphZoomOutBtn")?.addEventListener("click", () => {
      this.scale = Math.max(10, this.scale / 1.25);
      this.render();
    });
    document.getElementById("graphResetViewBtn")?.addEventListener("click", () => {
      this.scale = 40;
      this.originX = this.canvas.width / 2;
      this.originY = this.canvas.height / 2;
      this.render();
    });

    // Mouse coordinate tracing
    if (this.canvas) {
      this.canvas.addEventListener("mousemove", (e) => this.handleMouseMove(e));
    }

    // Quadratic Solver Button
    document.getElementById("solveQuadraticBtn")?.addEventListener("click", () => this.solveQuadratic());
  },

  handleMouseMove(e) {
    const rect = this.canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const mathX = (mouseX - this.originX) / this.scale;
    const mathY = -(mouseY - this.originY) / this.scale;

    const badge = document.getElementById("graphCoordsBadge");
    if (badge) {
      badge.innerText = `x: ${mathX.toFixed(2)}, y: ${mathY.toFixed(2)}`;
    }
  },

  plotFunction(expr) {
    this.currentExpression = expr;
    this.render();
    App.toast(`Plotted f(x) = ${expr}`, "info");
  },

  render() {
    if (!this.canvas || !this.ctx) return;
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    // Clear
    ctx.clearRect(0, 0, w, h);

    // Draw grid
    this.drawGrid();

    // Draw Axes
    ctx.beginPath();
    ctx.strokeStyle = "#334155";
    ctx.lineWidth = 2;
    // X Axis
    ctx.moveTo(0, this.originY);
    ctx.lineTo(w, this.originY);
    // Y Axis
    ctx.moveTo(this.originX, 0);
    ctx.lineTo(this.originX, h);
    ctx.stroke();

    // Plot Curve
    this.drawCurve(this.currentExpression, "#38bdf8", 3);
  },

  drawGrid() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    ctx.lineWidth = 1;
    ctx.strokeStyle = "#172033";
    ctx.font = "10px Inter, sans-serif";
    ctx.fillStyle = "#64748b";

    // Vertical grid lines
    const startX = this.originX % this.scale;
    for (let x = startX; x < w; x += this.scale) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();

      const unitVal = Math.round((x - this.originX) / this.scale);
      if (unitVal !== 0) {
        ctx.fillText(unitVal, x - 4, this.originY + 14);
      }
    }

    // Horizontal grid lines
    const startY = this.originY % this.scale;
    for (let y = startY; y < h; y += this.scale) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();

      const unitVal = Math.round(-(y - this.originY) / this.scale);
      if (unitVal !== 0) {
        ctx.fillText(unitVal, this.originX + 6, y + 4);
      }
    }
  },

  drawCurve(exprString, color, lineWidth) {
    if (!window.math) return;
    const ctx = this.ctx;
    const w = this.canvas.width;

    let compiled;
    try {
      compiled = math.compile(exprString);
    } catch (err) {
      console.warn("Invalid math expression:", err);
      return;
    }

    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;

    let isFirst = true;

    for (let px = 0; px < w; px += 2) {
      const mathX = (px - this.originX) / this.scale;
      try {
        const mathY = compiled.evaluate({ x: mathX });
        if (typeof mathY === "number" && !isNaN(mathY) && isFinite(mathY)) {
          const py = this.originY - mathY * this.scale;
          if (isFirst) {
            ctx.moveTo(px, py);
            isFirst = false;
          } else {
            ctx.lineTo(px, py);
          }
        } else {
          isFirst = true;
        }
      } catch (e) {
        isFirst = true;
      }
    }

    ctx.stroke();
  },

  async solveQuadratic() {
    const a = parseFloat(document.getElementById("quadA").value || "1");
    const b = parseFloat(document.getElementById("quadB").value || "-4");
    const c = parseFloat(document.getElementById("quadC").value || "3");

    try {
      const res = await App.api("/api/math/solve-quadratic", {
        method: "POST",
        body: JSON.stringify({ a, b, c })
      });

      const resultsBox = document.getElementById("quadResultsBox");
      if (resultsBox) {
        resultsBox.innerHTML = `
          <div><strong>Equation:</strong> ${res.equation}</div>
          <div><strong>Discriminant D:</strong> ${res.discriminant}</div>
          <div><strong>Roots:</strong> ${res.roots.join(", ")}</div>
          <div><strong>Vertex:</strong> (${res.vertex.x}, ${res.vertex.y})</div>
          <div><strong>Y-Intercept:</strong> (0, ${res.y_intercept})</div>
        `;
      }

      // Plot this quadratic curve
      const cleanExpr = `${a}*x^2 + (${b})*x + (${c})`;
      document.getElementById("graphFuncInput").value = cleanExpr;
      this.plotFunction(cleanExpr);

      App.toast("Quadratic equation calculated & plotted!", "success");
    } catch (err) {
      App.toast(err.message, "error");
    }
  }
};

document.addEventListener("DOMContentLoaded", () => GrapherModule.init());
