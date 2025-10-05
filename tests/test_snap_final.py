# -*- coding: utf-8 -*-
"""Финальный тест snap to grid с threshold=1.0"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from gui.main_window import MainWindow


def test_snap_final():
    """Финальный тест snap с правильным threshold"""
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    window.snap_enabled = True
    window._add_text()
    item = window.graphics_items[0]
    item.snap_enabled = True
    
    # Выбрать для PropertyPanel
    window.canvas.scene.clearSelection()
    item.setSelected(True)
    app.processEvents()
    
    tests = [
        # (target_x, target_y, expected_x, expected_y, description)
        (6.6, 2.0, 6.0, 2.0, "6.6mm -> 6.0mm (0.6mm от 6.0)"),
        (6.5, 2.0, 6.0, 2.0, "6.5mm -> 6.0mm (0.5mm от 6.0)"),
        (6.9, 2.0, 6.0, 2.0, "6.9mm -> 6.0mm (0.9mm от 6.0, в пределах threshold 1.0)"),
        (7.0, 2.0, 8.0, 2.0, "7.0mm -> 8.0mm (ровно посередине, round() округляет к 8.0)"),
        (7.1, 2.0, 8.0, 2.0, "7.1mm -> 8.0mm (0.9mm от 8.0)"),
        (8.5, 4.5, 8.0, 4.0, "8.5mm/4.5mm -> 8.0mm/4.0mm"),
        (11.2, 11.8, 12.0, 12.0, "11.2/11.8mm -> 12.0mm"),
    ]
    
    success = True
    tolerance = 0.01
    
    for target_x, target_y, expected_x, expected_y, desc in tests:
        # Установить позицию
        target_x_px = item._mm_to_px(target_x)
        target_y_px = item._mm_to_px(target_y)
        item.setPos(QPointF(target_x_px, target_y_px))
        app.processEvents()
        
        # Проверить результат
        actual_x = item.element.config.x
        actual_y = item.element.config.y
        panel_x = window.property_panel.x_input.value()
        panel_y = window.property_panel.y_input.value()
        
        x_ok = abs(actual_x - expected_x) < tolerance
        y_ok = abs(actual_y - expected_y) < tolerance
        panel_x_ok = abs(panel_x - expected_x) < tolerance
        panel_y_ok = abs(panel_y - expected_y) < tolerance
        
        if x_ok and y_ok and panel_x_ok and panel_y_ok:
            print(f"[OK] {desc}")
            print(f"     Element: ({actual_x:.1f}, {actual_y:.1f}), Panel: ({panel_x:.1f}, {panel_y:.1f})")
        else:
            print(f"[FAIL] {desc}")
            print(f"       Expected: ({expected_x:.1f}, {expected_y:.1f})")
            print(f"       Element: ({actual_x:.1f}, {actual_y:.1f})")
            print(f"       Panel: ({panel_x:.1f}, {panel_y:.1f})")
            success = False
    
    if success:
        print("\n" + "="*60)
        print("[SUCCESS] ALL SNAP TESTS PASSED WITH THRESHOLD=1.0")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("[FAILURE] SOME TESTS FAILED")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(test_snap_final())
