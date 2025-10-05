# -*- coding: utf-8 -*-
"""Автоматизований тест snap to grid"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF, Qt
from PySide6.QtTest import QTest
from gui.main_window import MainWindow

def test_snap_to_grid_automated():
    """Автоматизований тест snap функціоналу"""
    app = QApplication.instance() or QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    print("[TEST] Automated Snap to Grid Test")
    print("="*60)
    
    # ШАГ 1: Додати текстовий елемент
    print("\n[STEP 1] Adding text element...")
    window._add_text()
    assert len(window.graphics_items) == 1, "Element not added"
    item = window.graphics_items[0]
    print(f"[OK] Element added at ({item.pos().x():.1f}, {item.pos().y():.1f})")
    
    # ШАГ 2: Перевірити початковий snap_enabled
    print("\n[STEP 2] Checking snap enabled...")
    assert window.snap_enabled == True, "Snap should be ON by default"
    assert item.snap_enabled == True, "Item snap should be ON"
    print(f"[OK] Snap enabled: window={window.snap_enabled}, item={item.snap_enabled}")
    
    # ШАГ 3: Симулювати drag до позиції яка має snap
    print("\n[STEP 3] Simulating drag to snap position...")
    # Початкова позиція
    start_x = item.pos().x()
    start_y = item.pos().y()
    print(f"[INFO] Start position: ({start_x:.1f}, {start_y:.1f})")
    
    # Переміщення до позиції 8.3mm (має snap до 8.0mm)
    target_x_mm = 8.3
    target_y_mm = 4.7
    target_x_px = int(target_x_mm * 203 / 25.4)  # DPI 203
    target_y_px = int(target_y_mm * 203 / 25.4)
    
    print(f"[INFO] Target position: {target_x_mm}mm, {target_y_mm}mm = ({target_x_px}px, {target_y_px}px)")
    
    # Встановити позицію (викликає itemChange з snap)
    item.setPos(QPointF(target_x_px, target_y_px))
    
    # Отримати фактичну позицію після snap
    actual_x_px = item.pos().x()
    actual_y_px = item.pos().y()
    actual_x_mm = actual_x_px * 25.4 / 203
    actual_y_mm = actual_y_px * 25.4 / 203
    
    print(f"[INFO] Actual position after snap: {actual_x_mm:.1f}mm, {actual_y_mm:.1f}mm")
    
    # ШАГ 4: Перевірити що snap спрацював
    print("\n[STEP 4] Verifying snap result...")
    
    # Очікувана позиція після snap
    expected_x_mm = 8.0  # snap до 8mm
    expected_y_mm = 5.0  # snap до 5mm (якщо 4.7 -> 5.0)
    
    # Перевірка з tolerance 0.1mm
    tolerance = 0.1
    x_snapped = abs(actual_x_mm - expected_x_mm) < tolerance
    y_snapped = abs(actual_y_mm - expected_y_mm) < tolerance
    
    if x_snapped and y_snapped:
        print(f"[OK] SNAP WORKS! Position snapped to grid: ({actual_x_mm:.1f}, {actual_y_mm:.1f})")
    else:
        print(f"[ERROR] SNAP FAILED!")
        print(f"  Expected: ({expected_x_mm}, {expected_y_mm})")
        print(f"  Actual: ({actual_x_mm:.1f}, {actual_y_mm:.1f})")
    
    # ШАГ 5: Вимкнути snap та перевірити
    print("\n[STEP 5] Testing snap toggle OFF...")
    window._toggle_snap(0)  # 0 = unchecked
    assert window.snap_enabled == False, "Snap should be OFF"
    assert item.snap_enabled == False, "Item snap should be OFF"
    print(f"[OK] Snap disabled: window={window.snap_enabled}, item={item.snap_enabled}")
    
    # Переміщення без snap
    target_x_mm = 7.3
    target_y_mm = 3.8
    target_x_px = int(target_x_mm * 203 / 25.4)
    target_y_px = int(target_y_mm * 203 / 25.4)
    
    item.setPos(QPointF(target_x_px, target_y_px))
    
    actual_x_mm = item.pos().x() * 25.4 / 203
    actual_y_mm = item.pos().y() * 25.4 / 203
    
    print(f"[INFO] Position without snap: ({actual_x_mm:.1f}, {actual_y_mm:.1f})")
    
    # Має бути близько до target (НЕ snap)
    no_snap = abs(actual_x_mm - target_x_mm) < tolerance and abs(actual_y_mm - target_y_mm) < tolerance
    if no_snap:
        print(f"[OK] NO SNAP works correctly")
    else:
        print(f"[WARNING] Position unexpected: ({actual_x_mm:.1f}, {actual_y_mm:.1f})")
    
    # РЕЗУЛЬТАТ
    print("\n" + "="*60)
    if x_snapped and y_snapped and no_snap:
        print("[SUCCESS] ALL TESTS PASSED")
        return 0
    else:
        print("[FAILURE] SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    result = test_snap_to_grid_automated()
    sys.exit(result)
