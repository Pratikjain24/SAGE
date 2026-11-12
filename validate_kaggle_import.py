# Quick validation script
import json
import pandas as pd
from pathlib import Path

run_dir = Path("experiments/runs/kaggle_study")

# 1. Check trajectories exist
traj_files = list((run_dir / "trajectories").glob("*.jsonl"))
print(f"✅ Found {len(traj_files)} trajectory files")

# 2. Load and check results
results_file = run_dir / "results" / "task_results.csv"
if results_file.exists():
    df = pd.read_csv(results_file)
    print(f"✅ Results: {len(df)} task executions")
    print(f"   Agents: {df['agent'].unique()}")
    print(f"   Tasks: {df['task_id'].nunique()}")
else:
    print("⚠️ No task_results.csv found")

# 3. Check metrics
metrics_file = run_dir / "results" / "metrics_summary.json"
if metrics_file.exists():
    with open(metrics_file) as f:
        metrics = json.load(f)
    print(f"✅ Metrics available: {list(metrics.keys())}")
else:
    print("⚠️ No metrics_summary.json found")

print("\n🎉 Organization complete!")

