# Digital Ophthalmology Assistant - Frontend

Static HTML/CSS/JavaScript frontend for the AI-powered ophthalmology assistant.

> **Note**: No build tools or frameworks required. This is a pure static frontend that runs in any modern browser.

---

## 📋 Table of Contents

1. [Features](#features)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Configuration](#configuration)
5. [Pages Overview](#pages-overview)
6. [API Integration](#api-integration)
7. [Troubleshooting](#troubleshooting)

---

## ✨ Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Theme**: Toggle with system preference detection
- **Image Upload**: Drag & drop or click to upload eye images
- **AI Prediction**: Real-time disease classification from backend
- **Disease Library**: Searchable database with English/Arabic content
- **History**: View and manage past predictions
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support
- **No Framework**: Pure vanilla JavaScript - fast and lightweight

---

## 🚀 Quick Start

### Prerequisites

- Python 3.x (for simple HTTP server) OR Node.js
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Option 1: Python HTTP Server

```bash
# Navigate to frontend directory
cd frontend

# Start simple HTTP server
python -m http.server 8080

# Open browser
# http://127.0.0.1:8080/pages/index.html
```

### Option 2: Node.js HTTP Server

```bash
# Install http-server globally (once)
npm install -g http-server

# Navigate to frontend directory
cd frontend

# Start server
http-server -p 8080

# Open browser
# http://127.0.0.1:8080/pages/index.html
```

### Option 3: Direct File Open

Simply open `frontend/pages/index.html` in your browser. Note: Some features may be limited due to CORS restrictions when not using a server.

---

## 📁 Project Structure

```
frontend/
├── pages/                    # HTML pages
│   ├── index.html           # Home page
│   ├── diagnose.html        # Image upload & prediction
│   ├── diseases.html        # Disease library
│   ├── history.html         # Prediction history
│   ├── about.html           # About the project
│   ├── safety.html          # Safety & disclaimers
│   └── education.html       # Patient education
│
├── styles/
│   └── styles.css           # Main stylesheet (responsive, dark/light themes)
│
├── js/
│   └── app.js               # Main JavaScript (API calls, UI interactions)
│
├── assets/
│   └── icons.js             # SVG icons as JavaScript functions
│
└── README.md                # This file
```

---

## ⚙️ Configuration

### API Base URL

The frontend connects to the backend API. By default, it expects the backend at `http://127.0.0.1:8000`.

#### Change API URL

**Method 1**: Set in browser localStorage
```javascript
// Open browser console and run:
localStorage.setItem("doa-api-base", "http://your-backend-url:8000");
location.reload();
```

**Method 2**: Set global variable before app loads
```html
<script>
  window.DOA_API_BASE = "http://your-backend-url:8000";
</script>
<script src="js/app.js"></script>
```

---

## 📄 Pages Overview

### Home (`index.html`)
- Welcome page with project overview
- Quick links to main features
- Featured diseases showcase

### Diagnose (`diagnose.html`)
- **Main feature**: Upload eye image for AI analysis
- Drag & drop or click to upload
- Real-time prediction with confidence score
- Image preview with lightbox
- Result display with disease information

### Diseases (`diseases.html`)
- Searchable disease library
- Filter by disease type
- Detailed information in English and Arabic
- Symptoms, warnings, and safe tips

### History (`history.html`)
- View all past predictions
- Filter by disease type
- Delete individual records
- Clear all history

### About (`about.html`)
- Project information
- Team members
- Technology stack
- Deployment details

### Safety (`safety.html`)
- Important disclaimers
- Educational purpose notice
- Model limitations
- When to see a doctor

### Education (`education.html`)
- How to capture good eye images
- Urgent vs non-urgent conditions
- Hygiene and prevention tips
- Bilingual content (English/Arabic)

---

## 🔗 API Integration

The frontend uses these backend endpoints:

| Feature | Method | Endpoint | Description |
|---------|--------|----------|-------------|
| Prediction | POST | `/predict` | Upload image, get disease prediction |
| Results List | GET | `/api/v1/results` | Get all predictions (with optional filter) |
| Delete Result | DELETE | `/api/v1/results/{id}` | Remove a prediction from history |
| Content | GET | `/api/v1/content/{type}` | Get page content (about, safety, education) |
| Library | GET | `/api/v1/library` | Get disease library (with search) |

### Example: Image Prediction

```javascript
// From app.js
async function predictImage(file) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API_ROOT}/predict`, {
        method: "POST",
        body: formData
    });
    return parseApiResponse(response);
}
```

---

## 🎨 Features & UI Components

### Theme System
- Auto-detects system preference (light/dark)
- Manual toggle with localStorage persistence
- Smooth transitions between themes

### Responsive Design
- Mobile-first approach
- Breakpoints: 600px, 900px, 1200px
- Touch-friendly buttons and navigation

### Animations
- Scroll reveal animations
- Tilt effect on cards (desktop only)
- Ripple effect on buttons
- Hero parallax effect

### Accessibility
- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Focus indicators
- Screen reader friendly

---

## 🔧 Troubleshooting

### 1. "Failed to fetch" errors
**Cause**: Backend server is not running or URL is incorrect.

**Solution**:
1. Make sure backend is running: `http://127.0.0.1:8000/health`
2. Check API URL in localStorage: `localStorage.getItem("doa-api-base")`
3. Set correct URL: `localStorage.setItem("doa-api-base", "http://127.0.0.1:8000")`

### 2. CORS errors
**Cause**: Frontend and backend are on different origins without proper CORS headers.

**Solution**:
1. Run both frontend and backend on same origin (recommended)
2. Or configure backend CORS to allow frontend origin
3. Or use a proxy server

### 3. Images not uploading
**Cause**: File size too large or invalid format.

**Solution**:
- Supported formats: PNG, JPG, JPEG, BMP, WEBP
- Max file size: 10MB (configurable in backend)

### 4. Styles not loading
**Cause**: Incorrect file paths when opening HTML directly.

**Solution**:
- Always use a local HTTP server (see Quick Start)
- Don't open HTML files directly with `file://` protocol

### 5. Blank page
**Cause**: JavaScript error or missing dependencies.

**Solution**:
1. Open browser console (F12) to see errors
2. Make sure all files are in correct directories
3. Check that `app.js` is loaded after other scripts

---

## 📱 Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

---

## 🛠 Development Tips

### Adding New Pages
1. Create new HTML file in `pages/`
2. Add `data-page="your-page-name"` to `<body>` tag
3. Add initialization function in `app.js`:
   ```javascript
   if (page === "your-page") initYourPage();
   ```

### Changing Styles
1. Edit `styles/styles.css`
2. CSS variables for colors:
   ```css
   :root {
     --primary: #your-color;
     --background: #your-bg;
   }
   ```

### Adding New API Calls
1. Add async function in `app.js`:
   ```javascript
   async function yourNewFunction() {
     const response = await fetch(`${CONTENT_API_BASE}/your-endpoint`);
     return parseApiResponse(response);
   }
   ```

---

## 📄 License

Proprietary - Delta University for Science and Technology

---

## 👥 Credits

Developed by the AI-Based Eye Disease Classification Team at Delta University for Science and Technology.

**Supervisor**: Dr. Eman Salah  
**Team Members**: Fares Tamer, Israa Eldsouky, Mohamed Ayman, Mohamed Mahmoud, Karim Saeed, Rawan Elsaid, Ohoud Abdelnaem, Sama Abdeltawab, Waad Ahmed, Wesam Mohamed, Zeyad Waleed