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


def test_canvas_grid_persistence():
    print("=" * 60)
    print("[STEP 5] CANVAS GRID PERSISTENCE TEST")
    print("=" * 60)

    settings_manager.clear_all_settings()

    preset = {
        'size_x': 1.5,
        'size_y': 2.5,
        'offset_x': 0.5,
        'offset_y': 1.5,
        'show_gridlines': True,
        'snap_mode': 'grid',
    }
    settings_manager.save_grid_settings(preset)
    print(f"[1] Pre-saved grid settings: {preset}")

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()

    canvas = window.canvas
    print(f"[2] Canvas grid state:\n    Size X: {canvas.grid_config.size_x_mm}mm\n    Size Y: {canvas.grid_config.size_y_mm}mm\n    Offset X: {canvas.grid_config.offset_x_mm}mm\n    Offset Y: {canvas.grid_config.offset_y_mm}mm")

    window.close()
    window.deleteLater()
    app.processEvents()

    success = (
        abs(canvas.grid_config.size_x_mm - 1.5) < 1e-6 and
        abs(canvas.grid_config.size_y_mm - 2.5) < 1e-6 and
        abs(canvas.grid_config.offset_x_mm - 0.5) < 1e-6 and
        abs(canvas.grid_config.offset_y_mm - 1.5) < 1e-6
    )

    print("\n" + "=" * 60)
    if success:
        print("[OK] Canvas applies saved grid settings on startup")
        return 0

    print("[FAIL] Canvas did not apply saved grid settings")
    return 1


if __name__ == '__main__':
    sys.exit(test_canvas_grid_persistence())
