# ПРОМПТ: Доробка тесту інтеграції з 1С

## 🎯 ЗАВДАННЯ

Доробити умний тест `test_1c_integration_smart.py` за прикладом робочого тесту `test_cursor_tracking_smart.py`.

## 🔴 КРИТИЧНА ПРОБЛЕМА

**Тест НЕ створює файл `temp_1c_test.json` перед запуском!**

```python
# ❌ НЕПРАВИЛЬНО (поточний код):
temp_json = project_root / "temp_1c_test.json"
print(f"[TEST] Test JSON: {temp_json}")

# Запускаємо MainWindow з НЕІСНУЮЧИМ файлом!
window = MainWindow(template_file=str(temp_json))  # ← FileNotFoundError!
```

**Результат:** `_load_template_from_file()` падає з помилкою, логи `[1C-IMPORT]` НЕ з'являються, тест FAIL.

---

## 📖 КОНТЕКСТ

### Як працює загрузка з 1С:

**1. MainWindow.__init__(template_file=...)**
```python
def __init__(self, template_file=None):
    # ... ініціалізація UI ...
    
    # Зберігаємо шлях до файлу
    self._template_file_to_load = template_file
    
    # ... створення елементів ...
    
    # В КІНЦІ __init__ викликається завантаження:
    if self._template_file_to_load:
        self._load_template_from_file(self._template_file_to_load)
```

**2. TemplateMixin._load_template_from_file(filepath)**
```python
def _load_template_from_file(self, filepath):
    """Завантажити шаблон з файлу (для 1С інтеграції)"""
    try:
        logger.info(f"[1C-IMPORT] Loading template from: {filepath}")
        
        # Читаємо JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        logger.info(f"[1C-IMPORT] JSON loaded: {json_data.get('name', 'unnamed')}")
        
        # Перевіряємо структуру
        if 'zpl' not in json_data:
            logger.warning("[1C-IMPORT] No ZPL code in JSON")
            QMessageBox.warning(self, "Import", "В JSON нет ZPL кода")
            return
        
        # Показуємо діалог з ZPL
        dialog = QDialog(self)
        dialog.setWindowTitle("Шаблон з 1С")
        # ... створення діалогу ...
        dialog.exec()
        
        logger.info("[1C-IMPORT] Template displayed successfully")
        
    except Exception as e:
        logger.error(f"[1C-IMPORT] Failed to load: {e}", exc_info=True)
        QMessageBox.critical(self, "Import Error", f"Помилка завантаження:\n{e}")
```

**3. Логи які шукає LogAnalyzer:**
```python
@staticmethod
def parse_1c_logs(log_content):
    """Витягти логи [1C-IMPORT]"""
    logs = {
        'loading': [],   # [1C-IMPORT] Loading template from: {filepath}
        'loaded': [],    # [1C-IMPORT] JSON loaded: {name}
        'displayed': []  # [1C-IMPORT] Template displayed successfully
    }
    # ... парсинг регулярками ...
    return logs
```

---

## ✅ РОБОЧИЙ ПРИКЛАД (test_cursor_tracking_smart.py)

### Структура робочого тесту:

```python
def test_cursor_smart():
    """Умний тест cursor tracking з аналізом логів"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # 1. РОЗМІР ФАЙЛУ ЛОГІВ ДО ТЕСТУ
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # 2. СИМУЛЯЦІЯ ДІЇ: Створюємо QMouseEvent і викликаємо НАПРЯМУ
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent, QPoint
    
    mouse_event = QMouseEvent(
        QEvent.MouseMove,
        QPointF(x, y),
        Qt.NoButton,
        Qt.NoButton,
        Qt.NoModifier
    )
    window.canvas.mouseMoveEvent(mouse_event)  # ← ПРЯМИЙ ВИКЛИК!
    app.processEvents()
    
    # 3. ЧИТАЄМО НОВІ ЛОГИ (через seek!)
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)  # ← КРИТИЧНО: НЕ видаляти файл!
        new_logs = f.read()
    
    # 4. АНАЛІЗ ЛОГІВ
    analyzer = CursorLogAnalyzer()
    cursor_logs = analyzer.parse_cursor_logs(new_logs)
    ruler_logs = analyzer.parse_ruler_logs(new_logs)
    issues = analyzer.detect_issues(cursor_logs, ruler_logs)
    
    # 5. ДЕТАЛЬНИЙ ВИВІД З ЧИСЛАМИ
    print("=" * 60)
    print("[STAGE 1] CURSOR TRACKING - LOG ANALYSIS")
    print("=" * 60)
    print(f"\n[CURSOR] signals: {len(cursor_logs)}")
    print(f"[RULER-H] updates: {len(ruler_logs['h_update'])}")
    
    if cursor_logs:
        last = cursor_logs[-1]
        print(f"Last cursor position: {last[0]:.2f}mm, {last[1]:.2f}mm")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] CURSOR TRACKING HAS ISSUES")
        return 1
    
    print("\n[OK] Cursor tracking works correctly")
    return 0
```

**Ключові особливості:**
1. ✅ `file_size_before = log_file.stat().st_size` - НЕ видаляємо файл!
2. ✅ `f.seek(file_size_before)` - читаємо тільки нові логи
3. ✅ Прямий виклик обробника: `window.canvas.mouseMoveEvent(event)`
4. ✅ Детальний вивід з ЧИСЛАМИ: `{len(cursor_logs)}`, `{last[0]:.2f}mm`
5. ✅ Аналіз КІЛЬКОХ типів логів: cursor_logs, ruler_logs
6. ✅ Детектування КІЛЬКОХ типів проблем через `detect_issues()`

---

## 🔧 ЩО ПОТРІБНО ВИПРАВИТИ

### 1. Створити temp_1c_test.json ПЕРЕД тестом

**Структура JSON файлу (з Python редактора):**
```json
{
    "name": "TEST_TEMPLATE_1C",
    "zpl": "^XA^CI28^PW223^LL223^FO7,0^A0N,20,30^FDTest Label^FS^XZ",
    "variables": {
        "{{Модель}}": "TEST_MODEL",
        "{{Штрихкод}}": "1234567890"
    }
}
```

**Додати в тест:**
```python
def test_1c_integration_smart():
    """Умний тест завантаження з 1С"""
    
    print("\n" + "="*60)
    print("SMART TEST: 1C Integration - Template Loading")
    print("="*60)
    
    log_file = project_root / "logs" / "zpl_designer.log"
    log_file.parent.mkdir(exist_ok=True)
    
    # ✅ СТВОРЮЄМО ТЕСТОВИЙ JSON (НОВИЙ КОД!)
    temp_json = project_root / "temp_1c_test.json"
    test_template = {
        "name": "TEST_TEMPLATE_1C",
        "zpl": "^XA^CI28^PW223^LL223^FO7,0^A0N,20,30^FDTest Label^FS^XZ",
        "variables": {
            "{{Модель}}": "TEST_MODEL",
            "{{Штрихкод}}": "1234567890"
        }
    }
    
    import json
    with open(temp_json, 'w', encoding='utf-8') as f:
        json.dump(test_template, f, indent=2, ensure_ascii=False)
    
    print(f"[TEST] Test JSON created: {temp_json}")
    print(f"[TEST] Template name: {test_template['name']}")
    
    # Розмір файлу ДО тесту
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    print(f"[TEST] Log file size before: {file_size_before} bytes")
    
    # ... решта коду ...
```

### 2. Покращити вивід результатів (як у cursor test)

**Замінити:**
```python
# ❌ СТАРИЙ КОД (простий вивід):
print(f"Loading logs: {len(logs['loading'])}")
if logs['loading']:
    print(f"  Path: {logs['loading'][0]}")

print(f"Loaded logs: {len(logs['loaded'])}")
if logs['loaded']:
    print(f"  Name: {logs['loaded'][0]}")

print(f"Displayed logs: {len(logs['displayed'])}")
```

**На:**
```python
# ✅ НОВИЙ КОД (детальний вивід):
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
```

### 3. Додати очищення temp файлу

**В кінці тесту:**
```python
# Очищуємо тимчасовий файл
if temp_json.exists():
    temp_json.unlink()
    print(f"\n[TEST] Temp file cleaned: {temp_json}")
```

### 4. Покращити LogAnalyzer (опціонально)

**Додати детальніший парсинг:**
```python
@staticmethod
def parse_1c_logs(log_content):
    """Витягти логи [1C-IMPORT]"""
    logs = {
        'loading': [],
        'loaded': [],
        'displayed': [],
        'errors': []  # ← НОВИЙ: помилки
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
        
        # ← НОВИЙ: ловимо помилки
        if '[1C-IMPORT] Failed to load:' in line:
            match = re.search(r'load: (.+)$', line)
            if match:
                logs['errors'].append(match.group(1))
    
    return logs
```

---

## 📋 ПОВНИЙ ВИПРАВЛЕНИЙ КОД

```python
# -*- coding: utf-8 -*-
"""Умний тест: Завантаження шаблону з 1С JSON"""

import sys
import re
import json
from pathlib import Path

# Додаємо корінь проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import logger


class Load1CLogAnalyzer:
    """Аналізатор логів завантаження з 1С"""
    
    @staticmethod
    def parse_1c_logs(log_content):
        """Витягти логи [1C-IMPORT]"""
        logs = {
            'loading': [],
            'loaded': [],
            'displayed': [],
            'errors': []
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
            
            if '[1C-IMPORT] Failed to load:' in line:
                match = re.search(r'load: (.+)$', line)
                if match:
                    logs['errors'].append(match.group(1))
        
        return logs
    
    @staticmethod
    def detect_issues(logs):
        """Детектувати проблеми"""
        issues = []
        
        # Проблема 1: JSON не завантажений
        if not logs['loading']:
            issues.append({
                'type': 'NO_LOADING_LOG',
                'desc': 'Loading log not found - method not called or file not found'
            })
        
        # Проблема 2: Name не розпізнаний
        if not logs['loaded']:
            issues.append({
                'type': 'JSON_NOT_PARSED',
                'desc': 'JSON loaded log not found - parsing failed'
            })
        
        # Проблема 3: Dialog не показаний
        if not logs['displayed']:
            issues.append({
                'type': 'DIALOG_NOT_SHOWN',
                'desc': 'Template displayed log not found - dialog not shown'
            })
        
        # Проблема 4: Помилки в логах
        if logs['errors']:
            issues.append({
                'type': 'LOAD_ERROR',
                'desc': f'Load error found: {logs["errors"][0]}'
            })
        
        return issues


def test_1c_integration_smart():
    """Умний тест завантаження з 1С"""
    
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
            "{{Модель}}": "TEST_MODEL",
            "{{Штрихкод}}": "1234567890"
        }
    }
    
    with open(temp_json, 'w', encoding='utf-8') as f:
        json.dump(test_template, f, indent=2, ensure_ascii=False)
    
    print(f"[TEST] Test JSON created: {temp_json}")
    print(f"[TEST] Template name: {test_template['name']}")
    print(f"[TEST] ZPL length: {len(test_template['zpl'])} chars")
    
    # Розмір файлу ДО тесту
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    print(f"[TEST] Log file size before: {file_size_before} bytes")
    
    # Запускаємо додаток
    app = QApplication.instance() or QApplication(sys.argv)
    
    print(f"\n[TEST] Starting MainWindow with template_file={temp_json}")
    window = MainWindow(template_file=str(temp_json))
    window.show()
    
    # КРИТИЧНО: Даємо час на обробку подій
    for _ in range(5):
        app.processEvents()
    
    print("[TEST] MainWindow shown, events processed")
    
    # Закриваємо вікно БЕЗ event loop
    window.close()
    app.processEvents()
    
    print("[TEST] Window closed")
    
    # Читаємо НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    print(f"\n[TEST] New log size: {len(new_logs)} chars")
    
    # Аналізуємо
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
    
    if logs['errors']:
        print(f"\n[1C-IMPORT] Errors found: {len(logs['errors'])}")
        for error in logs['errors']:
            print(f"  Error: {error}")
    
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
```

---

## 🎯 ОЧІКУВАНИЙ РЕЗУЛЬТАТ

### При успішному виконанні:

```
============================================================
SMART TEST: 1C Integration - Template Loading
============================================================
[TEST] Test JSON created: D:\AiKlientBank\1C_Zebra\temp_1c_test.json
[TEST] Template name: TEST_TEMPLATE_1C
[TEST] ZPL length: 64 chars
[TEST] Log file size before: 15234 bytes

[TEST] Starting MainWindow with template_file=D:\AiKlientBank\1C_Zebra\temp_1c_test.json
[TEST] MainWindow shown, events processed
[TEST] Window closed

[TEST] New log size: 457 chars

============================================================
[1C-IMPORT] LOG ANALYSIS
============================================================

[1C-IMPORT] Loading logs found: 1
  Filepath: D:\AiKlientBank\1C_Zebra\temp_1c_test.json

[1C-IMPORT] Loaded logs found: 1
  Template name: TEST_TEMPLATE_1C

[1C-IMPORT] Displayed logs found: 1
  Dialog shown: YES

[TEST] Temp file cleaned: D:\AiKlientBank\1C_Zebra\temp_1c_test.json

============================================================
[OK] 1C Integration works correctly
============================================================
```

### При помилці:

```
============================================================
[1C-IMPORT] LOG ANALYSIS
============================================================

[1C-IMPORT] Loading logs found: 0
  [!] NO loading log - method not called!

[1C-IMPORT] Loaded logs found: 0
  [!] NO loaded log - JSON parsing failed!

[1C-IMPORT] Displayed logs found: 0
  [!] NO displayed log - dialog not shown!

DETECTED 3 ISSUE(S):
  NO_LOADING_LOG: Loading log not found - method not called or file not found
  JSON_NOT_PARSED: JSON loaded log not found - parsing failed
  DIALOG_NOT_SHOWN: Template displayed log not found - dialog not shown

============================================================
[FAILURE] 1C INTEGRATION HAS ISSUES
============================================================
```

---

## ✅ ЧЕКЛИСТ ВИПРАВЛЕНЬ

- [ ] Створити temp_1c_test.json ПЕРЕД тестом
- [ ] Додати JSON структуру з name, zpl, variables
- [ ] Покращити вивід результатів (детальний як у cursor test)
- [ ] Додати парсинг помилок в LogAnalyzer
- [ ] Додати очищення temp файлу в кінці
- [ ] Зберегти file_size_before логіку (НЕ видаляти файл!)
- [ ] Додати детальні print з числами та статусами
- [ ] Перевірити що логи [1C-IMPORT] з'являються

---

## 🔑 КЛЮЧОВІ ПРИНЦИПИ

1. **ЗАВЖДИ створюй тестові файли** - НЕ покладайся на існуючі
2. **file_size_before, НЕ видаляти логи** - зберігай історію
3. **Детальний вивід з ЧИСЛАМИ** - не просто len(), а `{len(logs)}` з описом
4. **LogAnalyzer детектує КІЛЬКА проблем** - мінімум 3-4 типи
5. **Очищуй за собою** - видаляй тимчасові файли

---

**Версія:** 1.0  
**Дата:** 2025-01-08  
**Автор:** Senior AI Assistant  
**Мова:** Українська (правило userPreferences)
