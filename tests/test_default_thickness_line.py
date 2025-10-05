# -*- coding: utf-8 -*-
"""Тест: Line має товщину 1 мм при створенні"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow

def test_line_default_thickness():
    """Тест: Line має товщину 1 мм при створенні"""
    
    print("=" * 60)
    print("[TEST] LINE DEFAULT THICKNESS")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Додати line
    window._add_line()
    app.processEvents()
    
    # Перевірити товщину
    if len(window.elements) > 0:
        element = window.elements[-1]
        thickness = element.config.thickness
        
        print(f"[1] Line thickness: {thickness} mm")
        
        if thickness == 1:
            print("\n[OK] Line has correct thickness: 1 mm")
            return 0
        else:
            print(f"\n[FAIL] Expected: 1 mm, Got: {thickness} mm")
            return 1
    else:
        print("\n[FAIL] No elements found")
        return 1

if __name__ == '__main__':
    sys.exit(test_line_default_thickness())
