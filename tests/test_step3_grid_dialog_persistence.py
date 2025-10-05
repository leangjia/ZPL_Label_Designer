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

from gui.grid_settings_dialog import GridSettingsDialog
from gui.main_window import MainWindow
from utils.settings_manager import settings_manager


def test_grid_dialog_persistence():
    print("=" * 60)
    print("[STEP 3] GRID DIALOG PERSISTENCE TEST")
    print("=" * 60)

    settings_manager.clear_all_settings()

    preset = {
        'size_x': 1.5,
        'size_y': 2.0,
        'offset_x': 0.5,
        'offset_y': 1.0,
        'show_gridlines': False,
        'snap_mode': 'objects',
    }
    settings_manager.save_grid_settings(preset)
    print(f"[1] Pre-saved test settings: {preset}")

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    app.processEvents()

    dialog = GridSettingsDialog(window.canvas.grid_config, parent=window)
    app.processEvents()

    loaded_x = dialog.size_x_spin.value()
    loaded_y = dialog.size_y_spin.value()
    loaded_offset_x = dialog.offset_x_spin.value()
    loaded_offset_y = dialog.offset_y_spin.value()
    print(f"[2] Dialog loaded: size_x={loaded_x}, size_y={loaded_y}")

    dialog.size_x_spin.setValue(3.0)
    dialog.size_y_spin.setValue(3.0)
    dialog.accept()

    saved = settings_manager.load_grid_settings()
    print(f"[3] After accept, saved settings: {saved}")

    window.close()
    window.deleteLater()
    app.processEvents()

    success = (
        abs(loaded_x - 1.5) < 1e-6 and
        abs(loaded_y - 2.0) < 1e-6 and
        abs(saved['size_x'] - 3.0) < 1e-6 and
        abs(saved['size_y'] - 3.0) < 1e-6
    )

    print("\n" + "=" * 60)
    if success:
        print("[OK] Grid Dialog persistence works")
        return 0

    print("[FAIL] Grid Dialog persistence failed")
    return 1


if __name__ == '__main__':
    sys.exit(test_grid_dialog_persistence())
