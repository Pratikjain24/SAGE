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

    # Hash human audit files
    audit_dir = run_path / "human_audit"
    if audit_dir.exists():
        for audit_file in sorted(audit_dir.glob("*")):
            if audit_file.is_file():
                file_hash = compute_sha256(audit_file)
                manifest["files"][str(audit_file.relative_to(run_path)).replace("\\", "/")] = {
                    "sha256": file_hash,
                    "size_bytes": audit_file.stat().st_size
                }

    # Hash tables
    tables_dir = run_path / "tables"
    if tables_dir.exists():
        for tbl_file in sorted(tables_dir.glob("*")):
            if tbl_file.is_file():
                file_hash = compute_sha256(tbl_file)
                manifest["files"][str(tbl_file.relative_to(run_path)).replace("\\", "/")] = {
                    "sha256": file_hash,
                    "size_bytes": tbl_file.stat().st_size
                }

    # Save trajectory manifest
    manifest_path = run_path / "trajectory_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    # Also build comprehensive MANIFEST.sha256 and SHA256_MANIFEST.json across all files in run_dir
    all_file_manifest = {}
    sha256_lines = []
    for fpath in sorted(run_path.rglob("*")):
        if not fpath.is_file():
            continue
        rel_str = str(fpath.relative_to(run_path)).replace("\\", "/")
        if rel_str in ["MANIFEST.sha256", "SHA256_MANIFEST.json", "trajectory_manifest.json"]:
            continue
        f_hash = compute_sha256(fpath)
        f_size = fpath.stat().st_size
        f_mtime = datetime.fromtimestamp(fpath.stat().st_mtime, tz=timezone.utc).isoformat()
        all_file_manifest[rel_str] = {
            "sha256": f_hash,
            "size_bytes": f_size,
            "modified_utc": f_mtime,
        }
        sha256_lines.append(f"{f_hash}  {rel_str}")

    # Write MANIFEST.sha256
    (run_path / "MANIFEST.sha256").write_text("\n".join(sha256_lines) + "\n", encoding="utf-8")

    # Write SHA256_MANIFEST.json
    root_json_manifest = {
        "manifest_version": "1.0.0",
        "study": "SAGE Live Distributed Kaggle Study",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_files": len(all_file_manifest),
        "files": all_file_manifest,
    }
    with open(run_path / "SHA256_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(root_json_manifest, f, indent=2)

    print(f"✅ Manifests generated:")
    print(f"   Trajectory Manifest : {manifest_path} ({len(manifest['files'])} files)")
    print(f"   Master SHA256 File  : {run_path / 'MANIFEST.sha256'} ({len(sha256_lines)} files)")
    print(f"   Master JSON Manifest: {run_path / 'SHA256_MANIFEST.json'} ({len(all_file_manifest)} files)")

    return manifest

if __name__ == "__main__":
    manifest = generate_manifest("experiments/runs/kaggle_study")
