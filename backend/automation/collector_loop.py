# automation/collector_loop.py
import time
from datetime import datetime

from backend.collector.collector import collect_incidents
from backend.ml.predict import classify_new_incidents
from backend.ml.drift import check_and_handle_drift

POLL_INTERVAL_SECONDS = 150   # 2.5 minutes


def main():
    print("🚀 CyberNow Automation Pipeline Started")

    while True:
        print("\n========================================")
        print(f"[{datetime.utcnow()}] ⏳ Running pipeline cycle...")

        # Step 1: Collect Incidents
        print("📥 Collecting new incidents...")
        new_ids = collect_incidents()
        print(f"   → {len(new_ids)} new incidents" if new_ids else "   → No new incidents")

        # Step 2: Classify
        print("🤖 Classifying incidents...")
        classify_new_incidents()

        # Step 3: Drift Detection (triggers auto-train)
        print("🧠 Checking model drift...")
        retrained = check_and_handle_drift()
        print("   ✔ Model retrained" if retrained else "   ✔ No drift")

        print(f"⏳ Sleeping for {POLL_INTERVAL_SECONDS} seconds...\n")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
