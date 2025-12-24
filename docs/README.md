📊 CyberNow Dashboard — Frontend (Demo Mode)

This folder contains the static frontend dashboard for the CyberNow – Real-Time Cyber Incident Monitoring System.

The frontend is designed to run independently of the backend in Demo Mode, making it suitable for:

GitHub Pages hosting

Resume and portfolio showcase

UI/UX demonstrations

🌐 What This Folder Contains
docs/
├── index.html        # Main dashboard UI
├── styles.css        # Dashboard styling
├── dashboard.js      # Frontend logic (Demo-aware)
├── assets/           # Icons / images (if any)
└── README.md         # This file

🚀 Features Demonstrated (Frontend)

📡 Live Cyber Threat Feed UI

🚨 Critical Incident Counter

🏭 Affected Sectors (Horizontal Bar Chart)

📈 Threat Trends Analysis

🔐 Password Breach Check UI

⚠️ Demo Mode Banner (Auto-detected)

🔁 Auto-refresh logic (every 60 seconds)

🎨 Modern, responsive dashboard design

⚠️ Demo Mode Explained

When this dashboard is opened via:

GitHub Pages

Local file (file://)

Without backend services running

It automatically switches to Demo Mode and displays a banner:

⚠ Demo Mode — Backend services are not active. Data shown is simulated.

This ensures:

No broken UI

Graceful fallback behavior

Clear communication to viewers/recruiters

🧪 How to Run (Demo Mode)
Option 1: Open Locally
docs/index.html


Just double-click the file or open it in a browser.

Option 2: GitHub Pages (Recommended)

Once GitHub Pages is enabled:

https://<your-username>.github.io/<repo-name>/

🔌 Backend Integration (Optional)

When connected to the backend:

API endpoints like /api/incidents/live and /api/dashboard/summary become active

Demo banner automatically hides

Real-time data is displayed

Backend code lives outside this folder and is not required for demo viewing.

🎯 Purpose of This Frontend

This dashboard is intended for:

Cybersecurity portfolio showcase

Academic projects

Resume demonstrations

UI/UX validation before deployment

It demonstrates real-world SOC-style dashboard behavior with fallback support.

🧠 Technologies Used

HTML5

CSS3

Vanilla JavaScript

Chart.js

Responsive Design

REST API integration (optional)

📸 Screenshots / Demo

Add screenshots or GIFs here (optional but recommended for recruiters)

👤 Author

Madhusudhan S
B.Tech Computer Science (Cyber Security)
🔗 GitHub: https://github.com/MADHU-55

✅ Notes for Recruiters

Backend services are not required to view this dashboard

Demo Mode is intentional and documented

Full backend pipeline exists in the main repository