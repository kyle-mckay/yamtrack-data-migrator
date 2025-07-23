"""
Column mapping for igdb adapter.
This module defines the column mapping for igdb export files and provides a function to map the columns from the input file to the expected format.

## Strategies

### steam_api

Uses the `steamExportLibrary.py` to fetch owned games from Steam and enrich them with IGDB IDs.

| Target Column Name | Source Column Name | Required | Normalization Notes |
| --- | --- | --- | --- |
| source | Cond. | Yes | Hardcoded value as "igdb" for all entries |
| media_id | `igdb_id` | Yes | As is |
| media_type | Cond. | Yes | Hardcoded value as "game" for all entries |
| title | `name` | Cond. | Can auto-populate from source |
| image | N/A | No | Can auto-populate from source |
| season_number | N/A | Cond. | Not applicable for this source |
| episode_number | N/A | Cond. | Not applicable for this source |
| score | N/A | No | Not supported by list csv export |
| status | Cond. | Yes | Default to `Planning`|
| notes | N/A | No | As is |
| start_date | N/A | No | |
| end_date | N/A | No | |
| progress | N/A | No | |

Full Column List as of 2025-07-10: appid, name, playtime_forever, playtime_windows_forever, playtime_mac_forever, playtime_linux_forever, rtime_last_played, playtime_2weeks, has_community_visible_stats, img_icon_url, img_logo_url, igdb_id

### igdb

Uses the `Download CSV` feature on igdb lists

| Target Column Name | Source Column Name | Required | Normalization Notes |
| --- | --- | --- | --- |
| source | Cond. | Yes | Hardcoded value as "igdb" for all entries |
| media_id | `id` | Yes | |
| media_type | Cond. | Yes | Hardcoded value as "game" for all entries |
| title | N/A | No | Can auto-populate from source |
| image | N/A | No | Can auto-populate from source |
| season_number | N/A | Cond. | Not applicable for this source |
| episode_number | N/A | Cond. | Not applicable for this source |
| score | N/A | No | Not supported by list csv export |
| status | Cond. | Yes | Strategy is passed by cli.py to determine dynamically|
| notes | N/A | No | As is |
| start_date | N/A | No | |
| end_date | N/A | No | |
| progress | N/A | No | |

Full Column List as of 2025-07-10: id, game, url, rating, category, release_date, platforms, genres, themes, companies, description

"""

from clilog import log, VERBOSITY, VERBOSITY_ERROR, VERBOSITY_WARNING, VERBOSITY_INFO, VERBOSITY_DEBUG, VERBOSITY_TRACE
from .validate import validate_row

def map_row(row, strategy=None, idx=None, total=None):
    """
    Map a single igdb row dict to the target schema.
    Optionally logs the row index and total.
    """
    log(f"[igdb.py.map_row] =========================", VERBOSITY_DEBUG)
    if idx is not None and total is not None:
        log(f"[igdb.py.map_row] Mapping row {idx}/{total}", VERBOSITY_DEBUG)

    source="igdb"
    media_id=None
    media_type="game"
    title=None
    image=None
    season_number=None
    episode_number=None
    score=None # igdb rating columns are global game ratings, not user ratings
    status="Planning"
    notes=None
    start_date=None
    end_date=None
    progress=None

    try:
        match strategy:
            case "steam_api":
                # File created with `cli.py --source igdb --input steam`
                media_id=row.get("igdb_id")
                title=row.get("name")
            case "list-played":
                # Stretegy set if `--strategy` is none and input file was `played.csv`
                media_id=row.get("id")
                status="Completed"
            case "list-playing":
                # Strategy set if `--strategy` is none and input file was `playing.csv`
                media_id=row.get("id")
                status="In progress"
            case "list-want":
                # Strategy set if `--strategy` is none and input file was `want-to-play.csv`
                media_id=row.get("id")
                status="Planning"
            case "igdb":
                # Default if `--source` is `igdb`
                media_id=row.get("id")
                title=row.get("game")
            case _:
                log(f"[igdb.py.map_row] Unknown strategy = {strategy}",VERBOSITY_ERROR)
                return "Unknown Souce"
    except Exception:
        log(f"[igdb.py.map_row] Error mapping row with strategy '{strategy}' in row {idx}. Writing as is.", VERBOSITY_ERROR)

    try:
        # Build mapped row
        mapped = {
            "source": source,
            "media_id": media_id,
            "media_type": media_type,
            "title": title,
            "image": image,
            "season_number": season_number,
            "episode_number": episode_number,
            "score": score,
            "status": status,
            "notes": notes,
            "start_date": start_date,
            "end_date": end_date,
            "progress": progress,
        }

        valid = validate_row(mapped)
        if valid:
            log(f"[igdb.py.map_row] Mapped row: {mapped}", VERBOSITY_DEBUG)
        return mapped
    except Exception:
        log(f"[igdb.py.map_row] Failed to build mapped row for row {idx}", VERBOSITY_ERROR)
        return []
    

def process_rows(rows,strategy=None):
    """
    Process a list of dictionaries representing rows from the file.
    Returns a list of mapped rows.
    """
    try:
        log("[igdb.py.process_rows] ==============================================", VERBOSITY_DEBUG)
        log(f"[igdb.py.process_rows] Processing {len(rows)} rows from igdb", VERBOSITY_DEBUG)
        log(f"[igdb.py.process_rows] Strategy being used = {strategy}", VERBOSITY_DEBUG)
        if rows:
            total = len(rows)
            mapped_rows = [map_row(row, strategy, idx+1, total) for idx, row in enumerate(rows)]
            log(f"[igdb.py.process_rows] =========================", VERBOSITY_DEBUG)
            log("[igdb.py.process_rows] Mapped all rows", VERBOSITY_DEBUG)
            return mapped_rows
    except Exception:
        log(f"[igdb.py.process_rows] Critical error processing rows", VERBOSITY_ERROR)
    return []