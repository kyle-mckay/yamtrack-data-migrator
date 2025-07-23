import sys
import os
import re
import traceback
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

ENV_PATH = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=ENV_PATH)

VERBOSITY = int(os.getenv("verbosity"))

VERBOSITY_ERROR = 0
VERBOSITY_WARNING = 1
VERBOSITY_INFO = 2
VERBOSITY_DEBUG = 3
VERBOSITY_TRACE = 4

write_to_file = os.getenv("write_to_file", "False").lower() in ("true", "1", "yes")
clear_logs_on_start = os.getenv("clear_logs_on_start", "False").lower() in ("true", "1", "yes")
log_file_path = Path(__file__).parent / 'logs' / 'app.log'
traceback_exit = os.getenv("traceback_exit", "False").lower() in ("true", "1", "yes")

_COLOR_RESET   = "\033[0m"
_COLOR_MAP = {
    VERBOSITY_ERROR:   ("\033[91m", "[ERROR]"),
    VERBOSITY_WARNING: ("\033[93m", "[WARN] "),
    VERBOSITY_INFO:    ("\033[92m", "[INFO] "),
    VERBOSITY_DEBUG:   ("\033[96m", "[DEBUG]"),
    VERBOSITY_TRACE:   ("\033[95m", "[TRACE]"),
}

_ansi_escape_re = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")

def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from a string."""
    return _ansi_escape_re.sub("", text)

def _log_internal_warning(msg):
    # Always print warning in yellow, ignoring verbosity filtering and recursion
    warning_label = "\033[38;5;208m[INTL] \033[0m"
    print(f"{warning_label}{msg}", file=sys.stdout)
    if write_to_file:
        _log_to_file(msg, VERBOSITY_WARNING)

_in_log_self_check = False

def log(msg, level=None):
    global _in_log_self_check
    if level is None:
        level = VERBOSITY_INFO

    # Always check malformed message first, regardless of verbosity
    if not _in_log_self_check:
        if level != VERBOSITY_INFO and not msg.startswith('['):
            _in_log_self_check = True
            warning_msg = (
                f"[logging.py.log] Malformed log message at level {level}, "
                f"missing correct '[filename.py.functionName]' prefix. Message: {msg}"
            )
            _log_internal_warning(warning_msg)
            _in_log_self_check = False

    # Now filter normal messages by verbosity
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
        traceback.print_exc()  # Prints to stderr

        if traceback_exit:
            log(f"[logging.py.log] Exiting due to traceback_exit",VERBOSITY_TRACE)
            sys.exit()

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
