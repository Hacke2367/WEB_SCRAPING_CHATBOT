import sys
from loguru import logger
from src.config import Config

def get_logger(name: str | None = None):

    logger.remove()

    logger.add(
        sys.stderr,
        level=Config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        diagnose=Config.DEBUG
    )

    logger.add(
        Config.LOG_FILE,
        level=Config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        rotation="10 MB", 
        compression="zip", 
        retention="7 days",  
        enqueue=True,  
        diagnose=Config.DEBUG
    )
    
    if name:
        return logger.bind(module_name=name)
    return logger

    


