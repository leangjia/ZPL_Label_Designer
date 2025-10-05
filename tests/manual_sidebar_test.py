# -*- coding: utf-8 -*-
"""
Ручний тест GUI Sidebar
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import logger

if __name__ == '__main__':
    print("=" * 60)
    print("MANUAL GUI TEST: SIDEBAR")
    print("=" * 60)
    print("Інструкції:")
    print("1. Перевір що Sidebar видимий СПРАВА від canvas")
    print("2. Клікни на кнопку 'Text' в sidebar")
    print("3. Перевір що елемент з'явився на canvas")
    print("4. Клікни на 'Barcode' (має додатися EAN-13)")
    print("5. Клікни на 'Rectangle'")
    print("6. Перевір що всі елементи можна виділити та перетягнути")
    print("7. Закрий вікно")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
