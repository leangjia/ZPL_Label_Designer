# -*- coding: utf-8 -*-
"""УМНИЙ ТЕСТ: Multi-Delete з аналізом логів"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from gui.main_window import MainWindow


class MultiDeleteLogAnalyzer:
    """Анализатор логів для множинного видалення"""
    
    @staticmethod
    def parse_delete_logs(log):
        """[DELETE] logs для множинного видалення"""
        # Скільки елементів видаляється
        removing = re.findall(r'\[DELETE\] Removing (\d+) element\(s\) from scene', log)
        # Скільки разів видалено з elements
        from_elements = len(re.findall(r'\[DELETE\] Removed from elements list', log))
        # Скільки разів видалено з graphics_items
        from_graphics = len(re.findall(r'\[DELETE\] Removed from graphics_items list', log))
        # Чи очищено UI
        ui_cleared = len(re.findall(r'\[DELETE\] UI cleared', log))
        # Повідомлення про видалення
        deleted_msg = re.findall(r'Deleted (\d+) element\(s\)', log)
        
        return {
            'removing_count': int(removing[0]) if removing else 0,
            'from_elements': from_elements,
            'from_graphics': from_graphics,
            'ui_cleared': ui_cleared,
            'deleted_count': int(deleted_msg[0]) if deleted_msg else 0
        }
    
    @staticmethod
    def detect_issues(delete_logs, expected_count):
        """Детектувати проблеми множинного видалення"""
        issues = []
        
        # 1. Кількість видалених != очікуваної
        if delete_logs['removing_count'] != expected_count:
            issues.append({
                'type': 'WRONG_DELETE_COUNT',
                'desc': f"Expected to delete {expected_count}, but removing {delete_logs['removing_count']}"
            })
        
        # 2. НЕ всі видалено з elements
        if delete_logs['from_elements'] != expected_count:
            issues.append({
                'type': 'NOT_ALL_FROM_ELEMENTS',
                'desc': f"Expected {expected_count}, removed {delete_logs['from_elements']} from elements"
            })
        
        # 3. НЕ всі видалено з graphics_items
        if delete_logs['from_graphics'] != expected_count:
            issues.append({
                'type': 'NOT_ALL_FROM_GRAPHICS',
                'desc': f"Expected {expected_count}, removed {delete_logs['from_graphics']} from graphics_items"
            })
        
        # 4. UI НЕ очищено
        if delete_logs['ui_cleared'] != 1:
            issues.append({
                'type': 'UI_NOT_CLEARED',
                'desc': f"UI should be cleared once, but cleared {delete_logs['ui_cleared']} times"
            })
        
        # 5. Фінальний підрахунок НЕ співпадає
        if delete_logs['deleted_count'] != expected_count:
            issues.append({
                'type': 'FINAL_COUNT_MISMATCH',
                'desc': f"Expected {expected_count}, but final deleted count is {delete_logs['deleted_count']}"
            })
        
        return issues


def test_multi_delete_smart():
    """Умний тест множинного видалення з аналізом логів"""
    
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
    print("[MULTI-DELETE TEST] LOG ANALYSIS")
    print("=" * 60)
    print(f"\nAdded 3 text elements")
    print(f"Elements count: {len(window.elements)}")
    print(f"Graphics items count: {len(window.graphics_items)}")
    
    # Виділити ВСІ елементи (Ctrl+A або вручну)
    for item in window.graphics_items:
        item.setSelected(True)
    app.processEvents()
    
    selected_count = len(window.canvas.scene.selectedItems())
    print(f"\nSelected {selected_count} items")
    
    # Розмір файла ДО delete
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # Симулювати Delete key
    key_event = QKeyEvent(
        QKeyEvent.KeyPress,
        Qt.Key_Delete,
        Qt.NoModifier
    )
    window.keyPressEvent(key_event)
    app.processEvents()
    
    # Читати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Аналізувати
    analyzer = MultiDeleteLogAnalyzer()
    delete_logs = analyzer.parse_delete_logs(new_logs)
    issues = analyzer.detect_issues(delete_logs, expected_count=3)
    
    print("\n[DELETE LOGS ANALYSIS]:")
    print(f"  Removing count: {delete_logs['removing_count']}")
    print(f"  From elements: {delete_logs['from_elements']}")
    print(f"  From graphics: {delete_logs['from_graphics']}")
    print(f"  UI cleared: {delete_logs['ui_cleared']}")
    print(f"  Deleted count: {delete_logs['deleted_count']}")
    
    print(f"\n[AFTER DELETE]:")
    print(f"  Elements remaining: {len(window.elements)}")
    print(f"  Graphics items remaining: {len(window.graphics_items)}")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[FAILURE] MULTI-DELETE HAS ISSUES")
        print("=" * 60)
        return 1
    
    # Перевірити що всі списки пусті
    if len(window.elements) != 0 or len(window.graphics_items) != 0:
        print(f"\n[CRITICAL] Lists not empty after delete!")
        print(f"  Elements: {len(window.elements)}")
        print(f"  Graphics items: {len(window.graphics_items)}")
        print("\n" + "=" * 60)
        print("[FAILURE] LISTS NOT CLEARED")
        print("=" * 60)
        return 1
    
    print("\n[OK] Multi-delete works correctly - all 3 elements deleted")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_multi_delete_smart())
