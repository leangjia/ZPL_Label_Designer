# -*- coding: utf-8 -*-
"""УМНИЙ ТЕСТ: Context Menu з аналізом логів"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QContextMenuEvent
from gui.main_window import MainWindow


class ContextMenuLogAnalyzer:
    """Аналізатор логів для context menu"""
    
    @staticmethod
    def parse_context_logs(log):
        """[CONTEXT] та [CONTEXT-MENU] logs"""
        menu_at = re.findall(r'\[CONTEXT\] Menu at: \(([\d.]+), ([\d.]+)\)px', log)
        item_found = len(re.findall(r'\[CONTEXT\] Item found:', log))
        no_item = len(re.findall(r'\[CONTEXT\] No item - canvas menu', log))
        item_menu = len(re.findall(r'\[CONTEXT-MENU\] Creating item menu', log))
        canvas_menu = len(re.findall(r'\[CONTEXT-MENU\] Creating canvas menu', log))
        
        return {
            'menu_at': [(float(m[0]), float(m[1])) for m in menu_at],
            'item_found': item_found,
            'no_item': no_item,
            'item_menu': item_menu,
            'canvas_menu': canvas_menu
        }
    
    @staticmethod
    def parse_clipboard_logs(log):
        """[CLIPBOARD] logs"""
        copied = re.findall(r'\[CLIPBOARD\] Copied: (\w+)', log)
        paste_at = re.findall(r'\[CLIPBOARD\] Paste at: \(([\d.]+), ([\d.]+)\)mm', log)
        empty = len(re.findall(r'\[CLIPBOARD\] Empty - nothing to paste', log))
        
        return {
            'copied': copied,
            'paste_at': [(float(m[0]), float(m[1])) for m in paste_at],
            'empty': empty
        }
    
    @staticmethod
    def parse_zorder_logs(log):
        """[Z-ORDER] logs"""
        bring_to_front = re.findall(r'\[Z-ORDER\] Bring to front: z=([\d.]+)', log)
        send_to_back = re.findall(r'\[Z-ORDER\] Send to back: z=([-\d.]+)', log)
        
        return {
            'bring_to_front': [float(z) for z in bring_to_front],
            'send_to_back': [float(z) for z in send_to_back]
        }
    
    @staticmethod
    def parse_duplicate_logs(log):
        """[DUPLICATE] logs"""
        duplicate_start = len(re.findall(r'\[DUPLICATE\] Start', log))
        return {'duplicate_start': duplicate_start}
    
    @staticmethod
    def detect_issues(context_logs, clipboard_logs, zorder_logs, duplicate_logs, elements_count_before, elements_count_after):
        """Детектувати проблеми context menu"""
        issues = []
        
        # 1. CONTEXT: item found != item menu
        if context_logs['item_found'] > 0 and context_logs['item_menu'] != context_logs['item_found']:
            issues.append({
                'type': 'CONTEXT_MENU_TYPE_MISMATCH',
                'desc': f"Item found={context_logs['item_found']}, but item_menu={context_logs['item_menu']}"
            })
        
        # 2. CLIPBOARD: copy без paste
        if len(clipboard_logs['copied']) > 0 and len(clipboard_logs['paste_at']) == 0:
            issues.append({
                'type': 'COPY_WITHOUT_PASTE',
                'desc': f"Copied {len(clipboard_logs['copied'])} times, but no paste detected"
            })
        
        # 3. DUPLICATE: НЕ викликав copy+paste
        if duplicate_logs['duplicate_start'] > 0:
            if len(clipboard_logs['copied']) == 0 or len(clipboard_logs['paste_at']) == 0:
                issues.append({
                    'type': 'DUPLICATE_LOGIC_BROKEN',
                    'desc': f"Duplicate started, but copy={len(clipboard_logs['copied'])}, paste={len(clipboard_logs['paste_at'])}"
                })
        
        # 4. DUPLICATE: кількість елементів НЕ збільшилась
        if duplicate_logs['duplicate_start'] > 0:
            if elements_count_after != elements_count_before + 1:
                issues.append({
                    'type': 'DUPLICATE_NO_NEW_ELEMENT',
                    'desc': f"Before={elements_count_before}, After={elements_count_after}, expected +1"
                })
        
        # 5. Z-ORDER: значення некоректні
        if zorder_logs['bring_to_front']:
            z_values = zorder_logs['bring_to_front']
            # Має бути > 0
            if any(z <= 0 for z in z_values):
                issues.append({
                    'type': 'ZORDER_FRONT_INVALID',
                    'desc': f"Bring to front z-values: {z_values}"
                })
        
        return issues


def test_context_menu_smart():
    """Умний тест context menu з аналізом логів"""
    
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
    
    print("=" * 60)
    print("[STAGE 6] CONTEXT MENU - LOG ANALYSIS")
    print("=" * 60)
    
    # ============ ТЕСТ DUPLICATE ============
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    elements_count_before = len(window.elements)
    
    print(f"\n[TEST] Duplicate (Ctrl+D):")
    print(f"Elements before: {elements_count_before}")
    
    # Викликати duplicate через метод
    window._duplicate_selected()
    app.processEvents()
    
    elements_count_after = len(window.elements)
    print(f"Elements after: {elements_count_after}")
    
    # Читати логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        duplicate_logs_text = f.read()
    
    analyzer = ContextMenuLogAnalyzer()
    clipboard_logs = analyzer.parse_clipboard_logs(duplicate_logs_text)
    duplicate_logs = analyzer.parse_duplicate_logs(duplicate_logs_text)
    
    print(f"[CLIPBOARD] copied: {clipboard_logs['copied']}")
    print(f"[CLIPBOARD] paste_at: {clipboard_logs['paste_at']}")
    print(f"[DUPLICATE] start: {duplicate_logs['duplicate_start']}")
    
    # ============ ТЕСТ Z-ORDER ============
    file_size_before = log_file.stat().st_size
    
    print(f"\n[TEST] Z-Order operations:")
    
    # Bring to Front
    window._bring_to_front()
    app.processEvents()
    
    # Send to Back
    window._send_to_back()
    app.processEvents()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        zorder_logs_text = f.read()
    
    zorder_logs = analyzer.parse_zorder_logs(zorder_logs_text)
    print(f"[Z-ORDER] bring_to_front: {zorder_logs['bring_to_front']}")
    print(f"[Z-ORDER] send_to_back: {zorder_logs['send_to_back']}")
    
    # ============ ТЕСТ CONTEXT MENU TRIGGER ============
    file_size_before = log_file.stat().st_size
    
    print(f"\n[TEST] Context menu trigger:")
    
    # Симулювати context menu на item
    item_pos = item.pos()
    view_pos = window.canvas.mapFromScene(item_pos)
    global_pos = window.canvas.mapToGlobal(view_pos)
    
    # Прямий виклик contextMenuEvent
    context_event = QContextMenuEvent(QContextMenuEvent.Mouse, view_pos, global_pos)
    window.canvas.contextMenuEvent(context_event)
    app.processEvents()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        context_logs_text = f.read()
    
    context_logs = analyzer.parse_context_logs(context_logs_text)
    print(f"[CONTEXT] item_found: {context_logs['item_found']}")
    print(f"[CONTEXT-MENU] item_menu: {context_logs['item_menu']}")
    
    # ============ ДЕТЕКЦІЯ ПРОБЛЕМ ============
    # Об'єднати всі логи для повного аналізу
    full_log = duplicate_logs_text + zorder_logs_text + context_logs_text
    
    all_context_logs = analyzer.parse_context_logs(full_log)
    all_clipboard_logs = analyzer.parse_clipboard_logs(full_log)
    all_zorder_logs = analyzer.parse_zorder_logs(full_log)
    all_duplicate_logs = analyzer.parse_duplicate_logs(full_log)
    
    issues = analyzer.detect_issues(
        all_context_logs, 
        all_clipboard_logs, 
        all_zorder_logs, 
        all_duplicate_logs,
        elements_count_before,
        elements_count_after
    )
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[FAILURE] CONTEXT MENU HAS ISSUES")
        print("=" * 60)
        return 1
    
    print("\n[OK] Context menu works correctly")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_context_menu_smart())
