# -*- coding: utf-8 -*-
"""Test STEP 2: Show Grid = True actually works and grid IS visible"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow
from utils.settings_manager import settings_manager

def test_show_grid_actually_works():
    """Test: Show Grid = True applies and grid IS VISIBLE"""
    
    print("=" * 60)
    print("[STEP 2] SHOW GRID ACTUALLY VISIBLE")
    print("=" * 60)
    
    # Set Show Grid = True
    settings_manager.clear_all_settings()
    test_settings = {
        'show_grid': True,
        'snap_to_grid': False,
        'smart_guides': False,
        'label_width': 28.0,
        'label_height': 28.0,
        'unit': 'mm'
    }
    settings_manager.save_toolbar_settings(test_settings)
    print(f"[1] Pre-saved: show_grid=True")
    
    # Create MainWindow
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Check checkbox
    grid_checked = window.grid_checkbox.isChecked()
    print(f"[2] Checkbox state: {grid_checked}")
    
    # Check REAL visibility
    grid_visible = window.canvas.grid_config.visible
    grid_items_count = len(window.canvas.grid_items)
    
    print(f"[3] Canvas grid state:")
    print(f"    grid_config.visible: {grid_visible}")
    print(f"    grid_items count: {grid_items_count}")
    
    # Check that items ARE REALLY visible in scene
    if grid_items_count > 0:
        first_item = window.canvas.grid_items[0]
        item_visible = first_item.isVisible()
        print(f"    first grid item isVisible(): {item_visible}")
    else:
        item_visible = False
        print(f"    [ERROR] grid_items is EMPTY!")
    
    # Result
    print("\n" + "=" * 60)
    if grid_checked and grid_visible and grid_items_count > 0 and item_visible:
        print("[OK] Show Grid works - grid IS visible")
        return 0
    else:
        print("[FAIL] Show Grid does NOT work properly")
        if not grid_checked:
            print("  - Checkbox should be CHECKED")
        if not grid_visible:
            print("  - grid_config.visible should be True")
        if grid_items_count == 0:
            print("  - grid_items should NOT be empty")
        if not item_visible:
            print("  - grid items should be VISIBLE")
        return 1

if __name__ == '__main__':
    sys.exit(test_show_grid_actually_works())
