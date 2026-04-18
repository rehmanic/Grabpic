"""Kaggle Hub integration for the LFW dataset mirror used in Grabpic demos."""

from __future__ import annotations

import kagglehub

from app.config import get_settings

# Kept in sync with Settings.kaggle_lfw_dataset_slug default for scripts and docs.
DEFAULT_LFW_KAGGLE_SLUG = "jessicali9530/lfw-dataset"


def default_lfw_slug() -> str:
    """Returns the default LFW dataset slug configured in the application settings."""
    return get_settings().kaggle_lfw_dataset_slug


def fetch_lfw_kaggle_path(dataset_slug: str | None = None) -> str:
    """Download the dataset (or return the local cache path) via kagglehub."""
    slug = dataset_slug or default_lfw_slug()
    return kagglehub.dataset_download(slug)
