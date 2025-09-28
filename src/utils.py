import logging
import getpass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def safe_input(prompt):
    """Safe input function with error handling"""
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        raise
    except Exception as e:
        logger.error(f"Input error: {e}")
        return ""

def safe_getpass(prompt):
    """Safe password input"""
    try:
        return getpass.getpass(prompt)
    except Exception as e:
        logger.error(f"Password input error: {e}")
        return ""
