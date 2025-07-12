import sys
import os
import re
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

ENV_PATH = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=ENV_PATH)

VERBOSITY = int(os.getenv("VERBOSITY"))
VERBOSITY_ERROR = 0
VERBOSITY_WARNING = 1
VERBOSITY_INFO = 2
VERBOSITY_DEBUG = 3
VERBOSITY_TRACE = 4

write_to_file = os.getenv("write_to_file", "False").lower() in ("true", "1", "yes")
clear_logs_on_start = os.getenv("clear_logs_on_start", "False").lower() in ("true", "1", "yes")
log_file_path = Path(__file__).parent / 'logs' / 'app.log'

_COLOR_RESET   = "\033[0m"
_COLOR_MAP = {
    VERBOSITY_ERROR:   ("\033[91m", "[ERROR]"),
    VERBOSITY_WARNING: ("\033[93m", "[WARN]"),
    VERBOSITY_INFO:    ("\033[92m", "[INFO]"),
    VERBOSITY_DEBUG:   ("\033[96m", "[DEBUG]"),
    VERBOSITY_TRACE:   ("\033[95m", "[TRACE]"),
}

_ansi_escape_re = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")

def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from a string."""
    return _ansi_escape_re.sub("", text)

def log(msg, level=None):
    if level is None:
        level = VERBOSITY_INFO
    if level > VERBOSITY:
        return

    color, label = _COLOR_MAP.get(level, ("", ""))
    prefix = f"{color}{label}{_COLOR_RESET} " if label else ""
    output_stream = sys.stderr if level == VERBOSITY_ERROR else sys.stdout

    formatted_msg = f"{prefix}{msg}"
    print(formatted_msg, file=output_stream)

    if write_to_file:
        plain_msg = _strip_ansi(formatted_msg)
        _log_to_file(plain_msg, level)

    if level == VERBOSITY_ERROR:
        raise Exception(msg)

def _log_to_file(msg, level):
    if level > VERBOSITY:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"[{timestamp}] {msg}\n")


def clear_logs():
    if clear_logs_on_start:
        if log_file_path.exists():
            log_file_path.unlink()
    return clear_logs_on_start

    