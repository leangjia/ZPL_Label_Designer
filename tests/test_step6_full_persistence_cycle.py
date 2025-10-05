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


def test_full_persistence_cycle():
    print("=" * 60)
    print("[STEP 6] FULL PERSISTENCE CYCLE TEST")
    print("=" * 60)

    app = QApplication.instance() or QApplication(sys.argv)

    settings_manager.clear_all_settings()
    print("[1] Cleared all settings")

    print("\n[2] FIRST LAUNCH")
    window1 = MainWindow()
    window1.show()
    app.processEvents()

    default_grid_x = window1.canvas.grid_config.size_x_mm
    default_show_grid = window1.grid_checkbox.isChecked()
    print(f"    Default grid size: {default_grid_x}mm")
    print(f"    Default show grid: {default_show_grid}")

    dialog = GridSettingsDialog(window1.canvas.grid_config, parent=window1)
    dialog.size_x_spin.setValue(1.25)
    dialog.size_y_spin.setValue(1.75)
    dialog.accept()
    print("[3] Changed grid via dialog: 1.25mm x 1.75mm")

    window1.grid_checkbox.setChecked(False)
    window1.snap_checkbox.setChecked(True)
    app.processEvents()
    print("[4] Changed toolbar: show_grid=False, snap=True")

    window1.close()
    window1.deleteLater()
    app.processEvents()
    print("[5] Closed first instance")

    print("\n[6] SECOND LAUNCH")
    window2 = MainWindow()
    window2.show()
    app.processEvents()

    loaded_grid_x = window2.canvas.grid_config.size_x_mm
    loaded_grid_y = window2.canvas.grid_config.size_y_mm
    loaded_show_grid = window2.grid_checkbox.isChecked()
    loaded_snap = window2.snap_checkbox.isChecked()

    print("[7] Second launch state:")
    print(f"    Grid size: {loaded_grid_x}mm x {loaded_grid_y}mm")
    print(f"    Show Grid: {loaded_show_grid}")
    print(f"    Snap to Grid: {loaded_snap}")

    window2.close()
    window2.deleteLater()
    app.processEvents()

    success = (
        abs(loaded_grid_x - 1.25) < 1e-6 and
        abs(loaded_grid_y - 1.75) < 1e-6 and
        loaded_show_grid is False and
        loaded_snap is True
    )

    print("\n" + "=" * 60)
    if success:
        print("[OK] Full persistence cycle works!")
        print("     All settings preserved between sessions")
        return 0

    print("[FAIL] Settings were not preserved")
    if abs(loaded_grid_x - 1.25) >= 1e-6:
        print(f"  - Grid X: expected 1.25, got {loaded_grid_x}")
    if abs(loaded_grid_y - 1.75) >= 1e-6:
        print(f"  - Grid Y: expected 1.75, got {loaded_grid_y}")
    if loaded_show_grid is not False:
        print(f"  - Show Grid: expected False, got {loaded_show_grid}")
    if loaded_snap is not True:
        print(f"  - Snap: expected True, got {loaded_snap}")
    return 1


if __name__ == '__main__':
    sys.exit(test_full_persistence_cycle())
