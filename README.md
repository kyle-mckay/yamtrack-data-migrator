# YamTrack CSV Importer

A Python script to convert external media tracker exports (Trakt, MyAnimeList, etc.) into YamTrack-compatible CSV files for easy import.

<figure>
    <img src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/yamtrack.svg" height="200" alt="YamTrack logo">
    <figcaption>Image Source - https://github.com/homarr-labs/dashboard-icons</figcaption>
</figure>

*Compatible with [YamTrack](https://github.com/FuzzyGrim/Yamtrack), a self-hosted media tracker.*

---

## Planned Features
- **Multi-Source Support**: Convert from Hardcover, The Internet Game Database (igdb), and more
- **Flexible Input Formats**: CSV, XML, or JSON (source-dependent)
- **Data Normalization**: Maps fields like statuses, scores, and dates to their specified format
- **CLI & Interactive Modes**: Use command-line arguments or prompts

---

## Supported Sources
| Source   | Input Format | Notes                          |
|----------|--------------|--------------------------------|
| [Hardcover](https://hardcover.app) | CSV | Built in export |
| [IGDB](https://igdb.com) | CSV | Exports from lists download |
| [Steam](https://store.steampowered.com) | API | Exports owned cames and queries igdb api for id's |
| [Open Library](openlibrary.org) | CSV | Built in export |
| *More coming soon!* | | Submit requests via Issues |

---

## Setup

Setting up the script is rather simple. The following setup steps assume the use of Python Virtual Environments.

1. Clone repo `git clone https://github.com/kyle-mckay/yamtrack-data-migrator/`
2. Navigate to the directory `cd yamtrack-data-migrator`
3. Create python venv in repo directory `python3 -m venv env`
4. Activate the venv `source env/bin/activate`
5. Install dependencies `pip install -r requirements.txt`
6. rename `template.env` to `.env` `mv template.env .env`
7. update variables as needed

### Variables

Breakdown to be added

---

## Usage
### Command-Line (Recommended)

```bash
python3 cli.py --source <source> --input <input_file> 
```

**Examples**:  
```bash
# Convert Hardcover CSV
python3 cli.py --source hardcover --input hardcover_export.csv --output yamtrack_import.csv

# Convert an IGDB auto list CSV
python3 cli.py --source igdb --input played.csv

# Convert your steam library and match to igdb (uses your own API keys)
python3 cli.py --source igdb --input steam
```

### Importing back into YamTrack

Once you have generated a csv with `cli.sh`, do the following with the output file to import it into YamTrack:

1. Open YamTrack via the web gui and sign in
2. On the bottom left, open settings and choose the `import data` option
3. Under the `YamTrack` source, click the `Select CSV File` button and upload your generated csv
4. Thats it!

---

## File Formats

*See [YamTrack's CSV Format](https://github.com/FuzzyGrim/Yamtrack/wiki/Yamtrack-CSV-Format) for full specifications.*

---

## Contributing
1. **Add New Sources**:
   - Create a parser in `adapters/` (see `adapters/hardcover.py` as example)
   - Update `SOURCES` in `cli.py`
2. **Report Issues**: Include sample files and error logs
3. **Submit PRs**
