#!/usr/bin/env bash
# ================================================================
# SYSTEM SPECIFICATION: COHERENCE COLLAPSE / UNIFIED TRIALITY PIPELINE
# AUTOMATED NIGHTLY LIFECYCLE RECOVERY LAYER: cron_archive.sh
# ================================================================
# CRONTAB REGISTRATION PROTOCOL:
# Open terminal, execute: crontab -e
# Pre-pend the following explicit execution vector string:
# 0 2 * * * /bin/bash /absolute/path/to/your/repository/cron_archive.sh >> /absolute/path/to/your/repository/cron_cron.log 2>&1
# ================================================================
#
# NOTE (Lotus, 2026-10-05): the archive engines now live in this repo at
# src/triality_pipeline/io/archive_engines.py (ported from the utp-v5 gap
# pack; S3 client made lazy so the cron idles cleanly without credentials).
# Imports below point at the real location; steps 3-4 run end to end.
set -e

# Establish local storage directory environments
# [REPAIRED] line-break joins across the PDF page boundary; BASH_SOURCE[0] is
# the standard idiom (bare ${BASH_SOURCE} is equivalent in bash).
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOT_DIR="$REPO_DIR/hot_tier"
WARM_DIR="$REPO_DIR/warm_dir"
VENV_ACTIVATE="$REPO_DIR/.venv/bin/activate"

echo "=== STARTING NIGHTLY DATA LIFECYCLE SWEEP: $(date -u) ==="

# 1. Verify Virtual Environment Initialization
if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "[CRITICAL FAULT] Hermetic environment missing. Execute deploy.sh first."
    exit 1
fi
source "$VENV_ACTIVATE"

# 2. Check for newly generated structural series.csv records
if [ ! -d "$HOT_DIR" ] || [ -z "$(ls -A "$HOT_DIR" 2>/dev/null)" ]; then
    echo "[IDLE] NVMe Hot Tier buffer array empty. No active data records to recompile."
    exit 0
fi

# 3. Call internal Python Data Management Plan Compactor
echo "[COMPACTING] Recompiling raw series text logs to columnar binary Parquet format..."
python3 -c "
from triality_pipeline.io.archive_engines import DataManagementPlanArchiveEngine
import os
engine = DataManagementPlanArchiveEngine(hot_dir='$HOT_DIR', warm_dir='$WARM_DIR')
for file in os.listdir('$HOT_DIR'):
    if file.endswith('.csv'):
        engine.archive_csv_to_parquet(file)
"

# 4. Stream and Freeze Compliant Parquet Tables into AWS Glacier Cold Archive
echo "[STORING] Calling CloudArchiveStorageManager for secure remote upload..."
python3 -c "
from triality_pipeline.io.archive_engines import CloudArchiveStorageManager
import os
manager = CloudArchiveStorageManager(bucket_name='triality-pipeline-telemetry-archive')
for file in os.listdir('$WARM_DIR'):
    if file.endswith('.parquet'):
        full_path = os.path.join('$WARM_DIR', file)
        success = manager.upload_parquet_to_cold_archive(full_path)
        if success:
            # Purge the local Warm file only after verified cloud commit confirmation
            os.remove(full_path)
"

echo "=== NIGHTLY COMPRESSION AND COLD ARCHIVE UPLOAD COMPLETE ==="
