import re
import sys
import logging

class IgnoreNoisyErrors(logging.Filter):
    def filter(self, record):
        ignore_patterns = [
            r"could not convert string to float",
            r"time data 'UTC' does not match format",
            r"Unknown string format: UTC",
        ]
        message = record.getMessage()
        return not any(re.search(p, message) for p in ignore_patterns)

logging.getLogger().addFilter(IgnoreNoisyErrors())    

def setup_logger(name: str = "", level=logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.ERROR)  # Only ERROR and higher severity levels
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
