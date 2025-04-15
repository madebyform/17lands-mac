import logging
import logging.handlers
import os
from typing import Dict, Optional


_LOG_FOLDER = os.path.join(os.path.expanduser("~"), ".seventeenlands")
if not os.path.exists(_LOG_FOLDER):
    os.makedirs(_LOG_FOLDER)
_LOG_FILENAME = os.path.join(_LOG_FOLDER, "seventeenlands.log")

_LOG_FORMATTER = logging.Formatter(
    "%(asctime)s.%(msecs)03d,%(levelname)s,%(name)s,%(message)s",
    datefmt="%Y%m%d %H%M%S",
)
_HANDLERS = [
    logging.handlers.TimedRotatingFileHandler(
        _LOG_FILENAME,
        when="D",
        interval=1,
        backupCount=7,
        utc=True,
    ),
    logging.StreamHandler(),
]

for handler in _HANDLERS:
    handler.setFormatter(_LOG_FORMATTER)

_loggers: Dict[str, logging.Logger] = {}
_log_location_logged = False


def get_logger(name: str, log_level: Optional[int] = None) -> logging.Logger:
    global _log_location_logged

    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    for handler in _HANDLERS:
        logger.addHandler(handler)

    logger.setLevel(log_level if log_level is not None else logging.INFO)

    if not _log_location_logged:
        logger.info(f"Saving logs to {_LOG_FILENAME}")
        _log_location_logged = True

    _loggers[name] = logger

    return logger
