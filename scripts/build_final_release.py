"""
Final Publication Release Package Builder (`scripts/build_final_release.py`).

Automates packaging of the complete KDR-CA-AEAD research release into `release/`:
- release/paper/
- release/docs/
- release/benchmark_results/
- release/validation_results/
- release/evaluation_results/
- release/supplementary/
- release/metadata/

Computes SHA-256, SHA-512, and detailed `release_manifest.json` metadata.
"""

import datetime
import hashlib
import json
import os
import shutil
import sys
from typing import Any, Dict


def compute_file_hash(filepath: str, algorithm: str = "sha256") -> str:
    """Compute hex hash for a file using specified algorithm (sha256 or sha512)."""
    hasher = getattr(hashlib, algorithm)()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def copy_tree_if_exists(src: str, dst: str) -> int:
    """Recursively copy directory tree if source exists."""
    if not os.path.exists(src):
        return 0
    os.makedirs(dst, exist_ok=True)
    count = 0
    for root, _, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        target_dir = os.path.join(dst, rel_path) if rel_path != "." else dst
        os.makedirs(target_dir, exist_ok=True)
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            shutil.copy2(src_file, dst_file)
            count += 1
    return count


def build_release_package(project_root: str = ".") -> Dict[str, Any]:
    """Assemble complete publication release package into release/ directory."""
    release_dir = os.path.join(project_root, "release")
    os.makedirs(release_dir, exist_ok=True)

    subdirs = {
        "paper": os.path.join(release_dir, "paper"),
        "docs": os.path.join(release_dir, "docs"),
        "benchmark_results": os.path.join(release_dir, "benchmark_results"),
        "validation_results": os.path.join(release_dir, "validation_results"),
        "evaluation_results": os.path.join(release_dir, "evaluation_results"),
        "supplementary": os.path.join(release_dir, "supplementary"),
        "metadata": os.path.join(release_dir, "metadata"),
    }

    for path in subdirs.values():
        os.makedirs(path, exist_ok=True)

    # 1. Copy paper artifacts
    copy_tree_if_exists(os.path.join(project_root, "paper"), subdirs["paper"])

    # 2. Copy documentation artifacts
    copy_tree_if_exists(os.path.join(project_root, "docs"), subdirs["docs"])

    # 3. Copy benchmark & validation results
    copy_tree_if_exists(os.path.join(project_root, "results"), subdirs["benchmark_results"])
    copy_tree_if_exists(os.path.join(project_root, "validation_results"), subdirs["validation_results"])
    copy_tree_if_exists(os.path.join(project_root, "evaluation_results"), subdirs["evaluation_results"])

    # 4. Save metadata manifests
    repro_manifest_file = os.path.join(subdirs["metadata"], "reproducibility_manifest.json")
    if not os.path.exists(repro_manifest_file):
        repro_data = {
            "version": "1.0.0",
            "git_commit_hash": "HEAD",
            "python_version": sys.version.split()[0],
            "os_name": sys.platform,
            "prng_seed": 42,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        with open(repro_manifest_file, "w", encoding="utf-8") as f:
            json.dump(repro_data, f, indent=2)

    # Copy requirements.txt to metadata for environment lock reproducibility
    req_src = os.path.join(project_root, "requirements.txt")
    if os.path.exists(req_src):
        shutil.copy2(req_src, os.path.join(subdirs["metadata"], "requirements.txt"))

    # 5. Build granular file inventory & compute checksums
    manifest_entries = []
    sha256_lines = []
    sha512_lines = []

    for root, _, files in os.walk(release_dir):
        for file in files:
            if file in ("checksums_sha256.txt", "checksums_sha512.txt", "release_manifest.json"):
                continue

            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, release_dir)
            size = os.path.getsize(filepath)

            h256 = compute_file_hash(filepath, "sha256")
            h512 = compute_file_hash(filepath, "sha512")

            category = rel_path.split(os.sep)[0] if os.sep in rel_path else "root"

            manifest_entries.append({
                "relative_path": rel_path.replace(os.sep, "/"),
                "file_size_bytes": size,
                "sha256": h256,
                "sha512": h512,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "version": "1.0.0",
                "category": category,
            })

            sha256_lines.append(f"{h256}  {rel_path.replace(os.sep, '/')}")
            sha512_lines.append(f"{h512}  {rel_path.replace(os.sep, '/')}")

    # Write Checksum Files
    with open(os.path.join(release_dir, "checksums_sha256.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(sha256_lines)) + "\n")

    with open(os.path.join(release_dir, "checksums_sha512.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(sha512_lines)) + "\n")

    # Write Granular Release Manifest
    release_manifest = {
        "project_name": "KDR-CA-AEAD",
        "version": "1.0.0",
        "release_title": "IEEE Transactions Publication & Final Release Package",
        "build_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_files": len(manifest_entries),
        "artifacts": manifest_entries,
    }

    manifest_json_path = os.path.join(release_dir, "release_manifest.json")
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump(release_manifest, f, indent=2)

    return release_manifest


if __name__ == "__main__":
    manifest = build_release_package()
    print(f"Successfully assembled final release package with {manifest['total_files']} artifacts.")
