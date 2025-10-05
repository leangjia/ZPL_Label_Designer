# -*- coding: utf-8 -*-
"""Фінальний тест - canvas grid lines ТОЧНО співпадають з ruler ticks"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Додати шлях проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow


def test_perfect_grid_ruler_alignment():
    """ФІНАЛЬНИЙ ТЕСТ: canvas grid та ruler ticks на ОДНАКОВИХ позиціях"""
    
    print("=" * 60)
    print("[PERFECT GRID-RULER ALIGNMENT TEST]")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # === CANVAS GRID SCENE POSITIONS ===
    print("\n[CANVAS GRID - SCENE COORDINATES]")
    
    grid_step_mm = 2.0
    canvas_grid_scene_px = []
    
    mm = 0.0
    while mm <= window.canvas.width_mm:
        scene_px = round(window.canvas._mm_to_px(mm))
        canvas_grid_scene_px.append(scene_px)
        mm += grid_step_mm
    
    print(f"  Grid step: {grid_step_mm}mm")
    print(f"  Scene positions (px): {canvas_grid_scene_px}")
    
    # Конвертувати в viewport (після scale 2.5x)
    canvas_grid_viewport_px = []
    for scene_px in canvas_grid_scene_px:
        viewport_pos = window.canvas.mapFromScene(scene_px, 0)
        canvas_grid_viewport_px.append(viewport_pos.x())
    
    print(f"  Viewport positions (px): {canvas_grid_viewport_px}")
    
    # === RULER TICKS POSITIONS ===
    print("\n[RULER TICKS]")
    
    ruler_tick_viewport_px = []
    
    mm = 0.0
    while mm <= window.h_ruler.length_mm:
        tick_px = round(window.h_ruler._mm_to_px(mm) * window.h_ruler.scale_factor)
        ruler_tick_viewport_px.append(tick_px)
        mm += grid_step_mm
    
    print(f"  Tick step: {grid_step_mm}mm")
    print(f"  Viewport positions (px): {ruler_tick_viewport_px}")
    
    # === ПОРІВНЯННЯ ===
    print("\n" + "=" * 60)
    print("[COMPARISON]")
    print("=" * 60)
    
    if len(canvas_grid_viewport_px) != len(ruler_tick_viewport_px):
        print(f"\n[ERROR] Different number of positions!")
        print(f"  Canvas: {len(canvas_grid_viewport_px)}")
        print(f"  Ruler: {len(ruler_tick_viewport_px)}")
        return 1
    
    # Порівняти кожну позицію
    mismatches = []
    for i, (canvas_px, ruler_px) in enumerate(zip(canvas_grid_viewport_px, ruler_tick_viewport_px)):
        mm_value = i * grid_step_mm
        diff = abs(canvas_px - ruler_px)
        
        if diff > 1:  # 1px tolerance
            mismatches.append({
                'mm': mm_value,
                'canvas': canvas_px,
                'ruler': ruler_px,
                'diff': diff
            })
    
    if mismatches:
        print(f"\n[ERROR] {len(mismatches)} MISMATCHES FOUND:")
        for m in mismatches:
            print(f"  {m['mm']:.0f}mm: Canvas={m['canvas']}px, Ruler={m['ruler']}px, Diff={m['diff']}px")
        return 1
    
    # === SUCCESS ===
    print("\n[SUCCESS] PERFECT ALIGNMENT!")
    print(f"  Tested {len(canvas_grid_viewport_px)} positions")
    print(f"  All canvas grid lines match ruler ticks exactly (≤1px)")
    
    # Показати кілька прикладів
    print("\n[EXAMPLES]")
    for i in [0, 5, 10, 14]:  # 0mm, 10mm, 20mm, 28mm
        if i < len(canvas_grid_viewport_px):
            mm_val = i * grid_step_mm
            canvas_px = canvas_grid_viewport_px[i]
            ruler_px = ruler_tick_viewport_px[i]
            print(f"  {mm_val:.0f}mm: Canvas={canvas_px}px, Ruler={ruler_px}px ✓")
    
    return 0


if __name__ == '__main__':
    exit_code = test_perfect_grid_ruler_alignment()
    print(f"\n{'=' * 60}")
    print(f"EXIT CODE: {exit_code}")
    print("=" * 60)
    sys.exit(exit_code)
