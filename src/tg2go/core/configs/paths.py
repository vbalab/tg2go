from pathlib import Path

_DIR_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
_DIR_DATA = _DIR_ROOT / "data"
_DIR_DOCS = _DIR_ROOT / "docs" / "bot"
_DIR_LOGS = _DIR_DATA / "logs"

DIR_TEMP = _DIR_DATA / "temp"
DIR_IMAGES = _DIR_DATA / "images"
DIR_CLIENT_HEADER = _DIR_DOCS / "client_header"
DIR_STAFF_HEADER = _DIR_DOCS / "staff_header"

_dirs = [
    _DIR_DATA,
    _DIR_LOGS,
    DIR_TEMP,
    DIR_IMAGES,
]

PATH_ENV = _DIR_ROOT / ".env"
PATH_BOT_LOGS = _DIR_LOGS / "bot" / "bot.log"
PATH_TERMS = _DIR_DOCS / "terms" / "source.pdf"
PATH_STAFF = _DIR_DOCS / "staff.json"


def EnsurePaths() -> None:
    for directory in _dirs:
        directory.mkdir(parents=True, exist_ok=True)

    PATH_STAFF.touch(exist_ok=True)

    if not PATH_ENV.exists():
        raise FileNotFoundError("`.env` file not found")
