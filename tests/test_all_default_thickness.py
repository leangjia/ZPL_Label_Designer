# -*- coding: utf-8 -*-
"""Інтеграційний тест: Rectangle, Circle, Line всі мають 1 мм"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow

def test_all_elements_default_thickness():
    """Інтеграційний тест: Rectangle, Circle, Line всі мають 1 мм"""
    
    print("=" * 60)
    print("[MASTER TEST] ALL ELEMENTS DEFAULT THICKNESS")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    results = []
    
    # Тест 1: Rectangle
    window._add_rectangle()
    app.processEvents()
    rect_element = window.elements[-1]
    rect_thickness = rect_element.config.border_thickness
    print(f"[1] Rectangle border_thickness: {rect_thickness} mm")
    results.append(("Rectangle", rect_thickness, 1))
    
    # Тест 2: Circle
    window._add_circle()
    app.processEvents()
    circle_element = window.elements[-1]
    circle_thickness = circle_element.config.border_thickness
    print(f"[2] Circle border_thickness: {circle_thickness} mm")
    results.append(("Circle", circle_thickness, 1))
    
    # Тест 3: Line
    window._add_line()
    app.processEvents()
    line_element = window.elements[-1]
    line_thickness = line_element.config.thickness
    print(f"[3] Line thickness: {line_thickness} mm")
    results.append(("Line", line_thickness, 1))
    
    # Перевірка результатів
    print("\n" + "=" * 60)
    all_passed = True
    for name, actual, expected in results:
        if actual == expected:
            print(f"[OK] {name}: {actual} mm")
        else:
            print(f"[FAIL] {name}: Expected {expected} mm, Got {actual} mm")
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("[SUCCESS] ALL ELEMENTS HAVE CORRECT THICKNESS: 1 mm")
        return 0
    else:
        print("[FAILURE] Some elements have incorrect thickness")
        return 1

if __name__ == '__main__':
    sys.exit(test_all_elements_default_thickness())
