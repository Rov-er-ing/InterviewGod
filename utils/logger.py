import logging
import sys
import os

def setup_logger(name="signal_detector", level=logging.INFO):
    """Sets up a structured logger that outputs to both console and file."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (Gracefully skip if filesystem is read-only)
    try:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, IOError) as e:
        # Fallback for read-only filesystems (Vercel/Lambda)
        logger.warning(f"File logging disabled: {e}")

    return logger

# Default instance
logger = setup_logger()
