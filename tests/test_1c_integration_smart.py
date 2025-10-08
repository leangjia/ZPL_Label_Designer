# -*- coding: utf-8 -*-
"""Умный тест: Загрузка шаблона из 1С JSON"""

import sys
import re
import json
from pathlib import Path

# Добавляем корень проекта
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from gui.main_window import MainWindow
from utils.logger import logger

class Load1CLogAnalyzer:
    """Анализатор логов загрузки из 1С"""
    
    @staticmethod
    def parse_1c_logs(log_content):
        """Извлечь логи [1C-IMPORT]"""
        logs = {
            'loading': [],
            'loaded': [],
            'displayed': []
        }
        
        for line in log_content.split('\n'):
            if '[1C-IMPORT] Loading template from:' in line:
                match = re.search(r'from: (.+)$', line)
                if match:
                    logs['loading'].append(match.group(1))
            
            if '[1C-IMPORT] JSON loaded:' in line:
                match = re.search(r'loaded: (.+)$', line)
                if match:
                    logs['loaded'].append(match.group(1))
            
            if '[1C-IMPORT] Template displayed successfully' in line:
                logs['displayed'].append(True)
        
        return logs
    
    @staticmethod
    def detect_issues(logs):
        """Детектировать проблемы"""
        issues = []
        
        # Проблема 1: JSON не загружен
        if not logs['loading']:
            issues.append({
                'type': 'NO_LOADING_LOG',
                'desc': 'Loading log not found - method not called'
            })
        
        # Проблема 2: Name не распознан
        if not logs['loaded']:
            issues.append({
                'type': 'JSON_NOT_PARSED',
                'desc': 'JSON loaded log not found - parsing failed'
            })
        
        # Проблема 3: Dialog не показан
        if not logs['displayed']:
            issues.append({
                'type': 'DIALOG_NOT_SHOWN',
                'desc': 'Template displayed log not found - dialog not shown'
            })
        
        return issues

def test_1c_integration_smart():
    """Умный тест загрузки из 1С"""
    
    print("\n" + "="*60)
    print("SMART TEST: 1C Integration - Template Loading")
    print("="*60)
    
    log_file = project_root / "logs" / "zpl_designer.log"
    log_file.parent.mkdir(exist_ok=True)
    
    # ✅ СТВОРЮЄМО ТЕСТОВИЙ JSON
    temp_json = project_root / "temp_1c_test.json"
    test_template = {
        "name": "TEST_TEMPLATE_1C",
        "zpl": "^XA^CI28^PW223^LL223^FO7,0^A0N,20,30^FDTest Label^FS^XZ",
        "variables": {
            "{{\u041c\u043e\u0434\u0435\u043b\u044c}}": "TEST_MODEL",
            "{{\u0428\u0442\u0440\u0438\u0445\u043a\u043e\u0434}}": "1234567890"
        }
    }
    
    # Зб\u0435\u0440\u0456\u0433\u0430\u0454\u043c\u043e JSON з BOM (\u044f\u043a 1\u0421 с\u0442\u0432\u043e\u0440\u044e\u0454)
    with open(temp_json, 'w', encoding='utf-8-sig') as f:
        json.dump(test_template, f, indent=2, ensure_ascii=False)
    
    print(f"[TEST] Test JSON created: {temp_json}")
    print(f"[TEST] Template name: {test_template['name']}")
    print(f"[TEST] ZPL length: {len(test_template['zpl'])} chars")
    
    # Розмір файлу ДО тесту
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    print(f"[TEST] Log file size before: {file_size_before} bytes")
    
    # Запускаем приложение
    app = QApplication.instance() or QApplication(sys.argv)
    
    print(f"\n[TEST] Starting MainWindow with template_file={temp_json}")
    window = MainWindow(template_file=str(temp_json))
    window.show()
    
    # КРИТИЧНО: Даем время на обработку событий
    for _ in range(5):
        app.processEvents()
    
    print("[TEST] MainWindow shown, events processed")
    
    # Закрываем окно БЕЗ event loop
    window.close()
    app.processEvents()
    
    print("[TEST] Window closed")
    
    # Читаем НОВЫЕ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    print(f"\n[TEST] New log size: {len(new_logs)} chars")
    
    # Анализируем
    analyzer = Load1CLogAnalyzer()
    logs = analyzer.parse_1c_logs(new_logs)
    issues = analyzer.detect_issues(logs)
    
    # Вивід
    print("\n" + "="*60)
    print("[1C-IMPORT] LOG ANALYSIS")
    print("="*60)
    
    print(f"\n[1C-IMPORT] Loading logs found: {len(logs['loading'])}")
    if logs['loading']:
        print(f"  Filepath: {logs['loading'][0]}")
    else:
        print("  [!] NO loading log - method not called!")
    
    print(f"\n[1C-IMPORT] Loaded logs found: {len(logs['loaded'])}")
    if logs['loaded']:
        print(f"  Template name: {logs['loaded'][0]}")
    else:
        print("  [!] NO loaded log - JSON parsing failed!")
    
    print(f"\n[1C-IMPORT] Displayed logs found: {len(logs['displayed'])}")
    if logs['displayed']:
        print(f"  Dialog shown: YES")
    else:
        print("  [!] NO displayed log - dialog not shown!")
    
    # Очищуємо тимчасовий файл
    if temp_json.exists():
        temp_json.unlink()
        print(f"\n[TEST] Temp file cleaned: {temp_json}")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n" + "="*60)
        print("[FAILURE] 1C INTEGRATION HAS ISSUES")
        print("="*60)
        return 1
    
    print("\n" + "="*60)
    print("[OK] 1C Integration works correctly")
    print("="*60)
    return 0

if __name__ == '__main__':
    exit_code = test_1c_integration_smart()
    sys.exit(exit_code)
