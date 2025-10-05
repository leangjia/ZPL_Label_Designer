# -*- coding: utf-8 -*-
"""Тест ЕТАП 3: Snap to Grid повна інтеграція"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def test_snap_to_grid():
    """Тест повної інтеграції snap to grid"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    print("="*60)
    print("[TEST] ЕТАП 3 - SNAP TO GRID (ПОВНА ІНТЕГРАЦІЯ)")
    print("="*60)
    
    print("\n[ІНСТРУКЦІЇ]:")
    print("1. Додай текстовий елемент (Add Text)")
    print("2. Перетягни елемент близько до grid line (наприклад, 5мм)")
    print("   [ПЕРЕВІРКА] Елемент автоматично 'прилипає' до найближчої grid лінії")
    print("")
    print("3. Спробуй перетягти БЕЗ snap:")
    print("   [ПЕРЕВІРКА] Checkbox 'Snap to Grid' - зняти галочку")
    print("   [ПЕРЕВІРКА] Елемент рухається плавно БЕЗ прив'язки")
    print("")
    print("4. Натисни Ctrl+G")
    print("   [ПЕРЕВІРКА] Snap увімкнувся/вимкнувся")
    print("")
    print("5. Додай barcode (EAN-13)")
    print("   [ПЕРЕВІРКА] Barcode також має snap до grid")
    print("")
    print("6. Параметри:")
    print("   Grid step = 2mm, threshold = 0.5mm")
    print("   [ПЕРЕВІРКА] Snap спрацьовує якщо елемент <0.5мм від grid лінії")
    print("")
    print("="*60)
    print("[КРИТЕРІЙ УСПІХУ]: ВСІ 6 пунктів працюють = [OK]")
    print("="*60)
    print("\n[INFO] Закрий вікно після завершення тестування")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_snap_to_grid()
