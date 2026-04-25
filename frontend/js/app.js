(() => {
  "use strict";

  const STORAGE_THEME = "doa-theme";
  const API_ROOT = (window.DOA_API_BASE || localStorage.getItem("doa-api-base") || "http://127.0.0.1:8000").replace(/\/+$/, "");
  const CONTENT_API_BASE = `${API_ROOT}/api/v1`;
  let diseases = null;

  initIcons();
  initTheme();
  initNav();
  initBackToTop();
  initRipple();
  initRevealSystem();
  initTiltCards();
  initHeroParallax();

  loadDiseases().catch(() => {
    diseases = {};
  }).then(() => {
    const page = document.body.dataset.page;
    if (page === "home") renderHomeDiseases();
    if (page === "diseases") initDiseasesPage();
    if (page === "diagnose") initDiagnosePage();
    if (page === "history") initHistoryPage();
    if (page === "about") initAboutPage();
    if (page === "safety") initSafetyPage();
    if (page === "education") initEducationPage();
  });

  function initIcons() {
    document.querySelectorAll("[data-icon]").forEach((el) => {
      el.innerHTML = getIconByName(el.dataset.icon);
    });
  }

  function getIconByName(name) {
    return window.getIcon ? window.getIcon(name || "") : "";
  }

  function initTheme() {
    const root = document.documentElement;
    const saved = localStorage.getItem(STORAGE_THEME);
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(saved || (prefersDark ? "dark" : "light"));

    const toggle = byId("theme-toggle");
    if (!toggle) return;
    toggle.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem(STORAGE_THEME, next);
    });
  }

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    const icon = document.querySelector(".theme-icon");
    if (icon) icon.innerHTML = getIconByName(theme === "dark" ? "moon" : "sun");
  }

  function initNav() {
    const navBtn = document.querySelector(".nav-toggle");
    const nav = byId("site-nav");
    if (!navBtn || !nav) return;

    navBtn.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      navBtn.setAttribute("aria-expanded", String(open));
    });

    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        if (window.innerWidth < 900) {
          nav.classList.remove("open");
          navBtn.setAttribute("aria-expanded", "false");
        }
      });
    });
  }

  function initBackToTop() {
    const btn = byId("back-to-top");
    if (!btn) return;

    window.addEventListener("scroll", () => {
      btn.classList.toggle("show", window.scrollY > 600);
    }, { passive: true });

    btn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  function initRipple() {
    document.querySelectorAll(".btn").forEach((btn) => {
      if (btn.dataset.rippleBound) return;
      btn.dataset.rippleBound = "1";

      btn.addEventListener("click", (event) => {
        const rect = btn.getBoundingClientRect();
        const ripple = document.createElement("span");
        ripple.className = "ripple";
        ripple.style.left = `${event.clientX - rect.left}px`;
        ripple.style.top = `${event.clientY - rect.top}px`;
        btn.appendChild(ripple);
        setTimeout(() => ripple.remove(), 560);
      });
    });
  }

  function initRevealSystem() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const nodes = document.querySelectorAll(".reveal, .stagger");
    if (!nodes.length) return;

    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        el.classList.add("in-view");

        if (el.classList.contains("stagger")) {
          Array.from(el.children).forEach((child, index) => {
            child.style.transitionDelay = `${index * 70}ms`;
          });
        }

        io.unobserve(el);
      });
    }, { threshold: 0.15 });

    nodes.forEach((n) => io.observe(n));
  }

  function initHeroParallax() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const a = document.querySelector(".hero-blob-a");
    const b = document.querySelector(".hero-blob-b");
    if (!a || !b) return;

    window.addEventListener("scroll", () => {
      const y = window.scrollY;
      a.style.transform = `translate3d(${y * 0.02}px, ${y * -0.05}px, 0)`;
      b.style.transform = `translate3d(${y * -0.015}px, ${y * 0.04}px, 0)`;
    }, { passive: true });
  }

  function initTiltCards() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || window.innerWidth < 900) return;

    document.querySelectorAll(".tilt-card").forEach((card) => {
      if (card.dataset.tiltBound) return;
      card.dataset.tiltBound = "1";

      card.addEventListener("mousemove", (event) => {
        const rect = card.getBoundingClientRect();
        const px = (event.clientX - rect.left) / rect.width;
        const py = (event.clientY - rect.top) / rect.height;
        const rx = (0.5 - py) * 4;
        const ry = (px - 0.5) * 4;
        card.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg) translateY(-2px)`;
      });

      card.addEventListener("mouseleave", () => {
        card.style.transform = "";
      });
    });
  }

  async function loadDiseases() {
    const items = await listLibrary();
    if (!Array.isArray(items) || !items.length) {
      throw new Error("No disease library data from backend");
    }
    diseases = items.reduce((acc, item) => {
      acc[item.id] = item;
      return acc;
    }, {});
  }

  function allDiseases() {
    return Object.values(diseases || {});
  }

  function renderHomeDiseases() {
    const target = byId("home-diseases");
    if (!target) return;

    target.innerHTML = allDiseases().map((d) => `
      <article class="card tilt-card">
        <h3>${escapeHtml(d.name)}</h3>
        <p class="small">${escapeHtml(d.short)}</p>
        <a class="btn btn-ghost" href="diseases.html#${encodeURIComponent(d.id)}">Learn more</a>
      </article>
    `).join("");

    initRipple();
    initTiltCards();
    initRevealSystem();
  }

  function initDiseasesPage() {
    const search = byId("disease-search");
    const tabs = byId("library-tabs");
    const sections = byId("disease-sections");
    if (!search || !sections || !tabs) return;

    let selectedDisease = "";

    const render = async () => {
      const term = search.value.trim();
      const diseaseName = selectedDisease.trim();
      let filtered = [];
      try {
        filtered = await listLibrary(term, diseaseName || null);
      } catch (_err) {
        sections.innerHTML = "<article class='card'><p class='small'>Failed to load library data from backend.</p></article>";
        return;
      }

      if (!filtered.length) {
        sections.innerHTML = "<article class='card'><p class='small'>No matching diseases found.</p></article>";
        return;
      }

      sections.innerHTML = filtered.map((d, i) => `
        <article id="${d.id}" class="card reveal ${i % 2 ? "reveal-right" : "reveal-left"}">
          <div class="stack">
            <h2>${escapeHtml(d.name)} - <span class="rtl" lang="ar" dir="rtl">${escapeHtml(d.name_ar)}</span></h2>
            <div class="rtl-box rtl" lang="ar" dir="rtl"><p>${escapeHtml(d.short_ar)}</p></div>
            <div class="rtl-box rtl" lang="ar" dir="rtl"><h3>الأعراض</h3><ul>${d.symptoms_ar.map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ul></div>
            <div class="rtl-box warning rtl" lang="ar" dir="rtl"><h3>علامات إنذار</h3><ul>${d.red_flags_ar.map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ul></div>
            <div class="rtl-box rtl" lang="ar" dir="rtl"><h3>نصائح آمنة</h3><ul>${d.safe_tips_ar.map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ul></div>
            <p class="small rtl" lang="ar" dir="rtl"><strong>متى تراجع الطبيب:</strong> ${escapeHtml(d.when_to_see_doctor_ar)}</p>
            <a class="btn btn-outline" href="diagnose.html">Back to Diagnose</a>
          </div>
        </article>
      `).join("");

      initRevealSystem();
      initRipple();
    };

    search.addEventListener("input", () => render());
    tabs.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        selectedDisease = btn.getAttribute("data-disease") || "";
        tabs.querySelectorAll(".tab-btn").forEach((node) => {
          const active = node === btn;
          node.classList.toggle("active", active);
          node.setAttribute("aria-selected", String(active));
        });
        render();
      });
    });
    render();
  }

  function initDiagnosePage() {
    const imageInput = byId("image-input");
    const dropzone = byId("dropzone");
    const preview = byId("preview-box");
    const analyzeBtn = byId("analyze-btn");
    const resetBtn = byId("reset-btn");
    const status = byId("status-indicator");
    const loadingLine = byId("loading-line");
    const skeleton = byId("result-skeleton");
    const result = byId("result-content");
    const message = byId("upload-inline-msg");
    const lightbox = byId("lightbox");
    const lightboxImg = byId("lightbox-image");
    const lightboxClose = byId("lightbox-close");

    if (!imageInput || !dropzone || !preview || !analyzeBtn || !resetBtn || !status || !loadingLine || !skeleton || !result || !message) return;

    let currentFile = null;
    let currentDataURL = "";

    const openPicker = () => imageInput.click();
    dropzone.addEventListener("click", openPicker);
    dropzone.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openPicker();
      }
    });

    imageInput.addEventListener("change", () => {
      const file = imageInput.files && imageInput.files[0];
      if (file) handleFile(file);
    });

    ["dragenter", "dragover"].forEach((evt) => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach((evt) => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
      });
    });

    dropzone.addEventListener("drop", (e) => {
      const file = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      if (file) handleFile(file);
    });

    preview.addEventListener("click", openLightbox);
    preview.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openLightbox();
      }
    });

    if (lightboxClose) lightboxClose.addEventListener("click", closeLightbox);
    if (lightbox) {
      lightbox.addEventListener("click", (e) => {
        if (e.target === lightbox) closeLightbox();
      });
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeLightbox();
      });
    }

    analyzeBtn.addEventListener("click", async () => {
      if (!currentFile) return;

      setStatus(status, "loading", "Analyzing");
      loadingLine.classList.remove("hidden");
      skeleton.classList.remove("hidden");
      result.classList.add("hidden");
      toast("Analyze started", "info");
      try {
        const predicted = await predictImage(currentFile);
        result.innerHTML = renderPredictionResultContent(predicted);
        skeleton.classList.add("hidden");
        result.classList.remove("hidden");
        loadingLine.classList.add("hidden");
        setStatus(status, "done", "Result ready");
        bindAccordions(result);
        initRipple();
        toast("Result ready", "success");
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Analysis failed";
        setStatus(status, "error", "Analysis failed");
        result.innerHTML = `<p class="small">Unable to complete analysis: ${escapeHtml(msg)}</p>`;
        result.classList.remove("hidden");
        toast(msg, "error");
      } finally {
        skeleton.classList.add("hidden");
        loadingLine.classList.add("hidden");
      }
    });

    resetBtn.addEventListener("click", () => {
      currentFile = null;
      currentDataURL = "";
      imageInput.value = "";
      preview.innerHTML = "<p>No image selected.</p>";
      analyzeBtn.disabled = true;
      resetBtn.disabled = true;
      setStatus(status, "idle", "Idle");
      result.innerHTML = "<p class='small'>No analysis yet. Upload a case and run analysis.</p>";
      message.textContent = "Upload cleared.";
      message.style.color = "var(--muted)";
      toast("Case reset", "info");
    });

    function handleFile(file) {
      if (!["image/png", "image/jpeg"].includes(file.type)) {
        setStatus(status, "error", "Invalid file type");
        message.textContent = "Invalid file type. Please upload PNG/JPG.";
        message.style.color = "var(--danger)";
        toast("Invalid file type", "error");
        return;
      }

      if (file.size > 10 * 1024 * 1024) {
        setStatus(status, "error", "File too large");
        message.textContent = "File exceeds 10MB limit.";
        message.style.color = "var(--danger)";
        toast("Size too big", "error");
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        currentFile = file;
        currentDataURL = String(reader.result || "");
        preview.innerHTML = `<img src="${currentDataURL}" alt="Selected eye image preview" />`;
        analyzeBtn.disabled = false;
        resetBtn.disabled = false;
        setStatus(status, "idle", "Image ready");
        message.textContent = `Selected: ${file.name}`;
        message.style.color = "var(--ok)";
      };
      reader.readAsDataURL(file);
    }

    function openLightbox() {
      if (!currentDataURL || !lightbox || !lightboxImg) return;
      lightboxImg.src = currentDataURL;
      lightbox.classList.remove("hidden");
      if (lightboxClose) lightboxClose.focus();
    }

    function closeLightbox() {
      if (!lightbox) return;
      lightbox.classList.add("hidden");
      preview.focus();
    }
  }

  function renderPredictionResultContent(prediction) {
    const label = String(prediction.label || "Unknown");
    const confidencePercent = Number(prediction.confidence || 0) * 100;
    const disease = findDiseaseByPrediction(label);
    const riskLevel = disease ? disease.risk_level : "Unknown";
    const riskClass = String(riskLevel || "low").toLowerCase();

    return `
      <div class="result-header ltr">
        <span class="badge"><span class="icon">${getIconByName("activity")}</span>Prediction: ${escapeHtml(label)}</span>
        <span class="badge">Confidence: ${confidencePercent.toFixed(1)}%</span>
        <span class="badge ${riskClass}">Risk: ${escapeHtml(riskLevel)}</span>
      </div>

      <div class="result-grid ltr">
        <article class="card">
          <h3>Inference Output</h3>
          <ul>
            <li><strong>Label:</strong> ${escapeHtml(label)}</li>
            <li><strong>Confidence:</strong> ${confidencePercent.toFixed(1)}%</li>
            <li><strong>Model:</strong> eye_disease_final_cropped.keras</li>
          </ul>
        </article>
        <article class="card">
          <h3>Clinical Note</h3>
          <p>This prediction was generated by the backend classification model. Confirm clinically before action.</p>
        </article>
      </div>

      ${accordionMarkup([
        {
          title: "API Response",
          content: `<pre class="api-json">${escapeHtml(JSON.stringify(prediction, null, 2))}</pre>`
        },
        {
          title: "Patient-safe Note",
          content: disease
            ? `<div class="rtl" lang="ar" dir="rtl">${escapeHtml(disease.when_to_see_doctor_ar)}</div>`
            : "No disease-specific note available for this label."
        }
      ])}
    `;
  }

  function initHistoryPage() {
    const filter = byId("history-filter");
    const container = byId("history-full");
    const clearAll = byId("clear-all-history");
    if (!filter || !container || !clearAll) return;

    const render = async () => {
      const value = filter.value;
      let rows = [];
      try {
        rows = await listResults(value === "all" ? null : value);
      } catch (_err) {
        container.innerHTML = "<p class='small'>Failed to load backend results.</p>";
        return;
      }

      if (!rows.length) {
        container.innerHTML = "<p class='small'>No entries for this filter.</p>";
        return;
      }

      container.innerHTML = rows.map((row) => `
        <article class="history-entry">
          <div class="history-placeholder">${escapeHtml((row.prediction || "?").slice(0, 1).toUpperCase())}</div>
          <div class="stack">
            <h3>${escapeHtml(row.prediction || "Unknown")} (${(Number(row.confidence || 0) * 100).toFixed(1)}%)</h3>
            <p class="small">${escapeHtml(row.created_at ? new Date(row.created_at).toLocaleString() : "Unknown")}</p>
            <p class="small">Record ID: ${escapeHtml(row.id)} | ${escapeHtml(row.image_path || "N/A")}</p>
          </div>
          <button class="btn btn-ghost" type="button" data-remove="${row.id}">Remove</button>
        </article>
      `).join("");

      container.querySelectorAll("[data-remove]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const id = btn.getAttribute("data-remove");
          try {
            await deleteResult(id);
            await render();
            toast("History item removed", "info");
          } catch (_err) {
            toast("Failed to delete result", "error");
          }
        });
      });

      initRipple();
    };

    const initFilterOptions = async () => {
      try {
        const all = await listResults();
        const labels = Array.from(new Set(all.map((r) => r.prediction).filter(Boolean))).sort();
        filter.innerHTML = `<option value="all">All</option>${labels.map((label) => `<option value="${escapeHtml(label)}">${escapeHtml(label)}</option>`).join("")}`;
      } catch (_err) {
        filter.innerHTML = `<option value="all">All</option>`;
      }
    };

    filter.addEventListener("change", () => { render(); });
    clearAll.addEventListener("click", async () => {
      try {
        const all = await listResults();
        await Promise.all(all.map((item) => deleteResult(item.id)));
        await render();
        toast("All backend history cleared", "info");
      } catch (_err) {
        toast("Failed to clear backend history", "error");
      }
    });

    initFilterOptions().then(() => render());
  }


  async function initAboutPage() {
    const target = byId("about-content");
    if (!target) return;
    try {
      const payload = await getSectionContent("about");
      const content = payload.content || {};
      target.innerHTML = `
        <article class="card stack reveal reveal-up">
          <h1>${escapeHtml(payload.title || "About")}</h1>
          <p><strong>${escapeHtml(content.subtitle || "")}</strong></p>
          <p>${escapeHtml(content.description || "")}</p>
          <p><strong>${escapeHtml(content.project_title || "")}</strong></p>
          <p>Supervised by: ${escapeHtml(content.supervisor || "N/A")}</p>
        </article>
        <article class="card stack reveal reveal-up">
          <h2>Team Members</h2>
          <ol class="stack page-list">${(content.team_members || []).map((member) => `<li>${escapeHtml(member)}</li>`).join("")}</ol>
        </article>
        <div class="grid grid-2 stagger reveal reveal-scale">
          <article class="card stack">
            <h2>Stack</h2>
            <ul class="stack">${(content.stack || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
          </article>
          <article class="card stack">
            <h2>Deployment Scope</h2>
            <ul class="stack">${(content.model_scope || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
          </article>
        </div>
      `;
      initRevealSystem();
      initRipple();
    } catch (_err) {
      target.innerHTML = "<article class='card'><p class='small'>Unable to load About content from backend.</p></article>";
    }
  }

  async function initSafetyPage() {
    const target = byId("safety-content");
    if (!target) return;
    try {
      const payload = await getSectionContent("safety");
      const content = payload.content || {};
      target.innerHTML = `
        <div class="warning-banner reveal reveal-up">
          <span class="icon" data-icon="warning"></span>
          <div class="stack">
            <h1>${escapeHtml(payload.title || "Safety")}</h1>
            <p>${escapeHtml(content.intro || "")}</p>
          </div>
        </div>
        <div class="grid grid-2 stagger reveal reveal-up">
          ${(content.cards || []).map((card) => `
            <article class="card stack">
              <h2>${escapeHtml(card.title || "")}</h2>
              <p class="small">${escapeHtml(card.content || "")}</p>
            </article>
          `).join("")}
        </div>
        <article class="card reveal reveal-scale stack">
          <h2>Clinical Escalation Advice</h2>
          <p class="small">${escapeHtml(content.escalation_advice || "")}</p>
        </article>
      `;
      initIcons();
      initRevealSystem();
    } catch (_err) {
      target.innerHTML = "<article class='card'><p class='small'>Unable to load Safety content from backend.</p></article>";
    }
  }

  async function initEducationPage() {
    const target = byId("education-content");
    if (!target) return;
    try {
      const payload = await getSectionContent("education");
      const content = payload.content || {};
      target.innerHTML = `
        <div class="section-head reveal reveal-up">
          <h1>${escapeHtml(payload.title || "Education")}</h1>
          <p>${escapeHtml(content.intro || "")}</p>
        </div>
        <div class="grid grid-3 stagger reveal reveal-up">
          ${(content.blocks || []).map((block) => `
            <article class="card tilt-card stack">
              <h2>${escapeHtml(block.title || "")}</h2>
              <ul class="stack">${(block.items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
              <div class="rtl rtl-box" lang="ar" dir="rtl">
                <h3>${escapeHtml(block.arabic_title || "")}</h3>
                <p>${escapeHtml(block.arabic_text || "")}</p>
              </div>
            </article>
          `).join("")}
        </div>
      `;
      initRevealSystem();
      initTiltCards();
    } catch (_err) {
      target.innerHTML = "<article class='card'><p class='small'>Unable to load Education content from backend.</p></article>";
    }
  }

  function accordionMarkup(items) {
    return items.map((item, idx) => `
      <div class="accordion-item">
        <button class="accordion-trigger" type="button" aria-expanded="${idx === 0 ? "true" : "false"}">
          <span>${escapeHtml(item.title)}</span>
          <span class="icon">${getIconByName("chevron")}</span>
        </button>
        <div class="accordion-panel" style="max-block-size:${idx === 0 ? "320px" : "0px"}">
          <div class="accordion-panel-inner">${item.content}</div>
        </div>
      </div>
    `).join("");
  }

  function bindAccordions(scope) {
    scope.querySelectorAll(".accordion-trigger").forEach((btn) => {
      if (btn.dataset.bound) return;
      btn.dataset.bound = "1";
      btn.addEventListener("click", () => {
        const panel = btn.nextElementSibling;
        const open = btn.getAttribute("aria-expanded") === "true";
        btn.setAttribute("aria-expanded", String(!open));
        panel.style.maxBlockSize = open ? "0px" : `${panel.scrollHeight}px`;
      });
    });
  }

  function setStatus(node, state, text) {
    node.className = `status ${state}`;
    node.innerHTML = `<span class="dot"></span>${escapeHtml(text)}`;
  }

  function findDiseaseByPrediction(prediction) {
    const aliases = {
      healthy_eye: "normal",
      normal: "normal",
      "conjunctivitis recognition": "conjunctivitis",
      conjunctivitis: "conjunctivitis",
      "cataract dataset": "cataract",
      cataract: "cataract",
      keratitis: "keratitis"
    };
    const target = aliases[String(prediction || "").trim().toLowerCase()] || String(prediction || "").trim().toLowerCase();
    return allDiseases().find((d) => {
      return String(d.id || "").toLowerCase() === target || String(d.name || "").toLowerCase() === target;
    }) || null;
  }

  async function predictImage(file) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API_ROOT}/predict`, {
      method: "POST",
      body: formData
    });
    return parseApiResponse(response);
  }

  async function parseApiResponse(response) {
    let data = null;
    try {
      data = await response.json();
    } catch (_err) {
      data = null;
    }

    if (!response.ok) {
      const detail = data && data.detail ? String(data.detail) : `Request failed (${response.status})`;
      throw new Error(detail);
    }

    return data || {};
  }

  function toast(text, type = "info") {
    const root = byId("toast-root");
    if (!root) return;
    const icon = type === "success" ? "check" : type === "error" ? "warning" : "info";
    const node = document.createElement("div");
    node.className = `toast ${type}`;
    node.innerHTML = `<span class="icon">${getIconByName(icon)}</span><span>${escapeHtml(text)}</span>`;
    root.appendChild(node);
    setTimeout(() => node.remove(), 2800);
  }

  function byId(id) { return document.getElementById(id); }
  async function listResults(prediction = null) {
    const url = prediction
      ? `${CONTENT_API_BASE}/results?prediction=${encodeURIComponent(prediction)}`
      : `${CONTENT_API_BASE}/results`;
    const response = await fetch(url);
    return parseApiResponse(response);
  }
  async function deleteResult(id) {
    const response = await fetch(`${CONTENT_API_BASE}/results/${encodeURIComponent(id)}`, { method: "DELETE" });
    return parseApiResponse(response);
  }
  function delay(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }
  async function getSectionContent(sectionType) {
    const response = await fetch(`${CONTENT_API_BASE}/content/${encodeURIComponent(sectionType)}`);
    return parseApiResponse(response);
  }
  async function listLibrary(q = "", diseaseName = null) {
    const params = new URLSearchParams();
    if (q && q.trim()) params.set("q", q.trim());
    if (diseaseName && diseaseName.trim()) params.set("name", diseaseName.trim());
    const query = params.toString();
    const response = await fetch(`${CONTENT_API_BASE}/library${query ? `?${query}` : ""}`);
    return parseApiResponse(response);
  }
  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
})();
