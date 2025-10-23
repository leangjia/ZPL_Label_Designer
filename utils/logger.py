# -*- coding: utf-8 -*-
"""
ZPL 标签设计器日志模块
每次启动时自动清理日志文件
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
    设置带有自动文件清理功能的日志记录器

    每次启动时：
    1. 删除旧的日志文件
    2. 创建新文件
    3. 写入会话开始标记

    Args:
        name: 日志记录器名称

    Returns:
        logger: 配置好的日志记录器
    """
    # 日志文件 - 始终使用同一个文件
    log_filename = os.path.join(LOG_DIR, 'zpl_designer.log')

    # 在创建新日志记录器时清理旧日志
    if os.path.exists(log_filename):
        try:
            os.remove(log_filename)
            print("[成功] 日志文件已清理")
        except Exception as e:
            print(f"[!] 清理日志失败: {e}")

    # 配置日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, FILE_LOG_LEVEL))

    # 清理旧的处理器（如果日志记录器已存在）
    logger.handlers.clear()

    # === 文件处理器 ===
    # 将所有消息（DEBUG 及以上级别）写入文件
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(FILE_LOG_FORMAT, LOG_DATE_FORMAT)
    file_handler.setFormatter(file_formatter)

    # === 控制台处理器 ===
    # 根据 CONSOLE_LOG_LEVEL 输出消息（INFO/DEBUG/ERROR）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, CONSOLE_LOG_LEVEL))
    console_formatter = logging.Formatter(CONSOLE_LOG_FORMAT)
    console_handler.setFormatter(console_formatter)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 会话开始标记
    session_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"=== ZPL 设计器会话开始 {session_start} ===")
    logger.info(f"日志文件: {log_filename}")
    logger.info(f"日志级别: {FILE_LOG_LEVEL}, 控制台级别: {CONSOLE_LOG_LEVEL}")

    return logger


# 全局日志记录器，供整个应用程序使用
logger = setup_logger()