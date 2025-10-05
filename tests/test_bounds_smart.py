# -*- coding: utf-8 -*-
"""УМНИЙ ТЕСТ: Element Bounds Highlighting з аналізом логів"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from gui.main_window import MainWindow


class BoundsLogAnalyzer:
    """Анализатор логів для bounds highlighting"""
    
    @staticmethod
    def parse_bounds_logs(log):
        """[BOUNDS] Element position and size"""
        element_at = re.findall(r'\[BOUNDS\] Element at: x=([\d.]+)mm, y=([\d.]+)mm', log)
        size = re.findall(r'\[BOUNDS\] Size: width=([\d.]+)mm, height=([\d.]+)mm', log)
        
        return {
            'element_at': [(float(m[0]), float(m[1])) for m in element_at],
            'size': [(float(m[0]), float(m[1])) for m in size]
        }
    
    @staticmethod
    def parse_ruler_bounds_logs(log):
        """[BOUNDS-H/V] Highlight and Draw logs"""
        h_highlight = re.findall(r'\[BOUNDS-H\] Highlight: start=([\d.]+)mm, width=([\d.]+)mm', log)
        v_highlight = re.findall(r'\[BOUNDS-V\] Highlight: start=([\d.]+)mm, width=([\d.]+)mm', log)
        h_draw = re.findall(r'\[BOUNDS-H\] Draw: start_px=([\d.]+), width_px=([\d.]+)', log)
        v_draw = re.findall(r'\[BOUNDS-V\] Draw: start_px=([\d.]+), width_px=([\d.]+)', log)
        clear_h = re.findall(r'\[BOUNDS-H\] Clear highlight', log)
        clear_v = re.findall(r'\[BOUNDS-V\] Clear highlight', log)
        
        return {
            'h_highlight': [(float(m[0]), float(m[1])) for m in h_highlight],
            'v_highlight': [(float(m[0]), float(m[1])) for m in v_highlight],
            'h_draw': [(int(m[0]), int(m[1])) for m in h_draw],
            'v_draw': [(int(m[0]), int(m[1])) for m in v_draw],
            'clear_h': len(clear_h),
            'clear_v': len(clear_v)
        }
    
    @staticmethod
    def detect_issues(bounds_logs, ruler_logs):
        """Детектувати проблеми bounds highlighting"""
        issues = []
        
        # 1. BOUNDS != RULER HIGHLIGHT
        if bounds_logs['element_at'] and ruler_logs['h_highlight']:
            element_x = bounds_logs['element_at'][-1][0]
            element_y = bounds_logs['element_at'][-1][1]
            ruler_h_start = ruler_logs['h_highlight'][-1][0]
            ruler_v_start = ruler_logs['v_highlight'][-1][0]
            
            if abs(element_x - ruler_h_start) > 0.1:
                issues.append({
                    'type': 'BOUNDS_RULER_MISMATCH_H',
                    'desc': f'Element X={element_x:.2f}mm, Ruler H start={ruler_h_start:.2f}mm'
                })
            
            if abs(element_y - ruler_v_start) > 0.1:
                issues.append({
                    'type': 'BOUNDS_RULER_MISMATCH_V',
                    'desc': f'Element Y={element_y:.2f}mm, Ruler V start={ruler_v_start:.2f}mm'
                })
        
        # 2. SIZE != RULER WIDTH
        if bounds_logs['size'] and ruler_logs['h_highlight']:
            element_width = bounds_logs['size'][-1][0]
            element_height = bounds_logs['size'][-1][1]
            ruler_width = ruler_logs['h_highlight'][-1][1]
            ruler_height = ruler_logs['v_highlight'][-1][1]
            
            if abs(element_width - ruler_width) > 0.5:
                issues.append({
                    'type': 'SIZE_WIDTH_MISMATCH',
                    'desc': f'Element width={element_width:.2f}mm, Ruler width={ruler_width:.2f}mm'
                })
            
            if abs(element_height - ruler_height) > 0.5:
                issues.append({
                    'type': 'SIZE_HEIGHT_MISMATCH',
                    'desc': f'Element height={element_height:.2f}mm, Ruler height={ruler_height:.2f}mm'
                })
        
        # 3. RULER HIGHLIGHT != DRAWN
        if ruler_logs['h_highlight'] and ruler_logs['h_draw']:
            highlight_start = ruler_logs['h_highlight'][-1][0]
            highlight_width = ruler_logs['h_highlight'][-1][1]
            drawn_start = ruler_logs['h_draw'][-1][0]
            drawn_width = ruler_logs['h_draw'][-1][1]
            
            # Конвертувати мм -> px
            dpi = 203
            scale = 2.5
            expected_start_px = int(highlight_start * dpi / 25.4 * scale)
            expected_width_px = int(highlight_width * dpi / 25.4 * scale)
            
            if abs(drawn_start - expected_start_px) > 2:
                issues.append({
                    'type': 'DRAW_START_INCORRECT',
                    'desc': f'Expected start={expected_start_px}px, drawn={drawn_start}px'
                })
            
            if abs(drawn_width - expected_width_px) > 2:
                issues.append({
                    'type': 'DRAW_WIDTH_INCORRECT',
                    'desc': f'Expected width={expected_width_px}px, drawn={drawn_width}px'
                })
        
        return issues


def test_bounds_smart():
    """Умний тест bounds highlighting з аналізом логів"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Розмір файла ДО тесту
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # СИМУЛЯЦІЯ: додати text елемент
    window._add_text()
    app.processEvents()
    
    # Виділити елемент
    item = window.graphics_items[0]
    window.canvas.scene.clearSelection()
    item.setSelected(True)
    app.processEvents()
    
    # Читати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Аналізувати
    analyzer = BoundsLogAnalyzer()
    bounds_logs = analyzer.parse_bounds_logs(new_logs)
    ruler_logs = analyzer.parse_ruler_bounds_logs(new_logs)
    issues = analyzer.detect_issues(bounds_logs, ruler_logs)
    
    print("=" * 60)
    print("[STAGE 4] ELEMENT BOUNDS - LOG ANALYSIS")
    print("=" * 60)
    print(f"\n[BOUNDS] element positions: {len(bounds_logs['element_at'])}")
    print(f"[BOUNDS] sizes: {len(bounds_logs['size'])}")
    print(f"[RULER-H] highlights: {len(ruler_logs['h_highlight'])}")
    print(f"[RULER-V] highlights: {len(ruler_logs['v_highlight'])}")
    print(f"[RULER-H] draws: {len(ruler_logs['h_draw'])}")
    print(f"[RULER-V] draws: {len(ruler_logs['v_draw'])}")
    
    if bounds_logs['element_at']:
        pos = bounds_logs['element_at'][-1]
        print(f"Element position: x={pos[0]:.2f}mm, y={pos[1]:.2f}mm")
    
    if bounds_logs['size']:
        size = bounds_logs['size'][-1]
        print(f"Element size: width={size[0]:.2f}mm, height={size[1]:.2f}mm")
    
    # Тест deselect (clear)
    print("\n[TEST] Deselect element...")
    file_size_before_clear = log_file.stat().st_size
    
    window.canvas.scene.clearSelection()
    app.processEvents()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before_clear)
        clear_logs = f.read()
    
    clear_ruler_logs = analyzer.parse_ruler_bounds_logs(clear_logs)
    print(f"[RULER-H] clears: {clear_ruler_logs['clear_h']}")
    print(f"[RULER-V] clears: {clear_ruler_logs['clear_v']}")
    
    if clear_ruler_logs['clear_h'] == 0 or clear_ruler_logs['clear_v'] == 0:
        issues.append({
            'type': 'NO_CLEAR_ON_DESELECT',
            'desc': f"Rulers not cleared on deselect (H={clear_ruler_logs['clear_h']}, V={clear_ruler_logs['clear_v']})"
        })
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[FAILURE] BOUNDS HIGHLIGHTING HAS ISSUES")
        print("=" * 60)
        return 1
    
    print("\n[OK] Bounds highlighting works correctly")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_bounds_smart())
