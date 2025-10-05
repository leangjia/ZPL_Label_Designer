# -*- coding: utf-8 -*-
"""Test для діагностики ruler alignment"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import QEvent

# Додати шлях проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow
from utils.logger import logger


def test_ruler_alignment():
    """Тест alignment лінійок з canvas"""
    
    print("=" * 60)
    print("[RULER ALIGNMENT TEST]")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # === КРОК 1: Перевірити canvas scene rect ===
    scene_rect = window.canvas.scene.sceneRect()
    print(f"\n[CANVAS] Scene rect: ({scene_rect.x():.1f}, {scene_rect.y():.1f}, {scene_rect.width():.1f}, {scene_rect.height():.1f})")
    print(f"[CANVAS] Width: {window.canvas.width_mm}mm = {window.canvas.width_px}px")
    print(f"[CANVAS] Height: {window.canvas.height_mm}mm = {window.canvas.height_px}px")
    print(f"[CANVAS] Scale: {window.canvas.current_scale}x")
    
    # === КРОК 2: Перевірити viewport transform ===
    viewport_rect = window.canvas.viewport().rect()
    print(f"\n[VIEWPORT] Rect: ({viewport_rect.x()}, {viewport_rect.y()}, {viewport_rect.width()}, {viewport_rect.height()})")
    
    # Перевірити mapToScene для лівого верхнього кута
    top_left_viewport = QPointF(0, 0)
    top_left_scene = window.canvas.mapToScene(top_left_viewport.toPoint())
    print(f"[VIEWPORT->SCENE] (0, 0) viewport -> ({top_left_scene.x():.2f}, {top_left_scene.y():.2f}) scene")
    
    # === КРОК 3: Перевірити rulers parameters ===
    print(f"\n[H-RULER] Length: {window.h_ruler.length_mm}mm = {window.h_ruler.length_px}px")
    print(f"[H-RULER] Scale factor: {window.h_ruler.scale_factor}x")
    print(f"[V-RULER] Length: {window.v_ruler.length_mm}mm = {window.v_ruler.length_px}px")
    print(f"[V-RULER] Scale factor: {window.v_ruler.scale_factor}x")
    
    # === КРОК 4: Тест: Додати текст на (10, 10)mm ===
    print("\n" + "=" * 60)
    print("[TEST] Add text at (10, 10)mm")
    print("=" * 60)
    
    window._add_text()
    app.processEvents()
    
    # Отримати створений елемент з lists
    if window.elements and window.graphics_items:
        element = window.elements[-1]  # Останній доданий
        graphics_item = window.graphics_items[-1]
        
        # Встановити позицію (10, 10)mm
        element.config.x = 10.0
        element.config.y = 10.0
        
        # Оновити graphics item
        scene_x_px = window.canvas._mm_to_px(10.0)
        scene_y_px = window.canvas._mm_to_px(10.0)
        graphics_item.setPos(scene_x_px, scene_y_px)
        
        print(f"\n[ELEMENT] Position: ({element.config.x}, {element.config.y})mm")
        print(f"[ELEMENT] Scene position: ({scene_x_px}, {scene_y_px})px")
        
        # Отримати позицію в viewport координатах
        viewport_pos = window.canvas.mapFromScene(QPointF(scene_x_px, scene_y_px))
        print(f"[ELEMENT] Viewport position: ({viewport_pos.x()}, {viewport_pos.y()})px")
        
        # === КРОК 5: Перевірити що ruler показує 10mm на тій же позиції ===
        # Ruler для 10mm повинен малювати tick на позиції:
        ruler_10mm_px = int(window.h_ruler._mm_to_px(10.0) * window.h_ruler.scale_factor)
        print(f"\n[RULER] 10mm should be drawn at: {ruler_10mm_px}px")
        print(f"[RULER] Element viewport X: {viewport_pos.x()}px")
        
        diff = abs(ruler_10mm_px - viewport_pos.x())
        print(f"[RULER] Difference: {diff}px")
        
        if diff <= 2:  # 2px tolerance
            print("\n[OK] Ruler aligned with element!")
            return 0
        else:
            print(f"\n[ERROR] Ruler NOT aligned! Difference: {diff}px")
            print("[DIAGNOSIS] Possible causes:")
            print("  1. Canvas has scroll offset despite ScrollBarAlwaysOff")
            print("  2. Transform matrix is not identity after scale")
            print("  3. Ruler calculation doesn't match canvas viewport mapping")
            return 1
    
    else:
        print("\n[ERROR] No element created")
        return 1


if __name__ == '__main__':
    exit_code = test_ruler_alignment()
    print(f"\n{'=' * 60}")
    print(f"EXIT CODE: {exit_code}")
    print("=" * 60)
    sys.exit(exit_code)
