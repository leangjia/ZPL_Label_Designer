# -*- coding: utf-8 -*-
"""Тест синхронізації grid canvas з ruler ticks"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Додати шлях проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow


def test_grid_ruler_sync():
    """Перевірити що ruler ticks співпадають з canvas grid"""
    
    print("=" * 60)
    print("[GRID-RULER SYNC TEST]")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # === CANVAS GRID ===
    print("\n[CANVAS GRID]")
    canvas_grid_step_mm = 2.0  # З canvas_view.py
    print(f"  Grid step: {canvas_grid_step_mm}mm")
    
    # Де canvas малює grid lines
    canvas_grid_positions_mm = []
    for i in range(0, int(window.canvas.width_mm) + 1, int(canvas_grid_step_mm)):
        canvas_grid_positions_mm.append(float(i))
    
    print(f"  Grid lines at: {canvas_grid_positions_mm} mm")
    
    # Конвертувати в viewport px
    canvas_grid_positions_px = []
    for mm in canvas_grid_positions_mm:
        scene_px = window.canvas._mm_to_px(mm)
        viewport_px = window.canvas.mapFromScene(scene_px, 0).x()
        canvas_grid_positions_px.append(viewport_px)
    
    print(f"  Grid lines in viewport: {canvas_grid_positions_px[:8]} px... (first 8)")
    
    # === RULER TICKS ===
    print("\n[RULER TICKS]")
    
    # З rulers.py - minor_step_mm залежить від units
    # Для MM: major_step_mm = 5.0, minor_step_mm = 1.0
    major_step_mm = 5.0
    minor_step_mm = 1.0
    
    print(f"  Major tick step: {major_step_mm}mm")
    print(f"  Minor tick step: {minor_step_mm}mm")
    
    # Де ruler малює ticks
    ruler_tick_positions_mm = []
    pos_mm = 0.0
    while pos_mm <= window.h_ruler.length_mm:
        ruler_tick_positions_mm.append(pos_mm)
        pos_mm += minor_step_mm
    
    print(f"  Tick positions: {ruler_tick_positions_mm[:15]} mm... (first 15)")
    
    # Конвертувати в px
    ruler_tick_positions_px = []
    for mm in ruler_tick_positions_mm:
        px = round(window.h_ruler._mm_to_px(mm) * window.h_ruler.scale_factor)
        ruler_tick_positions_px.append(px)
    
    print(f"  Tick positions in px: {ruler_tick_positions_px[:15]} px... (first 15)")
    
    # === ПОРІВНЯННЯ ===
    print("\n" + "=" * 60)
    print("[COMPARISON]")
    print("=" * 60)
    
    print(f"\n[ISSUE] Canvas grid: {canvas_grid_step_mm}mm != Ruler minor ticks: {minor_step_mm}mm")
    print(f"[EXPECTED] Canvas grid positions (every 2mm): {canvas_grid_positions_mm}")
    print(f"[ACTUAL] Ruler tick positions (every 1mm): {ruler_tick_positions_mm[:15]}...")
    
    # Знайти які ruler ticks співпадають з canvas grid
    matching_ticks = []
    for grid_mm in canvas_grid_positions_mm:
        if grid_mm in ruler_tick_positions_mm:
            matching_ticks.append(grid_mm)
    
    print(f"\n[MATCHING POSITIONS] {matching_ticks}")
    print(f"[MISMATCH] Ruler has ticks at odd mm (1, 3, 7, 9...) that don't match canvas grid")
    
    # === РІШЕННЯ ===
    print("\n" + "=" * 60)
    print("[SOLUTION]")
    print("=" * 60)
    
    print("Change ruler minor_step_mm from 1.0mm to 2.0mm to match canvas grid")
    print("  - Minor ticks: every 2mm (matching canvas grid)")
    print("  - Major ticks: every 10mm (every 5th grid line)")
    print("This will make ruler ticks align perfectly with canvas grid lines")
    
    return 1  # Fail - потрібні зміни


if __name__ == '__main__':
    exit_code = test_grid_ruler_sync()
    print(f"\n{'=' * 60}")
    print(f"EXIT CODE: {exit_code}")
    print("=" * 60)
    sys.exit(exit_code)
