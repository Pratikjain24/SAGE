import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

def compute_sha256(filepath):
    """Compute SHA-256 hash of file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_manifest(run_dir):
    """Generate integrity manifest for experiment run"""
    run_path = Path(run_dir)

    manifest = {
        "run_id": "kaggle_study",
        "generation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": "kaggle",
        "files": {}
    }

    # Hash all trajectory files
    traj_dir = run_path / "trajectories"
    if traj_dir.exists():
        for traj_file in sorted(traj_dir.glob("*.jsonl")):
            file_hash = compute_sha256(traj_file)
            manifest["files"][str(traj_file.relative_to(run_path)).replace("\\", "/")] = {
                "sha256": file_hash,
                "size_bytes": traj_file.stat().st_size
            }

    # Hash result files
    results_dir = run_path / "results"
    if results_dir.exists():
        for result_file in sorted(results_dir.glob("*")):
            if result_file.is_file():
                file_hash = compute_sha256(result_file)
                manifest["files"][str(result_file.relative_to(run_path)).replace("\\", "/")] = {
                    "sha256": file_hash,
                    "size_bytes": result_file.stat().st_size
                }

    # Save manifest
    manifest_path = run_path / "trajectory_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ Manifest generated: {manifest_path}")
    print(f"   Files tracked: {len(manifest['files'])}")

    return manifest

# Run it
if __name__ == "__main__":
    manifest = generate_manifest("experiments/runs/kaggle_study")
