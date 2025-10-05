# -*- coding: utf-8 -*-
"""Умний тест: Snap працює з offset (3.0mm grid + 0.5mm offset)"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
import re

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow

class SnapOffsetLogAnalyzer:
    """Аналізатор логів для snap з offset"""
    
    @staticmethod
    def parse_snap_logs(log_content):
        """Парсинг [SNAP-X/Y] логів"""
        value_x = re.findall(r'\[SNAP-X\] Value: ([\d.]+)mm, Offset: ([\d.]+)mm, Size: ([\d.]+)mm', log_content)
        value_y = re.findall(r'\[SNAP-Y\] Value: ([\d.]+)mm, Offset: ([\d.]+)mm, Size: ([\d.]+)mm', log_content)
        
        result_x = re.findall(r'\[SNAP-X\] Result: ([\d.]+)mm -> ([\d.]+)mm', log_content)
        result_y = re.findall(r'\[SNAP-Y\] Result: ([\d.]+)mm -> ([\d.]+)mm', log_content)
        
        snap_x = []
        for i, (val, offset, size) in enumerate(value_x):
            if i < len(result_x):
                old, new = result_x[i]
                snap_x.append((float(old), float(new), float(size), float(offset)))
        
        snap_y = []
        for i, (val, offset, size) in enumerate(value_y):
            if i < len(result_y):
                old, new = result_y[i]
                snap_y.append((float(old), float(new), float(size), float(offset)))
        
        return {'snap_x': snap_x, 'snap_y': snap_y}
    
    @staticmethod
    def detect_issues(snap_logs, expected_grid_size=3.0, expected_offset=0.5):
        """Детектувати проблеми для offset тесту"""
        issues = []
        
        if not snap_logs['snap_x'] or not snap_logs['snap_y']:
            issues.append({'type': 'NO_SNAP_LOGS', 'desc': 'Snap logs not found'})
            return issues
        
        # Проблема 1: WRONG_GRID_SIZE
        for old, new, grid, offset in snap_logs['snap_x']:
            if abs(grid - expected_grid_size) > 0.01:
                issues.append({
                    'type': 'WRONG_GRID_SIZE_X',
                    'desc': f'Snap uses grid={grid}mm, expected={expected_grid_size}mm'
                })
                break
        
        # Проблема 2: WRONG_OFFSET
        for old, new, grid, offset in snap_logs['snap_x']:
            if abs(offset - expected_offset) > 0.01:
                issues.append({
                    'type': 'WRONG_OFFSET_X',
                    'desc': f'Snap uses offset={offset}mm, expected={expected_offset}mm'
                })
                break
        
        # Проблема 3: SNAP_FORMULA_INCORRECT
        for old, new, grid, offset in snap_logs['snap_x']:
            expected_snap = offset + round((old - offset) / grid) * grid
            if abs(new - expected_snap) > 0.01:
                issues.append({
                    'type': 'SNAP_FORMULA_INCORRECT_X',
                    'desc': f'Snap {old}mm -> {new}mm, expected {expected_snap}mm (formula with offset)'
                })
                break
        
        for old, new, grid, offset in snap_logs['snap_y']:
            expected_snap = offset + round((old - offset) / grid) * grid
            if abs(new - expected_snap) > 0.01:
                issues.append({
                    'type': 'SNAP_FORMULA_INCORRECT_Y',
                    'desc': f'Snap {old}mm -> {new}mm, expected {expected_snap}mm'
                })
                break
        
        # Проблема 4: SNAP_NOT_TO_OFFSET_GRID
        # Перевірити що результат = offset + grid * n
        for old, new, grid, offset in snap_logs['snap_x']:
            # new має бути offset + grid * n
            relative = (new - offset) / grid
            if abs(relative - round(relative)) > 0.01:
                issues.append({
                    'type': 'SNAP_NOT_TO_OFFSET_GRID_X',
                    'desc': f'Result {new}mm is NOT on offset grid (offset={offset}, grid={grid})'
                })
                break
        
        return issues

def test_snap_with_offset():
    """Тест: Snap працює з offset (3.0mm grid + 0.5mm offset)"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("[TEST] SNAP WITH OFFSET (3.0mm + 0.5mm)")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Змінити Grid Settings: 3.0mm grid + 0.5mm offset
    print("[1] Changing GridConfig: Size=3.0mm, Offset=0.5mm")
    window.canvas.grid_config.size_x_mm = 3.0
    window.canvas.grid_config.size_y_mm = 3.0
    window.canvas.grid_config.offset_x_mm = 0.5
    window.canvas.grid_config.offset_y_mm = 0.5
    window.canvas._draw_grid()  # Redraw grid
    app.processEvents()
    
    grid_config = window.canvas.grid_config
    print(f"[2] GridConfig: Size=({grid_config.size_x_mm}mm, {grid_config.size_y_mm}mm), Offset=({grid_config.offset_x_mm}mm, {grid_config.offset_y_mm}mm)")
    
    # Додати Rectangle
    window._add_rectangle()
    app.processEvents()
    
    # Розмір файлу логів ДО drag
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # Drag rectangle: з (10.0, 10.0) до (8.7, 8.2)
    # Очікування: snap до (9.5, 9.5) - offset 0.5 + grid 3.0
    # Formula: 0.5 + round((8.7-0.5)/3.0)*3.0 = 0.5 + round(2.73)*3.0 = 0.5 + 9.0 = 9.5
    print("[3] Dragging rectangle to (8.7, 8.2)mm - expect snap to (9.5, 9.5)mm")
    rect_item = window.graphics_items[-1]
    rect_item.setPos(QPointF(8.7, 8.2))  # mm координати
    app.processEvents()
    
    # Читати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Аналіз логів
    analyzer = SnapOffsetLogAnalyzer()
    snap_logs = analyzer.parse_snap_logs(new_logs)
    issues = analyzer.detect_issues(snap_logs, expected_grid_size=3.0, expected_offset=0.5)
    
    # Вивід
    print("=" * 60)
    print("[SNAP LOGS ANALYSIS]")
    print("=" * 60)
    print(f"Snap X logs found: {len(snap_logs['snap_x'])}")
    print(f"Snap Y logs found: {len(snap_logs['snap_y'])}")
    
    if snap_logs['snap_x']:
        old_x, new_x, grid_x, offset_x = snap_logs['snap_x'][0]
        print(f"\n[SNAP-X] {old_x:.2f}mm -> {new_x:.2f}mm")
        print(f"  Grid size used: {grid_x}mm (expected: 3.0mm)")
        print(f"  Offset used: {offset_x}mm (expected: 0.5mm)")
        
        # Перевірити формулу вручну
        expected = offset_x + round((old_x - offset_x) / grid_x) * grid_x
        print(f"  Formula check: {offset_x} + round(({old_x}-{offset_x})/{grid_x})*{grid_x} = {expected:.2f}mm")
    
    if snap_logs['snap_y']:
        old_y, new_y, grid_y, offset_y = snap_logs['snap_y'][0]
        print(f"\n[SNAP-Y] {old_y:.2f}mm -> {new_y:.2f}mm")
        print(f"  Grid size used: {grid_y}mm (expected: 3.0mm)")
        print(f"  Offset used: {offset_y}mm (expected: 0.5mm)")
        
        expected = offset_y + round((old_y - offset_y) / grid_y) * grid_y
        print(f"  Formula check: {offset_y} + round(({old_y}-{offset_y})/{grid_y})*{grid_y} = {expected:.2f}mm")
    
    if issues:
        print(f"\n{'=' * 60}")
        print(f"DETECTED {len(issues)} ISSUE(S):")
        print("=" * 60)
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] SNAP WITH OFFSET HAS ISSUES")
        return 1
    
    print("\n[OK] Snap correctly uses offset (3.0mm grid + 0.5mm offset)")
    return 0

if __name__ == '__main__':
    sys.exit(test_snap_with_offset())
