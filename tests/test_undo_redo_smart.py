# -*- coding: utf-8 -*-
"""УМНЫЙ ТЕСТ: Undo/Redo з аналізом логів"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


class UndoRedoLogAnalyzer:
    """Аналізатор логів для undo/redo"""
    
    @staticmethod
    def parse_undo_stack_logs(log):
        """[UNDO-STACK] logs"""
        initialized = len(re.findall(r'\[UNDO-STACK\] Initialized', log))
        return {'initialized': initialized}
    
    @staticmethod
    def parse_undo_cmd_logs(log):
        """[UNDO-CMD] logs"""
        add_element = len(re.findall(r'\[UNDO-CMD\] AddElementCommand created', log))
        delete_element = len(re.findall(r'\[UNDO-CMD\] DeleteElementCommand created', log))
        move_element = re.findall(r'\[UNDO-CMD\] MoveElementCommand: \(([\d.]+), ([\d.]+)\) -> \(([\d.]+), ([\d.]+)\)', log)
        
        return {
            'add_element': add_element,
            'delete_element': delete_element,
            'move_element': [(float(m[0]), float(m[1]), float(m[2]), float(m[3])) for m in move_element]
        }
    
    @staticmethod
    def parse_undo_action_logs(log):
        """[UNDO-ACTION], [UNDO] REDO/UNDO logs"""
        undo_action = re.findall(r'\[UNDO-ACTION\] Undo: (.+)', log)
        redo_action = re.findall(r'\[UNDO-ACTION\] Redo: (.+)', log)
        nothing_to_undo = len(re.findall(r'\[UNDO-ACTION\] Nothing to undo', log))
        nothing_to_redo = len(re.findall(r'\[UNDO-ACTION\] Nothing to redo', log))
        
        undo_redo_add = len(re.findall(r'\[UNDO\] REDO AddElement', log))
        undo_undo_add = len(re.findall(r'\[UNDO\] UNDO AddElement', log))
        undo_redo_delete = len(re.findall(r'\[UNDO\] REDO DeleteElement', log))
        undo_undo_delete = len(re.findall(r'\[UNDO\] UNDO DeleteElement', log))
        undo_redo_move = len(re.findall(r'\[UNDO\] REDO MoveElement', log))
        undo_undo_move = len(re.findall(r'\[UNDO\] UNDO MoveElement', log))
        
        return {
            'undo_action': undo_action,
            'redo_action': redo_action,
            'nothing_to_undo': nothing_to_undo,
            'nothing_to_redo': nothing_to_redo,
            'undo_redo_add': undo_redo_add,
            'undo_undo_add': undo_undo_add,
            'undo_redo_delete': undo_redo_delete,
            'undo_undo_delete': undo_undo_delete,
            'undo_redo_move': undo_redo_move,
            'undo_undo_move': undo_undo_move
        }
    
    @staticmethod
    def parse_drag_logs(log):
        """[DRAG-START], [DRAG-END] logs"""
        drag_start = re.findall(r'\[DRAG-START\] Pos: \(([\d.]+), ([\d.]+)\)', log)
        drag_end_creating = len(re.findall(r'\[DRAG-END\] Creating MoveCommand', log))
        
        return {
            'drag_start': [(float(m[0]), float(m[1])) for m in drag_start],
            'drag_end_creating': drag_end_creating
        }
    
    @staticmethod
    def detect_issues(undo_cmd_logs, undo_action_logs, drag_logs, elements_count_after_add, elements_count_after_undo):
        """Детектувати проблеми undo/redo"""
        issues = []
        
        # 1. ADD COMMAND створено, але UNDO НЕ працює
        if undo_cmd_logs['add_element'] > 0:
            if undo_action_logs['undo_undo_add'] == 0:
                issues.append({
                    'type': 'ADD_UNDO_NOT_WORKING',
                    'desc': f"AddCommand created={undo_cmd_logs['add_element']}, but undo_add=0"
                })
        
        # 2. UNDO: кількість елементів НЕ зменшилась
        if undo_action_logs['undo_undo_add'] > 0:
            # Після undo add, має бути -1 елемент
            if elements_count_after_undo != elements_count_after_add - 1:
                issues.append({
                    'type': 'UNDO_ADD_WRONG_COUNT',
                    'desc': f"After add={elements_count_after_add}, after undo={elements_count_after_undo}, expected -1"
                })
        
        # 3. MOVE COMMAND: drag_start є, але MoveCommand НЕ створено
        if len(drag_logs['drag_start']) > 0:
            if drag_logs['drag_end_creating'] != len(drag_logs['drag_start']):
                issues.append({
                    'type': 'MOVE_COMMAND_NOT_CREATED',
                    'desc': f"Drag start={len(drag_logs['drag_start'])}, but MoveCommand created={drag_logs['drag_end_creating']}"
                })
        
        # 4. DELETE COMMAND створено, але UNDO НЕ працює
        if undo_cmd_logs['delete_element'] > 0:
            if undo_action_logs['undo_undo_delete'] == 0:
                issues.append({
                    'type': 'DELETE_UNDO_NOT_WORKING',
                    'desc': f"DeleteCommand created={undo_cmd_logs['delete_element']}, but undo_delete=0"
                })
        
        # 5. REDO після UNDO НЕ працює
        if undo_action_logs['undo_undo_add'] > 0:
            if undo_action_logs['undo_redo_add'] == 0:
                issues.append({
                    'type': 'REDO_NOT_WORKING',
                    'desc': f"Undo add={undo_action_logs['undo_undo_add']}, but redo add=0"
                })
        
        return issues


def test_undo_redo_smart():
    """Умний тест undo/redo з аналізом логів"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    print("=" * 60)
    print("[STAGE 8] UNDO/REDO - LOG ANALYSIS")
    print("=" * 60)
    
    # ============ ТЕСТ ADD + UNDO ============
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    print(f"\n[TEST] Add element + Undo:")
    elements_count_before = len(window.elements)
    print(f"Elements before add: {elements_count_before}")
    
    # Додати елемент
    window._add_text()
    app.processEvents()
    
    elements_count_after_add = len(window.elements)
    print(f"Elements after add: {elements_count_after_add}")
    
    # Undo
    window._undo()
    app.processEvents()
    
    elements_count_after_undo = len(window.elements)
    print(f"Elements after undo: {elements_count_after_undo}")
    
    # Читати логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        add_undo_logs_text = f.read()
    
    analyzer = UndoRedoLogAnalyzer()
    undo_cmd_logs = analyzer.parse_undo_cmd_logs(add_undo_logs_text)
    undo_action_logs = analyzer.parse_undo_action_logs(add_undo_logs_text)
    
    print(f"[UNDO-CMD] add_element: {undo_cmd_logs['add_element']}")
    print(f"[UNDO-ACTION] undo_action: {undo_action_logs['undo_action']}")
    print(f"[UNDO] undo_add: {undo_action_logs['undo_undo_add']}")
    
    # ============ ТЕСТ REDO ============
    file_size_before = log_file.stat().st_size
    
    print(f"\n[TEST] Redo:")
    
    # Redo
    window._redo()
    app.processEvents()
    
    elements_count_after_redo = len(window.elements)
    print(f"Elements after redo: {elements_count_after_redo}")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        redo_logs_text = f.read()
    
    redo_action_logs = analyzer.parse_undo_action_logs(redo_logs_text)
    print(f"[UNDO-ACTION] redo_action: {redo_action_logs['redo_action']}")
    print(f"[UNDO] redo_add: {redo_action_logs['undo_redo_add']}")
    
    # ============ ТЕСТ MOVE + UNDO ============
    file_size_before = log_file.stat().st_size
    
    print(f"\n[TEST] Move + Undo:")
    
    # Симулювати drag (через eventFilter)
    # Спрощено: викликаємо MoveCommand напряму
    item = window.graphics_items[0]
    old_x = item.element.config.x
    old_y = item.element.config.y
    new_x = old_x + 5.0
    new_y = old_y + 5.0
    
    from core.undo_commands import MoveElementCommand
    move_cmd = MoveElementCommand(item.element, item, old_x, old_y, new_x, new_y)
    window.undo_stack.push(move_cmd)
    app.processEvents()
    
    print(f"Moved from ({old_x}, {old_y}) to ({new_x}, {new_y})")
    
    # Undo move
    window._undo()
    app.processEvents()
    
    current_x = item.element.config.x
    current_y = item.element.config.y
    print(f"After undo move: ({current_x}, {current_y})")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        move_logs_text = f.read()
    
    move_undo_cmd_logs = analyzer.parse_undo_cmd_logs(move_logs_text)
    move_undo_action_logs = analyzer.parse_undo_action_logs(move_logs_text)
    
    print(f"[UNDO-CMD] move_element: {move_undo_cmd_logs['move_element']}")
    print(f"[UNDO] undo_move: {move_undo_action_logs['undo_undo_move']}")
    
    # ============ ДЕТЕКЦІЯ ПРОБЛЕМ ============
    # Об'єднати всі логи
    full_log = add_undo_logs_text + redo_logs_text + move_logs_text
    
    all_undo_cmd_logs = analyzer.parse_undo_cmd_logs(full_log)
    all_undo_action_logs = analyzer.parse_undo_action_logs(full_log)
    all_drag_logs = analyzer.parse_drag_logs(full_log)
    
    issues = analyzer.detect_issues(
        all_undo_cmd_logs,
        all_undo_action_logs,
        all_drag_logs,
        elements_count_after_add,
        elements_count_after_undo
    )
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[FAILURE] UNDO/REDO HAS ISSUES")
        print("=" * 60)
        return 1
    
    print("\n[OK] Undo/Redo works correctly")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_undo_redo_smart())
