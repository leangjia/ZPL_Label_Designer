# -*- coding: utf-8 -*-
"""УМНИЙ ТЕСТ: Keyboard Shortcuts з аналізом логів"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from gui.main_window import MainWindow


class ShortcutsLogAnalyzer:
    """Анализатор логів для keyboard shortcuts"""
    
    @staticmethod
    def parse_shortcut_logs(log):
        """[SHORTCUT] logs"""
        shortcuts = re.findall(r'\[SHORTCUT\] (.+)', log)
        return shortcuts
    
    @staticmethod
    def parse_move_logs(log):
        """[MOVE] Before/Delta/After logs"""
        before = re.findall(r'\[MOVE\] Before: \(([\d.]+), ([\d.]+)\)mm', log)
        delta = re.findall(r'\[MOVE\] Delta: \(([-\d.]+), ([-\d.]+)\)mm', log)
        after = re.findall(r'\[MOVE\] After: \(([\d.]+), ([\d.]+)\)mm', log)
        
        return {
            'before': [(float(m[0]), float(m[1])) for m in before],
            'delta': [(float(m[0]), float(m[1])) for m in delta],
            'after': [(float(m[0]), float(m[1])) for m in after]
        }
    
    @staticmethod
    def parse_delete_logs(log):
        """[DELETE] logs"""
        removing = len(re.findall(r'\[DELETE\] Removing element from scene', log))
        from_elements = len(re.findall(r'\[DELETE\] Removed from elements list', log))
        from_graphics = len(re.findall(r'\[DELETE\] Removed from graphics_items list', log))
        ui_cleared = len(re.findall(r'\[DELETE\] UI cleared', log))
        
        return {
            'removing': removing,
            'from_elements': from_elements,
            'from_graphics': from_graphics,
            'ui_cleared': ui_cleared
        }
    
    @staticmethod
    def detect_issues(shortcut_logs, move_logs, delete_logs):
        """Детектувати проблеми shortcuts"""
        issues = []
        
        # 1. MOVE: Before + Delta != After
        if move_logs['before'] and move_logs['delta'] and move_logs['after']:
            before = move_logs['before'][-1]
            delta = move_logs['delta'][-1]
            after = move_logs['after'][-1]
            
            expected_x = before[0] + delta[0]
            expected_y = before[1] + delta[1]
            
            if abs(after[0] - expected_x) > 0.01:
                issues.append({
                    'type': 'MOVE_CALCULATION_ERROR_X',
                    'desc': f'Before={before[0]:.2f} + Delta={delta[0]:.2f} = {expected_x:.2f}, but After={after[0]:.2f}'
                })
            
            if abs(after[1] - expected_y) > 0.01:
                issues.append({
                    'type': 'MOVE_CALCULATION_ERROR_Y',
                    'desc': f'Before={before[1]:.2f} + Delta={delta[1]:.2f} = {expected_y:.2f}, but After={after[1]:.2f}'
                })
        
        # 2. DELETE: не всі кроки виконано
        if delete_logs['removing'] > 0:
            if delete_logs['from_elements'] != delete_logs['removing']:
                issues.append({
                    'type': 'DELETE_NOT_FROM_ELEMENTS',
                    'desc': f"Removing={delete_logs['removing']}, but from_elements={delete_logs['from_elements']}"
                })
            
            if delete_logs['from_graphics'] != delete_logs['removing']:
                issues.append({
                    'type': 'DELETE_NOT_FROM_GRAPHICS',
                    'desc': f"Removing={delete_logs['removing']}, but from_graphics={delete_logs['from_graphics']}"
                })
            
            if delete_logs['ui_cleared'] != delete_logs['removing']:
                issues.append({
                    'type': 'DELETE_UI_NOT_CLEARED',
                    'desc': f"Removing={delete_logs['removing']}, but ui_cleared={delete_logs['ui_cleared']}"
                })
        
        return issues


def test_shortcuts_smart():
    """Умний тест shortcuts з аналізом логів"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Додати елемент
    window._add_text()
    app.processEvents()
    
    item = window.graphics_items[0]
    window.canvas.scene.clearSelection()
    item.setSelected(True)
    app.processEvents()
    
    # ============ ТЕСТ MOVE ============
    print("=" * 60)
    print("[STAGE 5] KEYBOARD SHORTCUTS - LOG ANALYSIS")
    print("=" * 60)
    
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # Симулювати Arrow Right (move +1mm)
    key_event = QKeyEvent(
        QKeyEvent.KeyPress,
        Qt.Key_Right,
        Qt.NoModifier
    )
    window.keyPressEvent(key_event)
    app.processEvents()
    
    # Читати логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        move_logs_text = f.read()
    
    analyzer = ShortcutsLogAnalyzer()
    shortcut_logs = analyzer.parse_shortcut_logs(move_logs_text)
    move_logs = analyzer.parse_move_logs(move_logs_text)
    
    print("\n[TEST] Arrow Right (+1mm):")
    print(f"Shortcuts detected: {shortcut_logs}")
    print(f"[MOVE] entries: {len(move_logs['before'])}")
    
    if move_logs['before']:
        print(f"Before: {move_logs['before'][-1]}")
        print(f"Delta: {move_logs['delta'][-1]}")
        print(f"After: {move_logs['after'][-1]}")
    
    # ============ ТЕСТ DELETE ============
    file_size_before = log_file.stat().st_size
    
    # Симулювати Delete
    key_event = QKeyEvent(
        QKeyEvent.KeyPress,
        Qt.Key_Delete,
        Qt.NoModifier
    )
    window.keyPressEvent(key_event)
    app.processEvents()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        delete_logs_text = f.read()
    
    delete_logs = analyzer.parse_delete_logs(delete_logs_text)
    
    print(f"\n[TEST] Delete:")
    print(f"[DELETE] removing: {delete_logs['removing']}")
    print(f"[DELETE] from_elements: {delete_logs['from_elements']}")
    print(f"[DELETE] from_graphics: {delete_logs['from_graphics']}")
    print(f"[DELETE] ui_cleared: {delete_logs['ui_cleared']}")
    
    # ============ ДЕТЕКЦІЯ ПРОБЛЕМ ============
    issues = analyzer.detect_issues(shortcut_logs, move_logs, delete_logs)
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[FAILURE] SHORTCUTS HAVE ISSUES")
        print("=" * 60)
        return 1
    
    print("\n[OK] Keyboard shortcuts work correctly")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_shortcuts_smart())
