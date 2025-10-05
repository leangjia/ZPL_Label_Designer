# -*- coding: utf-8 -*-
"""Test STEP 3: Snap to Grid = True actually works"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow
from utils.settings_manager import settings_manager

def test_snap_to_grid_actually_works():
    """Test: Snap to Grid = True applies"""
    
    print("=" * 60)
    print("[STEP 3] SNAP TO GRID WORKS")
    print("=" * 60)
    
    # Set Snap = True
    settings_manager.clear_all_settings()
    test_settings = {
        'show_grid': False,
        'snap_to_grid': True,
        'smart_guides': False,
        'label_width': 28.0,
        'label_height': 28.0,
        'unit': 'mm'
    }
    settings_manager.save_toolbar_settings(test_settings)
    print(f"[1] Pre-saved: snap_to_grid=True")
    
    # Create MainWindow
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Add text element to check snap
    window._add_text()
    app.processEvents()
    
    # Check checkbox
    snap_checked = window.snap_checkbox.isChecked()
    print(f"[2] Checkbox state: {snap_checked}")
    
    # Check window.snap_enabled
    snap_enabled = window.snap_enabled
    print(f"[3] window.snap_enabled: {snap_enabled}")
    
    # Check that element has snap_enabled = True
    if len(window.graphics_items) > 0:
        item = window.graphics_items[0]
        item_snap = getattr(item, 'snap_enabled', None)
        print(f"[4] First element snap_enabled: {item_snap}")
    else:
        item_snap = None
        print(f"[4] No elements added")
    
    # Result
    print("\n" + "=" * 60)
    if snap_checked and snap_enabled and item_snap == True:
        print("[OK] Snap to Grid works")
        return 0
    else:
        print("[FAIL] Snap to Grid does NOT work properly")
        if not snap_checked:
            print("  - Checkbox should be CHECKED")
        if not snap_enabled:
            print("  - window.snap_enabled should be True")
        if item_snap != True:
            print(f"  - element snap_enabled should be True, got: {item_snap}")
        return 1

if __name__ == '__main__':
    sys.exit(test_snap_to_grid_actually_works())
