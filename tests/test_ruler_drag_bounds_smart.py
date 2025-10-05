# -*- coding: utf-8 -*-
"""Умный тест: bounds highlight следует за элементом при drag"""

import os
import sys
import re
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from gui.main_window import MainWindow  # noqa: E402
from utils.logger import logger  # noqa: E402


class BoundsDragAnalyzer:
    """Анализатор логов для bounds during drag"""

    @staticmethod
    def parse_bounds_logs(log_content: str):
        """Извлечь логи обновления bounds"""
        pattern = r"\[RULER-(H|V)\] Bounds updated: start=([\d.\-]+)mm, end=([\d.\-]+)mm, width=([\d.\-]+)mm"
        matches = re.findall(pattern, log_content)
        return {
            'h_bounds': [(float(m[1]), float(m[2])) for m in matches if m[0] == 'H'],
            'v_bounds': [(float(m[1]), float(m[2])) for m in matches if m[0] == 'V']
        }

    @staticmethod
    def parse_drag_logs(log_content: str):
        """Извлечь логи drag событий"""
        pattern = r"\[ITEM-DRAG\] Position changed: bounds update needed"
        return len(re.findall(pattern, log_content))

    @staticmethod
    def detect_issues(bounds_logs, drag_count, expected_position):
        """Детектировать проблемы"""
        issues = []

        # 1. Bounds НЕ обновлялись во время drag
        if drag_count > 0 and len(bounds_logs['h_bounds']) == 0:
            issues.append({
                'type': 'NO_BOUNDS_UPDATE',
                'desc': f'Drag happened {drag_count} times but bounds never updated'
            })

        # 2. Количество обновлений bounds != количество drag событий (по горизонтали)
        if bounds_logs['h_bounds'] and len(bounds_logs['h_bounds']) != drag_count:
            issues.append({
                'type': 'BOUNDS_UPDATE_COUNT_MISMATCH',
                'desc': f'Drag: {drag_count}, Bounds updates: {len(bounds_logs["h_bounds"])}'
            })

        # 3. Финальная позиция bounds != ожидаемая
        if bounds_logs['h_bounds']:
            final_h_bounds = bounds_logs['h_bounds'][-1]
            expected_x = expected_position[0]
            if abs(final_h_bounds[0] - expected_x) > 0.5:
                issues.append({
                    'type': 'BOUNDS_POSITION_INCORRECT',
                    'desc': f'Expected x={expected_x:.2f}mm, got {final_h_bounds[0]:.2f}mm'
                })

        if bounds_logs['v_bounds'] and len(bounds_logs['v_bounds']) != drag_count:
            issues.append({
                'type': 'VERTICAL_BOUNDS_UPDATE_COUNT_MISMATCH',
                'desc': f'Drag: {drag_count}, V bounds updates: {len(bounds_logs["v_bounds"])}'
            })

        return issues


def test_ruler_bounds_during_drag():
    """Bounds highlight следует за элементом при drag"""

    log_file = ROOT_DIR / 'logs' / 'zpl_designer.log'
    log_file.parent.mkdir(exist_ok=True)

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()

    # Добавить text element и выбрать его
    window._add_text()
    app.processEvents()

    assert window.graphics_items, "Text graphics item not created"
    text_item = window.graphics_items[0]
    text_item.setSelected(True)
    app.processEvents()

    file_size_before = log_file.stat().st_size if log_file.exists() else 0

    # Симуляция drag через последовательные setPos (snap применяется внутри)
    new_positions = [
        QPointF(100, 100),
        QPointF(150, 120),
        QPointF(200, 140),
    ]

    for new_pos in new_positions:
        text_item.setPos(new_pos)
        app.processEvents()

    # Убедиться, что логи сброшены в файл
    for handler in logger.handlers:
        if hasattr(handler, 'flush'):
            handler.flush()

    with log_file.open('r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()

    analyzer = BoundsDragAnalyzer()
    bounds_logs = analyzer.parse_bounds_logs(new_logs)
    drag_count = analyzer.parse_drag_logs(new_logs)

    final_expected_x = text_item.element.config.x

    issues = analyzer.detect_issues(bounds_logs, drag_count, (final_expected_x, 0))

    print('=' * 60)
    print('[RULER BOUNDS DRAG] LOG ANALYSIS')
    print('=' * 60)
    print(f'Drag events: {drag_count}')
    print(f'H bounds updates: {len(bounds_logs["h_bounds"])}')
    print(f'V bounds updates: {len(bounds_logs["v_bounds"])}')

    if bounds_logs['h_bounds']:
        print('\nH bounds positions:')
        for i, (start, end) in enumerate(bounds_logs['h_bounds'], 1):
            print(f'  {i}. start={start:.2f}mm, end={end:.2f}mm')

    if bounds_logs['v_bounds']:
        print('\nV bounds positions:')
        for i, (start, end) in enumerate(bounds_logs['v_bounds'], 1):
            print(f'  {i}. start={start:.2f}mm, end={end:.2f}mm')

    window.close()
    app.processEvents()

    assert not issues, f"Detected issues: {issues}\nLogs:\n{new_logs}"


if __name__ == '__main__':
    sys.exit(0 if test_ruler_bounds_during_drag() is None else 1)
