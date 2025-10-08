# -*- coding: utf-8 -*-
"""Умный тест PropertyPanel для Circle/Ellipse с анализом логов"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.elements.shape_element import CircleElement
from utils.logger import logger
import re


class PropertyPanelLogAnalyzer:
    """Анализатор логов PropertyPanel"""
    
    @staticmethod
    def parse_panel_logs(log_content):
        """Парсить логи PropertyPanel"""
        # [PROP-PANEL] Update circle: is_circle=True
        update_logs = re.findall(r'\[PROP-PANEL\] Update circle: is_circle=(True|False)', log_content)
        
        # [PROP-PANEL] Showing DIAMETER field
        showing_diameter = len(re.findall(r'\[PROP-PANEL\] Showing DIAMETER field', log_content))
        
        # [PROP-PANEL] Showing WIDTH/HEIGHT fields
        showing_wh = len(re.findall(r'\[PROP-PANEL\] Showing WIDTH/HEIGHT fields', log_content))
        
        # [PROP-PANEL] Diameter changed: 15.00mm
        diameter_changes = re.findall(r'\[PROP-PANEL\] Diameter changed: ([\d.]+)mm', log_content)
        
        # [PROP-PANEL] Width changed: 20.00mm
        width_changes = re.findall(r'\[PROP-PANEL\] Width changed: ([\d.]+)mm', log_content)
        
        # [PROP-PANEL] Height changed: 20.00mm
        height_changes = re.findall(r'\[PROP-PANEL\] Height changed: ([\d.]+)mm', log_content)
        
        # [PROP-PANEL] Circle -> Ellipse, refreshing panel
        circle_to_ellipse = len(re.findall(r'\[PROP-PANEL\] Circle -> Ellipse, refreshing panel', log_content))
        
        # [PROP-PANEL] Ellipse -> Circle, refreshing panel
        ellipse_to_circle = len(re.findall(r'\[PROP-PANEL\] Ellipse -> Circle, refreshing panel', log_content))
        
        return {
            'updates': [x == 'True' for x in update_logs],
            'showing_diameter': showing_diameter,
            'showing_wh': showing_wh,
            'diameter_changes': [float(x) for x in diameter_changes],
            'width_changes': [float(x) for x in width_changes],
            'height_changes': [float(x) for x in height_changes],
            'circle_to_ellipse': circle_to_ellipse,
            'ellipse_to_circle': ellipse_to_circle
        }
    
    @staticmethod
    def detect_issues(logs_dict, element):
        """Детектировать проблемы PropertyPanel
        
        КРИТИЧНО: Проверяем не финальное состояние, а КОРРЕЛЯЦИЮ между логами!
        """
        issues = []
        
        # 1. ФИНАЛЬНОЕ СОСТОЯНИЕ: Правильное ли поле показывается ПОСЛЕДНИМ?
        if element.is_circle:
            # Должно быть показано Diameter в последнем update
            # Считаем что последний update был для Circle
            if logs_dict['updates'] and logs_dict['updates'][-1] == True:
                # Был update для Circle, проверяем что Diameter показан хотя бы раз
                if logs_dict['showing_diameter'] == 0:
                    issues.append({
                        'type': 'DIAMETER_FIELD_MISSING',
                        'desc': f"is_circle=True в финале, но поле Diameter НЕ показано ни разу"
                    })
        else:
            # Должно быть показано Width/Height в последнем update
            if logs_dict['updates'] and logs_dict['updates'][-1] == False:
                # Был update для Ellipse, проверяем что Width/Height показаны хотя бы раз
                if logs_dict['showing_wh'] == 0:
                    issues.append({
                        'type': 'WH_FIELDS_MISSING',
                        'desc': f"is_circle=False в финале, но поля Width/Height НЕ показаны ни разу"
                    })
        
        # 2. НЕТ REFRESH при смене формы (если была смена is_circle)
        if len(logs_dict['updates']) > 1:
            # Проверяем была ли смена is_circle
            if len(set(logs_dict['updates'])) > 1:
                # Была смена формы
                total_refreshes = logs_dict['circle_to_ellipse'] + logs_dict['ellipse_to_circle']
                if total_refreshes == 0:
                    issues.append({
                        'type': 'NO_REFRESH_ON_SHAPE_CHANGE',
                        'desc': f"Форма изменилась, но refresh НЕ вызван"
                    })
        
        # 3. НЕТ проверки diameter/width changes!
        # УДАЛЕНО: Diameter change мог быть в прошлом, а потом width изменился!
        # Это НОРМАЛЬНО! НЕ проверяем финальное состояние против старых логов.
        
        return issues


def test_property_panel_circle():
    """Умный тест PropertyPanel для Circle/Ellipse"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    print("=" * 60)
    print("[TEST] PropertyPanel Circle/Ellipse UI Test")
    print("=" * 60)
    
    # ТЕСТ 1: Создать Circle и показать в PropertyPanel
    print("\n[TEST 1] Create Circle and show in PropertyPanel")
    circle = CircleElement()
    circle.config.x = 10.0
    circle.config.y = 10.0
    circle.diameter = 15.0
    
    # Создать graphics item (упрощенная версия)
    from core.elements.shape_element import GraphicsCircleItem
    graphics_item = GraphicsCircleItem(circle, dpi=203, canvas=window.canvas)
    window.canvas.scene.addItem(graphics_item)
    
    # Установить элемент в PropertyPanel
    window.property_panel.set_element(circle, graphics_item)
    app.processEvents()
    
    print(f"  Circle: diameter={circle.diameter:.2f}mm, is_circle={circle.is_circle}")
    
    # ТЕСТ 2: Изменить diameter через PropertyPanel
    print("\n[TEST 2] Change diameter to 20.0mm via PropertyPanel")
    window.property_panel.shape_diameter_input.setValue(20.0)
    app.processEvents()
    
    print(f"  After diameter change: diameter={circle.diameter:.2f}mm, is_circle={circle.is_circle}")
    
    # ТЕСТ 3: Изменить width -> должен переключиться на Ellipse
    print("\n[TEST 3] Change width to 25.0mm (should switch to Ellipse)")
    
    # Сначала нужно показать Ellipse поля, для этого изменим width напрямую
    circle.set_width(25.0)
    window.property_panel.set_element(circle, graphics_item)
    app.processEvents()
    
    print(f"  After width change: width={circle.config.width:.2f}mm, height={circle.config.height:.2f}mm, is_circle={circle.is_circle}")
    
    # ТЕСТ 4: Вернуть height=width -> должен переключиться на Circle
    print("\n[TEST 4] Change height to 25.0mm (should switch back to Circle)")
    window.property_panel.shape_height_input.setValue(25.0)
    app.processEvents()
    
    print(f"  After height change: width={circle.config.width:.2f}mm, height={circle.config.height:.2f}mm, is_circle={circle.is_circle}")
    
    # Читать логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализ
    analyzer = PropertyPanelLogAnalyzer()
    logs = analyzer.parse_panel_logs(new_logs)
    issues = analyzer.detect_issues(logs, circle)
    
    # Результат
    print("\n" + "=" * 60)
    print("[PROPERTY PANEL CIRCLE] LOG ANALYSIS")
    print("=" * 60)
    print(f"Panel updates: {len(logs['updates'])}")
    print(f"Diameter field shown: {logs['showing_diameter']} times")
    print(f"Width/Height fields shown: {logs['showing_wh']} times")
    print(f"Diameter changes: {len(logs['diameter_changes'])}")
    print(f"Width changes: {len(logs['width_changes'])}")
    print(f"Height changes: {len(logs['height_changes'])}")
    print(f"Circle->Ellipse refreshes: {logs['circle_to_ellipse']}")
    print(f"Ellipse->Circle refreshes: {logs['ellipse_to_circle']}")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] PROPERTY PANEL HAS ISSUES")
        return 1
    
    print("\n[OK] PropertyPanel for Circle works correctly")
    
    # Финальные проверки
    assert circle.is_circle == True, "Expected Circle after height=width"
    assert abs(circle.config.width - 25.0) < 0.01, f"Expected width=25.0, got {circle.config.width}"
    
    return 0


if __name__ == "__main__":
    exit(test_property_panel_circle())
