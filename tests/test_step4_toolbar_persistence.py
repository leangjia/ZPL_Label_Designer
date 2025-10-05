import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtWidgets import QApplication
except ImportError as exc:  # pragma: no cover
    print(f"[SKIP] PySide6 unavailable: {exc}")
    sys.exit(0)

sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.main_window import MainWindow
from utils.settings_manager import settings_manager


def test_toolbar_persistence():
    print("=" * 60)
    print("[STEP 4] TOOLBAR PERSISTENCE TEST")
    print("=" * 60)

    settings_manager.clear_all_settings()

    preset = {
        'show_grid': False,
        'snap_to_grid': True,
        'smart_guides': True,
        'label_width': 50.0,
        'label_height': 30.0,
        'unit': 'mm',
    }
    settings_manager.save_toolbar_settings(preset)
    print(f"[1] Pre-saved toolbar settings: {preset}")

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()

    show_grid_state = window.grid_checkbox.isChecked()
    snap_state = window.snap_checkbox.isChecked()
    smart_guides_state = window.guides_checkbox.isChecked()
    label_width = window.canvas.width_mm
    label_height = window.canvas.height_mm

    print(f"[2] Loaded states:\n    Show Grid: {show_grid_state}\n    Snap to Grid: {snap_state}\n    Smart Guides: {smart_guides_state}\n    Label Size: {label_width}x{label_height}mm")

    window.grid_checkbox.setChecked(True)
    app.processEvents()

    saved = settings_manager.load_toolbar_settings()
    print(f"[3] After toggle, saved settings: {saved}")

    window.close()
    window.deleteLater()
    app.processEvents()

    success = (
        show_grid_state is False and
        snap_state is True and
        smart_guides_state is True and
        abs(label_width - 50.0) < 1e-6 and
        abs(label_height - 30.0) < 1e-6 and
        saved['show_grid'] is True
    )

    print("\n" + "=" * 60)
    if success:
        print("[OK] Toolbar persistence works")
        return 0

    print("[FAIL] Toolbar persistence failed")
    return 1


if __name__ == '__main__':
    sys.exit(test_toolbar_persistence())
