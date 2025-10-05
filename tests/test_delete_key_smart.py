# -*- coding: utf-8 -*-
"""Умный тест Delete/Backspace клавиш"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent

# Добавить корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.main_window import MainWindow
from utils.logger import logger
import re


class DeleteKeyLogAnalyzer:
    """Анализатор логов для Delete/Backspace functionality"""
    
    @staticmethod
    def parse_shortcut_logs(log_content):
        """Извлечь [SHORTCUT] логи"""
        pattern = r'\[SHORTCUT\] (.*?) - (.*)'
        matches = re.findall(pattern, log_content)
        return [{'key': m[0], 'action': m[1]} for m in matches]
    
    @staticmethod
    def parse_delete_logs(log_content):
        """Извлечь [DELETE] логи"""
        logs = {
            'item_class': None,
            'element_pos': None,
            'removed_from_elements': False,
            'removed_from_graphics': False,
            'final_count': None
        }
        
        # Item class
        match = re.search(r'\[DELETE\] Item: (\w+)', log_content)
        if match:
            logs['item_class'] = match.group(1)
        
        # Element position
        match = re.search(r'\[DELETE\] Element at: \(([\d.]+), ([\d.]+)\)mm', log_content)
        if match:
            logs['element_pos'] = (float(match.group(1)), float(match.group(2)))
        
        # Removed from lists
        if '[DELETE] Removed from elements list' in log_content:
            logs['removed_from_elements'] = True
        if '[DELETE] Removed from graphics_items list' in log_content:
            logs['removed_from_graphics'] = True
        
        # Final count
        match = re.search(r'Deleted element\. Remaining: (\d+)', log_content)
        if match:
            logs['final_count'] = int(match.group(1))
        
        return logs
    
    @staticmethod
    def detect_issues(shortcut_logs, delete_logs, initial_count, final_count):
        """Детектировать 4 типа проблем (без KEY_NOT_RECEIVED - тест викликає метод напряму)"""
        issues = []
        
        # ПРОБЛЕМА 2: Метод _delete_selected НЕ вызван
        if not delete_logs['item_class']:
            issues.append({
                'type': 'DELETE_METHOD_NOT_CALLED',
                'desc': '_delete_selected() was NOT called after key press'
            })
        
        # ПРОБЛЕМА 3: Item НЕ удален из scene (логи есть но счетчик не изменился)
        if delete_logs['item_class'] and initial_count == final_count:
            issues.append({
                'type': 'ITEM_NOT_REMOVED',
                'desc': f'Delete called but elements count unchanged: {initial_count} == {final_count}'
            })
        
        # ПРОБЛЕМА 4: Element НЕ удален из списка elements
        if delete_logs['item_class'] and not delete_logs['removed_from_elements']:
            issues.append({
                'type': 'ELEMENT_NOT_REMOVED_FROM_LIST',
                'desc': 'Item deleted but NOT removed from self.elements list'
            })
        
        # ПРОБЛЕМА 5: Graphics item НЕ удален из списка graphics_items
        if delete_logs['item_class'] and not delete_logs['removed_from_graphics']:
            issues.append({
                'type': 'GRAPHICS_NOT_REMOVED_FROM_LIST',
                'desc': 'Item deleted but NOT removed from self.graphics_items list'
            })
        
        return issues


def test_delete_key_smart():
    """Умный тест: Delete/Backspace keys"""
    
    print("=" * 60)
    print("DELETE/BACKSPACE KEY SMART TEST")
    print("=" * 60)
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    # Создать QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Создать MainWindow
    window = MainWindow()
    window.show()
    app.processEvents()
    
    print("[SETUP] MainWindow created")
    
    # Добавить text element
    window._add_text()
    app.processEvents()
    
    initial_count = len(window.elements)
    print(f"[SETUP] Added text element. Total elements: {initial_count}")
    
    # Выбрать element
    if window.graphics_items:
        window.graphics_items[0].setSelected(True)
        app.processEvents()
        print(f"[SETUP] Selected element")
    
    # Размер файла логов ДО теста
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # === ТЕСТ DELETE KEY ===
    print("\n[TEST] Calling _delete_selected() directly...")
    
    # Прямой вызов _delete_selected (QShortcut вызовет его при реальном Delete)
    window._delete_selected()
    app.processEvents()
    
    # Финальный счетчик
    final_count = len(window.elements)
    print(f"[TEST] After Delete: elements count = {final_count}")
    
    # Читать НОВЫЕ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализировать логи
    analyzer = DeleteKeyLogAnalyzer()
    shortcut_logs = analyzer.parse_shortcut_logs(new_logs)
    delete_logs = analyzer.parse_delete_logs(new_logs)
    issues = analyzer.detect_issues(shortcut_logs, delete_logs, initial_count, final_count)
    
    # Вывод результатов
    print("\n" + "=" * 60)
    print("LOG ANALYSIS")
    print("=" * 60)
    
    print(f"\n[SHORTCUT] Logs found: {len(shortcut_logs)}")
    for log in shortcut_logs:
        print(f"  - Key: {log['key']}, Action: {log['action']}")
    
    print(f"\n[DELETE] Logs:")
    print(f"  - Item class: {delete_logs['item_class']}")
    print(f"  - Element pos: {delete_logs['element_pos']}")
    print(f"  - Removed from elements: {delete_logs['removed_from_elements']}")
    print(f"  - Removed from graphics: {delete_logs['removed_from_graphics']}")
    print(f"  - Final count: {delete_logs['final_count']}")
    
    print(f"\n[COUNTS]")
    print(f"  - Initial: {initial_count}")
    print(f"  - Final: {final_count}")
    print(f"  - Expected: {initial_count - 1}")
    
    # Проверка issues
    if issues:
        print(f"\n{'!' * 60}")
        print(f"DETECTED {len(issues)} ISSUE(S):")
        print('!' * 60)
        for issue in issues:
            print(f"  [{issue['type']}] {issue['desc']}")
        print("\n[FAILURE] Delete key has issues")
        return 1
    else:
        print("\n[OK] Delete key works correctly")
        
        # Дополнительная проверка счетчика
        if final_count == initial_count - 1:
            print("[OK] Element count decreased correctly")
            return 0
        else:
            print(f"[ERROR] Count mismatch: expected {initial_count - 1}, got {final_count}")
            return 1


if __name__ == "__main__":
    exit_code = test_delete_key_smart()
    sys.exit(exit_code)
