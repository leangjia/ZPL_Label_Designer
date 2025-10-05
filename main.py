# -*- coding: utf-8 -*-
"""Точка входа приложения"""

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import logger

def main():
    logger.info("Starting ZPL Label Designer application")
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("ZPL Label Designer")
        logger.info("Qt Application created")
        
        window = MainWindow()
        window.show()
        logger.info("Main window shown")
        
        logger.info("Entering event loop")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
