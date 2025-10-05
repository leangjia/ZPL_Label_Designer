# -*- coding: utf-8 -*-
"""Умный тест Font Styles с LogAnalyzer"""

import sys
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF

from gui.main_window import MainWindow
from core.elements.text_element import TextElement
from core.elements.base import ElementConfig


class FontStylesLogAnalyzer:
    """Анализатор логов для Font Styles"""
    
    @staticmethod
    def parse_font_style_logs(log_content):
        """Парсить логи Font Styles"""
        # [ZPL-FONT] Bold: height=30, width=45 (height*1.5)
        bold_logs = re.findall(r'\[ZPL-FONT\] Bold: height=(\d+), width=(\d+)', log_content)
        
        # [ZPL-FONT] Normal: height=30
        normal_logs = re.findall(r'\[ZPL-FONT\] Normal: height=(\d+)', log_content)
        
        # [ZPL-UNDERLINE] y=132, width=120px
        underline_logs = re.findall(r'\[ZPL-UNDERLINE\] y=(\d+), width=(\d+)px', log_content)
        
        # [ZPL-FONT-STYLES] Bold=True, Italic=False, Underline=False
        styles_logs = re.findall(r'\[ZPL-FONT-STYLES\] Bold=(\w+), Italic=(\w+), Underline=(\w+)', log_content)
        
        # [PROP-PANEL] Bold changed: True
        panel_bold = re.findall(r'\[PROP-PANEL\] Bold changed: (\w+)', log_content)
        
        # [PROP-PANEL] Underline changed: True
        panel_underline = re.findall(r'\[PROP-PANEL\] Underline changed: (\w+)', log_content)
        
        # [SHORTCUT] Bold toggled: True
        shortcut_bold = re.findall(r'\[SHORTCUT\] Bold toggled: (\w+)', log_content)
        
        # [SHORTCUT] Underline toggled: True
        shortcut_underline = re.findall(r'\[SHORTCUT\] Underline toggled: (\w+)', log_content)
        
        # [TEXT-ITEM] Display updated: Bold=True, Underline=False
        display_update = re.findall(r'\[TEXT-ITEM\] Display updated: Bold=(\w+), Underline=(\w+)', log_content)
        
        return {
            'bold_widths': [(int(h), int(w)) for h, w in bold_logs],
            'normal_heights': [int(h) for h in normal_logs],
            'underline': [(int(y), int(w)) for y, w in underline_logs],
            'styles': [(b, i, u) for b, i, u in styles_logs],
            'panel_bold': [b=='True' for b in panel_bold],
            'panel_underline': [u=='True' for u in panel_underline],
            'shortcut_bold': [b=='True' for b in shortcut_bold],
            'shortcut_underline': [u=='True' for u in shortcut_underline],
            'display_update': [(b=='True', u=='True') for b, u in display_update]
        }
    
    @staticmethod
    def detect_issues(logs):
        """Детектирует 6 типов проблем"""
        issues = []
        
        # ISSUE 1: Bold width НЕ 1.5x height
        if logs['bold_widths']:
            height, width = logs['bold_widths'][0]
            expected_width = int(height * 1.5)
            
            if abs(width - expected_width) > 1:
                issues.append({
                    'type': 'BOLD_WIDTH_INCORRECT',
                    'desc': f"Expected width={expected_width} (height*1.5), got {width}"
                })
        
        # ISSUE 2: ZPL styles != PropertyPanel
        if logs['styles'] and logs['panel_bold']:
            zpl_bold = logs['styles'][-1][0] == 'True'
            panel_bold = logs['panel_bold'][-1]
            
            if zpl_bold != panel_bold:
                issues.append({
                    'type': 'ZPL_PANEL_BOLD_MISMATCH',
                    'desc': f"ZPL Bold={zpl_bold}, Panel Bold={panel_bold}"
                })
        
        if logs['styles'] and logs['panel_underline']:
            zpl_underline = logs['styles'][-1][2] == 'True'
            panel_underline = logs['panel_underline'][-1]
            
            if zpl_underline != panel_underline:
                issues.append({
                    'type': 'ZPL_PANEL_UNDERLINE_MISMATCH',
                    'desc': f"ZPL Underline={zpl_underline}, Panel Underline={panel_underline}"
                })
        
        # ISSUE 3: Underline НЕ сгенерировано когда underline=True
        if logs['styles']:
            zpl_underline = logs['styles'][-1][2] == 'True'
            if zpl_underline and not logs['underline']:
                issues.append({
                    'type': 'UNDERLINE_NOT_GENERATED',
                    'desc': "Underline=True but no ^GB command in ZPL"
                })
        
        # ISSUE 4: Underline Y позиция неправильная
        if logs['underline'] and logs['normal_heights']:
            height = logs['normal_heights'][0] if logs['normal_heights'] else logs['bold_widths'][0][0]
            text_y = 80  # 10mm = 80 dots at 203 DPI
            y_expected_min = text_y + height
            y_actual = logs['underline'][0][0]
            
            if y_actual < y_expected_min:
                issues.append({
                    'type': 'UNDERLINE_Y_TOO_LOW',
                    'desc': f"Underline y={y_actual}, expected >= {y_expected_min}"
                })
        
        # ISSUE 5: Underline width = 0
        if logs['underline']:
            width = logs['underline'][0][1]
            if width == 0:
                issues.append({
                    'type': 'UNDERLINE_WIDTH_ZERO',
                    'desc': "Underline width=0, text length not calculated"
                })
        
        # ISSUE 6: Display update != Element state
        if logs['display_update'] and logs['styles']:
            display_bold, display_underline = logs['display_update'][-1]
            zpl_bold = logs['styles'][-1][0] == 'True'
            zpl_underline = logs['styles'][-1][2] == 'True'
            
            if display_bold != zpl_bold:
                issues.append({
                    'type': 'DISPLAY_ELEMENT_BOLD_MISMATCH',
                    'desc': f"Display Bold={display_bold}, Element Bold={zpl_bold}"
                })
            
            if display_underline != zpl_underline:
                issues.append({
                    'type': 'DISPLAY_ELEMENT_UNDERLINE_MISMATCH',
                    'desc': f"Display Underline={display_underline}, Element Underline={zpl_underline}"
                })
        
        return issues


def test_font_styles_smart():
    """Умный тест Font Styles с LogAnalyzer"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    # Размер файла логов ДО теста
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # TEST 1: Bold + Underline через PropertyPanel
    print("=" * 60)
    print("TEST 1: PropertyPanel Bold + Underline")
    print("=" * 60)
    
    element = TextElement(
        config=ElementConfig(x=10.0, y=10.0),
        text="Test Bold Underline",
        font_size=30  # 30 dots height
    )
    element.bold = True
    element.underline = True
    
    # Добавить элемент
    window.elements.append(element)
    from core.elements.text_element import GraphicsTextItem
    item = GraphicsTextItem(element)
    window.canvas.scene.addItem(item)
    window.graphics_items.append(item)
    app.processEvents()
    
    # Генерировать ZPL
    from zpl.generator import ZPLGenerator
    generator = ZPLGenerator(dpi=203)
    label_config = {'width': 28, 'height': 28, 'dpi': 203}
    zpl_code = generator.generate(window.elements, label_config, data={})
    
    print("ZPL CODE:")
    print(zpl_code)
    
    # Читать НОВЫЕ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализировать
    analyzer = FontStylesLogAnalyzer()
    logs = analyzer.parse_font_style_logs(new_logs)
    issues = analyzer.detect_issues(logs)
    
    # Вывод
    print("=" * 60)
    print("FONT STYLES LOG ANALYSIS")
    print("=" * 60)
    print(f"Bold widths: {logs['bold_widths']}")
    print(f"Normal heights: {logs['normal_heights']}")
    print(f"Underline: {logs['underline']}")
    print(f"Styles: {logs['styles']}")
    print(f"Panel Bold: {logs['panel_bold']}")
    print(f"Panel Underline: {logs['panel_underline']}")
    print(f"Display update: {logs['display_update']}")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] FONT STYLES HAS ISSUES")
        return 1
    
    print("\n[OK] Font Styles work correctly")
    return 0


if __name__ == '__main__':
    sys.exit(test_font_styles_smart())
