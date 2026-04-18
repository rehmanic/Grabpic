#!/usr/bin/env python3
"""
Download the LFW Kaggle mirror used for Grabpic (same as:

    import kagglehub
    path = kagglehub.dataset_download("jessicali9530/lfw-dataset")

Requires Kaggle API credentials (see README).
Run from the Grabpic repository root.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.datasets_lfw import DEFAULT_LFW_KAGGLE_SLUG, fetch_lfw_kaggle_path  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Download LFW via Kaggle Hub for Grabpic.")
    parser.add_argument(
        "--dataset",
        default=DEFAULT_LFW_KAGGLE_SLUG,
        help=f'Kaggle dataset slug (default: "{DEFAULT_LFW_KAGGLE_SLUG}")',
    )
    parser.add_argument(
        "--symlink-into",
        type=Path,
        default=None,
        help=(
            "Optional: create this path as a symlink to the downloaded folder. "
            "Use a path under STORAGE_ROOT (e.g. ./data/storage/lfw) so POST /v1/ingest/scan can reach it."
        ),
    )
    args = parser.parse_args()

    path = fetch_lfw_kaggle_path(args.dataset)
    print("Path to dataset files:", path)

    if args.symlink_into is not None:
        dest = args.symlink_into.expanduser().resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() or dest.is_symlink():
            print(f"Refusing to overwrite existing path: {dest}", file=sys.stderr)
            sys.exit(2)
        dest.symlink_to(Path(path).resolve(), target_is_directory=True)
        print("Symlink created:", dest)


if __name__ == "__main__":
    main()
