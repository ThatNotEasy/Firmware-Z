import logging

def setup_logging() -> logging.Logger:
    """Set up and return a configured logger."""
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG
    )
    return logging.getLogger()