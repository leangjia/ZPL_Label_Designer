# -*- coding: utf-8 -*-
"""Test STEP 6: Full persistence cycle - change -> close -> reopen -> verify"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow
from utils.settings_manager import settings_manager
from utils.unit_converter import MeasurementUnit

def test_full_settings_persistence():
    """
    INTEGRATION TEST: Full cycle of settings persistence
    
    Scenario:
    1. Launch with default settings
    2. Change ALL settings
    3. Close application
    4. Reopen application
    5. Verify ALL settings applied
    """
    
    print("=" * 60)
    print("[STEP 6] FULL PERSISTENCE CYCLE")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Clear settings
    settings_manager.clear_all_settings()
    print("[1] Cleared all settings")
    
    # === FIRST LAUNCH ===
    print("\n[2] FIRST LAUNCH - Changing settings")
    window1 = MainWindow()
    window1.show()
    app.processEvents()
    
    # Change ALL settings manually
    # Show Grid = False
    window1.grid_checkbox.setChecked(False)
    window1._toggle_grid_visibility(0)
    
    # Snap = True
    window1.snap_checkbox.setChecked(True)
    window1._toggle_snap(2)
    
    # Guides = True
    window1.guides_checkbox.setChecked(True)
    window1._toggle_guides(2)
    
    # Label Size = 50 x 30
    window1.width_spinbox.setValue(50.0)
    window1.height_spinbox.setValue(30.0)
    window1._apply_label_size()
    
    # Units = inch
    inch_index = window1.units_combobox.findData(MeasurementUnit.INCH)
    window1.units_combobox.setCurrentIndex(inch_index)
    window1._on_unit_changed(inch_index)
    
    app.processEvents()
    
    print("[3] Changed settings:")
    print(f"    Show Grid: False")
    print(f"    Snap: True")
    print(f"    Guides: True")
    print(f"    Label Size: 50x30mm")
    print(f"    Units: inch")
    
    # "Close" application
    window1.close()
    window1.deleteLater()
    app.processEvents()
    print("[4] Closed first instance")
    
    # === SECOND LAUNCH ===
    print("\n[5] SECOND LAUNCH - Checking persisted settings")
    window2 = MainWindow()
    window2.show()
    app.processEvents()
    
    # Check ALL settings
    grid_checked = window2.grid_checkbox.isChecked()
    snap_checked = window2.snap_checkbox.isChecked()
    guides_checked = window2.guides_checkbox.isChecked()
    
    grid_visible = window2.canvas.grid_config.visible
    snap_enabled = window2.snap_enabled
    guides_enabled = window2.guides_enabled
    
    label_width = window2.canvas.width_mm
    label_height = window2.canvas.height_mm
    
    current_unit = window2.current_unit
    h_ruler_unit = window2.h_ruler.unit
    v_ruler_unit = window2.v_ruler.unit
    
    print(f"[6] Loaded settings:")
    print(f"    Show Grid checkbox: {grid_checked}")
    print(f"    Grid visible: {grid_visible}")
    print(f"    Snap checkbox: {snap_checked}")
    print(f"    Snap enabled: {snap_enabled}")
    print(f"    Guides checkbox: {guides_checked}")
    print(f"    Guides enabled: {guides_enabled}")
    print(f"    Label Size: {label_width}x{label_height}mm")
    print(f"    Units: {current_unit.value}")
    print(f"    H Ruler: {h_ruler_unit.value}")
    print(f"    V Ruler: {v_ruler_unit.value}")
    
    # Result
    print("\n" + "=" * 60)
    success = (
        grid_checked == False and
        grid_visible == False and
        snap_checked == True and
        snap_enabled == True and
        guides_checked == True and
        guides_enabled == True and
        abs(label_width - 50.0) < 0.1 and
        abs(label_height - 30.0) < 0.1 and
        current_unit == MeasurementUnit.INCH and
        h_ruler_unit == MeasurementUnit.INCH and
        v_ruler_unit == MeasurementUnit.INCH
    )
    
    if success:
        print("[SUCCESS] ALL SETTINGS PERSISTED AND APPLIED CORRECTLY!")
        return 0
    else:
        print("[FAILURE] Some settings were NOT persisted or applied")
        if grid_checked != False or grid_visible != False:
            print(f"  - Show Grid: expected False, got checkbox={grid_checked}, visible={grid_visible}")
        if snap_checked != True or snap_enabled != True:
            print(f"  - Snap: expected True, got checkbox={snap_checked}, enabled={snap_enabled}")
        if guides_checked != True or guides_enabled != True:
            print(f"  - Guides: expected True, got checkbox={guides_checked}, enabled={guides_enabled}")
        if abs(label_width - 50.0) > 0.1 or abs(label_height - 30.0) > 0.1:
            print(f"  - Label Size: expected 50x30mm, got {label_width}x{label_height}mm")
        if current_unit != MeasurementUnit.INCH:
            print(f"  - Units: expected INCH, got {current_unit.value}")
        if h_ruler_unit != MeasurementUnit.INCH or v_ruler_unit != MeasurementUnit.INCH:
            print(f"  - Rulers: expected INCH, got H={h_ruler_unit.value}, V={v_ruler_unit.value}")
        return 1

if __name__ == '__main__':
    sys.exit(test_full_settings_persistence())
