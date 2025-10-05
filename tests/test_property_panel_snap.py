# -*- coding: utf-8 -*-
"""Автотест для проверки PropertyPanel и snap после исправлений"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from gui.main_window import MainWindow


def test_property_panel_snap():
    """Проверка что PropertyPanel показывает снепленные значения"""
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Включить snap
    window.snap_enabled = True
    
    # Добавить текстовый элемент
    window._add_text()
    item = window.graphics_items[0]
    
    # Убедиться что snap включен
    item.snap_enabled = True
    
    # Выбрать элемент для PropertyPanel
    window.canvas.scene.clearSelection()
    item.setSelected(True)
    
    # PropertyPanel должен обновиться
    app.processEvents()
    
    # 1. Переместить на "неровную" позицию 8.5mm
    target_x_mm = 8.5
    target_y_mm = 8.5
    
    target_x_px = item._mm_to_px(target_x_mm)
    target_y_px = item._mm_to_px(target_y_mm)
    
    item.setPos(QPointF(target_x_px, target_y_px))
    app.processEvents()
    
    # 2. Проверить element.config
    element_x = item.element.config.x
    element_y = item.element.config.y
    
    print(f"Element config: X={element_x:.2f}mm, Y={element_y:.2f}mm")
    
    # 3. Проверить PropertyPanel
    panel_x = window.property_panel.x_input.value()
    panel_y = window.property_panel.y_input.value()
    
    print(f"PropertyPanel: X={panel_x:.1f}mm, Y={panel_y:.1f}mm")
    
    # 4. Ожидаем snap к 8.0mm
    expected = 8.0
    tolerance = 0.01
    
    success = True
    
    if abs(element_x - expected) > tolerance:
        print(f"[FAIL] Element X: expected {expected}mm, got {element_x}mm")
        success = False
    else:
        print(f"[OK] Element X: {element_x}mm")
    
    if abs(element_y - expected) > tolerance:
        print(f"[FAIL] Element Y: expected {expected}mm, got {element_y}mm")
        success = False
    else:
        print(f"[OK] Element Y: {element_y}mm")
    
    if abs(panel_x - expected) > tolerance:
        print(f"[FAIL] PropertyPanel X: expected {expected}mm, got {panel_x}mm")
        success = False
    else:
        print(f"[OK] PropertyPanel X: {panel_x}mm")
    
    if abs(panel_y - expected) > tolerance:
        print(f"[FAIL] PropertyPanel Y: expected {expected}mm, got {panel_y}mm")
        success = False
    else:
        print(f"[OK] PropertyPanel Y: {panel_y}mm")
    
    if success:
        print("\n" + "="*60)
        print("[SUCCESS] PROPERTY PANEL + SNAP TESTS PASSED")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("[FAILURE] TESTS FAILED")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(test_property_panel_snap())
