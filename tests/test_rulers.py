# -*- coding: utf-8 -*-
"""Тест лінійок у ZPL редакторі"""

import sys
from pathlib import Path

# Додати шлях проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import logger


def main():
    """Головна функція тесту"""
    print("[INFO] Starting rulers test...")
    print("[INFO] This test will open GUI with rulers")
    print("")
    
    # Створити QApplication
    app = QApplication(sys.argv)
    
    # Створити MainWindow (з лінійками)
    window = MainWindow()
    window.show()
    
    print("[INFO] GUI opened with rulers")
    print("[INFO] Check:")
    print("  [+] Horizontal ruler at the top")
    print("  [+] Vertical ruler at the left")
    print("  [+] Ticks every 1mm (small) and 5mm (large)")
    print("  [+] Labels: 0, 5, 10, 15, 20, 25")
    print("  [+] Canvas with grid below/right of rulers")
    print("")
    print("[INFO] Add text element to verify alignment")
    print("[INFO] Close window to exit test")
    print("")
    
    # Додати тестовий елемент для перевірки позиціонування
    window._add_text()
    
    # Запустити event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
