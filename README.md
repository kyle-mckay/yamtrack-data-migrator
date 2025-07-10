# YamTrack CSV Importer

A Python script to convert external media tracker exports (Trakt, MyAnimeList, etc.) into YamTrack-compatible CSV files for easy import.

![YamTrack Logo](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/yamtrack.svg)  
*Compatible with [YamTrack](https://github.com/FuzzyGrim/Yamtrack), a self-hosted media tracker.*

---

## Planned Features
- **Multi-Source Support**: Convert from Trakt, MyAnimeList (MAL), and more
- **Flexible Input Formats**: CSV, XML, or JSON (source-dependent)
- **Data Normalization**: Automatically maps fields like statuses, scores, and dates
- **CLI & Interactive Modes**: Use command-line arguments or prompts

---

## Supported Sources
| Source   | Input Format | Notes                          |
|----------|--------------|--------------------------------|
| Hardcover| CSV          | Exports from hardcover.app       |
| *More coming soon!* | | Submit requests via Issues |

---

## Installation

TBD

---

## Usage
### Command-Line (Recommended)
```bash
python3 cli.py --source <source> --input <input_file> 
```

**Examples**:  
```bash
# Convert Hardcover CSV
python cli.py --source hardcover --input hardcover_export.csv --output yamtrack_import.csv

# Convert MAL XML
python cli.py --source mal --input mal_export.xml --output yamtrack_import.csv
```

## File Formats

*See [YamTrack's CSV Format](https://github.com/FuzzyGrim/Yamtrack/wiki/Yamtrack-CSV-Format) for full specifications.*

---

## Contributing
1. **Add New Sources**:
   - Create a parser in `adapters/` (see `adapters/hardcover.py` as example)
   - Update `SOURCES` in `cli.py`
2. **Report Issues**: Include sample files and error logs
3. **Submit PRs**