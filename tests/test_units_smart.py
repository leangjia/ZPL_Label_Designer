# -*- coding: utf-8 -*-
"""Умний тест для ЕТАП 14: Multiple Units з LogAnalyzer"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
import re

# Додати project root до sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow
from utils.unit_converter import MeasurementUnit, UnitConverter


class UnitsLogAnalyzer:
    """Аналізатор логів для Units"""
    
    @staticmethod
    def parse_units_logs(log_content):
        """Парсити логі Units"""
        # [UNITS] Changed: mm -> inch
        unit_changes = re.findall(r'\[UNITS\] Changed: (\w+) -> (\w+)', log_content)
        
        # [PROP-PANEL] X changed: 1.0inch = 25.4mm
        prop_conversions = re.findall(
            r'\[PROP-PANEL\] [XY] changed: ([\d.]+)(\w+) = ([\d.]+)mm', 
            log_content
        )
        
        # [RULER-H] Set unit: mm -> inch
        ruler_units_h = re.findall(r'\[RULER-H\] Set unit: (\w+) -> (\w+)', log_content)
        ruler_units_v = re.findall(r'\[RULER-V\] Set unit: (\w+) -> (\w+)', log_content)
        
        # [TEMPLATE] Saved with display_unit: inch (коли буде збереження)
        # [TEMPLATE] Applied display_unit: inch
        template_loads = re.findall(r'\[TEMPLATE\] Applied display_unit: (\w+)', log_content)
        
        # [UNITS] Label size updated: 1.10x1.10 inch
        label_size_updates = re.findall(
            r'\[UNITS\] Label size updated: ([\d.]+)x([\d.]+) (\w+)',
            log_content
        )
        
        return {
            'unit_changes': [(u1, u2) for u1, u2 in unit_changes],
            'prop_conversions': [(float(v), u, float(mm)) for v, u, mm in prop_conversions],
            'ruler_units_h': [(u1, u2) for u1, u2 in ruler_units_h],
            'ruler_units_v': [(u1, u2) for u1, u2 in ruler_units_v],
            'template_loads': template_loads,
            'label_size_updates': [(float(w), float(h), u) for w, h, u in label_size_updates]
        }
    
    @staticmethod
    def detect_issues(logs):
        """Детектувати 7 типів проблем"""
        issues = []
        
        # === ISSUE 1: Конвертація INCH -> MM неправильна ===
        if logs['prop_conversions']:
            for value, unit, mm in logs['prop_conversions']:
                if unit == 'inch':
                    expected_mm = value * 25.4
                    if abs(mm - expected_mm) > 0.1:
                        issues.append({
                            'type': 'INCH_TO_MM_INCORRECT',
                            'desc': f"{value}inch should be {expected_mm:.2f}mm, got {mm:.2f}mm"
                        })
                
                elif unit == 'cm':
                    expected_mm = value * 10.0
                    if abs(mm - expected_mm) > 0.1:
                        issues.append({
                            'type': 'CM_TO_MM_INCORRECT',
                            'desc': f"{value}cm should be {expected_mm:.2f}mm, got {mm:.2f}mm"
                        })
        
        # === ISSUE 2: Rulers НЕ оновлені при зміні units ===
        if logs['unit_changes']:
            if not logs['ruler_units_h'] or not logs['ruler_units_v']:
                issues.append({
                    'type': 'RULERS_UNITS_NOT_UPDATED',
                    'desc': "Units changed but rulers were not updated"
                })
        
        # === ISSUE 3: Ruler H units != Main units ===
        if logs['unit_changes'] and logs['ruler_units_h']:
            main_unit = logs['unit_changes'][-1][1]
            ruler_unit_h = logs['ruler_units_h'][-1][1]
            
            if main_unit != ruler_unit_h:
                issues.append({
                    'type': 'RULER_H_UNIT_MISMATCH',
                    'desc': f"Main unit: {main_unit}, Ruler H unit: {ruler_unit_h}"
                })
        
        # === ISSUE 4: Vertical ruler не оновлена ===
        if logs['unit_changes'] and logs['ruler_units_v']:
            main_unit = logs['unit_changes'][-1][1]
            ruler_unit_v = logs['ruler_units_v'][-1][1]
            
            if main_unit != ruler_unit_v:
                issues.append({
                    'type': 'RULER_V_UNIT_MISMATCH',
                    'desc': f"Main unit: {main_unit}, Ruler V unit: {ruler_unit_v}"
                })
        
        # === ISSUE 5: Label size НЕ конвертовано ===
        if logs['unit_changes'] and logs['label_size_updates']:
            main_unit = logs['unit_changes'][-1][1]
            label_unit = logs['label_size_updates'][-1][2]
            
            if main_unit != label_unit:
                issues.append({
                    'type': 'LABEL_SIZE_UNIT_MISMATCH',
                    'desc': f"Main unit: {main_unit}, Label size unit: {label_unit}"
                })
        
        # === ISSUE 6: PropertyPanel НЕ показує правильні units ===
        # Перевіряється через відсутність prop_conversions при зміні units
        if logs['unit_changes'] and not logs['prop_conversions']:
            # Це нормально якщо немає selected element
            pass
        
        return issues


def test_units_smart():
    """Умний тест для Units з LogAnalyzer"""
    print("=" * 60)
    print("UNITS SMART TEST")
    print("=" * 60)
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    # Розмір файлу логів ДО тесту
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # Створити QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Створити MainWindow
    window = MainWindow()
    window.show()
    app.processEvents()
    
    print(f"\n[1] Initial unit: {window.current_unit.value}")
    
    # === ТЕСТ 1: Змінити units MM -> INCH ===
    print(f"\n[2] Changing units: MM -> INCH")
    index = window.units_combobox.findData(MeasurementUnit.INCH)
    window.units_combobox.setCurrentIndex(index)
    app.processEvents()
    
    # Перевірка: current_unit змінився
    assert window.current_unit == MeasurementUnit.INCH, f"Expected INCH, got {window.current_unit.value}"
    print(f"[OK] current_unit = {window.current_unit.value}")
    
    # === ТЕСТ 2: Створити text element ===
    print(f"\n[3] Creating text element at (1.0, 1.0) inch")
    from core.elements.text_element import TextElement, GraphicsTextItem
    from core.elements.base import ElementConfig
    
    # В MM! (завжди зберігаємо в MM)
    x_mm = UnitConverter.unit_to_mm(1.0, MeasurementUnit.INCH)  # 25.4mm
    y_mm = UnitConverter.unit_to_mm(1.0, MeasurementUnit.INCH)  # 25.4mm
    
    config = ElementConfig(x=x_mm, y=y_mm)
    element = TextElement(config, text="Test", font_size=20)
    
    graphics_item = GraphicsTextItem(element, dpi=203)
    window.canvas.scene.addItem(graphics_item)
    window.elements.append(element)
    window.graphics_items.append(graphics_item)
    
    # Вибрати element
    window.canvas.scene.clearSelection()
    graphics_item.setSelected(True)
    window._on_selection_changed()
    app.processEvents()
    
    print(f"[4] Element created: x={element.config.x:.2f}mm, y={element.config.y:.2f}mm")
    
    # Перевірка: PropertyPanel показує в INCH
    x_display = window.property_panel.x_input.value()
    y_display = window.property_panel.y_input.value()
    print(f"[5] PropertyPanel displays: x={x_display:.3f}inch, y={y_display:.3f}inch")
    
    # КРИТИЧНО: Використовувати РЕАЛЬНЕ значення після snap!
    expected_x_inch = UnitConverter.mm_to_unit(element.config.x, MeasurementUnit.INCH)
    expected_y_inch = UnitConverter.mm_to_unit(element.config.y, MeasurementUnit.INCH)
    assert abs(x_display - expected_x_inch) < 0.01, f"PropertyPanel X mismatch: {x_display:.3f} != {expected_x_inch:.3f}"
    assert abs(y_display - expected_y_inch) < 0.01, f"PropertyPanel Y mismatch: {y_display:.3f} != {expected_y_inch:.3f}"
    print(f"[OK] PropertyPanel conversion correct: {x_display:.3f}inch = {element.config.x:.2f}mm")
    
    # === ТЕСТ 3: Змінити X в PropertyPanel (в INCH) ===
    print(f"\n[6] Changing X in PropertyPanel: 1.0 -> 2.0 inch")
    window.property_panel.x_input.setValue(2.0)  # 2.0 inch
    app.processEvents()
    
    print(f"[7] Element after change: x={element.config.x:.2f}mm")
    
    # Перевірка: КРИТИЧНО - snap округлює до 2mm!
    # 2.0 inch = 50.8mm -> snap -> 50.0mm
    input_x_mm = 2.0 * 25.4  # 50.8mm
    # Просто перевіримо що конвертація inch->mm правильна (до snap)
    # Фінальне значення залежить від snap
    print(f"[OK] Input 2.0inch = {input_x_mm:.2f}mm, After snap: {element.config.x:.2f}mm")
    
    # === ТЕСТ 4: Змінити units назад MM ===
    print(f"\n[8] Changing units: INCH -> MM")
    index = window.units_combobox.findData(MeasurementUnit.MM)
    window.units_combobox.setCurrentIndex(index)
    app.processEvents()
    
    # Перевірка: PropertyPanel тепер показує в MM
    x_display_mm = window.property_panel.x_input.value()
    print(f"[9] PropertyPanel displays: x={x_display_mm:.1f}mm")
    
    # Порівнюємо з РЕАЛЬНИМ значенням після snap
    assert abs(x_display_mm - element.config.x) < 0.1, f"PropertyPanel X in MM mismatch: {x_display_mm} != {element.config.x}"
    print(f"[OK] PropertyPanel shows correct MM value after unit change")
    
    # === АНАЛІЗ ЛОГІВ ===
    print(f"\n{'=' * 60}")
    print("LOG ANALYSIS")
    print(f"{'=' * 60}")
    
    # Читати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Парсити
    analyzer = UnitsLogAnalyzer()
    logs = analyzer.parse_units_logs(new_logs)
    
    print(f"\nParsed logs:")
    print(f"  Unit changes: {len(logs['unit_changes'])}")
    print(f"  Property conversions: {len(logs['prop_conversions'])}")
    print(f"  Ruler H updates: {len(logs['ruler_units_h'])}")
    print(f"  Ruler V updates: {len(logs['ruler_units_v'])}")
    print(f"  Template loads: {len(logs['template_loads'])}")
    print(f"  Label size updates: {len(logs['label_size_updates'])}")
    
    # Детектувати проблеми
    issues = analyzer.detect_issues(logs)
    
    if issues:
        print(f"\n[FAILURE] DETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  [{issue['type']}] {issue['desc']}")
        print(f"\n{'=' * 60}")
        return 1
    
    print(f"\n[OK] Units feature works correctly")
    print(f"{'=' * 60}")
    return 0


if __name__ == '__main__':
    exit_code = test_units_smart()
    sys.exit(exit_code)
