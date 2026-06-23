import subprocess
import sys
import logging
import os
from datetime import datetime

# Force UTF-8 encoding for emoji support on Windows
os.environ["PYTHONIOENCODING"] = "utf-8"

# ─────────────────────────────────────────
# Setup Logging — records every run
# ─────────────────────────────────────────
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

logging.basicConfig(
    filename=f"{log_folder}/scheduler.log",
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def run_script(script_name):
    """Run a Python script and log the result."""
    print(f">>  Running {script_name}...")
    logging.info(f"Starting {script_name}")

    try:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", script_name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=300
        )

        if result.returncode == 0:
            print(f"OK  {script_name} completed successfully!")
            logging.info(f"{script_name} SUCCESS:\n{result.stdout}")
        else:
            print(f"ERR {script_name} failed!")
            logging.error(f"{script_name} FAILED:\n{result.stderr}")

    except subprocess.TimeoutExpired:
        print(f"TIMEOUT  {script_name} timed out!")
        logging.error(f"{script_name} TIMED OUT after 5 minutes")

    except Exception as e:
        print(f"ERR Error running {script_name}: {e}")
        logging.error(f"{script_name} ERROR: {e}")

# ─────────────────────────────────────────
# Main Pipeline
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print(f"  KENYA DEMAND ANALYSIS - AUTO REFRESH")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    logging.info("=" * 40)
    logging.info("WEEKLY REFRESH STARTED")

    # Run full pipeline in order
    run_script("pull_data.py")
    run_script("queries.py")
    run_script("visualize.py")
    run_script("export_excel.py")
    run_script("alerts.py") 

    print("\n" + "=" * 55)
    print(f"  WEEKLY REFRESH COMPLETE!")
    print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    logging.info("WEEKLY REFRESH COMPLETE")