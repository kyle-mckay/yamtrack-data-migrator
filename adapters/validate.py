"""
Assesses a mapped row against the YamTrack schema rules.

Reference: https://github.com/FuzzyGrim/Yamtrack/wiki/Yamtrack-CSV-Format
"""

from datetime import datetime
from typing import Any, Dict, Tuple
import os
from dotenv import load_dotenv
from pathlib import Path

from clilog import log, VERBOSITY, VERBOSITY_WARNING, VERBOSITY_WARNING, VERBOSITY_INFO, VERBOSITY_DEBUG, VERBOSITY_TRACE, VERBOSITY_ERROR

# Variable defenitions
ENV_PATH = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=ENV_PATH)

skip_invalid_row = os.getenv("skip_invalid_row", "False").lower() in ("true", "1", "yes")

# === YamTrack static rule sets =================================================

ALLOWED_SOURCES = {
    "tmdb", "mal", "mangaupdates", "igdb", "openlibrary", "hardcover",
    "comicvine", "manual",
}

ALLOWED_MEDIA_TYPES = {
    "tv", "season", "episode", "movie", "anime", "manga", "game", "book", "comic",
}

ALLOWED_STATUSES = {
    "Completed", "In progress", "Planning", "Paused", "Dropped",
}

# Main validation function

def validate_row(mapped: Dict[str, Any]) -> Tuple[bool, str]:  # noqa: C901 (complexity)
    """
    Validate a YamTrack row mapping.

    Returns bool  - True when valid, False otherwise
    """
    try:
        log(f"[validate.py.validate_row] Validating row: {mapped}", VERBOSITY_TRACE)
        # --- Required fields (always) ----------------------------------------------

        ## media_id
        column_name="media_id"
        if not _present(mapped, "media_id"):
            log("[validate.py.validate_row] Validation failed: media_id is required and cannot be blank", VERBOSITY_WARNING)
            return False
        else:
            log(f"[validate.py.validate_row] media_id: {mapped['media_id']}", VERBOSITY_TRACE)

        ## source
        column_name="source"
        if not _present(mapped, "source"):
            log("[validate.py.validate_row] Validation failed: source is required and cannot be blank", VERBOSITY_WARNING)
            return False
        else:
            log(f"[validate.py.validate_row] source: {mapped['source']}", VERBOSITY_TRACE)
            if mapped["source"] not in ALLOWED_SOURCES:
                log(f"[validate.py.validate_row] Validation failed: source '{mapped['source']}' is not allowed. Allowed values: {ALLOWED_SOURCES}", VERBOSITY_WARNING)
                return False

        ## media_type
        column_name="media_type"
        if not _present(mapped, "media_type"):
            log("[validate.py.validate_row] Validation failed: media_type is required", VERBOSITY_WARNING)
            return False
        else:
            mt = mapped["media_type"]
            log(f"[validate.py.validate_row] media_type: {mt}", VERBOSITY_TRACE)
            if mt not in ALLOWED_MEDIA_TYPES:
                log(f"[validate.py.validate_row] Validation failed: media_type '{mt}' is not allowed. Allowed values: {ALLOWED_MEDIA_TYPES}", VERBOSITY_WARNING)
                return False
            
            ## season_number:
            column_name="season_number"
            if _present(mapped, "season_number"):
                log(f"[validate.py.validate_row] season_number: {mapped["season_number"]}", VERBOSITY_TRACE)

            ## episode_number
            column_name="episode_number"
            if _present(mapped, "episode_number"):
                log(f"[validate.py.validate_row] episode_number: {mapped["episode_number"]}", VERBOSITY_TRACE)    
            
            column_name="season"
            if mt == "season" and not _present(mapped, "season_number"):
                log("[validate.py.validate_row] Validation failed: season_number is required when media_type = season", VERBOSITY_WARNING)
                return False

            column_name="episode"
            if mt == "episode" and not _present(mapped, "season_number") and not _present(mapped, "episode_number"):
                log("[validate.py.validate_row] Validation failed: season_number and episode_number are required when media_type = episode", VERBOSITY_WARNING)
                return False

        ## status
        column_name="status"
        if not _present(mapped, "status"):
            log("[validate.py.validate_row] Validation failed: status is required", VERBOSITY_WARNING)
            return False
        else:
            log(f"[validate.py.validate_row] status: {mapped['status']}", VERBOSITY_TRACE)
            if mapped["status"] not in ALLOWED_STATUSES:
                log(f"[validate.py.validate_row] Validation failed: status '{mapped['status']}' is not allowed. Allowed values: {ALLOWED_STATUSES}", VERBOSITY_WARNING)
                return False

        # --- Optional numeric and date fields --------------------------------------
        ## title
        column_name="title"
        if _present(mapped, "title"):
            log(f"[validate.py.validate_row] title: {mapped['title']}", VERBOSITY_TRACE)

        ## score
        column_name="score"
        if _present(mapped, "score"):
            log(f"[validate.py.validate_row] score: {mapped['score']}", VERBOSITY_TRACE)
            if not mapped["score"] is None:
                if not _is_decimal(mapped["score"]):
                    log("[validate.py.validate_row] Validation failed: score must be a decimal 0-10", VERBOSITY_WARNING)
                    return False
        
        ## progress
        column_name="progress"
        if _present(mapped, "progress"):
            log(f"[validate.py.validate_row] progress: {mapped['progress']}", VERBOSITY_TRACE)
            if not mapped["progress"] is None and not _is_int(mapped["progress"]):
                log("[validate.py.validate_row] Validation failed: progress must be an integer", VERBOSITY_WARNING)
                return False
            
        ## start_date and end_date
        for date_field in ("start_date", "end_date"):
            column_name="date_field"
            if _present(mapped, date_field):
                log(f"[validate.py.validate_row] {date_field}: {mapped[date_field]}", VERBOSITY_TRACE)
                if mapped[date_field] is not None and not _is_iso_ts(mapped[date_field]):
                    log(f"[validate.py.validate_row] Validation failed: {date_field} must be an ISO-8601 timestamp with timezone", VERBOSITY_WARNING)
                    return False, f"{date_field} must be an ISO-8601 timestamp with timezone"
        
            
        ## image
        column_name="image"
        if _present(mapped, "image"):
            log(f"[validate.py.validate_row] image: {mapped['image']}", VERBOSITY_TRACE)
        
            
        ## notes
        column_name="notes"
        if _present(mapped, "notes"):
            log(f"[validate.py.validate_row] notes: {mapped['notes']}", VERBOSITY_TRACE)

        # All rules satisfied
        log("[validate.py.validate_row] Validation succeeded: row is valid", VERBOSITY_DEBUG)
        return True
    except Exception:
        log(f"[validate.py.validate_row] Failed to validate the column '{column_name}'", VERBOSITY_ERROR)


# Helpers

def _present(d: Dict[str, Any], key: str) -> bool:
    """Key exists and is not an empty string."""
    return key in d and str(d[key]).strip() != ""


def _is_decimal(value: Any) -> bool:
    """Decimal between 0 and 10 inclusive."""
    try:
        f = float(value)
    except (ValueError, TypeError):
        return False
    return 0.0 <= f <= 10.0


def _is_int(value: Any) -> bool:
    """Integer check for progress."""
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def _is_iso_ts(value: str) -> bool:
    """Validate ISO-8601 timestamp with timezone (YYYY-MM-DD HH:MM:SS±HH:MM)."""
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M:%S%z")
        return True
    except (ValueError, TypeError):
        return False

# Smoke Test

if __name__ == "__main__":
    """
    Call with `python -m adapters.validate` to run a smoke test.
    """
    try:
        example = {
            "media_id": "12345",
            "source": "tmdb",
            "media_type": "movie",
            "status": "Completed",
            "score": "8.7",
            "start_date": "2023-01-16 03:56:13+00:00",
            "end_date": None,
        }
        result = validate_row(example)
        log(f"Smoke test result: {result}", VERBOSITY_INFO)  # (True, 'OK')
    except Exception:
        log(f"[validate.py.__main__] Critical error running smoke test", VERBOSITY_ERROR)
