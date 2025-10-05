# -*- coding: utf-8 -*-
"""Автоматизований тест ЕТАПІВ 1, 2, 3 Canvas Features"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF, Qt, QEvent
from gui.main_window import MainWindow

def test_stage_1_cursor_tracking():
    """ЕТАП 1: Cursor Tracking"""
    print("\n[TEST STAGE 1] CURSOR TRACKING")
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Перевірка 1: Сигнал cursor_position_changed
    signal_received = {'x': None, 'y': None}
    
    def on_cursor(x, y):
        signal_received['x'] = x
        signal_received['y'] = y
    
    window.canvas.cursor_position_changed.connect(on_cursor)
    
    # Симулювати рух миші
    test_point = QPointF(100, 100)
    scene_pos = window.canvas.mapToScene(test_point.toPoint())
    expected_x = scene_pos.x() * 25.4 / 203
    expected_y = scene_pos.y() * 25.4 / 203
    
    # Trigger mouseMoveEvent
    from PySide6.QtGui import QMouseEvent
    event = QMouseEvent(
        QEvent.MouseMove,
        test_point,
        Qt.NoButton,
        Qt.NoButton,
        Qt.NoModifier
    )
    window.canvas.mouseMoveEvent(event)
    
    # Перевірка результату
    if signal_received['x'] is not None:
        print(f"  [OK] Signal emitted: X={signal_received['x']:.2f}mm, Y={signal_received['y']:.2f}mm")
        stage1_pass = True
    else:
        print("  [ERROR] Signal NOT emitted!")
        stage1_pass = False
    
    # Перевірка 2: Ruler cursor markers
    if window.h_ruler.show_cursor and window.v_ruler.show_cursor:
        print("  [OK] Ruler cursor markers active")
    else:
        print("  [ERROR] Ruler cursor markers NOT active!")
        stage1_pass = False
    
    window.close()
    return stage1_pass


def test_stage_2_zoom():
    """ЕТАП 2: Zoom to Point"""
    print("\n[TEST STAGE 2] ZOOM TO POINT")
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Запам'ятати початковий scale
    initial_scale = window.canvas.current_scale
    print(f"  [INFO] Initial scale: {initial_scale}")
    
    # Перевірка 1: Zoom in
    window.canvas.zoom_in()
    new_scale = window.canvas.current_scale
    
    if new_scale > initial_scale:
        print(f"  [OK] Zoom in: {initial_scale} -> {new_scale}")
        stage2_pass = True
    else:
        print(f"  [ERROR] Zoom in failed: {initial_scale} -> {new_scale}")
        stage2_pass = False
    
    # Перевірка 2: Zoom out
    window.canvas.zoom_out()
    zoom_out_scale = window.canvas.current_scale
    
    if zoom_out_scale < new_scale:
        print(f"  [OK] Zoom out: {new_scale} -> {zoom_out_scale}")
    else:
        print(f"  [ERROR] Zoom out failed!")
        stage2_pass = False
    
    # Перевірка 3: Reset zoom
    window.canvas.reset_zoom()
    reset_scale = window.canvas.current_scale
    
    if reset_scale == 1.0:
        print(f"  [OK] Reset zoom to 1.0")
    else:
        print(f"  [ERROR] Reset zoom failed: {reset_scale}")
        stage2_pass = False
    
    # Перевірка 4: Zoom bounds
    if window.canvas.min_scale == 0.5 and window.canvas.max_scale == 10.0:
        print(f"  [OK] Zoom bounds: 0.5 - 10.0")
    else:
        print(f"  [ERROR] Wrong zoom bounds!")
        stage2_pass = False
    
    window.close()
    return stage2_pass


def test_stage_3_snap():
    """ЕТАП 3: Snap to Grid"""
    print("\n[TEST STAGE 3] SNAP TO GRID")
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Додати текстовий елемент
    window._add_text()
    
    if not window.graphics_items:
        print("  [ERROR] Failed to add text element!")
        window.close()
        return False
    
    item = window.graphics_items[0]
    
    # Перевірка 1: Snap enabled за замовчуванням
    if hasattr(item, 'snap_enabled') and item.snap_enabled:
        print("  [OK] Snap enabled by default")
        stage3_pass = True
    else:
        print("  [ERROR] Snap NOT enabled!")
        stage3_pass = False
    
    # Перевірка 2: Grid parameters
    if item.grid_step_mm == 2.0 and item.snap_threshold_mm == 0.5:
        print("  [OK] Grid params: step=2.0mm, threshold=0.5mm")
    else:
        print("  [ERROR] Wrong grid parameters!")
        stage3_pass = False
    
    # Перевірка 3: Snap logic
    # Встановити позицію близько до grid line (8.26мм -> має стати 8.0мм)
    test_x_mm = 8.26
    test_y_mm = 8.26
    test_position = QPointF(item._mm_to_px(test_x_mm), item._mm_to_px(test_y_mm))
    item.setPos(test_position)
    
    actual_pos = item.pos()
    actual_x_mm = item._px_to_mm(actual_pos.x())
    actual_y_mm = item._px_to_mm(actual_pos.y())
    
    # Очікується snap до 8.0мм (найближча grid line)
    expected_mm = 8.0
    tolerance = 0.01
    
    if abs(actual_x_mm - expected_mm) < tolerance and abs(actual_y_mm - expected_mm) < tolerance:
        print(f"  [OK] Snap worked: {test_x_mm}mm -> {actual_x_mm:.2f}mm")
    else:
        print(f"  [ERROR] Snap failed: expected {expected_mm}mm, got {actual_x_mm:.2f}mm")
        stage3_pass = False
    
    # Перевірка 4: Snap toggle
    item.snap_enabled = False
    item.setPos(test_position)
    new_pos = item.pos()
    new_x_mm = item._px_to_mm(new_pos.x())
    
    if abs(new_x_mm - test_x_mm) < tolerance:
        print(f"  [OK] Snap disabled: position {new_x_mm:.2f}mm (no snap)")
    else:
        print(f"  [ERROR] Snap toggle failed!")
        stage3_pass = False
    
    window.close()
    return stage3_pass


def main():
    """Запуск всіх тестів"""
    print("=" * 60)
    print("AUTOMATED TEST: Canvas Features Stages 1-3")
    print("=" * 60)
    
    results = []
    
    # ЕТАП 1
    results.append(("Stage 1: Cursor Tracking", test_stage_1_cursor_tracking()))
    
    # ЕТАП 2
    results.append(("Stage 2: Zoom to Point", test_stage_2_zoom()))
    
    # ЕТАП 3
    results.append(("Stage 3: Snap to Grid", test_stage_3_snap()))
    
    # Результати
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "[SUCCESS]" if passed else "[FAILURE]"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED")
        return 0
    else:
        print("[FAILURE] SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
