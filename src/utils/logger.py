"""
Sistema de logging centralizado.
"""
import sys
from pathlib import Path
from loguru import logger
from config.settings import config


def setup_logging():
    """Configura o sistema de logging do aplicativo"""
    
    # Remover logger padrão
    logger.remove()
    
    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=config.LOG_LEVEL,
        colorize=True,
    )
    
    # Arquivo de log geral
    logger.add(
        config.LOG_PATH / "app.log",
        rotation=f"{config.LOG_MAX_SIZE_MB} MB",
        retention=config.LOG_BACKUP_COUNT,
        compression="zip",
        level=config.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )
    
    # Log de erros separado
    logger.add(
        config.LOG_PATH / "errors.log",
        rotation=f"{config.LOG_MAX_SIZE_MB} MB",
        retention=config.LOG_BACKUP_COUNT,
        compression="zip",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )
    
    # Logs específicos por módulo
    logger.add(
        config.LOG_PATH / "monitors.log",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        level="DEBUG",
        filter=lambda record: "monitor" in record["name"].lower(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    )
    
    logger.add(
        config.LOG_PATH / "processors.log",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        level="DEBUG",
        filter=lambda record: "processor" in record["name"].lower(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    )
    
    logger.add(
        config.LOG_PATH / "publishers.log",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        level="DEBUG",
        filter=lambda record: "publisher" in record["name"].lower(),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    )
    
    logger.info("Sistema de logging inicializado")
    return logger


# Inicializar logger global
app_logger = setup_logging()
