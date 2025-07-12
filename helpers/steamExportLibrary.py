"""
Fetch owned games from Steam using the Steam Web API and export them to a CSV file.
Requirements:
- .env file with `steam_secret` and `steam_id64`
- The script will create a CSV file named `steam-export.csv` in the specified output directory
"""

import os
import csv
import requests
from dotenv import load_dotenv
from pathlib import Path

from clilog import log, VERBOSITY, VERBOSITY_ERROR, VERBOSITY_WARNING, VERBOSITY_INFO, VERBOSITY_DEBUG, VERBOSITY_TRACE

# ───────────────────────────────────────────
# MAIN BATCH PROCESSOR
# ───────────────────────────────────────────

def get_owned_games(steam_secret: str, steam_id64: str):
    log(f"steamExportLibrary.py.get_owned_games: API key = {steam_secret}", VERBOSITY_TRACE)
    log(f"steamExportLibrary.py.get_owned_games: Steam ID64 = {steam_id64}", VERBOSITY_TRACE)
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": steam_secret,
        "steamid": steam_id64,
        "include_appinfo": True,
        "include_played_free_games": True
    }
    response = requests.get(url, params=params, timeout=10)
    log(f"steamExportLibrary.py.get_owned_games: response = {response}", VERBOSITY_TRACE)
    response.raise_for_status()
    data = response.json()
    return data.get("response", {}).get("games", [])

def export_steam_library_to_csv(output_dir: Path = None) -> Path:
    steam_secret = os.getenv("steam_secret")
    log(f"steamExportLibrary.py: steam_secret read as {steam_secret}", VERBOSITY_TRACE)
    steam_id64 = os.getenv("steam_id64")
    log(f"steamExportLibrary.py: steam_id64 read as {steam_id64}", VERBOSITY_TRACE)

    if not steam_secret and not steam_id64:
        log("steamExportLibrary.py.export_steam_library_to_csv: Both steam_secret and steam_id64 must be provided in .env", VERBOSITY_ERROR)
        return None
    
    games = get_owned_games(steam_secret, steam_id64)
    if not games:
        log("steamExportLibrary.py.export_steam_library_to_csv: No games found or profile is private.",VERBOSITY_WARNING)

    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'output'
    log(f"steamExportLibrary.py.get_owned_games: output_dir = {output_dir}",VERBOSITY_TRACE)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'steam-export.csv'
    log(f"steamExportLibrary.py.get_owned_games: output_file = {output_file}",VERBOSITY_TRACE)

    fieldnames = [
        'appid', 'name', 'playtime_forever', 'playtime_windows_forever',
        'playtime_mac_forever', 'playtime_linux_forever', 'rtime_last_played',
        'playtime_2weeks', 'has_community_visible_stats', 'img_icon_url', 'img_logo_url'
    ]

    with output_file.open('w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for game in games:
            #TODO: Add trace output
            writer.writerow({
                'appid': game.get('appid', ''),
                'name': game.get('name', ''),
                'playtime_forever': game.get('playtime_forever', 0),
                'playtime_windows_forever': game.get('playtime_windows_forever', 0),
                'playtime_mac_forever': game.get('playtime_mac_forever', 0),
                'playtime_linux_forever': game.get('playtime_linux_forever', 0),
                'rtime_last_played': game.get('rtime_last_played', 0),
                'playtime_2weeks': game.get('playtime_2weeks', 0),
                'has_community_visible_stats': game.get('has_community_visible_stats', False),
                'img_icon_url': game.get('img_icon_url', ''),
                'img_logo_url': game.get('img_logo_url', ''),
            })

    return str(output_file.resolve())

# ───────────────────────────────────────────
# OPTIONAL STAND‑ALONE EXECUTION
# ───────────────────────────────────────────

if __name__ == "__main__":
    """
    Runs this script as a standalone utility to export the Steam library.
    """
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    path = export_steam_library_to_csv()
    print(f"Steam library exported to: {path}")
