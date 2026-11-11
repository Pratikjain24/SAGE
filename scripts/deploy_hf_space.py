#!/usr/bin/env python3
"""
1-Click Deploy SAGE Evaluation Dashboard to Hugging Face Spaces.

Usage:
    python scripts/deploy_hf_space.py --repo-id Pratikjain24/SAGE-Dashboard
    python scripts/deploy_hf_space.py --token <HF_TOKEN>
"""

from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Deploy SAGE Next.js Dashboard to Hugging Face Spaces")
    parser.add_argument("--repo-id", default="Pratikjain24/SAGE-Dashboard", help="Hugging Face Space repository ID (e.g. username/SAGE-Dashboard)")
    parser.add_argument("--token", default=os.environ.get("HF_TOKEN"), help="Hugging Face write token")
    parser.add_argument("--private", action="store_true", help="Make Space private")
    parser.add_argument("--dry-run", action="store_true", help="Validate Space files locally without network deployment")
    args = parser.parse_args()

    # Prepare root files for the Space
    hf_dir = Path("hf_space")
    if not hf_dir.exists():
        print(f"[!] Error: {hf_dir} does not exist.")
        sys.exit(1)

    required_files = ["README.md", "Dockerfile", "requirements.txt", "start.sh"]
    for req in required_files:
        fpath = hf_dir / req
        if not fpath.exists():
            print(f"[!] Error: required Space file {req} not found in {hf_dir}")
            sys.exit(1)
        print(f"[✓] Verified Space asset: {req} ({fpath.stat().st_size} bytes)")

    if args.dry_run:
        print(f"[DRY-RUN] Hugging Face Space package for '{args.repo_id}' validated successfully! Skipping network upload.")
        sys.exit(0)

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("[!] huggingface_hub is not installed. Please run: pip install huggingface_hub")
        sys.exit(1)

    if not args.token:
        print("[!] Error: HF_TOKEN required for live deployment.")
        sys.exit(1)

    api = HfApi(token=args.token)
    repo_id = args.repo_id

    print(f"[*] Initializing Hugging Face Space: {repo_id} (SDK: Docker, Port: 7860)...")
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            private=args.private,
            exist_ok=True,
        )
        print(f"[✓] Space repository ready: https://huggingface.co/spaces/{repo_id}")
    except Exception as e:
        print(f"[!] Note on repo creation: {e}")

    print("[*] Uploading Hugging Face Space configuration and dashboard assets...")
    try:
        # Upload Space README.md (frontmatter)
        api.upload_file(
            path_or_fileobj=str(hf_dir / "README.md"),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="space",
        )
        # Upload Dockerfile
        api.upload_file(
            path_or_fileobj=str(hf_dir / "Dockerfile"),
            path_in_repo="Dockerfile",
            repo_id=repo_id,
            repo_type="space",
        )
        # Upload requirements.txt
        api.upload_file(
            path_or_fileobj=str(hf_dir / "requirements.txt"),
            path_in_repo="hf_space/requirements.txt",
            repo_id=repo_id,
            repo_type="space",
        )
        # Upload start.sh
        api.upload_file(
            path_or_fileobj=str(hf_dir / "start.sh"),
            path_in_repo="hf_space/start.sh",
            repo_id=repo_id,
            repo_type="space",
        )
        print(f"[✓] Deployment complete! Space is live at: https://huggingface.co/spaces/{repo_id}")
    except Exception as e:
        print(f"[!] Upload status: {e}")

if __name__ == "__main__":
    main()
