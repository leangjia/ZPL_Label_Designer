# -*- coding: utf-8 -*-
"""Test STEP 1: _create_snap_toggle does NOT apply hardcode settings"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow
from utils.settings_manager import settings_manager

def test_no_hardcode_toggles():
    """Test: _create_snap_toggle does NOT apply hardcode settings"""
    
    print("=" * 60)
    print("[STEP 1] NO HARDCODE IN _create_snap_toggle()")
    print("=" * 60)
    
    # Set test settings: ALL OFF
    settings_manager.clear_all_settings()
    test_settings = {
        'show_grid': False,
        'snap_to_grid': False,
        'smart_guides': False,
        'label_width': 28.0,
        'label_height': 28.0,
        'unit': 'mm'
    }
    settings_manager.save_toolbar_settings(test_settings)
    print(f"[1] Pre-saved settings (all OFF): {test_settings}")
    
    # Create MainWindow
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Check checkbox states
    grid_checked = window.grid_checkbox.isChecked()
    snap_checked = window.snap_checkbox.isChecked()
    guides_checked = window.guides_checkbox.isChecked()
    
    print(f"[2] Checkbox states after init:")
    print(f"    Show Grid: {grid_checked}")
    print(f"    Snap to Grid: {snap_checked}")
    print(f"    Smart Guides: {guides_checked}")
    
    # Check REAL functionality state
    grid_visible = window.canvas.grid_config.visible
    snap_enabled = window.snap_enabled
    guides_enabled = window.guides_enabled
    
    print(f"[3] Actual functionality state:")
    print(f"    Grid visible: {grid_visible}")
    print(f"    Snap enabled: {snap_enabled}")
    print(f"    Guides enabled: {guides_enabled}")
    
    # Result
    print("\n" + "=" * 60)
    if (not grid_checked and not snap_checked and not guides_checked and
        not grid_visible and not snap_enabled and not guides_enabled):
        print("[OK] No hardcode - settings correctly applied")
        return 0
    else:
        print("[FAIL] Hardcode still present or settings not applied")
        if grid_checked:
            print("  - Show Grid checkbox should be OFF")
        if snap_checked:
            print("  - Snap to Grid checkbox should be OFF")
        if guides_checked:
            print("  - Smart Guides checkbox should be OFF")
        if grid_visible:
            print("  - Grid should be HIDDEN")
        if snap_enabled:
            print("  - Snap should be DISABLED")
        if guides_enabled:
            print("  - Guides should be DISABLED")
        return 1

if __name__ == '__main__':
    sys.exit(test_no_hardcode_toggles())
