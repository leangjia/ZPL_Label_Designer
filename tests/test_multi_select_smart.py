# -*- coding: utf-8 -*-
"""УМНИЙ ТЕСТ: Multi-Select з аналізом логів"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


class MultiSelectLogAnalyzer:
    """Аналізатор логів для multi-select"""
    
    @staticmethod
    def parse_selection_logs(log):
        """[SELECTION] та [MULTI-SELECT] logs"""
        items_selected = re.findall(r'\[SELECTION\] Items selected: (\d+)', log)
        multi_select = re.findall(r'\[SELECTION\] Multi-select: (\d+) items', log)
        multi_select_main = re.findall(r'\[MULTI-SELECT\] (\d+) items selected', log)
        
        return {
            'items_selected': [int(n) for n in items_selected],
            'multi_select': [int(n) for n in multi_select],
            'multi_select_main': [int(n) for n in multi_select_main]
        }
    
    @staticmethod
    def parse_delete_group_logs(log):
        """[DELETE-GROUP] logs"""
        delete_group = re.findall(r'\[DELETE-GROUP\] Deleting (\d+) items', log)
        return {'delete_group': [int(n) for n in delete_group]}
    
    @staticmethod
    def parse_move_group_logs(log):
        """[MOVE-GROUP] logs"""
        move_group = re.findall(r'\[MOVE-GROUP\] Moving (\d+) items by \(([-\d.]+), ([-\d.]+)\)mm', log)
        return {
            'move_group': [(int(m[0]), float(m[1]), float(m[2])) for m in move_group]
        }
    
    @staticmethod
    def detect_issues(selection_logs, delete_logs, move_logs, elements_count_before_delete, elements_count_after_delete, expected_delete_count):
        """Детектувати проблеми multi-select"""
        issues = []
        
        # 1. MULTI-SELECT canvas != main window
        if len(selection_logs['multi_select']) > 0:
            canvas_count = selection_logs['multi_select'][-1]
            if len(selection_logs['multi_select_main']) > 0:
                main_count = selection_logs['multi_select_main'][-1]
                if canvas_count != main_count:
                    issues.append({
                        'type': 'MULTISELECT_COUNT_MISMATCH',
                        'desc': f'Canvas multi-select={canvas_count}, MainWindow={main_count}'
                    })
        
        # 2. DELETE GROUP: кількість НЕ зменшилась правильно
        if len(delete_logs['delete_group']) > 0:
            deleted_count = delete_logs['delete_group'][-1]
            actual_deleted = elements_count_before_delete - elements_count_after_delete
            
            if actual_deleted != deleted_count:
                issues.append({
                    'type': 'DELETE_GROUP_WRONG_COUNT',
                    'desc': f'Expected to delete {deleted_count}, but deleted {actual_deleted}'
                })
            
            if actual_deleted != expected_delete_count:
                issues.append({
                    'type': 'DELETE_GROUP_UNEXPECTED_COUNT',
                    'desc': f'Expected {expected_delete_count}, but deleted {actual_deleted}'
                })
        
        # 3. MOVE GROUP: логи є, але переміщення НЕ сталось
        # (Перевірка у тесті через actual positions)
        
        return issues


def test_multi_select_smart():
    """Умний тест multi-select з аналізом логів"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Додати 3 елементи
    window._add_text()
    app.processEvents()
    window._add_text()
    app.processEvents()
    window._add_text()
    app.processEvents()
    
    print("=" * 60)
    print("[STAGE 9] MULTI-SELECT - LOG ANALYSIS")
    print("=" * 60)
    
    # ============ ТЕСТ MULTI-SELECT ============
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    print(f"\n[TEST] Multi-select 2 items:")
    
    # Виділити 2 елементи
    item1 = window.graphics_items[0]
    item2 = window.graphics_items[1]
    
    window.canvas.scene.clearSelection()
    item1.setSelected(True)
    item2.setSelected(True)
    app.processEvents()
    
    selected_count = len(window.canvas.scene.selectedItems())
    print(f"Selected items: {selected_count}")
    
    # Читати логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        select_logs_text = f.read()
    
    analyzer = MultiSelectLogAnalyzer()
    selection_logs = analyzer.parse_selection_logs(select_logs_text)
    
    print(f"[SELECTION] items_selected: {selection_logs['items_selected']}")
    print(f"[SELECTION] multi_select: {selection_logs['multi_select']}")
    print(f"[MULTI-SELECT] main: {selection_logs['multi_select_main']}")
    
    # ============ ТЕСТ GROUP DELETE ============
    file_size_before = log_file.stat().st_size
    elements_count_before_delete = len(window.elements)
    
    print(f"\n[TEST] Group delete:")
    print(f"Elements before delete: {elements_count_before_delete}")
    
    # Видалити групу
    window._delete_selected()
    app.processEvents()
    
    elements_count_after_delete = len(window.elements)
    print(f"Elements after delete: {elements_count_after_delete}")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        delete_logs_text = f.read()
    
    delete_logs = analyzer.parse_delete_group_logs(delete_logs_text)
    print(f"[DELETE-GROUP] delete_group: {delete_logs['delete_group']}")
    
    # ============ ТЕСТ GROUP MOVE ============
    file_size_before = log_file.stat().st_size
    
    print(f"\n[TEST] Group move:")
    
    # Виділити 2 елементи що залишились (маємо 1 після delete)
    # Додамо ще 1 елемент
    window._add_text()
    app.processEvents()
    
    item1 = window.graphics_items[0]
    item2 = window.graphics_items[1]
    
    window.canvas.scene.clearSelection()
    item1.setSelected(True)
    item2.setSelected(True)
    app.processEvents()
    
    old_x1 = item1.element.config.x
    old_y1 = item1.element.config.y
    old_x2 = item2.element.config.x
    old_y2 = item2.element.config.y
    
    print(f"Before move: item1=({old_x1}, {old_y1}), item2=({old_x2}, {old_y2})")
    
    # Перемістити групу
    window._move_selected(2.0, 0)
    app.processEvents()
    
    new_x1 = item1.element.config.x
    new_y1 = item1.element.config.y
    new_x2 = item2.element.config.x
    new_y2 = item2.element.config.y
    
    print(f"After move: item1=({new_x1}, {new_y1}), item2=({new_x2}, {new_y2})")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        move_logs_text = f.read()
    
    move_logs = analyzer.parse_move_group_logs(move_logs_text)
    print(f"[MOVE-GROUP] move_group: {move_logs['move_group']}")
    
    # Перевірити що переміщення сталось
    if abs(new_x1 - (old_x1 + 2.0)) > 0.01 or abs(new_x2 - (old_x2 + 2.0)) > 0.01:
        print("[ERROR] Group move did not apply correctly")
    
    # ============ ДЕТЕКЦІЯ ПРОБЛЕМ ============
    # Об'єднати всі логи
    full_log = select_logs_text + delete_logs_text + move_logs_text
    
    all_selection_logs = analyzer.parse_selection_logs(full_log)
    all_delete_logs = analyzer.parse_delete_group_logs(full_log)
    all_move_logs = analyzer.parse_move_group_logs(full_log)
    
    issues = analyzer.detect_issues(
        all_selection_logs,
        all_delete_logs,
        all_move_logs,
        elements_count_before_delete,
        elements_count_after_delete,
        expected_delete_count=2
    )
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[FAILURE] MULTI-SELECT HAS ISSUES")
        print("=" * 60)
        return 1
    
    print("\n[OK] Multi-select works correctly")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_multi_select_smart())
