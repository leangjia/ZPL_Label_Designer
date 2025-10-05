# -*- coding: utf-8 -*-
"""УМНЫЙ ТЕСТ: Zoom to Point с анализом логов"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF, Qt
from PySide6.QtTest import QTest
from gui.main_window import MainWindow


class ZoomLogAnalyzer:
    """Анализатор логов для zoom"""
    
    @staticmethod
    def parse_zoom_logs(log):
        """[ZOOM] Before/After scale, cursor_pos"""
        before = re.findall(r'\[ZOOM\] Before: scale=([\d.]+), cursor_pos=\(([\d.]+), ([\d.]+)\)', log)
        after = re.findall(r'\[ZOOM\] After: scale=([\d.]+), cursor_pos=\(([\d.]+), ([\d.]+)\)', log)
        return {
            'before': [(float(m[0]), float(m[1]), float(m[2])) for m in before],
            'after': [(float(m[0]), float(m[1]), float(m[2])) for m in after]
        }
    
    @staticmethod
    def parse_ruler_scale_logs(log):
        """[RULER-SCALE] Scale update"""
        pattern = r'\[RULER-SCALE\] Updated to: ([\d.]+)'
        return [float(m) for m in re.findall(pattern, log)]
    
    @staticmethod
    def detect_issues(zoom_logs, ruler_scales):
        """Детектувати проблеми zoom"""
        issues = []
        
        # 1. ZOOM НЕ ДО КУРСОРА (cursor_pos змінилась замість залишитись)
        if zoom_logs['before'] and zoom_logs['after']:
            before_cursor = (zoom_logs['before'][-1][1], zoom_logs['before'][-1][2])
            after_cursor = (zoom_logs['after'][-1][1], zoom_logs['after'][-1][2])
            
            tolerance = 5.0  # 5px допуск через округлення
            if abs(before_cursor[0] - after_cursor[0]) > tolerance:
                issues.append({
                    'type': 'ZOOM_NOT_TO_CURSOR_X',
                    'desc': f'Cursor X shifted from {before_cursor[0]:.1f}px to {after_cursor[0]:.1f}px'
                })
            
            if abs(before_cursor[1] - after_cursor[1]) > tolerance:
                issues.append({
                    'type': 'ZOOM_NOT_TO_CURSOR_Y',
                    'desc': f'Cursor Y shifted from {before_cursor[1]:.1f}px to {after_cursor[1]:.1f}px'
                })
        
        # 2. RULER SCALE != CANVAS SCALE
        if zoom_logs['after'] and ruler_scales:
            canvas_scale = zoom_logs['after'][-1][0]
            ruler_scale = ruler_scales[-1]
            
            if abs(canvas_scale - ruler_scale) > 0.01:
                issues.append({
                    'type': 'RULER_SCALE_MISMATCH',
                    'desc': f'Canvas scale={canvas_scale:.2f}, Ruler scale={ruler_scale:.2f}'
                })
        
        return issues


def test_zoom_smart():
    """Умный тест zoom с анализом логов"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    
    # Создать директорию логов если нужно
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Получить размер файла логов ДО теста
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # СИМУЛЯЦИЯ: zoom на точке (100, 100)
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QWheelEvent
    
    # Центр viewport
    center = window.canvas.viewport().rect().center()
    
    # Создать wheel event (zoom in)
    wheel_event = QWheelEvent(
        QPointF(center),
        QPointF(center),  # global position
        QPoint(0, 0),
        QPoint(0, 120),  # Positive = zoom in
        Qt.NoButton,
        Qt.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False
    )
    
    # Вызвать обработчик напрямую
    window.canvas.wheelEvent(wheel_event)
    app.processEvents()
    
    # Читать НОВЫЕ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализировать
    analyzer = ZoomLogAnalyzer()
    zoom_logs = analyzer.parse_zoom_logs(new_logs)
    ruler_scales = analyzer.parse_ruler_scale_logs(new_logs)
    issues = analyzer.detect_issues(zoom_logs, ruler_scales)
    
    print("=" * 60)
    print("[STAGE 2] ZOOM TO POINT - LOG ANALYSIS")
    print("=" * 60)
    print(f"\n[ZOOM] Before entries: {len(zoom_logs['before'])}")
    print(f"[ZOOM] After entries: {len(zoom_logs['after'])}")
    print(f"[RULER-SCALE] updates: {len(ruler_scales)}")
    
    if zoom_logs['before']:
        before = zoom_logs['before'][-1]
        print(f"Before zoom: scale={before[0]:.2f}, cursor=({before[1]:.1f}, {before[2]:.1f})")
    
    if zoom_logs['after']:
        after = zoom_logs['after'][-1]
        print(f"After zoom: scale={after[0]:.2f}, cursor=({after[1]:.1f}, {after[2]:.1f})")
    
    if ruler_scales:
        print(f"Ruler scale: {ruler_scales[-1]:.2f}")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[FAILURE] ZOOM HAS ISSUES")
        print("=" * 60)
        return 1
    
    print("\n[OK] Zoom works correctly")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_zoom_smart())
