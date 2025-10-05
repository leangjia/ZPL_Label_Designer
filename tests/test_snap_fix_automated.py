# -*- coding: utf-8 -*-
"""Автотест для проверки snap to grid после исправления"""

import sys
from pathlib import Path

# Добавить корень проекта в sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from gui.main_window import MainWindow


def test_snap_fix():
    """Проверка что snap работает в ItemPositionHasChanged"""
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
    
    # 1. Переместить на "неровную" позицию
    # Сетка 2mm, переместим на 8.5mm (между 8mm и 10mm)
    target_x_mm = 8.5
    target_y_mm = 8.5
    
    # Конвертировать в пиксели
    target_x_px = item._mm_to_px(target_x_mm)
    target_y_px = item._mm_to_px(target_y_mm)
    
    # Установить позицию (симуляция перетаскивания)
    item.setPos(QPointF(target_x_px, target_y_px))
    
    # Принудительно обновить
    app.processEvents()
    
    # 2. Проверить что позиция снеплена
    final_x = item.element.config.x
    final_y = item.element.config.y
    
    # Ожидаем snap к 8.0mm или 10.0mm (ближайшая grid line)
    # 8.5mm ближе к 8.0mm (расстояние 0.5mm)
    expected_x = 8.0
    expected_y = 8.0
    
    # Проверка с tolerance 0.01mm
    tolerance = 0.01
    
    success = True
    
    if abs(final_x - expected_x) > tolerance:
        print(f"[FAIL] X position: expected {expected_x}mm, got {final_x}mm")
        success = False
    else:
        print(f"[OK] X position: {final_x}mm (expected {expected_x}mm)")
    
    if abs(final_y - expected_y) > tolerance:
        print(f"[FAIL] Y position: expected {expected_y}mm, got {final_y}mm")
        success = False
    else:
        print(f"[OK] Y position: {final_y}mm (expected {expected_y}mm)")
    
    # 3. Тест на snap между grid lines
    # Переместим на 11.7mm (должно снепнуть к 12.0mm)
    target_x_mm = 11.7
    target_y_mm = 11.7
    
    target_x_px = item._mm_to_px(target_x_mm)
    target_y_px = item._mm_to_px(target_y_mm)
    
    item.setPos(QPointF(target_x_px, target_y_px))
    app.processEvents()
    
    final_x = item.element.config.x
    final_y = item.element.config.y
    
    expected_x = 12.0
    expected_y = 12.0
    
    if abs(final_x - expected_x) > tolerance:
        print(f"[FAIL] X position (test 2): expected {expected_x}mm, got {final_x}mm")
        success = False
    else:
        print(f"[OK] X position (test 2): {final_x}mm (expected {expected_x}mm)")
    
    if abs(final_y - expected_y) > tolerance:
        print(f"[FAIL] Y position (test 2): expected {expected_y}mm, got {final_y}mm")
        success = False
    else:
        print(f"[OK] Y position (test 2): {final_y}mm (expected {expected_y}mm)")
    
    # Результат
    if success:
        print("\n" + "="*60)
        print("[SUCCESS] ALL SNAP TESTS PASSED")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("[FAILURE] SNAP TESTS FAILED")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(test_snap_fix())
