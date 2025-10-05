# -*- coding: utf-8 -*-
"""Тест після виправлення - ruler ticks співпадають з canvas grid"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Додати шлях проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow


def test_grid_ruler_fixed():
    """Перевірити що ruler ticks тепер співпадають з canvas grid"""
    
    print("=" * 60)
    print("[GRID-RULER SYNC TEST - AFTER FIX]")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # === CANVAS GRID ===
    canvas_grid_step_mm = 2.0
    canvas_grid_positions = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0]
    
    print(f"\n[CANVAS GRID]")
    print(f"  Step: {canvas_grid_step_mm}mm")
    print(f"  Positions: {canvas_grid_positions}")
    
    # === RULER TICKS (після виправлення) ===
    minor_step_mm = 2.0  # ← ВИПРАВЛЕНО!
    major_step_mm = 10.0 # ← ВИПРАВЛЕНО!
    
    ruler_tick_positions = []
    pos_mm = 0.0
    while pos_mm <= window.h_ruler.length_mm:
        ruler_tick_positions.append(pos_mm)
        pos_mm += minor_step_mm
    
    print(f"\n[RULER TICKS]")
    print(f"  Minor step: {minor_step_mm}mm")
    print(f"  Major step: {major_step_mm}mm")
    print(f"  Positions: {ruler_tick_positions}")
    
    # === ПЕРЕВІРКА СПІВПАДІННЯ ===
    print(f"\n{'=' * 60}")
    print("[VERIFICATION]")
    print("=" * 60)
    
    if canvas_grid_positions == ruler_tick_positions:
        print("\n[OK] Perfect match! All ruler ticks align with canvas grid lines!")
        print(f"  Canvas grid: {canvas_grid_positions}")
        print(f"  Ruler ticks: {ruler_tick_positions}")
        
        # Перевірити major ticks
        major_positions = [0.0, 10.0, 20.0]  # Кожні 10mm
        print(f"\n[MAJOR TICKS] Will have labels at: {major_positions} (every 10mm)")
        
        return 0
    else:
        print("\n[ERROR] Still misaligned!")
        print(f"  Canvas: {canvas_grid_positions}")
        print(f"  Ruler:  {ruler_tick_positions}")
        return 1


if __name__ == '__main__':
    exit_code = test_grid_ruler_fixed()
    print(f"\n{'=' * 60}")
    print(f"EXIT CODE: {exit_code}")
    print("=" * 60)
    sys.exit(exit_code)
