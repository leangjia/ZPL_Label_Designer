# -*- coding: utf-8 -*-
"""УМНЫЙ ТЕСТ: Cursor Tracking с анализом логов"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF, Qt
from PySide6.QtTest import QTest
from gui.main_window import MainWindow


class CursorLogAnalyzer:
    """Анализатор логов для cursor tracking"""
    
    @staticmethod
    def parse_cursor_logs(log):
        """Витягти [CURSOR] записи: Signal emit"""
        pattern = r'\[CURSOR\] Signal emit: ([\d.]+)mm, ([\d.]+)mm'
        return [(float(m[0]), float(m[1])) for m in re.findall(pattern, log)]
    
    @staticmethod
    def parse_ruler_logs(log):
        """Витягти [RULER-H/V] записи: Update/Draw позицій"""
        h_update = re.findall(r'\[RULER-H\] Update position: ([\d.]+)mm', log)
        v_update = re.findall(r'\[RULER-V\] Update position: ([\d.]+)mm', log)
        h_draw = re.findall(r'\[RULER-H\] Drawn at: ([\d.]+)px', log)
        v_draw = re.findall(r'\[RULER-V\] Drawn at: ([\d.]+)px', log)
        
        return {
            'h_update': [float(x) for x in h_update],
            'v_update': [float(y) for y in v_update],
            'h_draw': [float(px) for px in h_draw],
            'v_draw': [float(px) for px in v_draw]
        }
    
    @staticmethod
    def detect_issues(cursor_logs, ruler_logs):
        """Детектувати проблеми cursor tracking"""
        issues = []
        tolerance = 0.1  # 0.1mm допуск
        
        # 1. CURSOR != RULER UPDATE
        if cursor_logs and ruler_logs['h_update']:
            last_cursor = cursor_logs[-1]
            last_h_update = ruler_logs['h_update'][-1]
            last_v_update = ruler_logs['v_update'][-1]
            
            if abs(last_cursor[0] - last_h_update) > tolerance:
                issues.append({
                    'type': 'CURSOR_RULER_MISMATCH_H',
                    'desc': f'Cursor X={last_cursor[0]:.2f}mm, Ruler update={last_h_update:.2f}mm'
                })
            
            if abs(last_cursor[1] - last_v_update) > tolerance:
                issues.append({
                    'type': 'CURSOR_RULER_MISMATCH_V',
                    'desc': f'Cursor Y={last_cursor[1]:.2f}mm, Ruler update={last_v_update:.2f}mm'
                })
        
        # 2. RULER UPDATE != DRAWN POSITION
        if ruler_logs['h_update'] and ruler_logs['h_draw']:
            mm_value = ruler_logs['h_update'][-1]
            px_drawn = ruler_logs['h_draw'][-1]
            # DPI = 203, scale = 2.5
            expected_px = mm_value * 203 / 25.4 * 2.5
            
            if abs(px_drawn - expected_px) > 2:  # 2px допуск
                issues.append({
                    'type': 'RULER_DRAW_INCORRECT_H',
                    'desc': f'Ruler H: update={mm_value}mm -> drawn={px_drawn}px (expected={expected_px:.0f}px)'
                })
        
        if ruler_logs['v_update'] and ruler_logs['v_draw']:
            mm_value = ruler_logs['v_update'][-1]
            px_drawn = ruler_logs['v_draw'][-1]
            expected_px = mm_value * 203 / 25.4 * 2.5
            
            if abs(px_drawn - expected_px) > 2:
                issues.append({
                    'type': 'RULER_DRAW_INCORRECT_V',
                    'desc': f'Ruler V: update={mm_value}mm -> drawn={px_drawn}px (expected={expected_px:.0f}px)'
                })
        
        return issues


def test_cursor_smart():
    """Умный тест cursor tracking с анализом логов"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    
    # Создать директорию логов если нужно
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Получить размер файла логов ДО теста
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # СИМУЛЯЦИЯ: переместить курсор на canvas в позицию 15mm, 10mm
    # Вызвать обработчик напрямую для гарантированного срабатывания
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent, QPoint
    
    dpi = 203
    x_mm = 15.0
    y_mm = 10.0
    
    # Создать mouse event
    scene_x = int(x_mm * dpi / 25.4)
    scene_y = int(y_mm * dpi / 25.4)
    viewport_pos = window.canvas.mapFromScene(QPointF(scene_x, scene_y))
    
    mouse_event = QMouseEvent(
        QEvent.MouseMove,
        QPointF(viewport_pos),
        Qt.NoButton,
        Qt.NoButton,
        Qt.NoModifier
    )
    
    # Вызвать обработчик
    window.canvas.mouseMoveEvent(mouse_event)
    app.processEvents()
    
    # Читать НОВЫЕ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализировать
    analyzer = CursorLogAnalyzer()
    cursor_logs = analyzer.parse_cursor_logs(new_logs)
    ruler_logs = analyzer.parse_ruler_logs(new_logs)
    issues = analyzer.detect_issues(cursor_logs, ruler_logs)
    
    print("=" * 60)
    print("[STAGE 1] CURSOR TRACKING - LOG ANALYSIS")
    print("=" * 60)
    print(f"\n[CURSOR] signals: {len(cursor_logs)}")
    print(f"[RULER-H] updates: {len(ruler_logs['h_update'])}")
    print(f"[RULER-V] updates: {len(ruler_logs['v_update'])}")
    
    if cursor_logs:
        last = cursor_logs[-1]
        print(f"Last cursor position: {last[0]:.2f}mm, {last[1]:.2f}mm")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[FAILURE] CURSOR TRACKING HAS ISSUES")
        print("=" * 60)
        return 1
    
    print("\n[OK] Cursor tracking works correctly")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_cursor_smart())
