# backend/run_collector.py
# Simple CLI to run collector once.
from backend.collector.rss_collector import run_once

if __name__ == "__main__":
    run_once()
    print("Collector run completed.")
