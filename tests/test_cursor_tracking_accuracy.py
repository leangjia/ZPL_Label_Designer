# -*- coding: utf-8 -*-
"""Тест cursor tracking після alignment змін"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import QEvent, Qt

# Додати шлях проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow


def test_cursor_tracking():
    """Тест cursor tracking coordinates"""
    
    print("=" * 60)
    print("[CURSOR TRACKING TEST]")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # === КРОК 1: Перевірити viewport->scene mapping ===
    print("\n[VIEWPORT->SCENE MAPPING]")
    
    test_points = [
        (0, 0, "Top-left corner"),
        (100, 100, "100px from corner"),
        (200, 200, "200px from corner (should be ~10mm)"),
    ]
    
    for vp_x, vp_y, label in test_points:
        viewport_pos = QPointF(vp_x, vp_y)
        scene_pos = window.canvas.mapToScene(viewport_pos.toPoint())
        
        # Конвертувати scene px -> mm
        mm_x = window.canvas._px_to_mm(scene_pos.x())
        mm_y = window.canvas._px_to_mm(scene_pos.y())
        
        print(f"\n[{label}]")
        print(f"  Viewport: ({vp_x}, {vp_y})px")
        print(f"  Scene: ({scene_pos.x():.2f}, {scene_pos.y():.2f})px")
        print(f"  MM: ({mm_x:.2f}, {mm_y:.2f})mm")
        print(f"  Scale: {window.canvas.current_scale}x")
    
    # === КРОК 2: Симулювати mouse move на позиції ~10mm ===
    print("\n" + "=" * 60)
    print("[SIMULATE MOUSE MOVE AT 10mm]")
    print("=" * 60)
    
    # Ruler каже що 10mm має бути на позиції:
    ruler_10mm_px = round(window.h_ruler._mm_to_px(10.0) * window.h_ruler.scale_factor)
    print(f"\n[RULER] 10mm should be at viewport position: {ruler_10mm_px}px")
    
    # Створити mouse event на цій позиції
    event = QMouseEvent(
        QEvent.MouseMove,
        QPointF(ruler_10mm_px, ruler_10mm_px),
        Qt.NoButton,
        Qt.NoButton,
        Qt.NoModifier
    )
    
    # Викликати mouseMoveEvent
    window.canvas.mouseMoveEvent(event)
    app.processEvents()
    
    # Перевірити що відбувається в mouseMoveEvent
    scene_pos = window.canvas.mapToScene(QPointF(ruler_10mm_px, ruler_10mm_px).toPoint())
    mm_x = window.canvas._px_to_mm(scene_pos.x())
    mm_y = window.canvas._px_to_mm(scene_pos.y())
    
    print(f"\n[MOUSE EVENT RESULT]")
    print(f"  Event position: ({ruler_10mm_px}, {ruler_10mm_px})px (viewport)")
    print(f"  mapToScene result: ({scene_pos.x():.2f}, {scene_pos.y():.2f})px (scene)")
    print(f"  _px_to_mm result: ({mm_x:.2f}, {mm_y:.2f})mm")
    
    # Очікуємо ~10mm
    expected = 10.0
    diff_x = abs(mm_x - expected)
    diff_y = abs(mm_y - expected)
    
    print(f"\n[ACCURACY]")
    print(f"  Expected: {expected}mm")
    print(f"  Got: ({mm_x:.2f}, {mm_y:.2f})mm")
    print(f"  Difference: X={diff_x:.2f}mm, Y={diff_y:.2f}mm")
    
    if diff_x < 0.5 and diff_y < 0.5:
        print("\n[OK] Cursor tracking accurate!")
        return 0
    else:
        print(f"\n[ERROR] Cursor tracking INACCURATE!")
        print("[DIAGNOSIS]")
        
        # Перевірити transform
        transform = window.canvas.transform()
        print(f"  Transform: m11={transform.m11():.3f}, m22={transform.m22():.3f}")
        print(f"  Expected scale: {window.canvas.current_scale}x")
        
        # Перевірити чи є offset
        top_left = window.canvas.mapToScene(QPointF(0, 0).toPoint())
        print(f"  Top-left scene position: ({top_left.x():.2f}, {top_left.y():.2f})")
        
        if top_left.x() != 0 or top_left.y() != 0:
            print(f"  [!] Canvas has offset! Should be (0, 0)")
        
        return 1


if __name__ == '__main__':
    exit_code = test_cursor_tracking()
    print(f"\n{'=' * 60}")
    print(f"EXIT CODE: {exit_code}")
    print("=" * 60)
    sys.exit(exit_code)
