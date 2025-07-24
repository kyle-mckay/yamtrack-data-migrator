"""
Column mapping for hardcover adapter.
This module defines the column mapping for hardcover export files and provides a function to map the columns from the input file to the expected format.

## Summary of the column mapping:

| Target Column Name | Source Column Name | Required | Normalization Notes |
| --- | --- | --- | --- |
| source | N/A | Yes | Hardcoded value as "hardcover" for all entries |
| media_id | `Hardcover Book ID` | Yes | |
| media_type | `Media` | Yes | "Book" or "Audiobook" = "book", "Comic" = "comic" |
| title | N/A | No | Can auto-populate from source |
| image | N/A | No | Can auto-populate from source |
| season_number | N/A | Cond. | Not applicable for this source |
| episode_number | N/A | Cond. | Not applicable for this source |
| score | `Rating` | No | 5 star rating system, value is `Rating` * 2 |
| status | `Status` | Yes | `Read` = `Completed`, `Want to Read` = `Planning`, `Currently Reading` = `In progress` |
| notes | `Private Notes` | No | As is |
| start_date | `Date Started` | No | Convert from `yyyy-MM-dd` to Full ISO-8601 (`YYYY-MM-DD HH:MM:SS+HH:MM`) |
| end_date | `Date Finished` | No | Convert from `yyyy-MM-dd` to Full ISO-8601 (`YYYY-MM-DD HH:MM:SS+HH:MM`) |
| progress | `Pages` | No | As is |

Full Column List as of 2025-07-10: Title,Author,Series,Status,Privacy,Hardcover Book ID,Hardcover Edition ID,ISBN 10,ISBN 13,ASIN,Media,Country Code,Language Code,Binding,Pages,Duration in Seconds,Publish Date,Publisher,Genres,Moods,Tags,Content Warnings,Lists,Date Added,Date Started,Date Finished,Rating,Review,Review Contains Spoilers,Sponsored Review,Review Date,Review URL,Review Media URL,Private Notes,Owned,Compilation,Review Slate
"""

from clilog import log, VERBOSITY, VERBOSITY_ERROR, VERBOSITY_WARNING, VERBOSITY_INFO, VERBOSITY_DEBUG, VERBOSITY_TRACE
from .validate import validate_row, skip_invalid_row

def map_row(row, strategy="default", idx=None, total=None):
    """
    Map a single hardcover row dict to the target schema.
    Optionally logs the row index and total.
    """
    log(f"[hardcover.py.map_row] =========================", VERBOSITY_DEBUG)
    if idx is not None and total is not None:
        log(f"[hardcover.py.map_row] Mapping row {idx}/{total}", VERBOSITY_DEBUG)
    log(f"[hardcover.py.map_row] Row {idx}: {row}", VERBOSITY_TRACE)
    
    source="hardcover"
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

    try:
        match strategy:
            case "default":
                media_id=row.get("Hardcover Book ID")
                log(f"[hardcover.py.map_row] Media ID: {media_id}", VERBOSITY_TRACE)
                
                status=row.get("Status").lower()
                log(f"[hardcover.py.map_row] Hardcover status: {status}", VERBOSITY_TRACE)\
                
                match status:
                    case "read":
                        status = "Completed"
                        log (f"[hardcover.py.map_row] Status mapped to Completed", VERBOSITY_TRACE)
                    case "want to read":
                        status = "Planning"
                        log (f"[hardcover.py.map_row] Status mapped to In progress", VERBOSITY_TRACE)
                    case "currently reading":
                        status = "In progress"
                        log (f"[hardcover.py.map_row] Status mapped to Planning", VERBOSITY_TRACE)
                    case _:
                        log(f"[hardcover.py.map_row] Bookshelf status not a default bookshelf name: {status}.", VERBOSITY_WARNING)
                        status = "In progress"
                        log(f"[hardcover.py.map_row] Status defaulting to In progress", VERBOSITY_TRACE)
                
                media_type = row.get("Media", "").lower()
                if media_type in ("book", "audio", "ebook"):
                    media_type = "book"
                    log(f"[hardcover.py.map_row] Mapped media_type to 'book'", VERBOSITY_TRACE)
                    progress = row.get("Pages")
                elif media_type == "comic":
                    media_type = "comic"
                    log(f"[hardcover.py.map_row] Mapped media_type to 'comic'", VERBOSITY_TRACE)
                else:
                    log(f"[hardcover.py.map_row] Unable to map media_type, defaulting to 'book'", VERBOSITY_WARNING)
                


                log(f"[hardcover.py.map_row] Mapping score from Rating: {row.get('Rating')}", VERBOSITY_TRACE)
                try:
                    score = row.get("Rating")
                    if score:
                        score = float(score) * 2
                    else:
                        score = None
                except Exception:
                    log("[hardcover.py.map_row] Unable to calculate score, defaulting to None", VERBOSITY_WARNING)
                    score = None
                log(f"[hardcover.py.map_row] Mapped score: {score}", VERBOSITY_TRACE)

                log(f"[hardcover.py.map_row] Mapping start_date from Date Started: {row.get('Date Started')}", VERBOSITY_TRACE)
                start_date_raw = row.get("Date Started")
                start_date = f"{start_date_raw} 00:00:00+00:00" if start_date_raw else None
                log(f"[hardcover.py.map_row] Mapped start_date: {start_date}", VERBOSITY_TRACE)

                log(f"[hardcover.py.map_row] Mapping end_date from Date Finished: {row.get('Date Finished')}", VERBOSITY_TRACE)
                end_date_raw = row.get("Date Finished")
                end_date = f"{end_date_raw} 00:00:00+00:00" if end_date_raw else None
                log(f"[hardcover.py.map_row] Mapped end_date: {end_date}", VERBOSITY_TRACE)

                notes = row.get("Private Notes")
                
            case _:
                log(f"[hardcover.py.map_row] Unknown or unsupported strategy = {strategy}",VERBOSITY_ERROR)
                log(f"[hardcover.py.map_row] Mapping media_type from Media: {media_type}", VERBOSITY_TRACE)
                return []

    except Exception:
        log(f"[hardcover.py.map_row] Error mapping row with strategy '{strategy}' in row {idx}. Writing as is.", VERBOSITY_ERROR)

    try:
        # Build mapped row
        mapped = {
            "source": "hardcover",
            "media_id": media_id,
            "media_type": media_type,
            "title": None,
            "image": None,
            "season_number": None,
            "episode_number": None,
            "score": score,
            "status": status,
            "notes": notes,
            "start_date": start_date,
            "end_date": end_date,
            "progress": progress,
        }
        
        valid = validate_row(mapped)
        if valid:
            log(f"[hardcover.py.map_row] Mapped row: {mapped}", VERBOSITY_DEBUG)
        else:
            log(f"[hardcover.py.map_row] Row {idx}: {mapped}", VERBOSITY_WARNING)
            if skip_invalid_row:
                log(f"skip_invalid_row is true, will not export row {idx}", VERBOSITY_INFO)
                return []
        return mapped
    except Exception:
        log(f"[hardcover.py.map_row] Failed to build mapped row for row {idx}", VERBOSITY_ERROR)
        return []

def process_rows(rows,strategy="default"):
    """
    Process a list of dictionaries representing rows from the hardcover CSV.
    Returns a list of mapped rows.
    """
    try:
        log(f"[hardcover.py.process_rows] ==============================================", VERBOSITY_DEBUG)
        log(f"[hardcover.py.process_rows] Processing {len(rows)} rows from hardcover", VERBOSITY_DEBUG)
        if rows:
            total = len(rows)
            mapped_rows = []
            for idx, row in enumerate(rows):
                mapped = map_row(row, strategy, idx + 1, total)
                # Skip if mapped is None or empty list
                if mapped is None or mapped == []:
                    log(f"[hardcover.py.process_rows] Detected empty row in {idx + 1}", VERBOSITY_DEBUG)
                    continue
                mapped_rows.append(mapped)
            log(f"[hardcover.py.process_rows] =========================", VERBOSITY_DEBUG)
            log("[hardcover.py.process_rows] Mapped all rows", VERBOSITY_DEBUG)
            return mapped_rows
    except Exception:
        log(f"[hardcover.py.process_rows] Critical error processing rows", VERBOSITY_ERROR)
    return []