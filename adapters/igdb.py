"""
Column mapping for igdb adapter.
This module defines the column mapping for igdb export files and provides a function to map the columns from the input file to the expected format.

## Summary of the column mapping:

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
| status | Cond. | Yes | Default to `Planning`, can parse filename for auto lists if filename starts with `Played` = `Completed`, `Want` = `Planning`, `playing` = `In progress` |
| notes | N/A | No | As is |
| start_date | N/A | No | |
| end_date | N/A | No | |
| progress | N/A | No | |

Full Column List as of 2025-07-10: id, game, url, rating, category, release_date, platforms, genres, themes, companies, description

"""

from helpers import log, VERBOSITY, VERBOSITY_ERROR, VERBOSITY_WARNING, VERBOSITY_INFO, VERBOSITY_DEBUG, VERBOSITY_TRACE

