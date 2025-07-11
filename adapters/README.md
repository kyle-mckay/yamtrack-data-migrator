# Adapter Column Mapping

Main Purpose: Take the passed data and convert, transpose, or format data into the expected format for YamTrack.

These modules define and manages the column mapping logic used to convert export files from sources (`hardcover`, `openlibrary`, etc) into a format compatible with importing YamTrack.

It enables reliable data migration by:
- Mapping known columns to target schema fields
- Handling missing or optional fields
- Ensuring consistent data types and formats

## 🛠 Usage

This module is intended to be used as part of a larger Python adapter pipeline. For standalone use:

```bash
python cli.py --source hardcover --input hardcover_export.csv --output yamtrack_ready.csv
````

## 🧱 Structure

Each adapter in `adapters/` is designed to be called via `cli.py` based on the source defined by the `--source` flag and is expecting to be fed the data in pythons own `csv.DictReader` format.

## ✅ Testing

Before using or deploying the adapter, validate functionality using the standard checklist.

👉 See [CHECKLIST.md](./CHECKLIST.md) for example testing steps.

## 🔒 Token Use (If Applicable)

If your extended use involves authenticated API transformation or metadata augmentation, ensure proper environment handling for tokens and secrets. This adapter itself does not (currently) directly handle API calls.
