# -*- coding: utf-8 -*-
"""Конфігурація застосунку"""
import os
from enum import Enum
from dataclasses import dataclass

# === Grid Configuration ===

class SnapMode(Enum):
    """Режими вирівнювання елементів"""
    GRID = 'grid'          # Align to Grid
    OBJECTS = 'objects'    # Align to Objects
    NONE = 'none'          # Do Not Align

@dataclass
class GridConfig:
    """Конфігурація сітки (аналогічно ZebraDesigner 3)"""
    size_x_mm: float = 2.0     # Grid Size X (крок по горизонталі)
    size_y_mm: float = 2.0     # Grid Size Y (крок по вертикалі)
    offset_x_mm: float = 0.0   # Grid Offset X (зсув початку сітки)
    offset_y_mm: float = 0.0   # Grid Offset Y
    visible: bool = True       # Display gridline guides
    snap_mode: SnapMode = SnapMode.GRID  # Режим snap

# Базові шляхи
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    'APP_NAME': 'ZPL Label Designer',
    'VERSION': '1.0.0',
    
    # Параметри етикетки за замовчуванням
    'DEFAULT_WIDTH_MM': 28,
    'DEFAULT_HEIGHT_MM': 28,
    'DEFAULT_DPI': 203,
    
    # Обмеження розмірів етикетки (Zebra принтери)
    'MIN_LABEL_WIDTH_MM': 10.0,
    'MAX_LABEL_WIDTH_MM': 110.0,
    'MIN_LABEL_HEIGHT_MM': 10.0,
    'MAX_LABEL_HEIGHT_MM': 300.0,
    
    # API
    'LABELARY_API': 'http://api.labelary.com/v1/printers',
    'API_HOST': '0.0.0.0',
    'API_PORT': 5000,
    
    # Шляхи
    'TEMPLATES_DIR': 'templates/library',
}

# === ЛОГУВАННЯ ===
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Рівні деталізації логування
LOG_LEVELS = {
    'MINIMAL': 'ERROR',      # Тільки помилки
    'NORMAL': 'INFO',        # Важлива інформація
    'DEBUG': 'DEBUG',        # Відладочна інформація
    'VERBOSE': 'DEBUG'       # Максимально детально (з усіма категоріями)
}

# Поточний рівень деталізації (змінюй тут для управління)
CURRENT_LOG_LEVEL = 'DEBUG'  # MINIMAL | NORMAL | DEBUG | VERBOSE (ТИМЧАСОВО для дебагу snap)

# Рівні для файлу та консолі
FILE_LOG_LEVEL = LOG_LEVELS[CURRENT_LOG_LEVEL]
CONSOLE_LOG_LEVEL = LOG_LEVELS[CURRENT_LOG_LEVEL]

# Формати
FILE_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
CONSOLE_LOG_FORMAT = "[%(levelname)s] %(name)s: %(message)s"  # З назвою модуля
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Категорії логування (можна вимикати окремо)
LOG_CATEGORIES = {
    'canvas': CURRENT_LOG_LEVEL in ['DEBUG', 'VERBOSE'],     # Canvas події
    'rulers': CURRENT_LOG_LEVEL in ['DEBUG', 'VERBOSE'],     # Лінійки
    'elements': CURRENT_LOG_LEVEL in ['VERBOSE'],            # Елементи (тільки VERBOSE)
    'zpl': True,                                              # ZPL генерація (завжди)
    'api': True,                                              # API запити (завжди)
    'template': True                                          # Шаблони (завжди)
}

# Створення директорії логів
os.makedirs(LOG_DIR, exist_ok=True)

# === Units Configuration ===
from utils.unit_converter import MeasurementUnit

DEFAULT_UNIT = MeasurementUnit.MM

# КРИТИЧНО: Всі елементи зберігають координати і розміри в MM!
# Це базова одиниця для всіх розрахунків і ZPL генерації.
# Units використовуються ТІЛЬКИ для відображення в GUI.

# Precision (кількість десяткових знаків) для кожної одиниці
UNIT_DECIMALS = {
    MeasurementUnit.MM: 1,    # 10.5 mm
    MeasurementUnit.CM: 2,    # 1.05 cm
    MeasurementUnit.INCH: 3   # 0.413 inch
}

# SpinBox step для кожної одиниці
UNIT_STEPS = {
    MeasurementUnit.MM: 0.1,    # 0.1 mm
    MeasurementUnit.CM: 0.01,   # 0.01 cm
    MeasurementUnit.INCH: 0.01  # 0.01 inch
}
