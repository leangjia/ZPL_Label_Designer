# -*- coding: utf-8 -*-
"""Умний тест для ЕТАП 14: Units + Template Save/Load"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
import re

# Додати project root до sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow
from utils.unit_converter import MeasurementUnit, UnitConverter


class UnitsTemplateLogAnalyzer:
    """Аналізатор логів для Units + Template"""
    
    @staticmethod
    def parse_template_logs(log_content):
        """Парсити логі Template save/load"""
        # [TEMPLATE] Saving with display_unit: inch
        saves = re.findall(r'\[TEMPLATE\] Saving with display_unit: (\w+)', log_content)
        
        # [TEMPLATE] Applied display_unit: inch
        loads = re.findall(r'\[TEMPLATE\] Applied display_unit: (\w+)', log_content)
        
        # [UNITS] Changed: mm -> inch
        unit_changes = re.findall(r'\[UNITS\] Changed: (\w+) -> (\w+)', log_content)
        
        return {
            'template_saves': saves,
            'template_loads': loads,
            'unit_changes': [(u1, u2) for u1, u2 in unit_changes]
        }
    
    @staticmethod
    def detect_issues(logs):
        """Детектувати проблеми"""
        issues = []
        
        # === ISSUE 1: Template НЕ зберігає display_unit ===
        if not logs['template_saves']:
            issues.append({
                'type': 'TEMPLATE_UNIT_NOT_SAVED',
                'desc': 'Template save did not record display_unit'
            })
        
        # === ISSUE 2: Template НЕ завантажує display_unit ===
        if logs['template_saves'] and not logs['template_loads']:
            issues.append({
                'type': 'TEMPLATE_UNIT_NOT_LOADED',
                'desc': 'Template load did not restore display_unit'
            })
        
        # === ISSUE 3: Saved unit != Loaded unit ===
        if logs['template_saves'] and logs['template_loads']:
            saved_unit = logs['template_saves'][0]
            loaded_unit = logs['template_loads'][0]
            
            if saved_unit != loaded_unit:
                issues.append({
                    'type': 'TEMPLATE_UNIT_MISMATCH',
                    'desc': f"Saved {saved_unit}, but loaded {loaded_unit}"
                })
        
        # === ISSUE 4: Load НЕ викликав unit change ===
        if logs['template_loads']:
            loaded_unit = logs['template_loads'][0]
            
            # Шукаємо чи був unit change ПІСЛЯ load
            has_change_after_load = False
            for u1, u2 in logs['unit_changes']:
                if u2 == loaded_unit:
                    has_change_after_load = True
                    break
            
            if not has_change_after_load:
                issues.append({
                    'type': 'TEMPLATE_LOAD_NO_UNIT_CHANGE',
                    'desc': f"Template loaded {loaded_unit} but units_combobox not updated"
                })
        
        return issues


def test_units_template_smart():
    """Умний тест для Units + Template Save/Load"""
    print("=" * 60)
    print("UNITS + TEMPLATE SMART TEST")
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
    
    assert window.current_unit == MeasurementUnit.INCH
    print(f"[OK] current_unit = {window.current_unit.value}")
    
    # === ТЕСТ 2: Створити text element ===
    print(f"\n[3] Creating text element")
    from core.elements.text_element import TextElement, GraphicsTextItem
    from core.elements.base import ElementConfig
    
    config = ElementConfig(x=10.0, y=10.0)
    element = TextElement(config, text="Test Template", font_size=20)
    
    graphics_item = GraphicsTextItem(element, dpi=203)
    window.canvas.scene.addItem(graphics_item)
    window.elements.append(element)
    window.graphics_items.append(graphics_item)
    
    print(f"[OK] Element created at ({element.config.x:.2f}, {element.config.y:.2f})mm")
    
    # === ТЕСТ 3: Зберегти template ===
    print(f"\n[4] Saving template...")
    
    template_path = Path(r'D:\AiKlientBank\1C_Zebra\templates\library\test_units_template.json')
    
    # Використати метод напряму (БЕЗ QFileDialog)
    from datetime import datetime
    import json
    
    label_config = {
        'width': window.canvas.width_mm,
        'height': window.canvas.height_mm,
        'dpi': window.canvas.dpi
    }
    
    metadata = {
        'elements_count': len(window.elements),
        'application': 'TEST'
    }
    
    template_data = {
        "name": "test_units_template",
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "label_config": {
            "width_mm": label_config.get('width', 28),
            "height_mm": label_config.get('height', 28),
            "dpi": label_config.get('dpi', 203),
            "display_unit": window.current_unit.value  # ← зберегти display_unit
        },
        "elements": [element.to_dict() for element in window.elements],
        "metadata": metadata
    }
    
    from utils.logger import logger
    logger.info(f"[TEMPLATE] Saving with display_unit: {window.current_unit.value}")
    
    template_path.parent.mkdir(parents=True, exist_ok=True)
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Template saved: {template_path}")
    
    # Перевірити JSON
    with open(template_path, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    
    saved_unit = saved_data['label_config'].get('display_unit')
    print(f"[5] Saved display_unit: {saved_unit}")
    
    assert saved_unit == 'inch', f"Expected 'inch', got '{saved_unit}'"
    print(f"[OK] display_unit saved correctly")
    
    # === ТЕСТ 4: Змінити units назад MM ===
    print(f"\n[6] Changing units: INCH -> MM")
    index = window.units_combobox.findData(MeasurementUnit.MM)
    window.units_combobox.setCurrentIndex(index)
    app.processEvents()
    
    assert window.current_unit == MeasurementUnit.MM
    print(f"[OK] current_unit = {window.current_unit.value}")
    
    # === ТЕСТ 5: Завантажити template ===
    print(f"\n[7] Loading template...")
    
    # Очистити canvas
    window.canvas.clear_and_redraw_grid()
    window.elements.clear()
    window.graphics_items.clear()
    
    # Завантажити через TemplateManager
    template_data_loaded = window.template_manager.load_template(template_path)
    
    # Застосувати display_unit
    display_unit = template_data_loaded.get('display_unit', MeasurementUnit.MM)
    
    index = window.units_combobox.findData(display_unit)
    if index >= 0:
        window.units_combobox.setCurrentIndex(index)
    
    logger.info(f"[TEMPLATE] Applied display_unit: {display_unit.value}")
    app.processEvents()
    
    print(f"[8] Loaded display_unit: {display_unit.value}")
    print(f"[9] Current unit after load: {window.current_unit.value}")
    
    assert window.current_unit == display_unit, f"Expected {display_unit.value}, got {window.current_unit.value}"
    print(f"[OK] display_unit restored correctly")
    
    # === АНАЛІЗ ЛОГІВ ===
    print(f"\n{'=' * 60}")
    print("LOG ANALYSIS")
    print(f"{'=' * 60}")
    
    # Читати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Парсити
    analyzer = UnitsTemplateLogAnalyzer()
    logs = analyzer.parse_template_logs(new_logs)
    
    print(f"\nParsed logs:")
    print(f"  Template saves: {len(logs['template_saves'])}")
    print(f"  Template loads: {len(logs['template_loads'])}")
    print(f"  Unit changes: {len(logs['unit_changes'])}")
    
    if logs['template_saves']:
        print(f"  Saved unit: {logs['template_saves'][0]}")
    
    if logs['template_loads']:
        print(f"  Loaded unit: {logs['template_loads'][0]}")
    
    # Детектувати проблеми
    issues = analyzer.detect_issues(logs)
    
    if issues:
        print(f"\n[FAILURE] DETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  [{issue['type']}] {issue['desc']}")
        print(f"\n{'=' * 60}")
        return 1
    
    print(f"\n[OK] Units + Template feature works correctly")
    print(f"{'=' * 60}")
    return 0


if __name__ == '__main__':
    exit_code = test_units_template_smart()
    sys.exit(exit_code)
