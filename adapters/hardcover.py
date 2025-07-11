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

def map_row(row, idx=None, total=None):
    """
    Map a single hardcover row dict to the target schema.
    Optionally logs the row index and total.
    """
    log(f"=========================", VERBOSITY_DEBUG)
    if idx is not None and total is not None:
        log(f"Mapping row {idx}/{total}", VERBOSITY_DEBUG)

    # Map media_type
    media_type = row.get("Media", "").lower()
    log(f"Mapping media_type from Media: {media_type}", VERBOSITY_TRACE)
    if media_type in ("book", "audio", "ebook"):
        mapped_media_type = "book"
        log(f"Mapped media_type to 'book'", VERBOSITY_TRACE)
    elif media_type == "comic":
        mapped_media_type = "comic"
        log(f"Mapped media_type to 'comic'", VERBOSITY_TRACE)
    else:
        mapped_media_type = media_type or None
        log(f"mapped_media_type to None or original value: {mapped_media_type}", VERBOSITY_WARNING)

    # Map status
    log(f"Mapping status from Status: {row.get('Status', '')}", VERBOSITY_TRACE)
    status_map = {
        "Read": "Completed",
        "Want to Read": "Planning",
        "Currently Reading": "In progress"
    }
    mapped_status = status_map.get(row.get("Status", ""), row.get("Status", ""))
    log(f"Mapped status: {mapped_status}", VERBOSITY_TRACE)

    # Map score
    log(f"Mapping score from Rating: {row.get('Rating', 0)}", VERBOSITY_TRACE)
    try:
        score = float(row.get("Rating", 0)) * 2
    except Exception:
        score = None
    log(f"Mapped score: {score}", VERBOSITY_TRACE)

    # Map dates 
    log(f"Mapping start_date from Date Started: {row.get('Date Started')}", VERBOSITY_TRACE)
    start_date_raw = row.get("Date Started")
    start_date = f"{start_date_raw} 00:00:00+00:00" if start_date_raw else None
    log(f"Mapped start_date: {start_date}", VERBOSITY_TRACE)

    log(f"Mapping end_date from Date Finished: {row.get('Date Finished')}", VERBOSITY_TRACE)
    end_date_raw = row.get("Date Finished")
    end_date = f"{end_date_raw} 00:00:00+00:00" if end_date_raw else None
    log(f"Mapped end_date: {end_date}", VERBOSITY_TRACE)

    # Build mapped row
    mapped = {
        "source": "hardcover",
        "media_id": row.get("Hardcover Book ID"),
        "media_type": mapped_media_type,
        "title": None,
        "image": None,
        "season_number": None,
        "episode_number": None,
        "score": score,
        "status": mapped_status,
        "notes": row.get("Private Notes"),
        "start_date": start_date,
        "end_date": end_date,
        "progress": row.get("Pages"),
    }
    log(f"Mapped row: {mapped}", VERBOSITY_DEBUG)
    return mapped

def process_rows(rows):
    """
    Process a list of dictionaries representing rows from the hardcover CSV.
    Returns a list of mapped rows.
    """
    log(f"==============================================", VERBOSITY_DEBUG)
    log(f"Processing {len(rows)} rows from hardcover", VERBOSITY_DEBUG)
    if rows:
        total = len(rows)
        mapped_rows = [map_row(row, idx+1, total) for idx, row in enumerate(rows)]
        log(f"Mapped all rows", VERBOSITY_DEBUG)
        return mapped_rows
    return []