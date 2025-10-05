# -*- coding: utf-8 -*-
"""
Етап 2: Тест інтеграції Sidebar в MainWindow
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
import re

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow
from utils.logger import logger


class LogAnalyzer:
    """Аналізатор логів для Sidebar"""
    
    @staticmethod
    def parse_sidebar_logs(log_content):
        """Витягти логи sidebar"""
        sidebar_logs = {
            'button_clicks': re.findall(r'\[SIDEBAR\] Button clicked: (\w+)', log_content),
            'signal_emits': re.findall(r'\[SIDEBAR\] Signal emitted.*?\'(\w+)\'', log_content),
            'main_receives': re.findall(r'\[SIDEBAR\] Element selected: (\w+)', log_content),
            'elements_added': re.findall(r'\[SIDEBAR\] Element (\w+) added successfully', log_content),
        }
        
        return sidebar_logs
    
    @staticmethod
    def detect_issues(logs_dict):
        """Детектувати проблеми"""
        issues = []
        
        # Перевірка 1: SIDEBAR SIGNAL != MAIN RECEIVED
        if logs_dict['signal_emits'] != logs_dict['main_receives']:
            issues.append({
                'type': 'SIGNAL_MISMATCH',
                'desc': f"Sidebar emit {logs_dict['signal_emits']}, Main receive {logs_dict['main_receives']}"
            })
        
        # Перевірка 2: НЕ СТВОРЕНО ЕЛЕМЕНТ
        if len(logs_dict['elements_added']) == 0:
            issues.append({
                'type': 'NO_ELEMENT_CREATED',
                'desc': 'Елемент НЕ доданий на scene'
            })
        
        # Перевірка 3: MAIN RECEIVE != ELEMENT ADDED
        if logs_dict['main_receives'] != logs_dict['elements_added']:
            issues.append({
                'type': 'ROUTING_MISMATCH',
                'desc': f"Main receive {logs_dict['main_receives']}, Added {logs_dict['elements_added']}"
            })
        
        return issues


def test_sidebar_integration():
    """Тест інтеграції Sidebar"""
    print("=" * 60)
    print("STAGE 2: Sidebar Integration Test")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    try:
        # Створити MainWindow
        window = MainWindow()
        window.show()
        app.processEvents()
        
        # Перевірка 1: Sidebar існує
        assert window.sidebar is not None, "Sidebar не створено в MainWindow"
        print("[OK] Sidebar exists in MainWindow")
        
        # Перевірка 2: Sidebar у layout
        assert window.sidebar.parent() is not None, "Sidebar не доданий в layout"
        print("[OK] Sidebar added to layout")
        
        # Симуляція: клік на Text
        print("\n[TEST] Simulating Text button click...")
        window.sidebar._on_button_clicked('text')
        app.processEvents()
        
        # Читати НОВІ логи
        with open(log_file, 'r', encoding='utf-8') as f:
            f.seek(file_size_before)
            new_logs = f.read()
        
        # Аналіз
        analyzer = LogAnalyzer()
        logs = analyzer.parse_sidebar_logs(new_logs)
        issues = analyzer.detect_issues(logs)
        
        # Вивід
        print(f"\n[LOGS] Button clicks: {logs['button_clicks']}")
        print(f"[LOGS] Signal emits: {logs['signal_emits']}")
        print(f"[LOGS] Main receives: {logs['main_receives']}")
        print(f"[LOGS] Elements added: {logs['elements_added']}")
        
        # Перевірка елементів
        print(f"\n[COUNTS] Elements count: {len(window.elements)}")
        print(f"[COUNTS] GraphicsItems count: {len(window.graphics_items)}")
        
        if issues:
            print(f"\n[FAIL] Detected {len(issues)} issue(s):")
            for issue in issues:
                print(f"  {issue['type']}: {issue['desc']}")
            return False
        
        # Фінальні перевірки
        if len(window.elements) != 1:
            print(f"[FAIL] Elements count = {len(window.elements)}, очікується 1")
            return False
        
        if hasattr(window.elements[0], 'element_type'):
            elem_type = window.elements[0].element_type
        else:
            elem_type = 'text'  # TextElement doesn't have element_type field
        
        print(f"[OK] Element type: {elem_type}")
        
        print("\n[OK] Sidebar integration works correctly")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_sidebar_integration()
    sys.exit(0 if success else 1)
