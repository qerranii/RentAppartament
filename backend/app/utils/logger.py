"""Конфигурация логирования приложения."""
import logging
import sys
from app.core.config import settings


def setup_logging():
    """
    Настройка логирования приложения.
    
    Конфигурирует формат логов, уровень детализации и вывод на консоль.
    """
    
    log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
    
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(detailed_formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    for logger_name in ['sqlalchemy', 'uvicorn']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
    
    return root_logger


logger = setup_logging()
