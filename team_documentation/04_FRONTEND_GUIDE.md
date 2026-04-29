# Frontend Technical Guide

## 🎨 Overview

This document provides a comprehensive guide to the web frontend, including architecture, pages, styling, and JavaScript functionality.

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Pages & Navigation](#pages--navigation)
4. [Styling System](#styling-system)
5. [JavaScript Architecture](#javascript-architecture)
6. [API Integration](#api-integration)
7. [Key Features](#key-features)
8. [Best Practices](#best-practices)

---

## Architecture Overview

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Structure** | HTML5 | Semantic markup |
| **Styling** | CSS3 (Custom) | Responsive design, theming |
| **Interactivity** | Vanilla JavaScript | No framework dependencies |
| **Icons** | Custom SVG (inline) | Consistent iconography |
| **Storage** | LocalStorage | User preferences, settings |

### Design Philosophy

- **No Framework**: Pure vanilla JavaScript for maximum performance and minimal dependencies
- **Responsive**: Mobile-first design that works on all screen sizes
- **Accessible**: WCAG 2.1 AA compliance with proper ARIA attributes
- **Bilingual**: Full English/Arabic support with RTL layout
- **Modern**: CSS custom properties, flexbox, grid, animations

### Application Flow

```
User → HTML Page → CSS Styling → JavaScript Enhancement → API Calls → Dynamic Content
```

---

## Project Structure

```
frontend/
├── 📁 pages/                    # HTML pages
│   ├── index.html              # Homepage
│   ├── diagnose.html           # AI diagnosis page
│   ├── diseases.html           # Disease library
│   ├── history.html            # Prediction history
│   ├── about.html              # About page
│   ├── safety.html             # Safety information
│   └── education.html          # Patient education
│
├── 📁 styles/                   # CSS files
│   └── styles.css              # Main stylesheet (all styles)
│
├── 📁 js/                       # JavaScript files
│   └── app.js                  # Main application script
│
├── 📁 assets/                   # Static assets
│   └── icons.js                # SVG icon definitions
│
└── README.md                   # Frontend documentation
```

### Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `styles.css` | ~1500+ | All styling, responsive breakpoints, themes |
| `app.js` | 759 | All JavaScript logic, API calls, UI interactions |
| `icons.js` | ~200+ | SVG icon definitions as JavaScript functions |

---

## Pages & Navigation

### 1. Homepage (`index.html`)

**Purpose:** Landing page with project overview and featured diseases.

**Key Sections:**
- Hero section with project title and tagline
- Featured diseases grid (cards with hover effects)
- Quick navigation to main features
- Call-to-action buttons

**Data Sources:**
- Disease data from backend API (`/api/v1/library`)
- Content from backend (`/api/v1/content/home`)

---

### 2. Diagnose Page (`diagnose.html`)

**Purpose:** Main AI diagnosis interface for uploading and analyzing eye images.

**Key Components:**
- **Dropzone**: Drag-and-drop file upload area
- **Preview**: Image preview with lightbox
- **Analyze Button**: Triggers AI prediction
- **Status Indicator**: Shows current state (idle, loading, done, error)
- **Results Display**: Shows prediction with confidence score
- **Reset Button**: Clears current case

**Workflow:**
1. User uploads/drops image
2. Frontend validates file type and size
3. Image preview displayed
4. User clicks "Analyze"
5. Image sent to backend (`POST /predict`)
6. Results displayed with confidence score
7. Prediction saved to database automatically

---

### 3. Diseases Page (`diseases.html`)

**Purpose:** Comprehensive disease library with search and filter capabilities.

**Key Features:**
- **Search Bar**: Filter diseases by name or symptoms
- **Disease Tabs**: Filter by specific disease category
- **Disease Cards**: Detailed information for each condition
- **Bilingual Content**: English and Arabic descriptions
- **RTL Support**: Proper Arabic text rendering

**Data Structure per Disease:**
```javascript
{
  id: "cataract",
  name: "Cataract",
  name_ar: "المياه البيضاء",
  short: "Clouding of the eye's lens...",
  short_ar: "تعكر في عدسة العين...",
  symptoms_ar: ["رؤية ضبابية", "حساسية للضوء"],
  red_flags_ar: ["فقدان البصر المفاجئ"],
  safe_tips_ar: ["جراحة إزالة المياه البيضاء"],
  when_to_see_doctor_ar: "فوراً عند ملاحظة أي تغير",
  risk_level: "Moderate"
}
```

---

### 4. History Page (`history.html`)

**Purpose:** View and manage past predictions.

**Key Features:**
- **Filter Dropdown**: Filter by disease type
- **History List**: Chronological list of predictions
- **Delete Functionality**: Remove individual or all records
- **Statistics**: Count and distribution of predictions

**Data Source:**
- Backend API: `GET /api/v1/results`

---

### 5. About Page (`about.html`)

**Purpose:** Project information, team members, and technology stack.

**Key Sections:**
- Project overview and objectives
- Team members list
- Technology stack
- Supervisor information
- University affiliation

**Data Source:**
- Backend API: `GET /api/v1/content/about`

---

### 6. Safety Page (`safety.html`)

**Purpose:** Important safety information and disclaimers.

**Key Components:**
- Warning banner
- Safety cards with guidelines
- Clinical escalation advice
- Medical disclaimer

**Data Source:**
- Backend API: `GET /api/v1/content/safety`

---

### 7. Education Page (`education.html`)

**Purpose:** Patient education materials and eye care tips.

**Key Features:**
- Educational blocks with icons
- Bilingual content (English/Arabic)
- Preventive care tips
- Healthy eye habits

**Data Source:**
- Backend API: `GET /api/v1/content/education`

---

## Styling System

### CSS Custom Properties (Variables)

```css
:root {
  /* Colors - Light Theme */
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --secondary: #64748b;
  --background: #ffffff;
  --surface: #f8fafc;
  --text: #0f172a;
  --text-muted: #64748b;
  --border: #e2e8f0;
  
  /* Status Colors */
  --success: #22c55e;
  --warning: #f59e0b;
  --danger: #ef4444;
  --info: #3b82f6;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Typography */
  --font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  --font-size-base: 16px;
  --line-height: 1.6;
  
  /* Borders & Shadows */
  --border-radius: 0.5rem;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  
  /* Transitions */
  --transition: all 0.3s ease;
}

/* Dark Theme */
[data-theme="dark"] {
  --background: #0f172a;
  --surface: #1e293b;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
  --border: #334155;
}
```

### Responsive Breakpoints

```css
/* Mobile First Approach */
/* Base styles for mobile (< 640px) */

/* Tablet */
@media (min-width: 640px) {
  /* Tablet-specific styles */
}

/* Desktop */
@media (min-width: 900px) {
  /* Desktop-specific styles */
}

/* Large Screens */
@media (min-width: 1200px) {
  /* Large screen optimizations */
}
```

### Key CSS Classes

| Class | Purpose |
|-------|---------|
| `.container` | Max-width container with padding |
| `.card` | Card component with shadow and border |
| `.btn` | Button base styles |
| `.btn-primary` | Primary action button |
| `.btn-ghost` | Subtle button with hover effect |
| `.btn-outline` | Outlined button |
| `.grid` | CSS Grid layout |
| `.flex` | Flexbox layout |
| `.stack` | Vertical stacking with gap |
| `.reveal` | Scroll animation trigger |
| `.tilt-card` | 3D tilt effect on hover |
| `.rtl` | Right-to-left text direction |
| `.ltr` | Left-to-right text direction |

---

## JavaScript Architecture

### Main Application Structure (`app.js`)

```javascript
(() => {
  "use strict";
  
  // Configuration
  const API_ROOT = (window.DOA_API_BASE || 
                   localStorage.getItem("doa-api-base") || 
                   "http://127.0.0.1:8000").replace(/\/+$/, "");
  const CONTENT_API_BASE = `${API_ROOT}/api/v1`;
  
  // State
  let diseases = null;
  
  // Initialization
  initIcons();
  initTheme();
  initNav();
  initBackToTop();
  initRipple();
  initRevealSystem();
  initTiltCards();
  initHeroParallax();
  
  // Load diseases data
  loadDiseases().catch(() => { diseases = {}; })
    .then(() => {
      const page = document.body.dataset.page;
      if (page === "home") renderHomeDiseases();
      if (page === "diseases") initDiseasesPage();
      if (page === "diagnose") initDiagnosePage();
      if (page === "history") initHistoryPage();
      if (page === "about") initAboutPage();
      if (page === "safety") initSafetyPage();
      if (page === "education") initEducationPage();
    });
  
  // ... rest of the code
})();
```

### Key Functions

#### 1. Theme Management

```javascript
function initTheme() {
  const root = document.documentElement;
  const saved = localStorage.getItem(STORAGE_THEME);
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(saved || (prefersDark ? "dark" : "light"));
  
  // Theme toggle button
  const toggle = byId("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem(STORAGE_THEME, next);
    });
  }
}
```

#### 2. Navigation

```javascript
function initNav() {
  const navBtn = document.querySelector(".nav-toggle");
  const nav = byId("site-nav");
  
  if (!navBtn || !nav) return;
  
  navBtn.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    navBtn.setAttribute("aria-expanded", String(open));
  });
}
```

#### 3. Reveal Animation System

```javascript
function initRevealSystem() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  
  const nodes = document.querySelectorAll(".reveal, .stagger");
  if (!nodes.length) return;
  
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("in-view");
      
      if (entry.target.classList.contains("stagger")) {
        Array.from(entry.target.children).forEach((child, index) => {
          child.style.transitionDelay = `${index * 70}ms`;
        });
      }
      
      io.unobserve(entry.target);
    });
  }, { threshold: 0.15 });
  
  nodes.forEach(n => io.observe(n));
}
```

#### 4. Diagnosis Page Logic

```javascript
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
  
  let currentFile = null;
  let currentDataURL = "";
  
  // File handling
  imageInput.addEventListener("change", () => {
    const file = imageInput.files?.[0];
    if (file) handleFile(file);
  });
  
  // Drag and drop
  dropzone.addEventListener("drop", (e) => {
    const file = e.dataTransfer?.files?.[0];
    if (file) handleFile(file);
  });
  
  // Analyze button
  analyzeBtn.addEventListener("click", async () => {
    if (!currentFile) return;
    
    setStatus(status, "loading", "Analyzing");
    try {
      const predicted = await predictImage(currentFile);
      result.innerHTML = renderPredictionResultContent(predicted);
      setStatus(status, "done", "Result ready");
    } catch (err) {
      setStatus(status, "error", "Analysis failed");
    }
  });
  
  function handleFile(file) {
    // Validate file type and size
    if (!["image/png", "image/jpeg"].includes(file.type)) {
      toast("Invalid file type", "error");
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
      toast("Size too big", "error");
      return;
    }
    
    // Read and preview
    const reader = new FileReader();
    reader.onload = () => {
      currentFile = file;
      currentDataURL = reader.result;
      preview.innerHTML = `<img src="${currentDataURL}" alt="Preview" />`;
      analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  }
}
```

#### 5. API Integration

```javascript
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
    const detail = data?.detail ? String(data.detail) : `Request failed (${response.status})`;
    throw new Error(detail);
  }
  
  return data || {};
}
```

---

## API Integration

### Base Configuration

```javascript
const API_ROOT = (window.DOA_API_BASE || 
                 localStorage.getItem("doa-api-base") || 
                 "http://127.0.0.1:8000").replace(/\/+$/, "");
const CONTENT_API_BASE = `${API_ROOT}/api/v1`;
```

### API Functions

| Function | Endpoint | Purpose |
|----------|----------|---------|
| `predictImage(file)` | `POST /predict` | AI disease prediction |
| `listResults(prediction)` | `GET /api/v1/results` | Get prediction history |
| `deleteResult(id)` | `DELETE /api/v1/results/{id}` | Delete a prediction |
| `listLibrary(q, name)` | `GET /api/v1/library` | Get disease information |
| `getSectionContent(type)` | `GET /api/v1/content/{type}` | Get page content |

### Error Handling

```javascript
async function parseApiResponse(response) {
  let data = null;
  try {
    data = await response.json();
  } catch (_err) {
    data = null;
  }
  
  if (!response.ok) {
    const detail = data?.detail ? String(data.detail) : `Request failed (${response.status})`;
    throw new Error(detail);
  }
  
  return data || {};
}
```

---

## Key Features

### 1. Theme System

- **Light/Dark Mode**: Automatic detection + manual toggle
- **Persistence**: Theme preference saved in LocalStorage
- **Smooth Transition**: CSS transitions for theme switching

### 2. Responsive Navigation

- **Mobile Menu**: Hamburger menu for mobile devices
- **Desktop Menu**: Full navigation bar for larger screens
- **Accessibility**: Proper ARIA attributes and keyboard navigation

### 3. Image Upload & Preview

- **Drag and Drop**: Intuitive file upload
- **File Validation**: Type and size checking
- **Image Preview**: Lightbox-style preview
- **Progress Indication**: Loading states and status

### 4. Animations & Effects

- **Scroll Reveal**: Elements animate in as user scrolls
- **Tilt Effect**: 3D card tilt on mouse movement
- **Ripple Effect**: Material Design-style button ripples
- **Parallax**: Hero section parallax on scroll

### 5. Accessibility

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: Proper ARIA labels and roles
- **Focus Management**: Visible focus indicators
- **Reduced Motion**: Respects user's motion preferences

### 6. Bilingual Support

- **English/Arabic**: Full content in both languages
- **RTL Layout**: Proper right-to-left text rendering
- **Language Toggle**: Easy language switching
- **Font Support**: Arabic-friendly fonts

---

## Best Practices

### 1. Code Organization

```javascript
// Use IIFE to avoid global scope pollution
(() => {
  "use strict";
  
  // Constants first
  const CONSTANTS = { ... };
  
  // State
  let state = { ... };
  
  // Initialization
  function init() { ... }
  
  // Event handlers
  function handleEvent() { ... }
  
  // Utility functions
  function utility() { ... }
  
  // Start application
  init();
})();
```

### 2. DOM Manipulation

```javascript
// Use helper functions for common operations
function byId(id) { 
  return document.getElementById(id); 
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&")
    .replace(/</g, "<")
    .replace(/>/g, ">")
    .replace(/\"/g, """)
    .replace(/'/g, "&#039;");
}
```

### 3. Event Delegation

```javascript
// Use event delegation for dynamic content
container.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-action]");
  if (btn) {
    handleAction(btn.dataset.action);
  }
});
```

### 4. Async Operations

```javascript
// Always handle errors in async operations
async function fetchData() {
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (err) {
    console.error("Fetch error:", err);
    throw err;
  }
}
```

### 5. Performance

```javascript
// Debounce expensive operations
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Use Intersection Observer for lazy loading
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      loadImage(entry.target);
      observer.unobserve(entry.target);
    }
  });
});
```

---

## Running the Frontend

### Development Server

```bash
cd frontend
python3 -m http.server 8080
```

Open: http://127.0.0.1:8080/pages/index.html

### Configure API URL

If backend is not on default URL:

```javascript
// In browser console:
localStorage.setItem("doa-api-base", "http://your-backend-url:8000");
location.reload();
```

### Production Deployment

1. **Static Hosting**: Deploy `frontend/` directory to any static host
2. **CDN**: Use CDN for better performance
3. **Environment Variables**: Set API URL via `window.DOA_API_BASE`

---

## Browser Support

| Browser | Version | Support |
|---------|---------|---------|
| Chrome | 90+ | ✅ Full |
| Firefox | 88+ | ✅ Full |
| Safari | 14+ | ✅ Full |
| Edge | 90+ | ✅ Full |
| Mobile Safari | iOS 14+ | ✅ Full |
| Chrome Mobile | Android 9+ | ✅ Full |

---

*For questions about the frontend, contact the Frontend team lead.*

*Last Updated: [Current Date]*  
*Document Version: 1.0*