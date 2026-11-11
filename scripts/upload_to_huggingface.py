#!/usr/bin/env python3
"""
upload_to_huggingface.py — SAGE Hugging Face Hub Dataset Publisher.

Uploads the 100-task SAGE benchmark catalog and/or longitudinal trajectory
datasets (canonical 18k and live distributed 9.8k) to Hugging Face Hub.

Usage:
    # 1. Dry-run validation (no token required):
    python scripts/upload_to_huggingface.py --dry-run
    python scripts/upload_to_huggingface.py --dataset-dir experiments/runs/full_study_live_distributed --dry-run

    # 2. Upload tasks catalog to Hub:
    python scripts/upload_to_huggingface.py --token hf_YOUR_TOKEN --repo-id Pratikjain24/SAGE-benchmark

    # 3. Upload trajectory directory to Hub (private or public):
    python scripts/upload_to_huggingface.py --dataset-dir experiments/runs/full_study_live_distributed --repo-id Pratikjain24/SAGE-benchmark --private
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_INDEX = REPO_ROOT / "tasks" / "tasks_index.json"
DEFAULT_REPO_ID = "Pratikjain24/SAGE-benchmark"


def ensure_tasks_index():
    """Generate the task catalog if it doesn't exist yet."""
    if not TASKS_INDEX.exists():
        print("tasks_index.json not found — generating now...")
        subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "generate_task_catalog.py")],
            check=True,
            cwd=str(REPO_ROOT),
        )
    if not TASKS_INDEX.exists():
        raise FileNotFoundError(
            f"tasks/tasks_index.json still not found after generation. "
            f"Run: python scripts/generate_task_catalog.py"
        )


def upload_tasks(hf_token: str, repo_id: str = DEFAULT_REPO_ID, private: bool = False, dry_run: bool = False) -> str:
    """Upload task catalog to HuggingFace Hub. Returns the dataset URL."""
    try:
        from datasets import Dataset
    except ImportError:
        print("Installing 'datasets' library...")
        subprocess.run([sys.executable, "-m", "pip", "install", "datasets"], check=True)
        from datasets import Dataset

    ensure_tasks_index()
    tasks = json.loads(TASKS_INDEX.read_text(encoding="utf-8"))
    print(f"Loaded {len(tasks)} benchmark tasks from {TASKS_INDEX}")

    ds = Dataset.from_list(tasks)
    print(f"Constructed PyArrow Dataset: {len(ds)} rows, {len(ds.column_names)} features: {ds.column_names}")

    if dry_run:
        print("[DRY-RUN] Task catalog dataset validated successfully! Skipping network upload.")
        return f"https://huggingface.co/datasets/{repo_id} (dry-run)"

    print(f"Pushing tasks dataset to HuggingFace Hub: {repo_id} (private={private}) ...")
    ds.push_to_hub(
        repo_id,
        token=hf_token,
        private=private,
        commit_message="Release: SAGE 100-task benchmark catalog v1.0",
    )

    url = f"https://huggingface.co/datasets/{repo_id}"
    print(f"\n✅ Tasks upload successful!")
    print(f"   Dataset URL: {url}")
    return url


def upload_directory(dataset_dir: Path, hf_token: str, repo_id: str = DEFAULT_REPO_ID, private: bool = False, dry_run: bool = False) -> str:
    """Upload an entire trajectory directory to HuggingFace Hub."""
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    files = list(dataset_dir.rglob("*"))
    file_list = [f for f in files if f.is_file()]
    total_bytes = sum(f.stat().st_size for f in file_list)
    print(f"Found {len(file_list)} files ({total_bytes / (1024*1024):.2f} MB) in {dataset_dir}")

    for f in file_list:
        print(f"  - {f.relative_to(dataset_dir)} ({f.stat().st_size / 1024:.1f} KB)")

    if dry_run:
        print(f"[DRY-RUN] Trajectory directory '{dataset_dir}' validated successfully! Skipping network upload.")
        return f"https://huggingface.co/datasets/{repo_id} (dry-run)"

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("Installing 'huggingface_hub'...")
        subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub"], check=True)
        from huggingface_hub import HfApi

    api = HfApi(token=hf_token)
    print(f"Ensuring HuggingFace dataset repo exists: {repo_id} (private={private})...")
    api.create_repo(
        repo_id=repo_id,
        repo_type="dataset",
        private=private,
        exist_ok=True,
    )

    print(f"Uploading folder '{dataset_dir}' to {repo_id}...")
    api.upload_folder(
        folder_path=str(dataset_dir),
        repo_id=repo_id,
        repo_type="dataset",
        commit_message=f"Upload trajectory artifacts from {dataset_dir.name}",
    )

    url = f"https://huggingface.co/datasets/{repo_id}"
    print(f"\n✅ Directory upload successful!")
    print(f"   Dataset URL: {url}")
    return url


def main():
    parser = argparse.ArgumentParser(
        description="Upload SAGE benchmark tasks and trajectory datasets to HuggingFace Hub."
    )
    parser.add_argument(
        "--token",
        type=str,
        default=os.environ.get("HF_TOKEN", ""),
        help="HuggingFace API write token (or set HF_TOKEN env var)",
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        default=DEFAULT_REPO_ID,
        help=f"HuggingFace dataset repo ID (default: {DEFAULT_REPO_ID})",
    )
    parser.add_argument(
        "--dataset-dir",
        type=str,
        default=None,
        help="Optional path to trajectory directory to upload (e.g. experiments/runs/full_study_live_distributed)",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create/set the HuggingFace dataset repository as private",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate datasets and file schemas locally without network upload",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.token:
        args.token = input("HuggingFace token (or set HF_TOKEN env var): ").strip()
    if not args.dry_run and not args.token:
        print("Error: HuggingFace token required for network operations.")
        sys.exit(1)

    if args.dataset_dir:
        target_dir = Path(args.dataset_dir).resolve()
        upload_directory(target_dir, args.token, repo_id=args.repo_id, private=args.private, dry_run=args.dry_run)
    else:
        upload_tasks(args.token, repo_id=args.repo_id, private=args.private, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
