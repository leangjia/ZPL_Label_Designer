# -*- coding: utf-8 -*-
"""
Модуль логування для ZPL Label Designer
Автоматична очистка лог-файлу при кожному запуску
"""
import logging
import os
from datetime import datetime
from config import (
    LOG_DIR, 
    FILE_LOG_LEVEL, 
    FILE_LOG_FORMAT, 
    LOG_DATE_FORMAT,
    CONSOLE_LOG_LEVEL,
    CONSOLE_LOG_FORMAT
)

def setup_logger(name="ZPL_Designer"):
    """
    Налаштування логгера з автоматичною очисткою файлу
    
    При кожному запуску:
    1. Видаляє старий лог-файл
    2. Створює новий файл
    3. Записує початок сесії
    
    Args:
        name: Ім'я логгера
        
    Returns:
        logger: Налаштований логгер
    """
    # Файл лога - завжди один і той самий
    log_filename = os.path.join(LOG_DIR, 'zpl_designer.log')
    
    # Очищення старого лога при створенні нового логгера
    if os.path.exists(log_filename):
        try:
            os.remove(log_filename)
            print("[OK] Log file cleared")
        except Exception as e:
            print(f"[!] Failed to clear log: {e}")
    
    # Налаштування логгера
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, FILE_LOG_LEVEL))
    
    # Очищення старих хендлерів (якщо логгер вже існував)
    logger.handlers.clear()
    
    # === ФАЙЛОВИЙ ХЕНДЛЕР ===
    # Записує ВСІ повідомлення (DEBUG і вище) в файл
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(FILE_LOG_FORMAT, LOG_DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # === КОНСОЛЬНИЙ ХЕНДЛЕР ===
    # Виводить повідомлення згідно CONSOLE_LOG_LEVEL (INFO/DEBUG/ERROR)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, CONSOLE_LOG_LEVEL))
    console_formatter = logging.Formatter(CONSOLE_LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # Додавання хендлерів
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Початок сесії
    session_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"=== ZPL Designer Session Started {session_start} ===")
    logger.info(f"Log file: {log_filename}")
    logger.info(f"Log level: {FILE_LOG_LEVEL}, Console level: {CONSOLE_LOG_LEVEL}")
    
    return logger

# Глобальний логгер для використання в усьому застосунку
logger = setup_logger()
