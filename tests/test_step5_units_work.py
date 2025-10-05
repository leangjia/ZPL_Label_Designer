# -*- coding: utf-8 -*-
"""Test STEP 5: Units = cm applied to rulers"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow
from utils.settings_manager import settings_manager
from utils.unit_converter import MeasurementUnit

def test_units_applied_to_rulers():
    """Test: Units = cm applies to rulers"""
    
    print("=" * 60)
    print("[STEP 5] UNITS APPLIED TO RULERS")
    print("=" * 60)
    
    # Set Units = cm
    settings_manager.clear_all_settings()
    test_settings = {
        'show_grid': False,
        'snap_to_grid': False,
        'smart_guides': False,
        'label_width': 28.0,
        'label_height': 28.0,
        'unit': 'cm'  # <- CRITICAL!
    }
    settings_manager.save_toolbar_settings(test_settings)
    print(f"[1] Pre-saved: unit='cm'")
    
    # Create MainWindow
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Check dropdown
    current_unit_value = window.units_combobox.currentData()
    print(f"[2] Dropdown unit: {current_unit_value.value if current_unit_value else None}")
    
    # Check window.current_unit
    window_unit = window.current_unit
    print(f"[3] window.current_unit: {window_unit.value}")
    
    # Check rulers
    h_ruler_unit = window.h_ruler.unit if hasattr(window.h_ruler, 'unit') else None
    v_ruler_unit = window.v_ruler.unit if hasattr(window.v_ruler, 'unit') else None
    
    print(f"[4] H Ruler unit: {h_ruler_unit.value if h_ruler_unit else None}")
    print(f"[5] V Ruler unit: {v_ruler_unit.value if v_ruler_unit else None}")
    
    # Result
    print("\n" + "=" * 60)
    if (current_unit_value == MeasurementUnit.CM and
        window_unit == MeasurementUnit.CM and
        h_ruler_unit == MeasurementUnit.CM and
        v_ruler_unit == MeasurementUnit.CM):
        print("[OK] Units correctly applied to rulers")
        return 0
    else:
        print("[FAIL] Units NOT applied correctly")
        if current_unit_value != MeasurementUnit.CM:
            print(f"  - Dropdown should be CM, got: {current_unit_value.value if current_unit_value else None}")
        if window_unit != MeasurementUnit.CM:
            print(f"  - window.current_unit should be CM, got: {window_unit.value}")
        if h_ruler_unit != MeasurementUnit.CM:
            print(f"  - H Ruler should be CM, got: {h_ruler_unit.value if h_ruler_unit else None}")
        if v_ruler_unit != MeasurementUnit.CM:
            print(f"  - V Ruler should be CM, got: {v_ruler_unit.value if v_ruler_unit else None}")
        return 1

if __name__ == '__main__':
    sys.exit(test_units_applied_to_rulers())
