import sys
import os
from dotenv import load_dotenv
from pathlib import Path
ENV_PATH = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=ENV_PATH)

VERBOSITY=int(os.getenv("VERBOSITY"))
VERBOSITY_ERROR = 0   # Only errors
VERBOSITY_WARNING = 1 # Warnings and errors
VERBOSITY_INFO = 2    # Info, warnings, errors
VERBOSITY_DEBUG = 3   # Debug, info, warnings, errors
VERBOSITY_TRACE = 4   # Trace, debug, info, warnings, errors

# Default verbosity
# TODO: (can be set via CLI in future)

_COLOR_RESET = "\033[0m"
_COLOR_RED = "\033[91m"
_COLOR_YELLOW = "\033[93m"
_COLOR_GREEN = "\033[92m"
_COLOR_CYAN = "\033[96m"
_COLOR_MAGENTA = "\033[95m"

def log(msg, level=None):
    """
    Print a log message to the terminal if the level is within the current verbosity.
    Color codes are used for different log levels.
    """
    if level is None:
        level = VERBOSITY_INFO
    if level > VERBOSITY:
        return
    if level == VERBOSITY_ERROR:
        prefix = f"{_COLOR_RED}[ERROR]{_COLOR_RESET} "
    elif level == VERBOSITY_WARNING:
        prefix = f"{_COLOR_YELLOW}[WARN]{_COLOR_RESET} "
    elif level == VERBOSITY_INFO:
        prefix = f"{_COLOR_GREEN}[INFO]{_COLOR_RESET} "
    elif level == VERBOSITY_DEBUG:
        prefix = f"{_COLOR_CYAN}[DEBUG]{_COLOR_RESET} "
    elif level == VERBOSITY_TRACE:
        prefix = f"{_COLOR_MAGENTA}[TRACE]{_COLOR_RESET} "
    else:
        prefix = ""
    print(f"{prefix}{msg}", file=sys.stderr if level == VERBOSITY_ERROR else sys.stdout)
