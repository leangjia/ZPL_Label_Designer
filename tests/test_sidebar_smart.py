# -*- coding: utf-8 -*-
"""
Умний тест Sidebar з LogAnalyzer
"""
import sys
import re
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Додати шлях проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow
from utils.logger import logger


class SidebarLogAnalyzer:
    """Аналізатор логів для Sidebar"""
    
    @staticmethod
    def parse_sidebar_logs(log_content):
        """Витягти логи sidebar"""
        sidebar_logs = {
            'button_clicks': re.findall(r'\[SIDEBAR\] Button clicked: (\w+)', log_content),
            'signal_emits': re.findall(r'\[SIDEBAR\] Signal emitted.*?\'(\w+)\'', log_content),
            'element_selected': re.findall(r'\[SIDEBAR\] Element selected: (\w+)', log_content),
            'elements_added': re.findall(r'\[SIDEBAR\] Element (\w+) added successfully', log_content),
        }
        
        return sidebar_logs
    
    @staticmethod
    def detect_issues(logs_dict, expected_type):
        """Детектувати проблеми"""
        issues = []
        
        # Перевірка 1: BUTTON CLICK != SIGNAL EMIT
        if logs_dict['button_clicks'] != logs_dict['signal_emits']:
            issues.append({
                'type': 'BUTTON_SIGNAL_MISMATCH',
                'desc': f"Button clicks: {logs_dict['button_clicks']}, Signal emits: {logs_dict['signal_emits']}"
            })
        
        # Перевірка 2: SIGNAL != ELEMENT_SELECTED
        if logs_dict['signal_emits'] != logs_dict['element_selected']:
            issues.append({
                'type': 'SIGNAL_HANDLER_MISMATCH',
                'desc': f"Signal emits: {logs_dict['signal_emits']}, Element selected: {logs_dict['element_selected']}"
            })
        
        # Перевірка 3: НЕ СТВОРЕНО ЕЛЕМЕНТ
        if len(logs_dict['elements_added']) == 0:
            issues.append({
                'type': 'NO_ELEMENT_ADDED',
                'desc': 'Елемент НЕ доданий після вибору з sidebar'
            })
        
        # Перевірка 4: НЕПРАВИЛЬНИЙ ТИП ЕЛЕМЕНТА
        if logs_dict['elements_added'] and logs_dict['elements_added'][0] != expected_type:
            issues.append({
                'type': 'WRONG_ELEMENT_TYPE',
                'desc': f"Expected: {expected_type}, Added: {logs_dict['elements_added'][0]}"
            })
        
        return issues


def test_sidebar_integration():
    """Тест інтеграції Sidebar"""
    print("=" * 60)
    print("SIDEBAR INTEGRATION TEST")
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
        print("[OK] Sidebar створено")
        
        # Перевірка 2: Sidebar у layout
        assert window.sidebar.parent() is not None, "Sidebar не доданий в layout"
        print("[OK] Sidebar в layout")
        
        # Перевірка 3: Signal підключений
        # Симуляція: клік на Text button
        initial_elements_count = len(window.elements)
        logger.debug(f"[TEST] Initial elements count: {initial_elements_count}")
        
        # Прямий виклик обробника (симуляція кліку)
        window.sidebar._on_button_clicked('text')
        app.processEvents()
        
        # Читати НОВІ логи
        with open(log_file, 'r', encoding='utf-8') as f:
            f.seek(file_size_before)
            new_logs = f.read()
        
        # Аналіз
        analyzer = SidebarLogAnalyzer()
        logs = analyzer.parse_sidebar_logs(new_logs)
        issues = analyzer.detect_issues(logs, expected_type='text')
        
        # Вивід результатів аналізу
        print(f"\n[ANALYSIS] Sidebar Logs")
        print(f"Button clicks: {logs['button_clicks']}")
        print(f"Signal emits: {logs['signal_emits']}")
        print(f"Element selected: {logs['element_selected']}")
        print(f"Elements added: {logs['elements_added']}")
        
        # Перевірка елементів
        final_elements_count = len(window.elements)
        print(f"\n[ELEMENTS] Before: {initial_elements_count}, After: {final_elements_count}")
        
        if issues:
            print(f"\n[FAIL] Detected {len(issues)} issue(s):")
            for issue in issues:
                print(f"  {issue['type']}: {issue['desc']}")
            return False
        
        # Фінальні перевірки
        if final_elements_count != initial_elements_count + 1:
            print(f"[FAIL] Elements count not increased. Expected: {initial_elements_count + 1}, Got: {final_elements_count}")
            return False
        
        # Перевірка типу елемента
        if window.elements:
            last_element = window.elements[-1]
            element_type = getattr(last_element, 'element_type', type(last_element).__name__)
            print(f"[ELEMENT] Last added: {element_type}")
            
            # TextElement не має element_type, перевіряємо через клас
            if 'Text' not in type(last_element).__name__:
                print(f"[FAIL] Wrong element type. Expected: TextElement, Got: {type(last_element).__name__}")
                return False
        
        print("\n[OK] Sidebar integration works correctly")
        print("[OK] All LogAnalyzer checks passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_elements():
    """Тест додавання кількох елементів через Sidebar"""
    print("\n" + "=" * 60)
    print("MULTIPLE ELEMENTS TEST")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    try:
        window = MainWindow()
        window.show()
        app.processEvents()
        
        initial_count = len(window.elements)
        
        # Додати різні елементи
        test_elements = ['text', 'barcode', 'rectangle', 'circle', 'line']
        
        for elem_type in test_elements:
            window.sidebar._on_button_clicked(elem_type)
            app.processEvents()
        
        # Читати логи
        with open(log_file, 'r', encoding='utf-8') as f:
            f.seek(file_size_before)
            new_logs = f.read()
        
        # Аналіз
        analyzer = SidebarLogAnalyzer()
        logs = analyzer.parse_sidebar_logs(new_logs)
        
        print(f"\n[ANALYSIS] Multiple Elements")
        print(f"Button clicks: {logs['button_clicks']}")
        print(f"Signal emits: {logs['signal_emits']}")
        print(f"Elements added: {logs['elements_added']}")
        
        # Перевірки
        final_count = len(window.elements)
        expected_count = initial_count + len(test_elements)
        
        print(f"\n[ELEMENTS] Initial: {initial_count}, Final: {final_count}, Expected: {expected_count}")
        
        if final_count != expected_count:
            print(f"[FAIL] Elements count mismatch")
            return False
        
        if len(logs['button_clicks']) != len(test_elements):
            print(f"[FAIL] Button clicks count: {len(logs['button_clicks'])}, Expected: {len(test_elements)}")
            return False
        
        print("\n[OK] Multiple elements added successfully")
        return True
        
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = True
    
    if not test_sidebar_integration():
        success = False
    
    if not test_multiple_elements():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
