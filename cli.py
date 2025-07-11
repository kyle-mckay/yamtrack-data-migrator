# Standard library imports
import csv
import argparse
import sys
import os
from datetime import datetime

# Add import for hardcover adapter
from adapters import hardcover
from helpers import (
    log,
    VERBOSITY_ERROR,
    VERBOSITY_WARNING,
    VERBOSITY_INFO,
    VERBOSITY_DEBUG,
    VERBOSITY_TRACE,
)
import helpers


# File Importers

# Imports from source file into Pythons `csv.DictReader` object for easy manipulation.
def import_csv(input_file):
    """
    Import a CSV file into Pythons `csv.DictReader` object for easy manipulation.
    If trace verbosity is enabled, output all row contents in detail.
    """
    log(f"Importing CSV file: {input_file}", VERBOSITY_INFO)
    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        for idx, row in enumerate(rows, 1):
            log(f"Row {idx}: {row}", VERBOSITY_TRACE)
        # Use helpers.VERBOSITY and helpers.VERBOSITY_TRACE
        if helpers.VERBOSITY >= VERBOSITY_TRACE:
            log("[TRACE] Outputting all row contents:", VERBOSITY_TRACE)
            for idx, row in enumerate(rows, 1):
                log(f"TRACE Row {idx}: {row}", VERBOSITY_TRACE)
    return rows

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
            log(f"Element {idx}: {ET.tostring(elem, encoding='unicode').strip()}", VERBOSITY_DEBUG)
            print(ET.tostring(elem, encoding='unicode').strip())
    except Exception as e:
        log(f"Failed to parse XML: {e}", VERBOSITY_ERROR)

def export_csv(rows, output_file):
    """
    Export a list of dictionaries to a CSV file.
    """
    if not rows:
        log("No rows to export.", VERBOSITY_WARNING)
        return
    fieldnames = list(rows[0].keys())
    log(f"Exporting {len(rows)} rows to {output_file}", VERBOSITY_INFO)
    with open(output_file, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    log(f"Full output file path: {os.path.abspath(output_file)}", VERBOSITY_DEBUG)
    log(f"Export complete.", VERBOSITY_INFO)

# Main entry point for the CLI
def main():
    """
    Parse command-line arguments, detect file type, and call the appropriate import function.
    """
    parser = argparse.ArgumentParser(description="YamTrack CSV Importer")
    parser.add_argument('--source', choices=['hardcover'], help='Source type (currently only hardcover CSV supported)')
    parser.add_argument('--input', required=True, help='Input file (CSV or XML)')
    parser.add_argument('--output', required=False, help='Output file (CSV)')
    parser.add_argument('--verbosity', '-v', type=int, choices=range(0, 5), help='Verbosity level: 0=ERROR, 1=WARNING, 2=INFO, 3=DEBUG, 4=TRACE')
    args = parser.parse_args()

    if args.verbosity is not None:
        helpers.VERBOSITY = args.verbosity
        log(f"Verbosity set to {helpers.VERBOSITY}", VERBOSITY_DEBUG)

    input_file = args.input
    log(f"Input file: {input_file}", VERBOSITY_DEBUG)
    output_file = args.output
    log(f"Output file: {output_file}", VERBOSITY_DEBUG)

    # If output_file is not provided, generate it based on input_file and timestamp
    if not output_file:
        log(f"No --output specified. Generating output filename based on input: {input_file}", VERBOSITY_WARNING)
        base, _ = os.path.splitext(os.path.basename(input_file))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{base}{timestamp}.csv")
        log(f"Auto-generated output filename: {output_file}", VERBOSITY_INFO)

    filetype = None
    # Detect file type by extension
    if input_file.lower().endswith('.csv'):
        filetype = 'csv'
    elif input_file.lower().endswith('.xml'):
        filetype = 'xml'
    else:
        log(f"Unsupported file type for input: {input_file}", VERBOSITY_ERROR)
        sys.exit(1)

    log(f"Detected file type: {filetype.upper()}", VERBOSITY_INFO)

    # Call the appropriate import function
    if filetype == 'csv':
        rows = import_csv(input_file)
        if args.source == 'hardcover':
            mapped_rows = hardcover.process_rows(rows)
        else:
            log("No adapter specified for CSV source.", VERBOSITY_ERROR)
            sys.exit(1)
    elif filetype == 'xml':
        import_xml(input_file)
    
    # Export mapped rows to CSV
    if mapped_rows and output_file:
        export_csv(mapped_rows, output_file)

if __name__ == "__main__":
    main()
