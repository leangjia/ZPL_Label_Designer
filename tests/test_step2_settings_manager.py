import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.settings_manager import settings_manager

def test_settings_manager():
    print("=" * 60)
    print("[STEP 2] SETTINGS MANAGER TEST")
    print("=" * 60)

    settings_manager.clear_all_settings()
    print("[1] Cleared all settings")

    test_grid = {
        'size_x': 1.5,
        'size_y': 1.5,
        'offset_x': 0.5,
        'offset_y': 0.5,
        'show_gridlines': False,
        'snap_mode': 'objects',
    }
    settings_manager.save_grid_settings(test_grid)
    print(f"[2] Saved grid settings: {test_grid}")

    loaded_grid = settings_manager.load_grid_settings()
    print(f"[3] Loaded grid settings: {loaded_grid}")

    grid_ok = (
        abs(loaded_grid['size_x'] - 1.5) < 1e-6 and
        abs(loaded_grid['size_y'] - 1.5) < 1e-6 and
        abs(loaded_grid['offset_x'] - 0.5) < 1e-6 and
        abs(loaded_grid['offset_y'] - 0.5) < 1e-6 and
        loaded_grid['show_gridlines'] is False and
        loaded_grid['snap_mode'].value == 'objects'
    )

    test_toolbar = {
        'show_grid': False,
        'snap_to_grid': True,
        'smart_guides': True,
        'label_width': 50.0,
        'label_height': 30.0,
        'unit': 'inch',
    }
    settings_manager.save_toolbar_settings(test_toolbar)
    print(f"[4] Saved toolbar settings: {test_toolbar}")

    loaded_toolbar = settings_manager.load_toolbar_settings()
    print(f"[5] Loaded toolbar settings: {loaded_toolbar}")

    toolbar_ok = (
        loaded_toolbar['show_grid'] is False and
        loaded_toolbar['snap_to_grid'] is True and
        loaded_toolbar['smart_guides'] is True and
        abs(loaded_toolbar['label_width'] - 50.0) < 1e-6 and
        abs(loaded_toolbar['label_height'] - 30.0) < 1e-6 and
        loaded_toolbar['unit'] == 'inch'
    )

    print("\n" + "=" * 60)
    if grid_ok and toolbar_ok:
        print("[OK] SettingsManager save/load works correctly")
        return 0

    print("[FAIL] SettingsManager failed")
    if not grid_ok:
        print("  - Grid settings mismatch")
    if not toolbar_ok:
        print("  - Toolbar settings mismatch")
    return 1


if __name__ == '__main__':
    sys.exit(test_settings_manager())
