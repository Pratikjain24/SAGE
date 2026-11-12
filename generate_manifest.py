"""
Generate SHA-256 integrity manifest for Kaggle experiment results
"""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

def compute_sha256(filepath):
    """Compute SHA-256 hash of file"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_manifest(run_dir):
    """Generate integrity manifest for experiment run"""
    run_path = Path(run_dir)
    
    manifest = {
        "run_id": "kaggle_study",
        "generation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": "kaggle",
        "total_files": 0,
        "files": {}
    }
    
    print(f"📂 Scanning directory: {run_path}")
    
    # Scan all files under run_path
    all_files = sorted([f for f in run_path.rglob("*") if f.is_file()])
    print(f"   Found {len(all_files)} total files")
    
    for f in all_files:
        rel_str = str(f.relative_to(run_path)).replace("\\", "/")
        if rel_str in ["trajectory_manifest.json", "MANIFEST.sha256", "SHA256_MANIFEST.json"]:
            continue
        file_hash = compute_sha256(f)
        manifest["files"][rel_str] = {
            "sha256": file_hash,
            "size_bytes": f.stat().st_size
        }
    
    manifest["total_files"] = len(manifest["files"])
    
    # Save manifest
    manifest_path = run_path / "trajectory_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Manifest generated: {manifest_path}")
    print(f"   Total files tracked: {len(manifest['files'])}")
    
    return manifest

if __name__ == "__main__":
    manifest = generate_manifest("experiments/runs/kaggle_study")
