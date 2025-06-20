from loguru import logger
import os
from datetime import datetime
import sys

def get_logger(name: str):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"{name}_{current_time}.log")

    # Remove default Loguru logger (to avoid duplicate logs)
    logger.remove()

    # File Handler
    logger.add(
        log_file,
        level="DEBUG",
        rotation="5 MB",            # Optional: Rotate log file after 5MB
        retention="10 days",        # Optional: Keep logs for 10 days
        compression="zip",          # Optional: Compress old logs
        backtrace=True,             # Show full trace on errors
        diagnose=True,              # Show variable values on errors
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "{file}:{function}:{line} - <cyan>{name}</cyan> - <level>{message}</level>"
        )
    )

    # Console Handler
    logger.add(
        sys.stdout,
        level="INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "{file}:{function}:{line} - <cyan>{name}</cyan> - <level>{message}</level>"
        )
    )

    return logger.bind(name=name)
