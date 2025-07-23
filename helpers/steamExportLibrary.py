"""
Fetch owned games from Steam using the Steam Web API and export them to a CSV file.
Supports two modes:
1. owned — Export full library to CSV
2. lookup — Return a single game's data by appid or title (public Steam Store search)

Requirements:
- .env file with `steam_secret` and `steam_id64`
- The script will create a CSV file named `steam-export.csv` in the specified output directory (for owned)
"""

import os
import csv
import argparse
import requests
from dotenv import load_dotenv
from pathlib import Path

from clilog import log, VERBOSITY, VERBOSITY_ERROR, VERBOSITY_WARNING, VERBOSITY_INFO, VERBOSITY_DEBUG, VERBOSITY_TRACE

# ───────────────────────────────────────────
# CONFIG & CONSTANTS
# ───────────────────────────────────────────

FIELDNAMES = [
    'appid', 'name', 'playtime_forever', 'playtime_windows_forever',
    'playtime_mac_forever', 'playtime_linux_forever', 'rtime_last_played',
    'playtime_2weeks', 'has_community_visible_stats', 'img_icon_url', 'img_logo_url'
]

# ───────────────────────────────────────────
# CORE STEAM API FUNCTIONS
# ───────────────────────────────────────────

def get_owned_games(steam_secret: str, steam_id64: str):
    '''
    Queries steams API for games owned by the api key holder
    '''
    try:
        log(f"[steamExportLibrary.get_owned_games] API key = {steam_secret}", VERBOSITY_TRACE)
        log(f"[steamExportLibrary.get_owned_games] Steam ID64 = {steam_id64}", VERBOSITY_TRACE)
        url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        params = {
            "key": steam_secret,
            "steamid": steam_id64,
            "include_appinfo": True,
            "include_played_free_games": True
        }
        response = requests.get(url, params=params, timeout=10)
        log(f"[steamExportLibrary.get_owned_games] response = {response}", VERBOSITY_TRACE)
        response.raise_for_status()
        data = response.json()
        return data.get("response", {}).get("games", [])
    except Exception:
        log(f"[steamExportLibrary.get_owned_games] Critical error when attempting to pull owned steam games from key holder.", VERBOSITY_ERROR)

def write_games_to_csv(games: list[dict], output_file: Path, append_file: bool = False):
    try:
        mode = 'a' if append_file else 'w'
        write_header = not append_file or not output_file.exists()

        log(f"[steamExportLibrary.write_games_to_csv] Opening file {output_file} in mode '{mode}'. Write header: {write_header}", VERBOSITY_DEBUG)

        with output_file.open(mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL)
            if write_header:
                writer.writeheader()
            for game in games:
                log(f"[steamExportLibrary.write_games_to_csv] Writing row for appid {game.get('appid')}", VERBOSITY_TRACE)
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
    except Exception:
        log(f"[steamExportLibrary.write_games_to_csv] Critical error while attempting to write games to CSV.", VERBOSITY_ERROR)


# ───────────────────────────────────────────
# BATCH EXPORT FUNCTION
# ───────────────────────────────────────────

def export_steam_library_to_csv(output_dir: Path = None) -> Path:
    try:
        steam_secret = os.getenv("steam_secret")
        steam_id64 = os.getenv("steam_id64")
        log(f"[steamExportLibrary.export_steam_library_to_csv] steam_secret = {steam_secret}", VERBOSITY_TRACE)
        log(f"[steamExportLibrary.export_steam_library_to_csv] steam_id64 = {steam_id64}", VERBOSITY_TRACE)

        if not steam_secret or not steam_id64:
            log("[steamExportLibrary.export_steam_library_to_csv] Both steam_secret and steam_id64 must be provided in .env", VERBOSITY_ERROR)
            return None

        games = get_owned_games(steam_secret, steam_id64)
        if not games:
            log("[steamExportLibrary.export_steam_library_to_csv] No games found or profile is private.", VERBOSITY_WARNING)

        if output_dir is None:
            output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / 'steam-export.csv'
        log(f"Writing to {output_file}", VERBOSITY_INFO)
        write_games_to_csv(games, output_file)

        return str(output_file.resolve())
    except Exception:
        log(f"[steamExportLibrary.export_steam_library_to_csv] Critical error while attempting to export games to CSV.", VERBOSITY_ERROR)


# ───────────────────────────────────────────
# SINGLE LOOKUP FUNCTION (PUBLIC STEAM STORE)
# ───────────────────────────────────────────

def lookup_game_by_id_or_title(appid: int = None, title: str = None) -> dict | None:
    """
    Lookup a game on the public Steam Store by appid or by title.
    Returns a dictionary with keys similar to owned games data where possible.
    """
    def fetch_app_details(appid: int) -> dict | None:
        '''
        Use steam app details
        '''
        url = f"https://store.steampowered.com/api/appdetails"
        params = {"appids": appid}
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            if not data or str(appid) not in data or not data[str(appid)]["success"]:
                log(f"[steamExportLibrary.py.fetch_app_details] No data for appid {appid}", VERBOSITY_WARNING)
                return None
            return data[str(appid)]["data"]
        except Exception:
            log(f"[steamExportLibrary.py.fetch_app_details] Exception fetching appid {appid}", VERBOSITY_ERROR)

    def search_app_by_name(name: str) -> int | None:
        '''
        Use Steam Store Search API (limited, unofficial)
        '''
        search_url = "https://store.steampowered.com/api/storesearch/"
        params = {"term": name, "l": "english", "cc": "us"}
        try:
            r = requests.get(search_url, params=params, timeout=10)
            r.raise_for_status()
            results = r.json().get("items", [])
            # Attempt exact match ignoring case
            for item in results:
                if item.get("name", "").lower() == name.lower():
                    return item.get("id")
            # Fallback to first result
            if results:
                return results[0].get("id")
            return None
        except Exception:
            log(f"[steamExportLibrary.py.search_app_by_name] Exception searching title '{name}'", VERBOSITY_ERROR)

    try:
        if appid:
            app_data = fetch_app_details(appid)
        elif title:
            found_appid = search_app_by_name(title)
            if found_appid is None:
                log(f"[steamExportLibrary.py.lookup_game_by_id_or_title] No appid found for title '{title}'", VERBOSITY_WARNING)
                return None
            app_data = fetch_app_details(found_appid)
        else:
            log("[steamExportLibrary.py.lookup_game_by_id_or_title] Neither appid nor title provided.", VERBOSITY_ERROR)
            return None

        if not app_data:
            return None

        # Map Steam Store data to similar keys as owned games
        mapped = {
            "appid": app_data.get("steam_appid", ""),
            "name": app_data.get("name", ""),
            "playtime_forever": 0,  # Not available publicly
            "playtime_windows_forever": 0,
            "playtime_mac_forever": 0,
            "playtime_linux_forever": 0,
            "rtime_last_played": 0,
            "playtime_2weeks": 0,
            "has_community_visible_stats": False,
            "img_icon_url": app_data.get("header_image", ""),
            "img_logo_url": app_data.get("header_image", ""),
        }
        return mapped
    except Exception:
        log("[steamExportLibrary.py.lookup_game_by_id_or_title] Exception occured attempting to look up game.", VERBOSITY_ERROR)

# ───────────────────────────────────────────
# CLI ENTRY POINT
# ───────────────────────────────────────────

if __name__ == "__main__":
    """
    Command-line interface for the Steam library exporter and single game lookup tool.

    Usage:
        Bulk Export:
            python3 -m helpers.steamExportLibrary --strategy=owned

        Single Game Lookup:
            python3 -m helpers.steamExportLibrary --strategy=lookup --id=123456
            python3 -m helpers.steamExportLibrary --strategy=lookup --title="Game Title"

        Optional Flags (Lookup Mode Only):
            --export            Export the lookup result to CSV
            --append            Append to the CSV instead of overwriting (used with --export)
    """
    try:
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)

        parser = argparse.ArgumentParser(description="Steam library exporter and single game lookup tool.")
        parser.add_argument("--strategy", choices=["owned", "lookup"], required=True, help="Specify the strategy: 'owned' for full export, 'lookup' for a single game.")
        parser.add_argument("--id", type=int, help="App ID for lookup mode.")
        parser.add_argument("--title", type=str, help="Title for lookup mode.")
        parser.add_argument("--export", type=bool, required=False, default=False, help="Export to CSV file (default: False).")
        parser.add_argument("--append", type=bool, required=False, default=False, help="Append to existing CSV file (default: False).")
        args = parser.parse_args()

        if args.strategy == "owned":
            output_path = export_steam_library_to_csv()
        elif args.strategy == "lookup":
            if not args.id and not args.title:
                log("[steamExportLibrary.py.__main__] When using strategy=lookup, you must provide --id or --title.", VERBOSITY_ERROR)
            game = lookup_game_by_id_or_title(appid=args.id, title=args.title)
            if game:
                log(game, VERBOSITY_INFO)
                if args.export:
                    output_dir = Path(__file__).parent.parent / 'output'
                    output_path = output_dir / 'steam-lookup.csv'
                    write_games_to_csv([game], output_path,args.append)
            else:
                log("[steamExportLibrary.py.__main__] No matching game found.",VERBOSITY_WARNING)
    except Exception:
        log("[steamExportLibrary.py.__main__] Exception occured while running helper manually.", VERBOSITY_ERROR)
