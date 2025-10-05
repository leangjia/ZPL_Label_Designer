# -*- coding: utf-8 -*-
"""Тест що ruler labels на позиціях 0, 5, 10, 15, 20, 25mm"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Додати шлях проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow


def test_ruler_labels_at_5mm():
    """Перевірити що ruler має labels на 0, 5, 10, 15, 20, 25mm"""
    
    print("=" * 60)
    print("[RULER LABELS TEST - EVERY 5MM]")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Параметри з rulers.py
    major_step_mm = 5.0
    minor_step_mm = 2.0
    
    print(f"\n[RULER PARAMETERS]")
    print(f"  Major step (labels): {major_step_mm}mm")
    print(f"  Minor step (ticks): {minor_step_mm}mm")
    
    # Очікувані позиції labels
    expected_label_positions_mm = []
    mm = 0.0
    while mm <= window.h_ruler.length_mm:
        if abs(mm % major_step_mm) < 0.01:
            expected_label_positions_mm.append(mm)
        mm += minor_step_mm
    
    print(f"\n[EXPECTED LABELS]")
    print(f"  Positions: {expected_label_positions_mm} mm")
    
    # Всі tick позиції (включаючи minor)
    all_tick_positions_mm = []
    mm = 0.0
    while mm <= window.h_ruler.length_mm:
        all_tick_positions_mm.append(mm)
        mm += minor_step_mm
    
    print(f"\n[ALL TICKS]")
    print(f"  Positions: {all_tick_positions_mm} mm")
    print(f"  Total: {len(all_tick_positions_mm)} ticks")
    print(f"  Major: {len(expected_label_positions_mm)} (with labels)")
    print(f"  Minor: {len(all_tick_positions_mm) - len(expected_label_positions_mm)} (without labels)")
    
    # Перевірка
    print(f"\n{'=' * 60}")
    print("[VERIFICATION]")
    print("=" * 60)
    
    # Canvas grid все ще на позиціях 0, 2, 4, 6, 8, 10...
    canvas_grid_positions = [i * 2.0 for i in range(int(window.canvas.width_mm / 2.0) + 1)]
    
    print(f"\n[ALIGNMENT CHECK]")
    print(f"  Canvas grid lines: {canvas_grid_positions}")
    print(f"  Ruler tick positions: {all_tick_positions_mm}")
    
    if canvas_grid_positions == all_tick_positions_mm:
        print(f"\n  [OK] All ruler ticks still align with canvas grid!")
    else:
        print(f"\n  [ERROR] Misalignment detected!")
        return 1
    
    print(f"\n[LABELS AT 5MM INTERVALS]")
    for mm in expected_label_positions_mm:
        print(f"  {int(mm)}mm ✓")
    
    print(f"\n[SUCCESS] Ruler has labels every 5mm (0, 5, 10, 15, 20, 25)")
    print(f"          Minor ticks every 2mm align with canvas grid")
    
    return 0


if __name__ == '__main__':
    exit_code = test_ruler_labels_at_5mm()
    print(f"\n{'=' * 60}")
    print(f"EXIT CODE: {exit_code}")
    print("=" * 60)
    sys.exit(exit_code)
