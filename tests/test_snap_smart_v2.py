# -*- coding: utf-8 -*-
"""УМНЫЙ тест v2 - анализ лог-файла после выполнения"""

import sys
import re
import time
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from gui.main_window import MainWindow


class LogAnalyzer:
    """Анализатор логов для поиска проблем"""
    
    @staticmethod
    def parse_snap_logs(log_content):
        """Извлечь все [SNAP] записи"""
        pattern = r'\[SNAP\] ([\d.]+)mm, ([\d.]+)mm -> ([\d.]+)mm, ([\d.]+)mm'
        matches = re.findall(pattern, log_content)
        return [(float(m[0]), float(m[1]), float(m[2]), float(m[3])) for m in matches]
    
    @staticmethod
    def parse_final_pos_logs(log_content):
        """Извлечь все [FINAL-POS] записи"""
        before_pattern = r'\[FINAL-POS\] Before snap: ([\d.]+)mm, ([\d.]+)mm'
        after_pattern = r'\[FINAL-POS\] After snap: ([\d.]+)mm, ([\d.]+)mm'
        saved_pattern = r'\[FINAL-POS\] Saved to element: \(([\d.]+), ([\d.]+)\)'
        
        before_matches = re.findall(before_pattern, log_content)
        after_matches = re.findall(after_pattern, log_content)
        saved_matches = re.findall(saved_pattern, log_content)
        
        return {
            'before': [(float(m[0]), float(m[1])) for m in before_matches],
            'after': [(float(m[0]), float(m[1])) for m in after_matches],
            'saved': [(float(m[0]), float(m[1])) for m in saved_matches]
        }
    
    @staticmethod
    def detect_snap_issues(snap_logs, final_logs):
        """Детектировать проблемы snap"""
        issues = []
        
        # Проверка 1: Последний SNAP должен совпадать с FINAL-POS After
        if snap_logs and final_logs['after']:
            last_snap = snap_logs[-1]  # (from_x, from_y, to_x, to_y)
            last_final = final_logs['after'][-1]  # (x, y)
            
            if abs(last_snap[2] - last_final[0]) > 0.01 or abs(last_snap[3] - last_final[1]) > 0.01:
                issues.append({
                    'type': 'SNAP_FINAL_MISMATCH',
                    'desc': f'SNAP показал {last_snap[2]:.1f}mm, но FINAL-POS After = {last_final[0]:.2f}mm',
                    'snap': last_snap,
                    'final': last_final
                })
        
        # Проверка 2: FINAL-POS Before должен отличаться от After если snap включен
        if final_logs['before'] and final_logs['after']:
            for i, (before, after) in enumerate(zip(final_logs['before'], final_logs['after'])):
                if before == after:  # Snap НЕ сработал!
                    # Проверить что это не уже снепленное значение
                    if before[0] % 2.0 != 0 or before[1] % 2.0 != 0:  # Не кратно grid_step
                        issues.append({
                            'type': 'NO_SNAP_IN_FINAL',
                            'desc': f'FINAL-POS Before={before[0]:.2f}mm, After={after[0]:.2f}mm (не снепнуло!)',
                            'position': i,
                            'before': before,
                            'after': after
                        })
        
        # Проверка 3: Saved должен совпадать с After
        if final_logs['after'] and final_logs['saved']:
            for after, saved in zip(final_logs['after'], final_logs['saved']):
                if abs(after[0] - saved[0]) > 0.01 or abs(after[1] - saved[1]) > 0.01:
                    issues.append({
                        'type': 'FINAL_SAVED_MISMATCH',
                        'desc': f'FINAL-POS After={after[0]:.2f}mm, но Saved={saved[0]:.2f}mm',
                        'after': after,
                        'saved': saved
                    })
        
        return issues


def test_snap_with_log_file_analysis():
    """Тест с чтением лог-файла"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    
    # Запомнить размер файла ДО теста
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    window.snap_enabled = True
    window._add_text()
    item = window.graphics_items[0]
    item.snap_enabled = True
    
    # Выбрать для PropertyPanel
    window.canvas.scene.clearSelection()
    item.setSelected(True)
    app.processEvents()
    
    # Тест: переместить на 6.55mm (должно снепнуться к 6.0mm)
    target_x_mm = 6.55
    target_y_mm = 2.0
    
    target_x_px = item._mm_to_px(target_x_mm)
    target_y_px = item._mm_to_px(target_y_mm)
    
    item.setPos(QPointF(target_x_px, target_y_px))
    app.processEvents()
    
    # Подождать чтобы логи записались
    time.sleep(0.1)
    
    # Прочитать НОВЫЕ логи (после file_size_before)
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализировать логи
    analyzer = LogAnalyzer()
    snap_logs = analyzer.parse_snap_logs(new_logs)
    final_logs = analyzer.parse_final_pos_logs(new_logs)
    issues = analyzer.detect_snap_issues(snap_logs, final_logs)
    
    # Вывести результаты анализа
    print("=" * 60)
    print("LOG ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"\n[SNAP] entries found: {len(snap_logs)}")
    if snap_logs:
        print("Last SNAP:")
        last = snap_logs[-1]
        print(f"  {last[0]:.2f}mm, {last[1]:.2f}mm -> {last[2]:.1f}mm, {last[3]:.1f}mm")
    
    print(f"\n[FINAL-POS] entries found:")
    print(f"  Before: {len(final_logs['before'])}")
    print(f"  After: {len(final_logs['after'])}")
    print(f"  Saved: {len(final_logs['saved'])}")
    
    if final_logs['after']:
        print("Last FINAL-POS After:")
        last = final_logs['after'][-1]
        print(f"  {last[0]:.2f}mm, {last[1]:.2f}mm")
    
    # Проверить результат
    actual_x = item.element.config.x
    actual_y = item.element.config.y
    expected_x = 6.0
    expected_y = 2.0
    
    print(f"\nFinal element position: ({actual_x:.2f}, {actual_y:.2f})")
    print(f"Expected position: ({expected_x:.1f}, {expected_y:.1f})")
    
    # Вывести обнаруженные проблемы
    if issues:
        print("\n" + "!" * 60)
        print(f"DETECTED {len(issues)} ISSUE(S):")
        print("!" * 60)
        for i, issue in enumerate(issues, 1):
            print(f"\n{i}. {issue['type']}")
            print(f"   {issue['desc']}")
            for key, val in issue.items():
                if key not in ['type', 'desc']:
                    print(f"   {key}: {val}")
    else:
        print("\n[OK] No issues detected in logs")
    
    # Проверить финальный результат
    tolerance = 0.01
    position_ok = abs(actual_x - expected_x) < tolerance and abs(actual_y - expected_y) < tolerance
    
    if position_ok and not issues:
        print("\n" + "=" * 60)
        print("[SUCCESS] SNAP WORKS CORRECTLY")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("[FAILURE] SNAP HAS ISSUES")
        print("=" * 60)
        if not position_ok:
            print(f"Position mismatch: got ({actual_x:.2f}, {actual_y:.2f}), expected ({expected_x:.1f}, {expected_y:.1f})")
        if issues:
            print(f"Log analysis found {len(issues)} issue(s)")
        return 1


if __name__ == "__main__":
    sys.exit(test_snap_with_log_file_analysis())
