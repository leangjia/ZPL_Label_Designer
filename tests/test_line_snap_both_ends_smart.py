# -*- coding: utf-8 -*-
"""Умный тест Line snap to grid для ОБОИХ концов"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QGraphicsItem
from PySide6.QtCore import QPointF
from gui.main_window import MainWindow
from core.elements.shape_element import LineElement, LineConfig, GraphicsLineItem
from utils.logger import logger
import re


class LineSnapBothEndsAnalyzer:
    """Анализатор логов Line snap для обоих концов"""
    
    @staticmethod
    def parse_line_snap_logs(log_content):
        """Парсить логи snap для Line"""
        
        # [LINE-DRAG] Start before snap: (10.45, 10.23)mm
        start_before = re.findall(
            r'\[LINE-DRAG\] Start before snap: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-DRAG] End before snap: (25.67, 10.89)mm
        end_before = re.findall(
            r'\[LINE-DRAG\] End before snap: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-SNAP] Start: (10.45, 10.23) -> (10.00, 10.00)mm
        start_snap = re.findall(
            r'\[LINE-SNAP\] Start: \(([\d.]+), ([\d.]+)\) -> \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-SNAP] End: (25.67, 10.89) -> (25.00, 11.00)mm
        end_snap = re.findall(
            r'\[LINE-SNAP\] End: \(([\d.]+), ([\d.]+)\) -> \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-FINAL] Start: (10.00, 10.00)mm
        final_start = re.findall(
            r'\[LINE-FINAL\] Start: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-FINAL] End: (25.00, 11.00)mm
        final_end = re.findall(
            r'\[LINE-FINAL\] End: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        return {
            'start_before': [(float(m[0]), float(m[1])) for m in start_before],
            'end_before': [(float(m[0]), float(m[1])) for m in end_before],
            'start_snap': [
                {'before': (float(m[0]), float(m[1])), 'after': (float(m[2]), float(m[3]))}
                for m in start_snap
            ],
            'end_snap': [
                {'before': (float(m[0]), float(m[1])), 'after': (float(m[2]), float(m[3]))}
                for m in end_snap
            ],
            'final_start': [(float(m[0]), float(m[1])) for m in final_start],
            'final_end': [(float(m[0]), float(m[1])) for m in final_end]
        }
    
    @staticmethod
    def detect_issues(logs_dict, grid_size=1.0):
        """Детектировать 5 типов проблем"""
        issues = []
        
        # 1. END SNAP НЕ ПРОИЗОШЕЛ (логи end_snap пустые)
        if not logs_dict['end_snap']:
            issues.append({
                'type': 'END_SNAP_NOT_APPLIED',
                'desc': f"End snap логи отсутствуют - snap работает только для start point!"
            })
            return issues  # Дальше проверять нет смысла
        
        # 2. START SNAP INCORRECT (snapped координата НЕ кратна grid_size)
        if logs_dict['start_snap']:
            start_snapped = logs_dict['start_snap'][-1]['after']
            if start_snapped[0] % grid_size > 0.01 or start_snapped[1] % grid_size > 0.01:
                issues.append({
                    'type': 'START_SNAP_NOT_ON_GRID',
                    'desc': f"Start snapped to ({start_snapped[0]}, {start_snapped[1]}) но НЕ кратно {grid_size}mm"
                })
        
        # 3. END SNAP INCORRECT (snapped координата НЕ кратна grid_size)
        if logs_dict['end_snap']:
            end_snapped = logs_dict['end_snap'][-1]['after']
            if end_snapped[0] % grid_size > 0.01 or end_snapped[1] % grid_size > 0.01:
                issues.append({
                    'type': 'END_SNAP_NOT_ON_GRID',
                    'desc': f"End snapped to ({end_snapped[0]}, {end_snapped[1]}) но НЕ кратно {grid_size}mm"
                })
        
        # 4. SNAP != FINAL (snap показал одно, final другое)
        if logs_dict['start_snap'] and logs_dict['final_start']:
            start_snap_result = logs_dict['start_snap'][-1]['after']
            final_start_result = logs_dict['final_start'][-1]
            if abs(start_snap_result[0] - final_start_result[0]) > 0.01 or \
               abs(start_snap_result[1] - final_start_result[1]) > 0.01:
                issues.append({
                    'type': 'START_SNAP_FINAL_MISMATCH',
                    'desc': f"Start snap={start_snap_result}, final={final_start_result} - НЕ совпадают!"
                })
        
        if logs_dict['end_snap'] and logs_dict['final_end']:
            end_snap_result = logs_dict['end_snap'][-1]['after']
            final_end_result = logs_dict['final_end'][-1]
            if abs(end_snap_result[0] - final_end_result[0]) > 0.01 or \
               abs(end_snap_result[1] - final_end_result[1]) > 0.01:
                issues.append({
                    'type': 'END_SNAP_FINAL_MISMATCH',
                    'desc': f"End snap={end_snap_result}, final={final_end_result} - НЕ совпадают!"
                })
        
        # 5. FINAL НЕ НА GRID (финальные координаты НЕ кратны grid_size)
        if logs_dict['final_start']:
            final_s = logs_dict['final_start'][-1]
            if final_s[0] % grid_size > 0.01 or final_s[1] % grid_size > 0.01:
                issues.append({
                    'type': 'FINAL_START_NOT_ON_GRID',
                    'desc': f"Final start ({final_s[0]}, {final_s[1]}) НЕ на grid {grid_size}mm"
                })
        
        if logs_dict['final_end']:
            final_e = logs_dict['final_end'][-1]
            if final_e[0] % grid_size > 0.01 or final_e[1] % grid_size > 0.01:
                issues.append({
                    'type': 'FINAL_END_NOT_ON_GRID',
                    'desc': f"Final end ({final_e[0]}, {final_e[1]}) НЕ на grid {grid_size}mm"
                })
        
        return issues


def test_line_snap_both_ends():
    """Умный тест Line snap для обоих концов"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    print("=" * 60)
    print("[TEST] Line Snap to Grid - BOTH ENDS")
    print("=" * 60)
    
    # ТЕСТ: Создать Line и сдвинуть чтобы вызвать snap
    print("\n[TEST 1] Create Line and drag to trigger snap")
    
    # Создать Line элемент: start (9.55, 9.67), end (24.89, 10.23)
    config = LineConfig(x=9.55, y=9.67, x2=24.89, y2=10.23, thickness=1.0, color='black')
    line = LineElement(config)
    
    # Добавить в canvas
    graphics_line = GraphicsLineItem(line, dpi=203, canvas=window.canvas)
    window.canvas.scene.addItem(graphics_line)
    window.elements.append(line)
    window.graphics_items.append(graphics_line)
    
    app.processEvents()
    
    print(f"  Before drag: start=({line.config.x:.2f}, {line.config.y:.2f}), end=({line.config.x2:.2f}, {line.config.y2:.2f})mm")
    
    # Симулировать drag через itemChange (сдвиг на 1px чтобы вызвать snap)
    new_pos = QPointF(graphics_line.pos().x() + 1.0, graphics_line.pos().y() + 1.0)
    snapped_pos = graphics_line.itemChange(QGraphicsItem.ItemPositionChange, new_pos)
    
    if snapped_pos != new_pos:
        graphics_line.setPos(snapped_pos)
        graphics_line.itemChange(QGraphicsItem.ItemPositionHasChanged, None)
    
    app.processEvents()
    
    print(f"  After drag: start=({line.config.x:.2f}, {line.config.y:.2f}), end=({line.config.x2:.2f}, {line.config.y2:.2f})mm")
    
    # Читать логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализ
    analyzer = LineSnapBothEndsAnalyzer()
    logs = analyzer.parse_line_snap_logs(new_logs)
    issues = analyzer.detect_issues(logs, grid_size=1.0)
    
    # Результат
    print("\n" + "=" * 60)
    print("[LINE SNAP BOTH ENDS] LOG ANALYSIS")
    print("=" * 60)
    print(f"Start snap logs: {len(logs['start_snap'])}")
    print(f"End snap logs: {len(logs['end_snap'])}")
    print(f"Final start logs: {len(logs['final_start'])}")
    print(f"Final end logs: {len(logs['final_end'])}")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] LINE SNAP HAS ISSUES")
        return 1
    
    print("\n[OK] Line snap for BOTH ends works correctly")
    
    # Финальные проверки
    assert line.config.x % 1.0 < 0.01, f"Start X {line.config.x} должно быть кратно 1mm"
    assert line.config.y % 1.0 < 0.01, f"Start Y {line.config.y} должно быть кратно 1mm"
    assert line.config.x2 % 1.0 < 0.01, f"End X {line.config.x2} должно быть кратно 1mm"
    assert line.config.y2 % 1.0 < 0.01, f"End Y {line.config.y2} должно быть кратно 1mm"
    
    print(f"\nFinal verification:")
    print(f"  Start: ({line.config.x:.2f}, {line.config.y:.2f})mm on grid ✓")
    print(f"  End: ({line.config.x2:.2f}, {line.config.y2:.2f})mm on grid ✓")
    
    return 0


if __name__ == "__main__":
    exit(test_line_snap_both_ends())
