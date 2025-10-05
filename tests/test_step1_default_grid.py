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


def test_default_grid_size():
    settings_manager.clear_all_settings()

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    app.processEvents()

    canvas = window.canvas
    print("=" * 60)
    print("[STEP 1] DEFAULT GRID SIZE TEST")
    print("=" * 60)
    print(f"Grid Size X: {canvas.grid_config.size_x_mm}mm")
    print(f"Grid Size Y: {canvas.grid_config.size_y_mm}mm")

    ok = canvas.grid_config.size_x_mm == 1.0 and canvas.grid_config.size_y_mm == 1.0

    window.close()
    window.deleteLater()
    app.processEvents()

    if ok:
        print("\n[OK] Default grid size is 1mm x 1mm")
        return 0

    print(
        "\n[FAIL] Expected 1.0mm x 1.0mm, "
        f"got {canvas.grid_config.size_x_mm}mm x {canvas.grid_config.size_y_mm}mm"
    )
    return 1


if __name__ == "__main__":
    sys.exit(test_default_grid_size())
