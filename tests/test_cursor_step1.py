# -*- coding: utf-8 -*-
"""Тест КРОК 1.1: Перевірка сигналу cursor_position_changed"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from gui.canvas_view import CanvasView

def test_cursor_signal():
    app = QApplication(sys.argv)
    canvas = CanvasView(width_mm=28, height_mm=28, dpi=203)
    
    # Прапорець для перевірки
    signal_received = {'x': None, 'y': None}
    
    def on_cursor_move(x, y):
        signal_received['x'] = x
        signal_received['y'] = y
        print(f"[OK] Signal received: X={x:.2f}mm, Y={y:.2f}mm")
    
    # Підключити сигнал
    canvas.cursor_position_changed.connect(on_cursor_move)
    
    canvas.show()
    
    print("[TEST] КРОК 1.1 - Cursor Signal")
    print("1. Рухай мишею по canvas")
    print("2. Має з'явитися вивід: [OK] Signal received...")
    print("3. Закрий вікно якщо все ОК")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_cursor_signal()
