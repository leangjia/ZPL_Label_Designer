# -*- coding: utf-8 -*-
"""应用程序配置"""
import os
from enum import Enum
from dataclasses import dataclass


# === 网格配置 ===

class SnapMode(Enum):
    """元素对齐模式"""
    GRID = 'grid'  # 对齐到网格
    OBJECTS = 'objects'  # 对齐到对象
    NONE = 'none'  # 不对齐


@dataclass
class GridConfig:
    """网格配置（类似于 ZebraDesigner 3）"""
    size_x_mm: float = 1.0  # 网格大小 X（水平步长）
    size_y_mm: float = 1.0  # 网格大小 Y（垂直步长）
    offset_x_mm: float = 0.0  # 网格偏移 X（网格起始点偏移）
    offset_y_mm: float = 0.0  # 网格偏移 Y
    visible: bool = True  # 显示网格线参考线
    snap_mode: SnapMode = SnapMode.GRID  # 吸附模式


# 基本路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = {
    'APP_NAME': 'ZPL 标签设计器',
    'VERSION': '1.0.0',

    # 默认标签参数
    'DEFAULT_WIDTH_MM': 28,
    'DEFAULT_HEIGHT_MM': 28,
    'DEFAULT_DPI': 203,

    # 标签尺寸限制（Zebra 打印机）
    'MIN_LABEL_WIDTH_MM': 10.0,
    'MAX_LABEL_WIDTH_MM': 110.0,
    'MIN_LABEL_HEIGHT_MM': 10.0,
    'MAX_LABEL_HEIGHT_MM': 300.0,

    # API
    'LABELARY_API': 'http://api.labelary.com/v1/printers',
    'API_HOST': '0.0.0.0',
    'API_PORT': 5000,

    # 路径
    'TEMPLATES_DIR': 'templates/library',
}

# === 日志配置 ===
LOG_DIR = os.path.join(BASE_DIR, "logs")

# 日志详细级别
LOG_LEVELS = {
    'MINIMAL': 'ERROR',  # 仅错误
    'NORMAL': 'INFO',  # 重要信息
    'DEBUG': 'DEBUG',  # 调试信息
    'VERBOSE': 'DEBUG'  # 最详细（包含所有类别）
}

# 当前日志详细级别（在此处更改以控制日志输出）
CURRENT_LOG_LEVEL = 'DEBUG'  # MINIMAL | NORMAL | DEBUG | VERBOSE（临时用于调试吸附功能）

# 文件和控制台的日志级别
FILE_LOG_LEVEL = LOG_LEVELS[CURRENT_LOG_LEVEL]
CONSOLE_LOG_LEVEL = LOG_LEVELS[CURRENT_LOG_LEVEL]

# 格式
FILE_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
CONSOLE_LOG_FORMAT = "[%(levelname)s] %(name)s: %(message)s"  # 包含模块名称
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志类别（可以单独禁用）
LOG_CATEGORIES = {
    'canvas': CURRENT_LOG_LEVEL in ['DEBUG', 'VERBOSE'],  # 画布事件
    'rulers': CURRENT_LOG_LEVEL in ['DEBUG', 'VERBOSE'],  # 标尺
    'elements': CURRENT_LOG_LEVEL in ['VERBOSE'],  # 元素（仅 VERBOSE）
    'zpl': True,  # ZPL 生成（始终启用）
    'api': True,  # API 请求（始终启用）
    'template': True  # 模板（始终启用）
}

# 创建日志目录
os.makedirs(LOG_DIR, exist_ok=True)

# === 单位配置 ===
from utils.unit_converter import MeasurementUnit

DEFAULT_UNIT = MeasurementUnit.MM

# 关键：所有元素以 MM 为单位存储坐标和尺寸！
# 这是所有计算和 ZPL 生成的基本单位。
# 单位仅用于 GUI 显示。

# 每个单位的精度（小数位数）
UNIT_DECIMALS = {
    MeasurementUnit.MM: 1,  # 10.5 mm
    MeasurementUnit.CM: 2,  # 1.05 cm
    MeasurementUnit.INCH: 3  # 0.413 inch
}

# 每个单位的 SpinBox 步长
UNIT_STEPS = {
    MeasurementUnit.MM: 0.1,  # 0.1 mm
    MeasurementUnit.CM: 0.01,  # 0.01 cm
    MeasurementUnit.INCH: 0.01  # 0.01 inch
}