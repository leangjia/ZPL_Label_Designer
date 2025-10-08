# -*- coding: utf-8 -*-
"""Умний тест: ZEBRA Fonts підтримка для Text елемента"""

import sys
import re
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.main_window import MainWindow
from core.elements.text_element import ZplFont

class ZebraFontsLogAnalyzer:
    """Аналізатор логів для перевірки підтримки ZEBRA fonts"""
    
    @staticmethod
    def parse_zpl_font_logs(log_content):
        """Парсити [ZPL-FONT] логи"""
        pattern = r'\[ZPL-FONT\] Font=(\w+) \(([^)]+)\), height=(\d+), width=(\d+)'
        matches = re.findall(pattern, log_content)
        
        return [{
            'font_code': m[0],
            'font_name': m[1],
            'height': int(m[2]),
            'width': int(m[3])
        } for m in matches]
    
    @staticmethod
    def parse_prop_panel_logs(log_content):
        """Парсити [PROP-PANEL] логи зміни font"""
        pattern = r'\[PROP-PANEL\] Font family changed: (\w+) \(([^)]+)\)'
        matches = re.findall(pattern, log_content)
        
        return [{
            'font_code': m[0],
            'font_name': m[1]
        } for m in matches]
    
    @staticmethod
    def detect_issues(zpl_logs, panel_logs, expected_font):
        """Детектувати проблеми"""
        issues = []
        
        # 1. ZPL логів немає
        if not zpl_logs:
            issues.append({
                'type': 'NO_ZPL_LOGS',
                'desc': '[ZPL-FONT] logs not found - to_zpl() не викликався або font не логується'
            })
            return issues  # критична помилка
        
        # 2. PropertyPanel логів немає
        if not panel_logs:
            issues.append({
                'type': 'NO_PANEL_LOGS',
                'desc': '[PROP-PANEL] logs not found - _on_font_family_changed() не викликався'
            })
        
        # 3. ZPL font code != expected
        zpl_font = zpl_logs[-1]
        if zpl_font['font_code'] != expected_font.zpl_code:
            issues.append({
                'type': 'ZPL_FONT_MISMATCH',
                'desc': f"ZPL font code: {zpl_font['font_code']}, expected: {expected_font.zpl_code}"
            })
        
        # 4. ZPL font name != expected
        if zpl_font['font_name'] != expected_font.display_name:
            issues.append({
                'type': 'ZPL_FONT_NAME_MISMATCH',
                'desc': f"ZPL font name: {zpl_font['font_name']}, expected: {expected_font.display_name}"
            })
        
        # 5. PropertyPanel font != ZPL font
        if panel_logs:
            panel_font = panel_logs[-1]
            if panel_font['font_code'] != zpl_font['font_code']:
                issues.append({
                    'type': 'PANEL_ZPL_FONT_MISMATCH',
                    'desc': f"Panel: {panel_font['font_code']}, ZPL: {zpl_font['font_code']}"
                })
        
        return issues


def test_zebra_fonts():
    """Умний тест перевірки ZEBRA fonts підтримки"""
    
    print("=" * 60)
    print(" ZEBRA FONTS SUPPORT TEST")
    print("=" * 60)
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Створити text element через toolbar
    window._add_text()
    app.processEvents()
    
    # Обрати створений елемент
    if not window.graphics_items:
        print("\n[ERROR] No graphics items created!")
        return 1
    
    text_item = window.graphics_items[-1]
    window.canvas.scene.clearSelection()
    text_item.setSelected(True)
    app.processEvents()
    
    # Змінити font на Font D через PropertyPanel
    print("\n[ACTION] Setting Font to D (18x10 Fixed)...")
    
    # Знайти index Font D у dropdown
    property_panel = window.property_panel
    font_d = ZplFont.FONT_D
    
    for i in range(property_panel.font_family_combo.count()):
        if property_panel.font_family_combo.itemData(i) == font_d:
            # Log file size before action
            file_size_before = log_file.stat().st_size if log_file.exists() else 0
            
            # Змінити font
            property_panel.font_family_combo.setCurrentIndex(i)
            app.processEvents()
            
            # Export ZPL для генерації [ZPL-FONT] логів
            window._export_zpl()
            app.processEvents()
            break
    
    # Читати НОВI логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    print("\nLOGS CAPTURED:")
    print(new_logs)
    
    # Аналіз логів
    analyzer = ZebraFontsLogAnalyzer()
    zpl_logs = analyzer.parse_zpl_font_logs(new_logs)
    panel_logs = analyzer.parse_prop_panel_logs(new_logs)
    
    print(f"\nZPL Font Logs: {len(zpl_logs)}")
    for log in zpl_logs:
        print(f"  Font {log['font_code']}: {log['font_name']}, h={log['height']}, w={log['width']}")
    
    print(f"\nPropertyPanel Logs: {len(panel_logs)}")
    for log in panel_logs:
        print(f"  Font {log['font_code']}: {log['font_name']}")
    
    # Детектувати проблеми
    issues = analyzer.detect_issues(zpl_logs, panel_logs, font_d)
    
    if issues:
        print(f"\n[FAILURE] DETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  - {issue['type']}: {issue['desc']}")
        return 1
    
    print("\n[OK] ZEBRA fonts support works correctly!")
    print("  - Font D selected in PropertyPanel")
    print("  - ZPL generation uses ^ADN command")
    print("  - Font code and name match expected values")
    return 0


if __name__ == '__main__':
    exit_code = test_zebra_fonts()
    
    # Schedule app quit
    QTimer.singleShot(100, QApplication.quit)
    
    sys.exit(exit_code)
