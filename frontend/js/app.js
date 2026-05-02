(() => {
  "use strict";

  const STORAGE_THEME = "doa-theme";
  const API_ROOT = (window.DOA_API_BASE || localStorage.getItem("doa-api-base") || "http://127.0.0.1:8000").replace(/\/+$/, "");
  const CONTENT_API_BASE = `${API_ROOT}/api/v1`;
  const DISEASE_IMAGE_BY_ID = {
    cataract: "disease-cataract.png",
    conjunctivitis: "disease-conjunctivitis.png",
    keratitis: "disease-keratitis.png",
    normal: "disease-normal.png",
    pterygium: "disease-normal.png",
    healthy_eye: "disease-normal.png"
  };
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

    const nodes = document.querySelectorAll(".reveal, .stagger, .timeline, .footer");
    if (!nodes.length) return;

    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        el.classList.add("in-view");

        // If this is a section with a stagger child, also trigger the stagger
        if (el.classList.contains("reveal") && el.classList.contains("section")) {
          const staggerChild = el.querySelector(".stagger");
          if (staggerChild && !staggerChild.classList.contains("in-view")) {
            setTimeout(() => {
              staggerChild.classList.add("in-view");
            }, 200);
          }
        }

        if (el.classList.contains("stagger")) {
          Array.from(el.children).forEach((child, index) => {
            child.style.transitionDelay = `${index * 80}ms`;
            // Add spring-like animation with custom properties
            child.style.transitionTimingFunction = 'cubic-bezier(0.34, 1.56, 0.64, 1)';
          });
        }

        // Trigger timeline item animations
        if (el.classList.contains("timeline")) {
          const items = el.querySelectorAll("li");
          items.forEach((item, index) => {
            setTimeout(() => {
              item.classList.add("animate-in");
            }, index * 200);
          });
        }

        // Trigger tilt card content entrance
        if (el.classList.contains("tilt-card")) {
          setTimeout(() => {
            el.classList.add("in-view");
          }, 100);
        }

        // Create particle effects for sections
        if (el.classList.contains("section") || el.closest('.section')) {
          createParticleEffects(el.closest('.section') || el);
        }

        io.unobserve(el);
      });
    }, { threshold: 0.1 });

    nodes.forEach((n) => io.observe(n));
  }

  // Create floating particle effects
  function createParticleEffects(container) {
    if (container.querySelector('.particle-container')) return;
    
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particle-container';
    
    // Create 8-12 particles per section
    const particleCount = 8 + Math.floor(Math.random() * 5);
    
    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      
      // Random positioning
      particle.style.left = `${Math.random() * 100}%`;
      particle.style.top = `${70 + Math.random() * 30}%`;
      
      // Random size variation
      const size = 2 + Math.random() * 3;
      particle.style.width = `${size}px`;
      particle.style.height = `${size}px`;
      
      // Random animation duration and delay
      const duration = 3 + Math.random() * 4;
      const delay = Math.random() * 3;
      particle.style.animationDuration = `${duration}s`;
      particle.style.animationDelay = `${delay}s`;
      
      // Random color variation
      const colors = ['var(--primary-400)', 'var(--accent-400)', 'var(--primary-300)'];
      particle.style.background = colors[Math.floor(Math.random() * colors.length)];
      
      particleContainer.appendChild(particle);
    }
    
    container.appendChild(particleContainer);
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

      // Add magnetic pull effect
      let isHovering = false;
      let currentRotateX = 0;
      let currentRotateY = 0;
      let targetRotateX = 0;
      let targetRotateY = 0;

      function animateTilt() {
        if (!isHovering) {
          // Smoothly return to center
          currentRotateX += (0 - currentRotateX) * 0.1;
          currentRotateY += (0 - currentRotateY) * 0.1;
          
          if (Math.abs(currentRotateX) < 0.1 && Math.abs(currentRotateY) < 0.1) {
            card.style.transform = '';
            return;
          }
        }
        
        card.style.transform = `perspective(1000px) rotateX(${currentRotateX}deg) rotateY(${currentRotateY}deg) translateY(-4px) scale3d(1.02, 1.02, 1.02)`;
        requestAnimationFrame(animateTilt);
      }

      card.addEventListener("mouseenter", () => {
        isHovering = true;
        animateTilt();
      });

      card.addEventListener("mousemove", (event) => {
        const rect = card.getBoundingClientRect();
        const px = (event.clientX - rect.left) / rect.width;
        const py = (event.clientY - rect.top) / rect.height;
        
        // Calculate rotation with magnetic pull effect
        targetRotateX = (0.5 - py) * 8;
        targetRotateY = (px - 0.5) * 8;
        
        // Smooth interpolation
        currentRotateX = targetRotateX;
        currentRotateY = targetRotateY;
        
        // Set CSS custom properties for magnetic glow effect
        card.style.setProperty('--mouse-x', `${px * 100}%`);
        card.style.setProperty('--mouse-y', `${py * 100}%`);
      });

      card.addEventListener("mouseleave", () => {
        isHovering = false;
        card.style.removeProperty('--mouse-x');
        card.style.removeProperty('--mouse-y');
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

  function getDiseaseImageName(id) {
    return DISEASE_IMAGE_BY_ID[String(id || "").toLowerCase()] || "disease-normal.png";
  }

  function renderSurfaceMessage(text) {
    return `<article class="surface-message"><p class="small">${escapeHtml(text)}</p></article>`;
  }

  function renderDiseaseTile(disease, options = {}) {
    const imageName = getDiseaseImageName(disease.id);
    const titleTag = options.titleTag || "h3";
    const bodyClass = options.bodyClass || "disease-tile-body";
    const title = `<${titleTag}>${escapeHtml(disease.name || "Unknown")}</${titleTag}>`;
    return `
      <article class="card tilt-card">
        <div class="disease-tile">
          <img src="../assets/images/${imageName}" alt="${escapeHtml(disease.name || "Disease image")}" class="disease-tile-media" loading="lazy" />
          <div class="${bodyClass}">
            ${title}
            <p class="small">${escapeHtml(disease.short || "")}</p>
            <a class="btn btn-ghost btn-sm" href="diseases.html#${encodeURIComponent(disease.id || "")}">Learn more</a>
          </div>
        </div>
      </article>
    `;
  }

  function renderDiseaseDetail(disease, index) {
    const imageName = getDiseaseImageName(disease.id);
    return `
      <article id="${disease.id}" class="card reveal ${index % 2 ? "reveal-right" : "reveal-left"}">
        <div class="stack">
          <div class="disease-detail-head">
            <img src="../assets/images/${imageName}" alt="${escapeHtml(disease.name)}" class="disease-detail-media" loading="lazy" />
            <div class="disease-detail-title">
              <h2>${escapeHtml(disease.name)} - <span class="rtl" lang="ar" dir="rtl">${escapeHtml(disease.name_ar)}</span></h2>
            </div>
          </div>
          <div class="rtl-box rtl" lang="ar" dir="rtl"><p>${escapeHtml(disease.short_ar)}</p></div>
          <div class="rtl-box rtl stack-panel" lang="ar" dir="rtl"><h3>الأعراض</h3><ul>${(disease.symptoms_ar || []).map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ul></div>
          <div class="rtl-box warning rtl stack-panel" lang="ar" dir="rtl"><h3>علامات إنذار</h3><ul>${(disease.red_flags_ar || []).map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ul></div>
          <div class="rtl-box rtl stack-panel" lang="ar" dir="rtl"><h3>نصائح آمنة</h3><ul>${(disease.safe_tips_ar || []).map((x) => `<li>${escapeHtml(x)}</li>`).join("")}</ul></div>
          <p class="small rtl" lang="ar" dir="rtl"><strong>متى تراجع الطبيب:</strong> ${escapeHtml(disease.when_to_see_doctor_ar || "")}</p>
          <a class="btn btn-outline" href="diagnose.html">Back to Diagnose</a>
        </div>
      </article>
    `;
  }

  function renderHomeDiseases() {
    const target = byId("home-diseases");
    if (!target) return;

    const allD = allDiseases();
    
    if (!allD || allD.length === 0) {
      target.innerHTML = `
        ${renderDiseaseTile({ id: "cataract", name: "Cataract", short: "Clouding of the eye's lens, leading to vision impairment." })}
        ${renderDiseaseTile({ id: "conjunctivitis", name: "Conjunctivitis", short: "Inflammation of the conjunctiva causing redness and irritation." })}
        ${renderDiseaseTile({ id: "keratitis", name: "Keratitis", short: "Inflammation of the cornea that can affect vision." })}
        ${renderDiseaseTile({ id: "normal", name: "Normal", short: "Healthy eye examination with no detected abnormalities." })}
      `;
    } else {
      target.innerHTML = allD.map((d) => renderDiseaseTile(d)).join("");
    }

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
        sections.innerHTML = renderSurfaceMessage("Failed to load library data from backend.");
        return;
      }

      if (!filtered.length) {
        sections.innerHTML = renderSurfaceMessage("No matching diseases found.");
        return;
      }
      sections.innerHTML = filtered.map((d, i) => renderDiseaseDetail(d, i)).join("");

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
    const qualityText = byId("quality-text");
    const qualityBar = byId("quality-bar");
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
        initIcons();
        skeleton.classList.add("hidden");
        result.classList.remove("hidden");
        loadingLine.classList.add("hidden");
        setStatus(status, predicted.needs_review ? "review" : "done", predicted.needs_review ? "Needs clinical review" : "Result ready");
        bindAccordions(result);
        initRipple();
        toast(predicted.needs_review ? "Low-confidence result" : "Result ready", predicted.needs_review ? "warning" : "success");
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
      preview.innerHTML = `
        <div class="preview-placeholder">
          <span class="preview-kicker">Preview</span>
          <strong>Image preview will appear here</strong>
          <span>Use a centered, well-lit image for the cleanest signal.</span>
        </div>`;
      analyzeBtn.disabled = true;
      resetBtn.disabled = true;
      setStatus(status, "idle", "Idle");
      result.innerHTML = "<p class='small'>No analysis yet. Upload a case and run analysis.</p>";
      message.textContent = "Upload cleared.";
      message.style.color = "var(--text-tertiary)";
      if (qualityText) qualityText.textContent = "—";
      if (qualityBar) qualityBar.style.width = "0%";
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
        message.style.color = "var(--success-700)";
        estimateImageQuality(currentDataURL, file);
      };
      reader.readAsDataURL(file);
    }

    function estimateImageQuality(dataURL, file) {
      if (!qualityText || !qualityBar) return;
      const img = new Image();
      img.onload = () => {
        const minSide = Math.min(img.width, img.height);
        const aspectPenalty = Math.abs((img.width / img.height) - 1);
        let score = 0;

        if (minSide >= 800) score += 45;
        else if (minSide >= 500) score += 35;
        else if (minSide >= 300) score += 24;
        else score += 12;

        if (file.size <= 4 * 1024 * 1024) score += 28;
        else if (file.size <= 8 * 1024 * 1024) score += 18;
        else score += 10;

        if (aspectPenalty < 0.25) score += 20;
        else if (aspectPenalty < 0.6) score += 12;
        else score += 5;

        score = Math.max(8, Math.min(100, score));
        qualityBar.style.width = `${score}%`;

        if (score >= 75) qualityText.textContent = `Good · ${score}%`;
        else if (score >= 50) qualityText.textContent = `Fair · ${score}%`;
        else qualityText.textContent = `Weak · ${score}%`;
      };
      img.src = dataURL;
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
    const predictedDisease = findDiseaseByPrediction(prediction.predicted_class || "");
    const effectiveDisease = disease || predictedDisease;
    const riskLevel = prediction.needs_review ? "Unknown" : (effectiveDisease ? effectiveDisease.risk_level : "Unknown");
    const riskClass = String(riskLevel || "low").toLowerCase();
    const secondBestPercent = Number(prediction.second_best_confidence || 0) * 100;
    const marginPercent = Number(prediction.confidence_margin || 0) * 100;
    const entropyPercent = Number(prediction.normalized_entropy || 0) * 100;
    const displayName = disease ? disease.name : (predictedDisease ? predictedDisease.name : getDiseaseName(String(prediction.predicted_class || label)));
    const displayNameAr = disease ? disease.name_ar : (predictedDisease ? predictedDisease.name_ar : getDiseaseNameAr(String(prediction.predicted_class || label)));
    const displayShort = disease ? disease.short : "";

    // Map risk class to badge class
    const getRiskBadgeClass = (level) => {
      const l = String(level).toLowerCase();
      if (l === 'high' || l === 'urgent') return 'high';
      if (l === 'moderate' || l === 'medium') return 'moderate';
      return 'low';
    };

    const prettyLabel = (raw) => {
      return String(raw || "")
        .split("_")
        .map((part) => part ? part[0].toUpperCase() + part.slice(1) : "")
        .join(" ");
    };

    const diseaseSymptoms = disease ? (disease.symptoms || []) : [];
    const diseaseRedFlags = disease ? (disease.red_flags || []) : [];
    const diseaseSafeTips = disease ? (disease.safe_tips || []) : [];
    const whenToSeeDoctor = disease ? (disease.when_to_see_doctor || "") : "";

    const confidenceEntries = Object.entries(prediction.all_probabilities || {})
      .sort((a, b) => Number(b[1]) - Number(a[1]));

    const resultFacts = [];
    if (displayName) {
      resultFacts.push(["Predicted Condition", displayName, false]);
    }
    if (displayNameAr) {
      resultFacts.push(["Arabic Name", displayNameAr, true]);
    }
    resultFacts.push(["API Label", `<code>${escapeHtml(label)}</code>`, false, true]);
    resultFacts.push(["Top Raw Class", prettyLabel(prediction.predicted_class), false]);
    resultFacts.push(["Confidence", `${confidencePercent.toFixed(1)}%`, false]);
    resultFacts.push(["Needs Review", prediction.needs_review ? "Yes" : "No", false]);

    // Build result HTML - only include sections with actual data from backend
    let html = '';

    // Result header with badges
    html += '<div class="result-header ltr">';
    if (displayName) {
      html += `<span class="badge badge-primary"><span class="icon">${getIconByName("activity")}</span>${escapeHtml(displayName)}</span>`;
    }
    html += `<span class="badge ${prediction.needs_review ? "warning" : "badge-success"}">Confidence: ${confidencePercent.toFixed(1)}%</span>`;
    if (riskLevel !== "Unknown") {
      html += `<span class="badge ${getRiskBadgeClass(riskClass)}">Risk: ${escapeHtml(riskLevel)}</span>`;
    }
    if (prediction.needs_review) {
      html += '<span class="badge warning">Review Required</span>';
    }
    html += '</div>';

    html += '<section class="result-hero">';
    html += `<article class="signal-banner ${prediction.needs_review ? "review" : "safe"}">`;
    html += `<h3><span class="icon" data-icon="${prediction.needs_review ? "warning" : "check"}"></span>${prediction.needs_review ? "Low-confidence classification" : "Confident classification"}</h3>`;
    if (prediction.needs_review) {
      html += `<p>The image does not match the trained classes strongly enough. Closest class: <strong>${escapeHtml(displayName || prettyLabel(prediction.predicted_class))}</strong> at ${confidencePercent.toFixed(1)}%, with ${escapeHtml(prettyLabel(prediction.second_best_class))} very close at ${secondBestPercent.toFixed(1)}%.</p>`;
    } else {
      html += `<p>The strongest class is <strong>${escapeHtml(displayName || prettyLabel(prediction.predicted_class))}</strong> with a margin of ${marginPercent.toFixed(1)}% over the next class.</p>`;
    }
    html += '</article>';

    html += '<div class="result-title">';
    if (displayName) {
      html += `<h3 class="ltr">${escapeHtml(displayName)}</h3>`;
    }
    if (displayNameAr) {
      html += `<p class="rtl" lang="ar" dir="rtl">${escapeHtml(displayNameAr)}</p>`;
    } else {
      html += `<p>${prediction.needs_review ? "This output should be treated as triage support only." : "Result is inside the trained class space."}</p>`;
    }
    if (displayShort) {
      html += `<p class="small">${escapeHtml(displayShort)}</p>`;
    }
    html += '</div>';

    html += '<div class="metric-strip">';
    html += `<article class="metric-tile"><span>Top class</span><strong>${escapeHtml(prettyLabel(prediction.predicted_class))}</strong></article>`;
    html += `<article class="metric-tile"><span>Runner-up</span><strong>${escapeHtml(prettyLabel(prediction.second_best_class))}</strong></article>`;
    html += `<article class="metric-tile"><span>Margin / Entropy</span><strong>${marginPercent.toFixed(1)}% / ${entropyPercent.toFixed(1)}%</strong></article>`;
    html += '</div>';
    html += '</section>';

    html += '<div class="result-grid result-grid-primary ltr">';
    html += renderResultFactsCard(resultFacts);
    html += renderConfidenceCard(confidenceEntries, prettyLabel);
    html += '</div>';

    const secondaryCards = [];
    if (prediction.needs_review) {
      secondaryCards.push(renderReviewCard());
    }

    if (diseaseSafeTips.length > 0) {
      secondaryCards.push(renderClinicalGuidanceCard(diseaseSafeTips));
    }

    if (secondaryCards.length > 0) {
      const secondaryGridClass = secondaryCards.length === 1
        ? "result-grid result-grid-secondary result-grid-secondary-single ltr"
        : "result-grid result-grid-secondary ltr";
      html += `<div class="${secondaryGridClass}">${secondaryCards.join("")}</div>`;
    }

    // Symptoms - only if available from backend
    if (diseaseSymptoms.length > 0) {
      html += '<article class="card stack ltr stack-panel">';
      html += '<h3><span class="icon" data-icon="activity"></span>Common Symptoms</h3>';
      html += '<ul class="plain-list">';
      diseaseSymptoms.forEach(s => {
        html += `<li><span class="icon" data-icon="circle"></span>${escapeHtml(s)}</li>`;
      });
      html += '</ul>';
      html += '</article>';
    }

    // Red flags - only if available from backend
    if (diseaseRedFlags.length > 0) {
      html += '<article class="card stack ltr stack-panel stack-panel-danger">';
      html += '<h3><span class="icon" data-icon="warning"></span>Warning Signs - Seek Immediate Care</h3>';
      html += '<ul class="plain-list">';
      diseaseRedFlags.forEach(f => {
        html += `<li><span class="icon" data-icon="alert"></span>${escapeHtml(f)}</li>`;
      });
      html += '</ul>';
      html += '</article>';
    }

    // When to see doctor - only if available from backend
    if (whenToSeeDoctor) {
      html += `<article class="card stack rtl-box rtl stack-panel" lang="ar" dir="rtl">`;
      html += '<h3>متى يجب مراجعة الطبيب</h3>';
      html += `<p>${escapeHtml(whenToSeeDoctor)}</p>`;
      html += '</article>';
    }

    return html;
  }

  function renderResultFactsCard(facts) {
    return `
      <article class="card result-card">
        <h3><span class="icon" data-icon="activity"></span>Analysis Results</h3>
        <div class="fact-list">
          ${facts.map(([label, value, isRtl = false, isHtml = false]) => `
            <div class="fact-row">
              <span class="fact-label"><span class="icon" data-icon="check"></span>${escapeHtml(label)}</span>
              <span class="fact-value ${isRtl ? "rtl" : ""}" ${isRtl ? 'lang="ar" dir="rtl"' : ""}>${isHtml ? value : escapeHtml(value)}</span>
            </div>
          `).join("")}
        </div>
      </article>
    `;
  }

  function renderConfidenceCard(confidenceEntries, prettyLabel) {
    return `
      <article class="card confidence-panel">
        <h3><span class="icon" data-icon="activity"></span>Confidence Breakdown</h3>
        <div class="confidence-list">
          ${confidenceEntries.map(([entryLabel, value], index) => {
            const percent = Number(value || 0) * 100;
            return `
              <div class="confidence-row">
                <div class="confidence-meta">
                  <div class="confidence-label">
                    <span class="badge ${index === 0 ? "badge-primary" : "low"}">${index + 1}</span>
                    <strong>${escapeHtml(prettyLabel(entryLabel))}</strong>
                  </div>
                  <span class="confidence-value">${percent.toFixed(1)}%</span>
                </div>
                <div class="confidence-track">
                  <div class="confidence-fill ${index === 0 ? "is-top" : ""}" style="width:${Math.max(2, Math.min(100, percent))}%"></div>
                </div>
              </div>
            `;
          }).join("")}
        </div>
        <p class="mini-note">When the top two classes are too close, the backend returns <code>unrecognized</code> to avoid a misleading diagnosis.</p>
      </article>
    `;
  }

  function renderReviewCard() {
    return `
      <article class="card review-card">
        <h3><span class="icon" data-icon="warning"></span>Review Guidance</h3>
        <ul class="plain-list">
          <li><span class="icon" data-icon="check"></span>Do not treat this as a confirmed diagnosis.</li>
          <li><span class="icon" data-icon="check"></span>Request another image with better focus, lighting, or framing.</li>
          <li><span class="icon" data-icon="check"></span>Use the closest class only as a hint for manual review.</li>
        </ul>
      </article>
    `;
  }

  function renderClinicalGuidanceCard(tips) {
    return `
      <article class="card guidance-card">
        <h3><span class="icon" data-icon="shield"></span>Clinical Guidance</h3>
        <ul class="plain-list">
          ${tips.map((tip) => `<li><span class="icon" data-icon="check"></span>${escapeHtml(tip)}</li>`).join("")}
        </ul>
      </article>
    `;
  }

  function getDiseaseName(label) {
    const names = {
      healthy_eye: "Healthy Eye",
      normal: "Normal",
      conjunctivitis: "Conjunctivitis",
      cataract: "Cataract",
      keratitis: "Keratitis"
    };
    return names[label.toLowerCase()] || label;
  }

  function getDiseaseNameAr(label) {
    const names = {
      healthy_eye: "عين سليمة",
      normal: "طبيعي",
      conjunctivitis: "التهاب الملتحمة",
      cataract: "إعتام عدسة العين (المياه البيضاء)",
      keratitis: "التهاب القرنية"
    };
    return names[label.toLowerCase()] || label;
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
        container.innerHTML = renderSurfaceMessage("Failed to load backend results.");
        return;
      }

      if (!rows.length) {
        container.innerHTML = renderSurfaceMessage("No entries for this filter.");
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
      target.innerHTML = renderSurfaceMessage("Unable to load About content from backend.");
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
      target.innerHTML = renderSurfaceMessage("Unable to load Safety content from backend.");
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
      target.innerHTML = renderSurfaceMessage("Unable to load Education content from backend.");
    }
  }

  function accordionMarkup(items) {
    return items.map((item, idx) => {
      const isOpen = typeof item.open === "boolean" ? item.open : idx === 0;
      return `
      <div class="accordion-item">
        <button class="accordion-trigger" type="button" aria-expanded="${isOpen ? "true" : "false"}">
          <span>${escapeHtml(item.title)}</span>
          <span class="icon">${getIconByName("chevron")}</span>
        </button>
        <div class="accordion-panel" style="max-block-size:${isOpen ? "320px" : "0px"}">
          <div class="accordion-panel-inner">${item.content}</div>
        </div>
      </div>
    `;
    }).join("");
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

  function normalizeCollectionResponse(data) {
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.data)) return data.data;
    if (data && Array.isArray(data.items)) return data.items;
    return [];
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
    return normalizeCollectionResponse(await parseApiResponse(response));
  }
  async function deleteResult(id) {
    const response = await fetch(`${CONTENT_API_BASE}/results/${encodeURIComponent(id)}`, { method: "DELETE" });
    return parseApiResponse(response);
  }
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
    return normalizeCollectionResponse(await parseApiResponse(response));
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
