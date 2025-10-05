# -*- coding: utf-8 -*-
"""Master тест: Всі типи елементів використовують GridConfig для snap"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
import re

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow

class AllElementsLogAnalyzer:
    """Аналізатор логів для всіх типів елементів"""
    
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
    def detect_issues(snap_logs, expected_grid_size=1.0, expected_offset=0.0):
        """Детектувати проблеми"""
        issues = []
        
        if not snap_logs['snap_x'] or not snap_logs['snap_y']:
            issues.append({'type': 'NO_SNAP_LOGS', 'desc': 'Snap logs not found'})
            return issues
        
        # Проблема 1: WRONG_GRID_SIZE
        for old, new, grid, offset in snap_logs['snap_x']:
            if abs(grid - expected_grid_size) > 0.01:
                issues.append({
                    'type': 'WRONG_GRID_SIZE',
                    'desc': f'Grid={grid}mm, expected={expected_grid_size}mm'
                })
                break
        
        # Проблема 2: WRONG_OFFSET
        for old, new, grid, offset in snap_logs['snap_x']:
            if abs(offset - expected_offset) > 0.01:
                issues.append({
                    'type': 'WRONG_OFFSET',
                    'desc': f'Offset={offset}mm, expected={expected_offset}mm'
                })
                break
        
        # Проблема 3: SNAP_FORMULA_INCORRECT
        for old, new, grid, offset in snap_logs['snap_x']:
            expected_snap = offset + round((old - offset) / grid) * grid
            if abs(new - expected_snap) > 0.01:
                issues.append({
                    'type': 'SNAP_FORMULA_INCORRECT',
                    'desc': f'Snap {old}mm -> {new}mm, expected {expected_snap}mm'
                })
                break
        
        return issues

def test_snap_all_element_types():
    """Master тест: всі типи елементів використовують GridConfig для snap"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("[MASTER TEST] ALL ELEMENT TYPES USE GRID CONFIG")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Перевірити GridConfig
    grid_config = window.canvas.grid_config
    print(f"[1] GridConfig: Size=({grid_config.size_x_mm}mm, {grid_config.size_y_mm}mm), Offset=({grid_config.offset_x_mm}mm, {grid_config.offset_y_mm}mm)")
    
    # Тести для кожного типу елемента
    element_tests = [
        ("Text", window._add_text),
        ("Rectangle", window._add_rectangle),
        ("Circle", window._add_circle),
        ("Line", window._add_line),
        ("Barcode", window._add_ean13),
    ]
    
    results = []
    analyzer = AllElementsLogAnalyzer()
    
    for name, add_func in element_tests:
        print(f"\n{'-' * 60}")
        print(f"[{name.upper()}] Testing snap to grid...")
        
        # Додати елемент
        add_func()
        app.processEvents()
        
        # Розмір файлу логів ДО drag
        file_size_before = log_file.stat().st_size if log_file.exists() else 0
        
        # Drag element: з (10.0, 10.0) до (11.3, 9.7) - має snap до (11.0, 10.0)
        element_item = window.graphics_items[-1]
        element_item.setPos(QPointF(11.3, 9.7))  # mm координати
        app.processEvents()
        
        # Читати НОВІ логи
        with open(log_file, 'r', encoding='utf-8') as f:
            f.seek(file_size_before)
            new_logs = f.read()
        
        # Аналіз логів
        snap_logs = analyzer.parse_snap_logs(new_logs)
        issues = analyzer.detect_issues(snap_logs, expected_grid_size=1.0, expected_offset=0.0)
        
        # Вивід результату для цього елемента
        if snap_logs['snap_x']:
            old_x, new_x, grid_x, offset_x = snap_logs['snap_x'][0]
            print(f"  SNAP-X: {old_x:.2f}mm -> {new_x:.2f}mm (grid: {grid_x}mm, offset: {offset_x}mm)")
        
        if snap_logs['snap_y']:
            old_y, new_y, grid_y, offset_y = snap_logs['snap_y'][0]
            print(f"  SNAP-Y: {old_y:.2f}mm -> {new_y:.2f}mm (grid: {grid_y}mm, offset: {offset_y}mm)")
        
        # Збереження результату
        results.append({
            'element': name,
            'issues': issues,
            'snap_x_count': len(snap_logs['snap_x']),
            'snap_y_count': len(snap_logs['snap_y'])
        })
        
        if issues:
            print(f"  [FAIL] {len(issues)} issue(s): {', '.join(i['type'] for i in issues)}")
        else:
            print(f"  [OK] Snap works correctly")
    
    # Фінальний звіт
    print(f"\n{'=' * 60}")
    print("[FINAL RESULTS]")
    print("=" * 60)
    
    all_passed = all(len(r['issues']) == 0 for r in results)
    
    for r in results:
        status = "[OK]  " if len(r['issues']) == 0 else "[FAIL]"
        print(f"{status} {r['element']:10} - Snap X/Y logs: {r['snap_x_count']}/{r['snap_y_count']}")
        if r['issues']:
            for issue in r['issues']:
                print(f"         - {issue['type']}: {issue['desc']}")
    
    print("=" * 60)
    if all_passed:
        print("[SUCCESS] ALL ELEMENTS USE GRID CONFIG FOR SNAP")
        return 0
    else:
        failed_count = sum(1 for r in results if len(r['issues']) > 0)
        print(f"[FAILURE] {failed_count}/{len(results)} elements have issues")
        return 1

if __name__ == '__main__':
    sys.exit(test_snap_all_element_types())
