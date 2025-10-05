import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.main_window import MainWindow

class ShowGridLogAnalyzer:
    @staticmethod
    def parse_grid_logs(log_content):
        # [GRID-VISIBILITY] Set to: True/False
        visibility_pattern = r'\[GRID-VISIBILITY\] Set to: (True|False)'
        # [GRID-DRAW] Created N items, visibility: True/False
        draw_pattern = r'\[GRID-DRAW\] Created (\d+) items, visibility: (True|False)'
        
        return {
            'visibility_changes': [(m == 'True') for m in re.findall(visibility_pattern, log_content)],
            'draw_events': [(int(m[0]), m[1] == 'True') for m in re.findall(draw_pattern, log_content)]
        }
    
    @staticmethod
    def detect_issues(logs):
        issues = []
        
        # ПРОБЛЕМА 1: Grid drawn with 0 items
        for count, visible in logs['draw_events']:
            if count == 0:
                issues.append({
                    'type': 'GRID_NOT_CREATED',
                    'desc': f'Grid draw event with 0 items'
                })
        
        return issues

def test_show_grid_toggle():
    """Тест Show Grid toggle"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # СЦЕНАРІЙ БАГА:
    # 1. Вимкнути Show Grid
    print("[TEST] Step 1: Disable Show Grid")
    window.grid_checkbox.setChecked(False)
    app.processEvents()
    
    # 2. Змінити розмір canvas (симулює set_label_size)
    print("[TEST] Step 2: Change canvas size")
    window.canvas.set_label_size(50, 40)
    app.processEvents()
    
    # 3. Ввімкнути Show Grid
    print("[TEST] Step 3: Enable Show Grid")
    window.grid_checkbox.setChecked(True)
    app.processEvents()
    
    # 4. Перевірити чи сітка ВИДИМА
    grid_visible_in_scene = False
    for item in window.canvas.grid_items:
        if item.isVisible():
            grid_visible_in_scene = True
            break
    
    print(f"[TEST] Grid visible in scene: {grid_visible_in_scene}")
    print(f"[TEST] Grid items count: {len(window.canvas.grid_items)}")
    
    # Читати логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    analyzer = ShowGridLogAnalyzer()
    logs = analyzer.parse_grid_logs(new_logs)
    issues = analyzer.detect_issues(logs)
    
    print("=" * 60)
    print("[SHOW GRID BUG] LOG ANALYSIS")
    print("=" * 60)
    print(f"Visibility changes: {logs['visibility_changes']}")
    print(f"Draw events: {logs['draw_events']}")
    
    # ПЕРЕВІРКА: Чи сітка ВИДИМА після toggle?
    if not grid_visible_in_scene:
        print("\n[FAILURE] Grid NOT visible after toggle!")
        return 1
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        return 1
    
    print("\n[OK] Show Grid toggle works correctly")
    return 0

if __name__ == '__main__':
    sys.exit(test_show_grid_toggle())
