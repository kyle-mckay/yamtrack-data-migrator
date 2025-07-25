# Third party imports
import csv
import argparse
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# First party imports
from clilog import (
    log,
    clear_logs,
    VERBOSITY,
    VERBOSITY_ERROR,
    VERBOSITY_WARNING,
    VERBOSITY_INFO,
    VERBOSITY_DEBUG,
    VERBOSITY_TRACE,
    traceback_exit,
    clear_logs_on_start,
)
import clilog

from adapters import (
    hardcover,
    igdb,
    openlibrary,
)
import adapters
from helpers.steamExportLibrary import export_steam_library_to_csv
from helpers.igdbSteamLookup import process_and_export_steam_rows

# Variable defenitions
ENV_PATH = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=ENV_PATH)

log(f"[cli.py] verbosity obtained fron .env = {VERBOSITY}",VERBOSITY_DEBUG)
log(f"[cli.py] .env path loaded as {ENV_PATH}",VERBOSITY_TRACE)
log(f"[cli.py] clear_logs = {clear_logs()}", VERBOSITY_DEBUG)
log(f"[cli.py] Errors trigger traceback = {traceback_exit}", VERBOSITY_DEBUG)

# File Importers

# Imports from source file into Pythons `csv.DictReader` object for easy manipulation.
def import_csv(input_file):
    """
    Import a CSV file into Pythons `csv.DictReader` object for easy manipulation.
    If trace verbosity is enabled, output all row contents in detail.
    """
    log(f"Importing CSV file: {input_file}", VERBOSITY_INFO)
    try:
        with open(input_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            # Use clilog.VERBOSITY and clilog.VERBOSITY_TRACE
            if clilog.VERBOSITY >= VERBOSITY_TRACE:
                log("[cli.py.import_csv] Outputting all row contents:", VERBOSITY_TRACE)
                for idx, row in enumerate(rows, 1):
                    log(f"[cli.py.import_csv] Row {idx}: {row}", VERBOSITY_TRACE)
        return rows
    except Exception:
        log(f"[cli.py.import_csv] Failed to parse CSV: {input_file}", VERBOSITY_ERROR)

# Import and print contents of an XML file
def import_xml(input_file):
    """
    Import an XML file and print each element.
    If parsing fails, log an error.
    """
    log(f"Importing XML file: {input_file}", VERBOSITY_INFO)
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(input_file)
        root = tree.getroot()
        for idx, elem in enumerate(root, 1):
            log(f"[cli.py.export_xml] Element {idx}: {ET.tostring(elem, encoding='unicode').strip()}", VERBOSITY_DEBUG)
            print(ET.tostring(elem, encoding='unicode').strip())
    except Exception:
        log(f"[cli.py.export_xml] Failed to parse XML: {input_file}", VERBOSITY_ERROR)

def export_csv(rows, output_file):
    """
    Export a list of dictionaries to a CSV file.
    """
    try:
        if not rows:
            log("[cli.py.export_csv] No rows to export.", VERBOSITY_WARNING)
            return
        fieldnames = list(rows[0].keys())
        log(f"Exporting {len(rows)} rows to {output_file}", VERBOSITY_INFO)
        with open(output_file, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        log(f"[cli.py.export_csv] Full output file path: {os.path.abspath(output_file)}", VERBOSITY_DEBUG)
        log("Export complete.", VERBOSITY_INFO)
    except Exception:
        log(f"[cli.py.export_csv] Failed to export CSV",VERBOSITY_ERROR)

# Main entry point for the CLI
def main():
    """
    Parse command-line arguments, detect file type, and call the appropriate import function.
    """

    try:    
        parser = argparse.ArgumentParser(description="YamTrack CSV Importer")
        parser.add_argument('--source', choices=['hardcover', 'igdb', 'openlibrary'], help='Source type (currently only hardcover CSV supported)')
        parser.add_argument('--input', required=True, help='Input file (CSV or XML)')
        parser.add_argument('--output', required=False, help='Output file (CSV)')
        parser.add_argument('--verbosity', '-v', type=int, choices=range(0, 5), help='Verbosity level: 0=ERROR, 1=WARNING, 2=INFO, 3=DEBUG, 4=TRACE')
        parser.add_argument('--strategy', required=False, help="Strategy override when calling adapter")
        args = parser.parse_args()
        load_dotenv()
        
        if args.verbosity is not None:
            clilog.VERBOSITY = args.verbosity
            log(f"[cli.py.main] Verbosity set to {clilog.VERBOSITY}", VERBOSITY_DEBUG)

        strategy = getattr(args, 'strategy', None)
        log(f"[cli.py.main] Strategy parsed: {strategy}", VERBOSITY_DEBUG)

        input_file = args.input
        log(f"[cli.py.main] Input file parsed from switch: {input_file}", VERBOSITY_DEBUG)
        if input_file == "steam":
            log("[cli.py.main] Detecting put as steam, attempting to generate csv from steam API", VERBOSITY_DEBUG)
            strategy="steam_api"
            log("Input is steam, attempting to get steam library",VERBOSITY_INFO)
            input_file = export_steam_library_to_csv()
            log(f"[cli.py.main] updated input_file = {input_file}",VERBOSITY_DEBUG)
            if args.source == "igdb":
                log("Source is igdb, using steam export to lookup id's",VERBOSITY_INFO)
                input_file = process_and_export_steam_rows(import_csv(input_file))
                log(f"igdb ID's obtained and saved to {input_file}", VERBOSITY_INFO)
        
        output_file = args.output
        log(f"[cli.py.main] Output file: {output_file}", VERBOSITY_DEBUG)
    except Exception:
        log(f"[cli.py.main] Failed to parse arguments", VERBOSITY_ERROR)
    
    # If output_file is not provided, generate it based on input_file and timestamp
    try:
        if not output_file:
            log(f"No --output specified. Generating output filename based on input: {input_file}", VERBOSITY_INFO)
            base, _ = os.path.splitext(os.path.basename(input_file))
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_dir = os.path.join(os.path.dirname(__file__), "output")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{base}{timestamp}.csv")
            log(f"Auto-generated output filename: {output_file}", VERBOSITY_INFO)
    except Exception:
        log(f"[cli.py.main] Failed to determine/generate output file name", VERBOSITY_ERROR)

    # Detect file type by extension
    try:
        filetype = None
        input_path = Path(input_file)
        log(f"[cli.py.main] Input file path: {input_path}", VERBOSITY_DEBUG)
        file_name = input_path.name.lower()
        log(f"[cli.py.main] Lowercase input file name: {file_name}", VERBOSITY_DEBUG)
        if file_name.endswith('.csv'):
            filetype = 'csv'
        elif file_name.endswith('.xml'):
            filetype = 'xml'
        else:
            log(f"[cli.py.main] Unsupported file type for input: {input_file}", VERBOSITY_ERROR)

        log(f"Detected file type: {filetype.upper()}", VERBOSITY_INFO)
    except Exception:
        log(f"[cli.py.main] Unable to detect file type for {input_path}", VERBOSITY_ERROR)

    try:
        # Detect file name based on source and enforce different strategy
        
        if strategy is None:
            strategy = "default" # Default to default
            if filetype == 'csv':
                if args.source == 'igdb':
                    if file_name.endswith('played.csv'):
                        log("[cli.py.main] Detected IGDB played list CSV", VERBOSITY_DEBUG)
                        strategy = 'list-played'
                    if file_name.endswith('playing.csv'):
                        log("[cli.py.main] Detected IGDB playing list CSV", VERBOSITY_DEBUG)
                        strategy = 'list-playing'
                    if file_name.endswith('want-to-play.csv'):
                        log("[cli.py.main] Detected IGDB want-to-play list CSV", VERBOSITY_DEBUG)
                        strategy = 'list-want'
                if args.source == 'openlibrary':
                    log("[cli.py.main] Placeholder logic for openlibrary exports.", VERBOSITY_TRACE)
                    #if file_name.endswith('openlibrary_readinglog.csv'):
                        #log("[cli.py.main] Detected OpenLibrary reading log CSV", VERBOSITY_DEBUG)
                        #strategy = 'openlibrary-reading-log'

        log(f"[cli.py.main] Strategy: {strategy}", VERBOSITY_DEBUG)
    except Exception:
        log("[cli.py.main] Unable to set strategy", VERBOSITY_ERROR)

    try:
        # Call the appropriate import function
        if filetype == 'csv':
            rows = import_csv(input_file)
            if args.source == 'hardcover':
                mapped_rows = hardcover.process_rows(rows, strategy)
            elif args.source == 'igdb':
                mapped_rows = igdb.process_rows(rows, strategy)
            elif args.source == 'openlibrary':
                mapped_rows = adapters.openlibrary.process_rows(rows, strategy)
            else:
                log("[cli.py.main] No adapter specified for CSV source.", VERBOSITY_ERROR)
                sys.exit(1)
        elif filetype == 'xml':
            import_xml(input_file)
    except Exception:
        log("[cli.py.main] Unable to adapt input to source", VERBOSITY_ERROR)

    try:
        # Export mapped rows to CSV
        if mapped_rows and output_file:
            export_csv(mapped_rows, output_file)
        log(f"[cli.py.main] CSV Exported",VERBOSITY_TRACE)
    except Exception:
        log("[cli.py.main] Failed to export CSV", VERBOSITY_ERROR)

if __name__ == "__main__":
    main()
