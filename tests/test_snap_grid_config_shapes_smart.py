# -*- coding: utf-8 -*-
"""Умный тест: Snap использует GridConfig з Grid Settings для shape элементов"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
import re

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow

class SnapGridConfigLogAnalyzer:
    """Анализатор логов для snap с GridConfig"""
    
    @staticmethod
    def parse_snap_logs(log_content):
        """Парсинг [SNAP-X] и [SNAP-Y] логов"""
        snap_x = re.findall(r'\[SNAP-X\] Value: ([\d.]+)mm, Offset: ([\d.]+)mm, Size: ([\d.]+)mm', log_content)
        snap_y = re.findall(r'\[SNAP-Y\] Value: ([\d.]+)mm, Offset: ([\d.]+)mm, Size: ([\d.]+)mm', log_content)
        snap_result_x = re.findall(r'\[SNAP-X\] Result: ([\d.]+)mm -> ([\d.]+)mm', log_content)
        snap_result_y = re.findall(r'\[SNAP-Y\] Result: ([\d.]+)mm -> ([\d.]+)mm', log_content)
        
        return {
            'snap_x_config': [(float(m[0]), float(m[1]), float(m[2])) for m in snap_x],
            'snap_y_config': [(float(m[0]), float(m[1]), float(m[2])) for m in snap_y],
            'snap_x_result': [(float(m[0]), float(m[1])) for m in snap_result_x],
            'snap_y_result': [(float(m[0]), float(m[1])) for m in snap_result_y]
        }
    
    @staticmethod
    def detect_issues(snap_logs, expected_grid_size=1.0, expected_offset=0.0):
        """Детектировать 5 типов проблем"""
        issues = []
        
        if not snap_logs['snap_x_config'] or not snap_logs['snap_y_config']:
            issues.append({'type': 'NO_SNAP_LOGS', 'desc': 'Snap logs not found - snap may not be working'})
            return issues
        
        # Проблема 1: WRONG_GRID_SIZE - snap використовує стару сітку (2.0mm замість 1.0mm)
        if snap_logs['snap_x_config']:
            value, offset, grid = snap_logs['snap_x_config'][0]
            if abs(grid - expected_grid_size) > 0.01:
                issues.append({
                    'type': 'WRONG_GRID_SIZE_X',
                    'desc': f'Snap uses grid={grid}mm, expected={expected_grid_size}mm (using old hardcoded value!)'
                })
        
        if snap_logs['snap_y_config']:
            value, offset, grid = snap_logs['snap_y_config'][0]
            if abs(grid - expected_grid_size) > 0.01:
                issues.append({
                    'type': 'WRONG_GRID_SIZE_Y',
                    'desc': f'Snap uses grid={grid}mm, expected={expected_grid_size}mm (using old hardcoded value!)'
                })
        
        # Проблема 2: WRONG_OFFSET - snap НЕ враховує offset
        if snap_logs['snap_x_config']:
            value, offset_used, grid = snap_logs['snap_x_config'][0]
            if abs(offset_used - expected_offset) > 0.01:
                issues.append({
                    'type': 'WRONG_OFFSET_X',
                    'desc': f'Snap uses offset={offset_used}mm, expected={expected_offset}mm'
                })
        
        # Проблема 3: SNAP_FORMULA_INCORRECT - результат snap НЕ відповідає формулі
        if snap_logs['snap_x_result']:
            old, new = snap_logs['snap_x_result'][0]
            value, offset, grid = snap_logs['snap_x_config'][0]
            expected_snap = offset + round((old - offset) / grid) * grid
            if abs(new - expected_snap) > 0.01:
                issues.append({
                    'type': 'SNAP_FORMULA_INCORRECT_X',
                    'desc': f'Snap {old}mm -> {new}mm, expected {expected_snap}mm (formula: offset + round((value-offset)/grid)*grid)'
                })
        
        if snap_logs['snap_y_result']:
            old, new = snap_logs['snap_y_result'][0]
            value, offset, grid = snap_logs['snap_y_config'][0]
            expected_snap = offset + round((old - offset) / grid) * grid
            if abs(new - expected_snap) > 0.01:
                issues.append({
                    'type': 'SNAP_FORMULA_INCORRECT_Y',
                    'desc': f'Snap {old}mm -> {new}mm, expected {expected_snap}mm'
                })
        
        # Проблема 4: NO_SNAP_APPLIED - координаты НЕ изменились (snap не сработал)
        snap_applied_x = len(snap_logs['snap_x_result']) > 0
        if not snap_applied_x:
            issues.append({'type': 'NO_SNAP_APPLIED_X', 'desc': 'Snap X not applied - coordinates unchanged'})
        
        # Проблема 5: GRID_CONFIG_NOT_USED - snap використовує hardcoded 2.0mm замість GridConfig 1.0mm
        using_old_grid = any(abs(grid - 2.0) < 0.01 for _, _, grid in snap_logs['snap_x_config'])
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
    print("[TEST] SNAP USES GRID CONFIG (SHAPES)")
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
    rect_item.setPos(QPointF(rect_item._mm_to_px(11.3), rect_item._mm_to_px(9.7)))
    app.processEvents()
    
    # Читати НОВI логи
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
    print(f"Snap X config logs found: {len(snap_logs['snap_x_config'])}")
    print(f"Snap Y config logs found: {len(snap_logs['snap_y_config'])}")
    print(f"Snap X result logs found: {len(snap_logs['snap_x_result'])}")
    print(f"Snap Y result logs found: {len(snap_logs['snap_y_result'])}")
    
    if snap_logs['snap_x_config']:
        value, offset, grid = snap_logs['snap_x_config'][0]
        print(f"\n[SNAP-X CONFIG] Value={value:.2f}mm, Offset={offset:.2f}mm, Size={grid:.2f}mm")
        print(f"  Expected: grid=1.0mm, offset=0.0mm")
    
    if snap_logs['snap_x_result']:
        old_x, new_x = snap_logs['snap_x_result'][0]
        print(f"\n[SNAP-X RESULT] {old_x:.2f}mm -> {new_x:.2f}mm")
    
    if snap_logs['snap_y_config']:
        value, offset, grid = snap_logs['snap_y_config'][0]
        print(f"\n[SNAP-Y CONFIG] Value={value:.2f}mm, Offset={offset:.2f}mm, Size={grid:.2f}mm")
        print(f"  Expected: grid=1.0mm, offset=0.0mm")
    
    if snap_logs['snap_y_result']:
        old_y, new_y = snap_logs['snap_y_result'][0]
        print(f"\n[SNAP-Y RESULT] {old_y:.2f}mm -> {new_y:.2f}mm")
    
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
