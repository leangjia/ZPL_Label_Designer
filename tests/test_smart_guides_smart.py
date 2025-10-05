# -*- coding: utf-8 -*-
"""УМНИЙ ТЕСТ: Smart Guides з аналізом логів"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from gui.main_window import MainWindow


class SmartGuidesLogAnalyzer:
    """Аналізатор логів для smart guides"""
    
    @staticmethod
    def parse_guides_logs(log):
        """[GUIDES] logs"""
        initialized = len(re.findall(r'\[GUIDES\] SmartGuides initialized', log))
        check_alignment = re.findall(r'\[GUIDES\] Check alignment for: x=([\d.]+), y=([\d.]+)', log)
        vertical_guides = re.findall(r'\[GUIDES\] Vertical guide at x=([\d.]+)mm', log)
        horizontal_guides = re.findall(r'\[GUIDES\] Horizontal guide at y=([\d.]+)mm', log)
        snap_detected = re.findall(r'\[GUIDES\] Snap detected: x=([\w.]+), y=([\w.]+)', log)
        drew_vertical = re.findall(r'\[GUIDES\] Drew vertical guide at ([\d.]+)px', log)
        drew_horizontal = re.findall(r'\[GUIDES\] Drew horizontal guide at ([\d.]+)px', log)
        cleared = len(re.findall(r'\[GUIDES\] Cleared all guides', log))
        
        return {
            'initialized': initialized,
            'check_alignment': [(float(m[0]), float(m[1])) for m in check_alignment],
            'vertical_guides': [float(x) for x in vertical_guides],
            'horizontal_guides': [float(y) for y in horizontal_guides],
            'snap_detected': snap_detected,
            'drew_vertical': [float(px) for px in drew_vertical],
            'drew_horizontal': [float(px) for px in drew_horizontal],
            'cleared': cleared
        }
    
    @staticmethod
    def parse_toggle_logs(log):
        """[GUIDES-TOGGLE] logs"""
        toggle = re.findall(r'\[GUIDES-TOGGLE\] Enabled: (\w+)', log)
        enabled_in_class = re.findall(r'\[GUIDES\] Enabled: (\w+)', log)
        return {
            'toggle': toggle,
            'enabled_in_class': enabled_in_class
        }
    
    @staticmethod
    def detect_issues(guides_logs, toggle_logs):
        """Детектувати проблеми smart guides"""
        issues = []
        
        # 1. CHECK_ALIGNMENT без GUIDES
        if len(guides_logs['check_alignment']) > 0:
            # Має бути хоча б спроба намалювати guide або snap
            if len(guides_logs['vertical_guides']) == 0 and len(guides_logs['horizontal_guides']) == 0:
                if len(guides_logs['snap_detected']) == 0:
                    issues.append({
                        'type': 'CHECK_WITHOUT_RESULT',
                        'desc': f"Check alignment {len(guides_logs['check_alignment'])} times, but no guides or snap"
                    })
        
        # 2. GUIDES логи є, але НЕ DREW
        if len(guides_logs['vertical_guides']) > 0:
            if len(guides_logs['drew_vertical']) != len(guides_logs['vertical_guides']):
                issues.append({
                    'type': 'VERTICAL_GUIDE_NOT_DREW',
                    'desc': f"Vertical guides={len(guides_logs['vertical_guides'])}, but drew={len(guides_logs['drew_vertical'])}"
                })
        
        if len(guides_logs['horizontal_guides']) > 0:
            if len(guides_logs['drew_horizontal']) != len(guides_logs['horizontal_guides']):
                issues.append({
                    'type': 'HORIZONTAL_GUIDE_NOT_DREW',
                    'desc': f"Horizontal guides={len(guides_logs['horizontal_guides'])}, but drew={len(guides_logs['drew_horizontal'])}"
                })
        
        # 3. TOGGLE не працює
        if len(toggle_logs['toggle']) > 0:
            if len(toggle_logs['enabled_in_class']) != len(toggle_logs['toggle']):
                issues.append({
                    'type': 'TOGGLE_NOT_PROPAGATED',
                    'desc': f"Toggle={len(toggle_logs['toggle'])}, but enabled_in_class={len(toggle_logs['enabled_in_class'])}"
                })
        
        return issues


def test_smart_guides_smart():
    """Умний тест smart guides з аналізом логів"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Додати 2 елементи
    window._add_text()
    app.processEvents()
    window._add_text()
    app.processEvents()
    
    # Перемістити другий елемент БЛИЖЧЕ (в межах SNAP_THRESHOLD 2mm)
    item2 = window.graphics_items[1]
    item2.element.config.x = 10.0  # Та сама X - повинен alignment!
    item2.element.config.y = 15.0  # Відступ 5mm по Y
    dpi = 203
    item2.setPos(10.0 * dpi / 25.4, 15.0 * dpi / 25.4)
    
    print("=" * 60)
    print("[STAGE 7] SMART GUIDES - LOG ANALYSIS")
    print("=" * 60)
    
    # ============ ТЕСТ ALIGNMENT CHECK ============
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    print(f"\n[TEST] Check alignment:")
    
    # Викликати check_alignment через SmartGuides
    item1 = window.graphics_items[0]
    snap_pos = window.smart_guides.check_alignment(item1, window.graphics_items, dpi=203)
    
    print(f"Snap position: {snap_pos}")
    
    # Читати логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        guides_logs_text = f.read()
    
    analyzer = SmartGuidesLogAnalyzer()
    guides_logs = analyzer.parse_guides_logs(guides_logs_text)
    
    print(f"[GUIDES] check_alignment: {len(guides_logs['check_alignment'])}")
    print(f"[GUIDES] vertical_guides: {guides_logs['vertical_guides']}")
    print(f"[GUIDES] horizontal_guides: {guides_logs['horizontal_guides']}")
    print(f"[GUIDES] snap_detected: {guides_logs['snap_detected']}")
    print(f"[GUIDES] drew_vertical: {len(guides_logs['drew_vertical'])}")
    print(f"[GUIDES] drew_horizontal: {len(guides_logs['drew_horizontal'])}")
    
    # ============ ТЕСТ TOGGLE ============
    file_size_before = log_file.stat().st_size
    
    print(f"\n[TEST] Toggle smart guides:")
    
    # Вимкнути
    window._toggle_guides(0)
    app.processEvents()
    
    # Увімкнути
    window._toggle_guides(2)
    app.processEvents()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        toggle_logs_text = f.read()
    
    toggle_logs = analyzer.parse_toggle_logs(toggle_logs_text)
    print(f"[GUIDES-TOGGLE] toggle: {toggle_logs['toggle']}")
    print(f"[GUIDES] enabled_in_class: {toggle_logs['enabled_in_class']}")
    
    # ============ ТЕСТ CLEAR ============
    file_size_before = log_file.stat().st_size
    
    print(f"\n[TEST] Clear guides:")
    
    window.smart_guides.clear_guides()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        clear_logs_text = f.read()
    
    clear_guides_logs = analyzer.parse_guides_logs(clear_logs_text)
    print(f"[GUIDES] cleared: {clear_guides_logs['cleared']}")
    
    # ============ ДЕТЕКЦІЯ ПРОБЛЕМ ============
    # Об'єднати всі логи
    full_log = guides_logs_text + toggle_logs_text + clear_logs_text
    
    all_guides_logs = analyzer.parse_guides_logs(full_log)
    all_toggle_logs = analyzer.parse_toggle_logs(full_log)
    
    issues = analyzer.detect_issues(all_guides_logs, all_toggle_logs)
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "=" * 60)
        print("[FAILURE] SMART GUIDES HAVE ISSUES")
        print("=" * 60)
        return 1
    
    print("\n[OK] Smart guides work correctly")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(test_smart_guides_smart())
