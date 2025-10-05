# -*- coding: utf-8 -*-
"""Умний тест: Snap використовує GridConfig з Grid Settings"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import QEvent, Qt
import re

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow

class SnapGridConfigLogAnalyzer:
    """Аналізатор логів для snap з GridConfig"""
    
    @staticmethod
    def parse_snap_logs(log_content):
        """Парсинг [SNAP-X/Y] логів з реального формату (3 рядки)"""
        # [SNAP-X] Value: 1.41mm, Offset: 0.00mm, Size: 1.00mm
        value_x = re.findall(r'\[SNAP-X\] Value: ([\d.]+)mm, Offset: ([\d.]+)mm, Size: ([\d.]+)mm', log_content)
        value_y = re.findall(r'\[SNAP-Y\] Value: ([\d.]+)mm, Offset: ([\d.]+)mm, Size: ([\d.]+)mm', log_content)
        
        # [SNAP-X] Result: 1.41mm -> 1.00mm
        result_x = re.findall(r'\[SNAP-X\] Result: ([\d.]+)mm -> ([\d.]+)mm', log_content)
        result_y = re.findall(r'\[SNAP-Y\] Result: ([\d.]+)mm -> ([\d.]+)mm', log_content)
        
        # Об'єднати: (old, new, grid, offset)
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
        
        return {
            'snap_x': snap_x,
            'snap_y': snap_y
        }
    
    @staticmethod
    def detect_issues(snap_logs, expected_grid_size=1.0, expected_offset=0.0):
        """Детектувати 5 типів проблем"""
        issues = []
        
        if not snap_logs['snap_x'] or not snap_logs['snap_y']:
            issues.append({'type': 'NO_SNAP_LOGS', 'desc': 'Snap logs not found - snap may not be working'})
            return issues
        
        # Проблема 1: WRONG_GRID_SIZE - snap використовує стару сітку (2.0mm замість 1.0mm)
        for old, new, grid, offset in snap_logs['snap_x']:
            if abs(grid - expected_grid_size) > 0.01:
                issues.append({
                    'type': 'WRONG_GRID_SIZE_X',
                    'desc': f'Snap uses grid={grid}mm, expected={expected_grid_size}mm (using old hardcoded value!)'
                })
                break
        
        for old, new, grid, offset in snap_logs['snap_y']:
            if abs(grid - expected_grid_size) > 0.01:
                issues.append({
                    'type': 'WRONG_GRID_SIZE_Y',
                    'desc': f'Snap uses grid={grid}mm, expected={expected_grid_size}mm (using old hardcoded value!)'
                })
                break
        
        # Проблема 2: WRONG_OFFSET - snap НЕ враховує offset
        for old, new, grid, offset in snap_logs['snap_x']:
            if abs(offset - expected_offset) > 0.01:
                issues.append({
                    'type': 'WRONG_OFFSET_X',
                    'desc': f'Snap uses offset={offset}mm, expected={expected_offset}mm'
                })
                break
        
        # Проблема 3: SNAP_FORMULA_INCORRECT - результат snap НЕ відповідає формулі
        for old, new, grid, offset in snap_logs['snap_x']:
            expected_snap = offset + round((old - offset) / grid) * grid
            if abs(new - expected_snap) > 0.01:
                issues.append({
                    'type': 'SNAP_FORMULA_INCORRECT_X',
                    'desc': f'Snap {old}mm -> {new}mm, expected {expected_snap}mm (formula: offset + round((value-offset)/grid)*grid)'
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
        
        # Проблема 4: NO_SNAP_APPLIED - координати НЕ змінились (snap не спрацював)
        snap_applied_x = any(abs(old - new) > 0.01 for old, new, _, _ in snap_logs['snap_x'])
        if not snap_applied_x:
            issues.append({'type': 'NO_SNAP_APPLIED_X', 'desc': 'Snap X not applied - coordinates unchanged'})
        
        # Проблема 5: GRID_CONFIG_NOT_USED - snap використовує hardcoded 2.0mm замість GridConfig 1.0mm
        using_old_grid = any(abs(grid - 2.0) < 0.01 for _, _, grid, _ in snap_logs['snap_x'])
        if using_old_grid:
            issues.append({
                'type': 'GRID_CONFIG_NOT_USED',
                'desc': 'CRITICAL: Snap still uses hardcoded 2.0mm grid! GridConfig NOT applied!'
            })
        
        return issues

def test_snap_uses_grid_config():
    """Тест: Snap використовує GridConfig (1.00mm grid, 0.00mm offset)"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("[TEST] SNAP USES GRID CONFIG")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Перевірити що Grid Settings: 1.0mm x 1.0mm, offset 0.0mm x 0.0mm
    grid_config = window.canvas.grid_config
    print(f"[1] GridConfig: Size=({grid_config.size_x_mm}mm, {grid_config.size_y_mm}mm), Offset=({grid_config.offset_x_mm}mm, {grid_config.offset_y_mm}mm)")
    
    # Додати Rectangle
    window._add_rectangle()
    app.processEvents()
    
    # Розмір файлу логів ДО drag
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # Drag rectangle: з (10.0, 10.0) до (11.3, 9.7) - має snap до (11.0, 10.0)
    rect_item = window.graphics_items[-1]
    rect_item.setPos(QPointF(11.3, 9.7))  # mm координати
    app.processEvents()
    
    # Читати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Аналіз логів
    analyzer = SnapGridConfigLogAnalyzer()
    snap_logs = analyzer.parse_snap_logs(new_logs)
    issues = analyzer.detect_issues(snap_logs, expected_grid_size=1.0, expected_offset=0.0)
    
    # Вивід
    print("=" * 60)
    print("[SNAP LOGS ANALYSIS]")
    print("=" * 60)
    print(f"Snap X logs found: {len(snap_logs['snap_x'])}")
    print(f"Snap Y logs found: {len(snap_logs['snap_y'])}")
    
    if snap_logs['snap_x']:
        old_x, new_x, grid_x, offset_x = snap_logs['snap_x'][0]
        print(f"\n[SNAP-X] {old_x:.2f}mm -> {new_x:.2f}mm")
        print(f"  Grid size used: {grid_x}mm (expected: 1.0mm)")
        print(f"  Offset used: {offset_x}mm (expected: 0.0mm)")
    
    if snap_logs['snap_y']:
        old_y, new_y, grid_y, offset_y = snap_logs['snap_y'][0]
        print(f"\n[SNAP-Y] {old_y:.2f}mm -> {new_y:.2f}mm")
        print(f"  Grid size used: {grid_y}mm (expected: 1.0mm)")
        print(f"  Offset used: {offset_y}mm (expected: 0.0mm)")
    
    if issues:
        print(f"\n{'=' * 60}")
        print(f"DETECTED {len(issues)} ISSUE(S):")
        print("=" * 60)
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] SNAP DOES NOT USE GRID CONFIG")
        return 1
    
    print("\n[OK] Snap correctly uses GridConfig (1.0mm grid, 0.0mm offset)")
    return 0

if __name__ == '__main__':
    sys.exit(test_snap_uses_grid_config())
