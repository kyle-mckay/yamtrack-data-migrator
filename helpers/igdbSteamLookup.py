# igdb_lookup.py
# -------------------------------------------------------------
# Fetch IGDB game IDs for each Steam App ID found in a Steam CSV
# -------------------------------------------------------------
# 1. Read rows produced by steam_library.export_steam_library_to_csv
# 2. Obtain a Twitch bearer token (client‑credentials flow)
# 3. Query /external_games (category 1 = Steam) → IGDB game ID
# 4. Append a new column “igdb_id” to every row
# 5. Respect the rate limit (default 250 ms between calls)
# 6. Write the enriched rows to ../outputs/steamIgdbLookup.csv
# 7. Return the updated row list to the caller
# -------------------------------------------------------------

import os
import csv
import time
import requests
from typing import Optional, Dict, List
from pathlib import Path
from dotenv import load_dotenv

from clilog import log, VERBOSITY_INFO, VERBOSITY_DEBUG, VERBOSITY_TRACE, VERBOSITY_ERROR, VERBOSITY_WARNING

# ───────────────────────────────────────────
# ENV / CONFIG
# ───────────────────────────────────────────
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

twitch_client_id: str = os.getenv("twitch_client_id")
twitch_client_secret: str = os.getenv("twitch_client_secret")
igbd_rate_frequency_ms: int = int(os.getenv("igbd_rate_frequency_ms", "250"))

log(f"[igdb_lookup] twitch_client_id = {twitch_client_id}", VERBOSITY_TRACE)
log(f"[igdb_lookup] igbd_rate_frequency_ms = {igbd_rate_frequency_ms}", VERBOSITY_TRACE)

IGDB_BASE = "https://api.igdb.com/v4"

# ───────────────────────────────────────────
# AUTH & API HELPERS
# ───────────────────────────────────────────
def get_bearer_token(client_id: str, client_secret: str) -> str:
    resp = requests.post(
        "https://id.twitch.tv/oauth2/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        timeout=10,
    )
    if resp.status_code != 200:
        log(f"igdbSteamLookup.py.get_bearer_token: Auth failed: {resp.status_code} - {resp.text}", VERBOSITY_ERROR)
        raise RuntimeError(f"Auth failed: {resp.status_code} - {resp.text}")
    return resp.json()["access_token"]

def igdb_headers(token: str, client_id: str) -> Dict[str, str]:
    return {
        "Client-ID": client_id,
        "Authorization": f"Bearer {token}",
    }

def steam_to_igdb_id(steam_appid: str | int, headers: Dict[str, str]) -> Optional[int]:
    query = f'fields game; where category = 1 & uid = "{steam_appid}";'
    resp = requests.post(f"{IGDB_BASE}/external_games", headers=headers, data=query, timeout=10)
    if resp.status_code == 429:
        # Too many requests – wait and retry once
        log(f"igdbSteamLookup.py.steam_to_igdb_id: API Response = 429, sleeping and continuing...",VERBOSITY_WARNING)
        time.sleep(1)
        resp = requests.post(f"{IGDB_BASE}/external_games", headers=headers, data=query, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data[0]["game"] if data else None

# ───────────────────────────────────────────
# MAIN BATCH PROCESSOR
# ───────────────────────────────────────────
#TODO: OLD def process_and_export_steam_rows(input_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
def process_and_export_steam_rows(input_rows: List[Dict[str, str]]):
    """
    Enrich each row from a Steam export with its IGDB game ID.
    Writes the result to ../output/steamIgdbLookup.csv and returns the new rows.
    """
    token = get_bearer_token(twitch_client_id, twitch_client_secret)
    headers = igdb_headers(token, twitch_client_id)

    total = len(input_rows)

    log(f"Looking up {total} steam ID's", VERBOSITY_INFO)

    enriched: List[Dict[str, str]] = []
    for idx, row in enumerate(input_rows, start=1):
        appid = row.get("appid")
        igdb_id = steam_to_igdb_id(appid, headers)
        log(f"igdbSteamLookup.py.process_and_export_steam_rows: {idx}/{total} SteamID {appid} is igdbID {igdb_id}", VERBOSITY_DEBUG)
        #TODO: Add error log if id is empty and skip row
        row["igdb_id"] = str(igdb_id) if igdb_id is not None else ""
        enriched.append(row)

        time.sleep(igbd_rate_frequency_ms / 1000)

    # Output
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "steamIgdbLookup.csv"

    with output_path.open("w", newline="", encoding="utf-8") as fh:
        fieldnames = list(enriched[0].keys())
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched)

    log(f"igdbSteamLookup.py.process_and_export_steam_rows: Wrote {len(enriched)} rows to {output_path}", VERBOSITY_INFO)
    return str(output_path.resolve())

# ───────────────────────────────────────────
# OPTIONAL STAND‑ALONE EXECUTION
# ───────────────────────────────────────────
if __name__ == "__main__":
    # Quick demo: load the steam-export CSV and enrich it
    demo_input = Path(__file__).parent.parent / "output" / "steam-export.csv"
    if not demo_input.exists():
        raise FileNotFoundError("Run steam_library.py first to produce steam-export.csv")

    with demo_input.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    process_and_export_steam_rows(rows)
