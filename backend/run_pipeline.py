import time

from backend.collector.rss_collector import run_once as collect
from backend.collector.ml_classifier import classify_new_incidents
from backend.automation.retrain_controller import run_retraining

print("🚀 CyberNow pipeline started")

while True:
    try:
        print("📥 Collecting incidents...")
        collect()

        print("🧠 Classifying new incidents...")
        classify_new_incidents()


        print("🔁 Checking drift & retraining if needed...")
        run_retraining()

        print("✅ Pipeline cycle complete. Sleeping...")
    except Exception as e:
        print("❌ Pipeline error:", e)

    time.sleep(600)  # run every 10 minutes
