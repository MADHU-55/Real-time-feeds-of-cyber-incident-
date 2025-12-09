# CyberNow

Local dev + automated pipeline for CyberNow dashboard:
- Flask backend (SQLite)
- RSS collector (feedparser)
- Simple ML pipeline (train, isolation forest drift detection)
- Automation scripts + GitHub Actions

## Quickstart (local)

1. Create venv and install:
```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
pip install -r backend/requirements.txt
