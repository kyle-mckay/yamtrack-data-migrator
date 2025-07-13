"""
Column mapping for openlibrary adapter.
This module defines the column mapping for openlibrary export files and provides a function to map the columns from the input file to the expected format.

## Strategies

### openlibrary (reading log)

Uses the download button in the export page (https://openlibrary.org/account/import)

| Target Column Name | Source Column Name | Required | Normalization Notes |
| --- | --- | --- | --- |
|media_id | Edition ID | Yes | |
| source | Cond. | Yes| Hardcoded as `openlibrary|
|media_type| Cond. | Yes | Hardcoded as book |
|title | N/A | No | Can be skipped as it will pull from source |
|image | N/A | No |  Can be skipped as it will pull from source |
|season_number | N/A | No |  |
|episode_number | N/A | No |  |
|score | My Ratings | No |  Base 5 ratings, so multiply by 2
|status | Bookshelf | No |  Has auto lists that can be converted: `Already Read` = Completed, `Currently Reading` = In progress, `Want to Read` = Planning. Could also build in logic to assume status based on users own custom list name such as `Dropped`.
|notes | N/A | No |  No field in export |
|start_date | N/A | No |  No field in export |
|end_date | N/A | No |  No field in export |
|progress | N/A | No |  No field in export |

Full Column List as of 2025-07-13: Work ID, Title, Authors, First Publish Year, Edition ID, Edition Count, Bookshelf, My Ratings, Ratings Average, Ratings Count, Has Ebook, Subjects, Subject People, Subject Places, Subject Times

"""

from clilog import log, VERBOSITY, VERBOSITY_ERROR, VERBOSITY_WARNING, VERBOSITY_INFO, VERBOSITY_DEBUG, VERBOSITY_TRACE
from .validate import validate_row

def map_row(row, strategy=None, idx=None, total=None):
    """
    Map a single openlibrary row dict to the target schema.
    Optionally logs the row index and total.
    """
    log(f"[openlibrary.py.map_row] =========================", VERBOSITY_DEBUG)
    if idx is not None and total is not None:
        log(f"[openlibrary.py.map_row] Mapping row {idx}/{total}", VERBOSITY_DEBUG)

    source="openlibrary"
    media_id=None
    media_type="book"
    title=None
    image=None
    season_number=None
    episode_number=None
    score=None
    status="Planning"
    notes=None
    start_date=None
    end_date=None
    progress=None

    match strategy:
        case "openlibrary-reading-log":
            # Stretegy set if `--strategy` is none and input file was `OpenLibrary_ReadingLog.csv`
            media_id=row.get("Edition ID")
            log(f"[openlibrary.py.map_row] Media ID: {media_id}", VERBOSITY_TRACE)
            
            status= row.get("Bookshelf").lower()
            log(f"[openlibrary.py.map_row] Bookshelf status: {status}", VERBOSITY_TRACE)

            match status:
                case "already read":
                    status = "Completed"
                    log (f"[openlibrary.py.map_row] Status mapped to Completed", VERBOSITY_TRACE)
                case "currently reading":
                    status = "In progress"
                    log (f"[openlibrary.py.map_row] Status mapped to In progress", VERBOSITY_TRACE)
                case "want to read":
                    status = "Planning"
                    log (f"[openlibrary.py.map_row] Status mapped to Planning", VERBOSITY_TRACE)
                case _:
                    log(f"[openlibrary.py.map_row] Bookshelf status not a default bookshelf name: {status}.", VERBOSITY_WARNING)
                    if status == "dropped" or status == "did Not Finish" or status == "abandoned":
                        status = "Dropped"
                        log(f"[openlibrary.py.map_row] Status mapped to Dropped", VERBOSITY_TRACE)
                    elif status == "paused" or status == "on hold":
                        status = "Paused"
                        log(f"[openlibrary.py.map_row] Status mapped to Paused", VERBOSITY_TRACE)
                    else:
                        status = "In progress"
                        log(f"[openlibrary.py.map_row] Status mapped to In progress", VERBOSITY_TRACE)
            
            if row.get("My Ratings") is not None and row.get("My Ratings").isdigit():
                log(f"[openlibrary.py.map_row] My Ratings: {row.get('My Ratings')}", VERBOSITY_TRACE)
                score = int(row.get("My Ratings")) * 2
            else:
                log("[openlibrary.py.map_row] No My Ratings found, score will be None", VERBOSITY_TRACE)
                score = None
        case _:
            log(f"[openlibrary.py.map_row] Unknown strategy = {strategy}",VERBOSITY_ERROR)
            return "Unknown Souce"

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
        log(f"[openlibrary.py.map_row] Mapped row: {mapped}", VERBOSITY_DEBUG)
    return mapped
    

def process_rows(rows,strategy=None):
    """
    Process a list of dictionaries representing rows from the file.
    Returns a list of mapped rows.
    """
    log("[openlibrary.py.process_rows] ==============================================", VERBOSITY_DEBUG)
    log(f"[openlibrary.py.process_rows] Processing {len(rows)} rows from openlibrary", VERBOSITY_DEBUG)
    log(f"[openlibrary.py.process_rows] Strategy being used = {strategy}", VERBOSITY_DEBUG)
    if rows:
        total = len(rows)
        mapped_rows = [map_row(row, strategy, idx+1, total) for idx, row in enumerate(rows)]
        log(f"[openlibrary.py.process_rows] =========================", VERBOSITY_DEBUG)
        log("[openlibrary.py.process_rows] Mapped all rows", VERBOSITY_DEBUG)
        return mapped_rows
    return []