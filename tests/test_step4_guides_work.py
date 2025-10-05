# -*- coding: utf-8 -*-
"""Test STEP 4: Smart Guides = True actually works"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow
from utils.settings_manager import settings_manager

def test_smart_guides_work():
    """Test: Smart Guides = True applies"""
    
    print("=" * 60)
    print("[STEP 4] SMART GUIDES WORK")
    print("=" * 60)
    
    # Set Guides = True
    settings_manager.clear_all_settings()
    test_settings = {
        'show_grid': False,
        'snap_to_grid': False,
        'smart_guides': True,
        'label_width': 28.0,
        'label_height': 28.0,
        'unit': 'mm'
    }
    settings_manager.save_toolbar_settings(test_settings)
    print(f"[1] Pre-saved: smart_guides=True")
    
    # Create MainWindow
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Check checkbox
    guides_checked = window.guides_checkbox.isChecked()
    print(f"[2] Checkbox state: {guides_checked}")
    
    # Check window.guides_enabled
    guides_enabled = window.guides_enabled
    print(f"[3] window.guides_enabled: {guides_enabled}")
    
    # Check SmartGuides.enabled
    smart_guides_enabled = window.smart_guides.enabled if hasattr(window.smart_guides, 'enabled') else None
    print(f"[4] smart_guides.enabled: {smart_guides_enabled}")
    
    # Result
    print("\n" + "=" * 60)
    if guides_checked and guides_enabled and smart_guides_enabled == True:
        print("[OK] Smart Guides work")
        return 0
    else:
        print("[FAIL] Smart Guides do NOT work properly")
        if not guides_checked:
            print("  - Checkbox should be CHECKED")
        if not guides_enabled:
            print("  - window.guides_enabled should be True")
        if smart_guides_enabled != True:
            print(f"  - smart_guides.enabled should be True, got: {smart_guides_enabled}")
        return 1

if __name__ == '__main__':
    sys.exit(test_smart_guides_work())
