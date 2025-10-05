"""Тест: Rectangle має товщину 1 мм при створенні"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.main_window import MainWindow

def test_rectangle_default_thickness():
    """Тест: Rectangle має товщину 1 мм при створенні"""
    
    print("=" * 60)
    print("[TEST] RECTANGLE DEFAULT THICKNESS")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # Додати rectangle
    window._add_rectangle()
    app.processEvents()
    
    # Перевірити товщину
    if len(window.elements) > 0:
        element = window.elements[-1]  # Останній доданий
        thickness = element.config.border_thickness
        
        print(f"[1] Rectangle border_thickness: {thickness} mm")
        
        if thickness == 1:
            print("\n[OK] Rectangle has correct thickness: 1 mm")
            return 0
        else:
            print(f"\n[FAIL] Expected: 1 mm, Got: {thickness} mm")
            return 1
    else:
        print("\n[FAIL] No elements found")
        return 1

if __name__ == '__main__':
    sys.exit(test_rectangle_default_thickness())
