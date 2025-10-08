# -*- coding: utf-8 -*-
"""Тест запуска редактора с JSON файлом из 1С"""

import sys
import json
from pathlib import Path

# Добавляем корень проекта в sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import logger

def test_1c_integration():
    """Тест: запуск редактора с JSON файлом"""
    
    print("\n" + "="*60)
    print("TEST: 1C Integration - Loading JSON template")
    print("="*60)
    
    # 1. Создаем тестовый JSON (как создает 1С)
    test_json = {
        "name": "TEST TEMPLATE FROM 1C",
        "zpl": "^XA\n^CI28\n^PW720\n^LL223\n^FO7,31^A0N,28,28^FD{{Модель}}^FS\n^FO7,62^BY2^BCN,50,N,N,N^FD{{Штрихкод}}^FS\n^XZ",
        "variables": {
            "{{Модель}}": "[Номенклатура.А_Модель]",
            "{{Штрихкод}}": "[Номенклатура.ШтрихКод]"
        }
    }
    
    # 2. Сохраняем во временный файл
    temp_file = project_root / "temp_1c_test.json"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(test_json, f, indent=2, ensure_ascii=False)
    
    print(f"[TEST] Created test JSON: {temp_file}")
    print(f"[TEST] JSON content:\n{json.dumps(test_json, indent=2, ensure_ascii=False)}")
    
    # 3. Запускаем приложение с параметром
    app = QApplication.instance() or QApplication(sys.argv)
    
    print(f"\n[TEST] Starting MainWindow with template_file={temp_file}")
    window = MainWindow(template_file=str(temp_file))
    window.show()
    
    print("[TEST] MainWindow created and shown")
    print("[TEST] Check if dialog opened with ZPL code")
    print("="*60)
    
    # 4. Запускаем event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    test_1c_integration()
