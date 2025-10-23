# -*- coding: utf-8 -*-
"""应用程序入口点"""

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import logger


def main():
    logger.info("正在启动 ZPL 标签设计器应用程序")

    try:
        app = QApplication(sys.argv)
        app.setApplicationName("ZPL 标签设计器")
        logger.info("Qt 应用程序已创建")

        # 检查命令行参数
        template_file = None
        if len(sys.argv) > 1:
            template_file = sys.argv[1]
            logger.info(f"来自命令行的模板文件: {template_file}")

        window = MainWindow(template_file=template_file)
        window.show()
        logger.info("主窗口已显示")

        logger.info("进入事件循环")
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"应用程序错误: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()