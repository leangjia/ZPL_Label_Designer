# -*- coding: utf-8 -*-
"""Розширений тест ruler alignment з zoom і resize"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF

# Додати шлях проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow


def check_alignment(window, label=""):
    """Перевірити alignment елемента на (10,10)mm"""
    if not window.elements:
        return None
    
    element = window.elements[-1]
    graphics_item = window.graphics_items[-1]
    
    scene_pos = graphics_item.pos()
    viewport_pos = window.canvas.mapFromScene(scene_pos)
    
    # Ruler position для 10mm
    ruler_10mm_px = int(window.h_ruler._mm_to_px(10.0) * window.h_ruler.scale_factor)
    
    diff_x = abs(ruler_10mm_px - viewport_pos.x())
    diff_y = abs(ruler_10mm_px - viewport_pos.y())
    
    print(f"\n[{label}]")
    print(f"  Element: ({element.config.x:.1f}, {element.config.y:.1f})mm")
    print(f"  Scene: ({scene_pos.x():.1f}, {scene_pos.y():.1f})px")
    print(f"  Viewport: ({viewport_pos.x()}, {viewport_pos.y()})px")
    print(f"  Ruler 10mm at: {ruler_10mm_px}px")
    print(f"  Difference: X={diff_x}px, Y={diff_y}px")
    print(f"  Scale: {window.canvas.current_scale:.2f}x")
    
    return diff_x <= 2 and diff_y <= 2


def test_ruler_alignment_extended():
    """Розширений тест з різними сценаріями"""
    
    print("=" * 60)
    print("[EXTENDED RULER ALIGNMENT TEST]")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Додати елемент на (10, 10)mm
    window._add_text()
    app.processEvents()
    
    element = window.elements[-1]
    graphics_item = window.graphics_items[-1]
    
    element.config.x = 10.0
    element.config.y = 10.0
    scene_x = window.canvas._mm_to_px(10.0)
    scene_y = window.canvas._mm_to_px(10.0)
    graphics_item.setPos(scene_x, scene_y)
    app.processEvents()
    
    results = []
    
    # === ТЕСТ 1: Початковий alignment ===
    ok = check_alignment(window, "TEST 1: Initial (scale 2.5x)")
    results.append(("Initial alignment", ok))
    
    # === ТЕСТ 2: Після Zoom IN ===
    window.canvas.zoom_in()
    app.processEvents()
    ok = check_alignment(window, f"TEST 2: After Zoom IN (scale {window.canvas.current_scale:.2f}x)")
    results.append(("After Zoom IN", ok))
    
    # === ТЕСТ 3: Після Zoom OUT ===
    window.canvas.zoom_out()
    window.canvas.zoom_out()
    app.processEvents()
    ok = check_alignment(window, f"TEST 3: After Zoom OUT (scale {window.canvas.current_scale:.2f}x)")
    results.append(("After Zoom OUT", ok))
    
    # === ТЕСТ 4: Reset Zoom ===
    window.canvas.reset_zoom()
    app.processEvents()
    ok = check_alignment(window, "TEST 4: After Reset Zoom (scale 1.0x)")
    results.append(("After Reset Zoom", ok))
    
    # === ТЕСТ 5: Resize Window ===
    window.resize(1400, 900)
    app.processEvents()
    ok = check_alignment(window, "TEST 5: After Window Resize")
    results.append(("After Window Resize", ok))
    
    # === ФІНАЛЬНИЙ ЗВІТ ===
    print("\n" + "=" * 60)
    print("[FINAL RESULTS]")
    print("=" * 60)
    
    failed_tests = []
    for test_name, ok in results:
        status = "[OK]" if ok else "[FAIL]"
        print(f"{status} {test_name}")
        if not ok:
            failed_tests.append(test_name)
    
    if failed_tests:
        print(f"\n[ERROR] {len(failed_tests)} test(s) failed:")
        for name in failed_tests:
            print(f"  - {name}")
        return 1
    else:
        print("\n[SUCCESS] All tests passed!")
        return 0


if __name__ == '__main__':
    exit_code = test_ruler_alignment_extended()
    print(f"\n{'=' * 60}")
    print(f"EXIT CODE: {exit_code}")
    print("=" * 60)
    sys.exit(exit_code)
