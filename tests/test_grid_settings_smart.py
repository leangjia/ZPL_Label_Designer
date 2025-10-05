# -*- coding: utf-8 -*-
"""Умний тест Grid Settings з LogAnalyzer"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import QEvent, QPointF, Qt
import re

# Додати project root до sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.main_window import MainWindow
from config import GridConfig, SnapMode


class GridLogAnalyzer:
    """Аналізатор логів Grid Settings"""
    
    @staticmethod
    def parse_grid_draw_logs(log_content):
        """Парсити логи малювання сітки"""
        config_pattern = r'\[GRID-DRAW\] Config: Size X=([\d.]+)mm, Y=([\d.]+)mm'
        offset_pattern = r'\[GRID-DRAW\] Config: Offset X=([\d.]+)mm, Y=([\d.]+)mm'
        vline_pattern = r'\[GRID-DRAW\] Vertical line: mm=([\d.]+), px=(\d+)'
        hline_pattern = r'\[GRID-DRAW\] Horizontal line: mm=([\d.]+), px=(\d+)'
        
        return {
            'config': re.findall(config_pattern, log_content),
            'offset': re.findall(offset_pattern, log_content),
            'vlines': [(float(m[0]), int(m[1])) for m in re.findall(vline_pattern, log_content)],
            'hlines': [(float(m[0]), int(m[1])) for m in re.findall(hline_pattern, log_content)]
        }
    
    @staticmethod
    def parse_snap_logs(log_content):
        """Парсити логи snap to grid"""
        config_pattern = r'\[SNAP-CONFIG\] Size: X=([\d.]+)mm, Y=([\d.]+)mm, Offset: X=([\d.]+)mm, Y=([\d.]+)mm'
        snap_x_pattern = r'\[SNAP-X\] Result: ([\d.]+)mm -> ([\d.]+)mm'
        snap_y_pattern = r'\[SNAP-Y\] Result: ([\d.]+)mm -> ([\d.]+)mm'
        
        return {
            'config': re.findall(config_pattern, log_content),
            'snap_x': [(float(m[0]), float(m[1])) for m in re.findall(snap_x_pattern, log_content)],
            'snap_y': [(float(m[0]), float(m[1])) for m in re.findall(snap_y_pattern, log_content)]
        }
    
    @staticmethod
    def detect_issues(grid_logs, snap_logs, expected_config):
        """Детектувати проблеми в логах"""
        issues = []
        
        # ПРОБЛЕМА 1: Grid Config != Expected
        if grid_logs['config']:
            size_x, size_y = grid_logs['config'][0]
            if abs(float(size_x) - expected_config['size_x']) > 0.1:
                issues.append({
                    'type': 'GRID_SIZE_X_MISMATCH',
                    'desc': f'Expected Size X={expected_config["size_x"]}mm, Got {size_x}mm'
                })
            if abs(float(size_y) - expected_config['size_y']) > 0.1:
                issues.append({
                    'type': 'GRID_SIZE_Y_MISMATCH',
                    'desc': f'Expected Size Y={expected_config["size_y"]}mm, Got {size_y}mm'
                })
        
        # ПРОБЛЕМА 2: Offset не застосований
        if grid_logs['offset']:
            offset_x, offset_y = grid_logs['offset'][0]
            if grid_logs['vlines'] and abs(grid_logs['vlines'][0][0] - float(offset_x)) > 0.1:
                issues.append({
                    'type': 'OFFSET_X_NOT_APPLIED',
                    'desc': f'First vline at {grid_logs["vlines"][0][0]:.2f}mm, Expected offset_x={offset_x}mm'
                })
            if grid_logs['hlines'] and abs(grid_logs['hlines'][0][0] - float(offset_y)) > 0.1:
                issues.append({
                    'type': 'OFFSET_Y_NOT_APPLIED',
                    'desc': f'First hline at {grid_logs["hlines"][0][0]:.2f}mm, Expected offset_y={offset_y}mm'
                })
        
        # ПРОБЛЕМА 3: Grid lines не на правильних позиціях
        if grid_logs['config'] and grid_logs['offset'] and len(grid_logs['vlines']) > 1:
            size_x = float(grid_logs['config'][0][0])
            offset_x = float(grid_logs['offset'][0][0])
            
            for i, (mm, px) in enumerate(grid_logs['vlines'][:3]):  # Перевіряємо перші 3 лінії
                expected_mm = offset_x + i * size_x
                if abs(mm - expected_mm) > 0.1:
                    issues.append({
                        'type': 'GRID_LINE_POSITION_WRONG',
                        'desc': f'Vline {i}: at {mm:.2f}mm, Expected {expected_mm:.2f}mm'
                    })
        
        # ПРОБЛЕМА 4: Snap формула неправильна (якщо є snap логи)
        if snap_logs['snap_x'] and grid_logs['config'] and grid_logs['offset']:
            size_x = float(grid_logs['config'][0][0])
            offset_x = float(grid_logs['offset'][0][0])
            
            for before_x, after_x in snap_logs['snap_x']:
                # Очікуваний snap: offset + round((value - offset) / size) * size
                expected = offset_x + round((before_x - offset_x) / size_x) * size_x
                if abs(after_x - expected) > 0.1:
                    issues.append({
                        'type': 'SNAP_FORMULA_INCORRECT',
                        'desc': f'Snap X: {before_x:.2f}mm -> {after_x:.2f}mm, Expected {expected:.2f}mm'
                    })
        
        return issues


def test_grid_settings_smart():
    """Умний тест налаштувань сітки з LogAnalyzer"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # 1. Розмір файлу логів ДО тесту
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # 2. СИМУЛЯЦІЯ: Встановити grid config
    expected_config = {
        'size_x': 3.0,
        'size_y': 2.5,
        'offset_x': 0.5,
        'offset_y': 1.0
    }
    
    new_config = GridConfig(
        size_x_mm=expected_config['size_x'],
        size_y_mm=expected_config['size_y'],
        offset_x_mm=expected_config['offset_x'],
        offset_y_mm=expected_config['offset_y'],
        visible=True,
        snap_mode=SnapMode.GRID
    )
    window.canvas.set_grid_config(new_config)
    window.canvas._redraw_grid()
    app.processEvents()
    
    # 3. СИМУЛЯЦІЯ: Додати текст та перемістити (snap test)
    window._add_text()
    app.processEvents()
    
    # Знайти елемент
    text_item = None
    for item in window.graphics_items:
        if hasattr(item, 'element') and item.element.__class__.__name__ == 'TextElement':
            text_item = item
            break
    
    # Перемістити елемент для snap тесту
    if text_item:
        # Position: 8.7mm, 7.3mm -> повинно snap до nearest grid
        # Expected: X: 0.5 + round((8.7-0.5)/3.0)*3.0 = 0.5 + 3*3.0 = 9.5mm
        # Expected: Y: 1.0 + round((7.3-1.0)/2.5)*2.5 = 1.0 + 3*2.5 = 8.5mm
        px_x = 8.7 * 203 / 25.4
        px_y = 7.3 * 203 / 25.4
        text_item.setPos(px_x, px_y)
        app.processEvents()
    
    # 4. Читати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # 5. Аналізувати
    analyzer = GridLogAnalyzer()
    grid_logs = analyzer.parse_grid_draw_logs(new_logs)
    snap_logs = analyzer.parse_snap_logs(new_logs)
    issues = analyzer.detect_issues(grid_logs, snap_logs, expected_config)
    
    # 6. Вивід
    print("=" * 60)
    print("[GRID SETTINGS] LOG ANALYSIS")
    print("=" * 60)
    print(f"Grid draw logs: {len(grid_logs['vlines'])} vlines, {len(grid_logs['hlines'])} hlines")
    print(f"Snap logs: {len(snap_logs['snap_x'])} X snaps, {len(snap_logs['snap_y'])} Y snaps")
    
    if grid_logs['config']:
        print(f"Grid config detected: Size X={grid_logs['config'][0][0]}mm, Y={grid_logs['config'][0][1]}mm")
    if grid_logs['offset']:
        print(f"Grid offset detected: X={grid_logs['offset'][0][0]}mm, Y={grid_logs['offset'][0][1]}mm")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] GRID SETTINGS HAS ISSUES")
        return 1
    
    print("\n[OK] Grid settings work correctly")
    return 0


if __name__ == '__main__':
    sys.exit(test_grid_settings_smart())
