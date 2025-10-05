# -*- coding: utf-8 -*-
"""Тест КРОК 1.2: Перевірка cursor marker на rulers"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from gui.rulers import HorizontalRuler, VerticalRuler

def test_ruler_marker():
    app = QApplication(sys.argv)
    
    widget = QWidget()
    layout = QVBoxLayout()
    
    h_ruler = HorizontalRuler(length_mm=28, dpi=203, scale=2.5)
    v_ruler = VerticalRuler(length_mm=28, dpi=203, scale=2.5)
    
    layout.addWidget(h_ruler)
    layout.addWidget(v_ruler)
    widget.setLayout(layout)
    widget.resize(800, 200)
    widget.show()
    
    # Симулювати cursor на 15мм
    h_ruler.update_cursor_position(15.0)
    v_ruler.update_cursor_position(15.0)
    
    print("[TEST] КРОК 1.2 - Ruler Cursor Marker")
    print("[+] Horizontal ruler - червона лінія на 15мм")
    print("[+] Vertical ruler - червона лінія на 15мм")
    print("[INFO] Якщо бачиш ЧЕРВОНІ лінії - тест ОК")
    print("[INFO] Закрий вікно для завершення")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_ruler_marker()
