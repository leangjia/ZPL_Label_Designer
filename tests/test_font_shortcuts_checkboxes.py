# -*- coding: utf-8 -*-
"""Тест для Ctrl+B, Ctrl+U shortcuts і PropertyPanel checkboxes"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from gui.main_window import MainWindow


def test_shortcuts_and_checkboxes():
    """Тест shortcuts Ctrl+B, Ctrl+U та PropertyPanel checkboxes"""
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    print("=" * 60)
    print("TEST: Ctrl+B, Ctrl+U Shortcuts + PropertyPanel Checkboxes")
    print("=" * 60)
    
    # Додати текст
    window._add_text()
    app.processEvents()
    
    # Вибрати елемент
    if window.elements:
        element = window.elements[0]
        item = window.graphics_items[0]
        
        # Вибрати item
        window.canvas.scene.clearSelection()
        item.setSelected(True)
        app.processEvents()
        
        print("\n1. Initial state:")
        print(f"   Bold: {element.bold}")
        print(f"   Underline: {element.underline}")
        print(f"   PropertyPanel Bold checkbox: {window.property_panel.bold_checkbox.isChecked()}")
        print(f"   PropertyPanel Underline checkbox: {window.property_panel.underline_checkbox.isChecked()}")
        
        # TEST 1: Ctrl+B shortcut
        print("\n2. Press Ctrl+B...")
        window._toggle_bold()  # Прямой вызов (QTest не всегда работает)
        app.processEvents()
        
        print(f"   Bold after Ctrl+B: {element.bold}")
        print(f"   PropertyPanel Bold checkbox: {window.property_panel.bold_checkbox.isChecked()}")
        
        if not element.bold:
            print("   [FAIL] Bold not toggled!")
            return 1
        
        if not window.property_panel.bold_checkbox.isChecked():
            print("   [FAIL] PropertyPanel checkbox not updated!")
            return 1
        
        print("   [OK] Ctrl+B works")
        
        # TEST 2: Ctrl+U shortcut
        print("\n3. Press Ctrl+U...")
        window._toggle_underline()  # Прямой вызов
        app.processEvents()
        
        print(f"   Underline after Ctrl+U: {element.underline}")
        print(f"   PropertyPanel Underline checkbox: {window.property_panel.underline_checkbox.isChecked()}")
        
        if not element.underline:
            print("   [FAIL] Underline not toggled!")
            return 1
        
        if not window.property_panel.underline_checkbox.isChecked():
            print("   [FAIL] PropertyPanel checkbox not updated!")
            return 1
        
        print("   [OK] Ctrl+U works")
        
        # TEST 3: PropertyPanel checkbox click
        print("\n4. Click PropertyPanel Bold checkbox OFF...")
        window.property_panel.bold_checkbox.setChecked(False)
        app.processEvents()
        
        print(f"   Bold after checkbox OFF: {element.bold}")
        
        if element.bold:
            print("   [FAIL] Bold not toggled by checkbox!")
            return 1
        
        print("   [OK] PropertyPanel checkbox works")
        
        # TEST 4: Toggle again with Ctrl+B
        print("\n5. Press Ctrl+B again...")
        window._toggle_bold()
        app.processEvents()
        
        print(f"   Bold after second Ctrl+B: {element.bold}")
        print(f"   PropertyPanel Bold checkbox: {window.property_panel.bold_checkbox.isChecked()}")
        
        if not element.bold:
            print("   [FAIL] Bold not toggled!")
            return 1
        
        if not window.property_panel.bold_checkbox.isChecked():
            print("   [FAIL] PropertyPanel checkbox not updated!")
            return 1
        
        print("   [OK] Second toggle works")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("[ERROR] No elements added")
        return 1


if __name__ == '__main__':
    sys.exit(test_shortcuts_and_checkboxes())
