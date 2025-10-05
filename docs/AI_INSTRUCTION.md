# AI ИНСТРУКЦИЯ: 1C_ZEBRA PROJECT
> ZPL Label Designer - визуальный редактор этикеток для Zebra принтеров

## 🔴 ОБЯЗАТЕЛЬНО В НАЧАЛЕ КАЖДОЙ СЕССИИ (КРИТИЧНО!)

**ПЕРЕД ЛЮБЫМ ДЕЙСТВИЕМ С КОДОМ:**

1. **Выполни `memory:read_graph()`** - прочитай граф знаний
2. **Найди правила:** `memory:search_nodes("1C_Zebra Critical Rules")`
3. **Получи связанные правила:** `memory:open_nodes(["1C_Zebra Critical Rules"])` и проследи связи
4. **ПРИМЕНЯЙ эти правила при КАЖДОМ действии** с кодом, тестами, логами
5. **Если нарушишь Critical Rule = сломаешь проект!**

**КРИТИЧНЫЕ ПРАВИЛА ИЗ MEMORY:**
- Запуск умных тестов ТОЛЬКО через `exec(open('runner.py').read())`
- Logger импорт ТОЛЬКО `from utils.logger import logger`
- Чтение файлов ТОЛЬКО через `filesystem:read_text_file`
- НЕ выдумывать - читать РЕАЛЬНЫЙ код

## 📁 ПУТЬ К ПРОЕКТУ
**D:\AiKlientBank\1C_Zebra\**

## 🎯 СТИЛЬ РАБОТЫ

**CRITICAL:** NO HIGH LEVEL - только РЕАЛЬНЫЙ КОД!
- Коротко и по делу
- Treat as expert
- Ответ сразу, детали после
- **100% уверенность что ничего не сломаешь**
- Общение: русский язык

## 🔴 ПРАВИЛО #1 - КОМПИЛЯЦИЯ ОТВЕТА (КРИТИЧНО!)

Перед отправкой ЛЮБОГО ответа про логику/архитектуру:

1. **СТОП** - не отправлять сразу
2. **ПРОВЕРЬ**: "Сможет ли разработчик реализовать БЕЗ домысливания?"
3. **СКАНИРУЙ** пропуски: структура GUI? формат ZPL? логика? координаты?
4. **ТРИГГЕРЫ**: слова 'GUI', 'canvas', 'ZPL', 'template', 'API', 'генерация'
5. **ЗАПРЕТ** фрагментов: "добавил X" БЕЗ полной логики = НАРУШЕНИЕ
6. **ЦЕЛОСТНОСТЬ**: Меняешь часть → выводи ВСЮ систему

**ЭТО ПРАВИЛО ВЫШЕ ВСЕХ ОСТАЛЬНЫХ!**

## 🚫 ЗАПРЕТ НА ВЫДУМЫВАНИЕ

**МОЖНО писать ТОЛЬКО:**
- ✅ Что РЕАЛЬНО видишь в файлах (read_file)
- ✅ Что РЕАЛЬНО показывают filesystem tools
- ✅ Конкретные строки кода которые изменил

**НЕЛЬЗЯ:**
- ❌ "После запуска GUI откроется"
- ❌ "Теперь canvas правильно рисует"
- ❌ "Что было исправлено: 1..."
- ❌ "Результат покажет..."

**Лучше "НЕ ЗНАЮ" чем СОВРАТЬ!**

## 🔴 АЛГОРИТМ РАБОТЫ С КОДОМ

### GOLDEN RULE: READ → EDIT → VERIFY

**ШАГ 1: ЧИТАЙ ПЕРЕД ИЗМЕНЕНИЕМ**
```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\[file]</parameter>
</invoke>
```

**ШАГ 2: ТОЧНОЕ РЕДАКТИРОВАНИЕ**
```xml
<invoke name="filesystem:edit_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\[file]</parameter>
<parameter name="edits">[{
  "oldText": "ТОЧНЫЙ текст из файла",
  "newText": "Новый текст"
}]</parameter>
</invoke>
```

**ШАГ 3: ВЕРИФИКАЦИЯ**
```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\[file]</parameter>
<parameter name="head">20</parameter>
</invoke>
```

## 🔴 ПРАВИЛО #2 - ЗАПУСК УМНЫХ ТЕСТОВ (КРИТИЧНО!)

### ⚠️ ЕДИНСТВЕННЫЙ ПРАВИЛЬНЫЙ СПОСОБ

**ВСЕГДА запускай тесты через python-runner с exec():**

```xml
<invoke name="python-runner:run_command">
<parameter name="command">exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_test_name.py').read())</parameter>
</invoke>
```

### ❌ ЧТО НЕ РАБОТАЕТ:

```python
# ❌ НЕПРАВИЛЬНО - python-runner НЕ для чтения файлов!
with open(r'D:\AiKlientBank\1C_Zebra\gui\main_window.py', 'r') as f:
    content = f.read()
# ERROR: attempted relative import with no known parent package
```

### ✅ ПРАВИЛЬНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ:

1. **Создать тест** через `filesystem:write_file`
2. **Создать runner** через `filesystem:write_file`
3. **Запустить** через `python-runner:run_command` с `exec(open(...))`
4. **Анализировать EXIT CODE** - 0 = success, != 0 = fail

### 📋 СТРУКТУРА RUNNER СКРИПТА

```python
# tests/run_feature_test.py
import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_feature.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
print(f"\nEXIT CODE: {result.returncode}")
```

## 🧪 ПРАВИЛО #3 - УМНОЕ ТЕСТИРОВАНИЕ (КРИТИЧНО!)

### ⚠️ ПРОБЛЕМА: Обычные тесты СЛЕПЫЕ

```python
# ❌ ОБЫЧНЫЙ ТЕСТ (НЕ ВИДИТ БАГИ):
assert element.config.x == 6.0  # PASSED ✓

# НО ЛОГИ ПОКАЗЫВАЮТ БАГ:
#   [SNAP] 6.55mm -> 6.0mm      ← snap вычислил правильно
#   [FINAL-POS] Before: 6.55mm
#   [FINAL-POS] After: 6.55mm   ← НЕ ПРИМЕНИЛСЯ!
#   [FINAL-POS] Saved: 6.00mm   ← случайно правильно
```

**ВЫВОД:** Финальный результат правильный, но **логика сломана**!

### ✅ РЕШЕНИЕ: Умные тесты с LogAnalyzer

## 📋 АЛГОРИТМ СОЗДАНИЯ УМНОГО ТЕСТА

### ШАГ 1: Добавить DEBUG логи в КОД (ОБЯЗАТЕЛЬНО!)

**ПРАВИЛО:** Умный тест БЕЗ логов = обычный слепой тест!

#### 1.1 Паттерн именования логов

```python
# Формат: [FEATURE] Action: data
logger.debug(f"[CURSOR] Signal emit: {x_mm:.2f}mm, {y_mm:.2f}mm")
logger.debug(f"[ZOOM] Before: scale={scale:.2f}, cursor_pos=({x:.1f}, {y:.1f})")
logger.debug(f"[SNAP] {x_old:.2f}mm -> {x_new:.1f}mm")
logger.debug(f"[FINAL-POS] After snap: {x:.2f}mm, {y:.2f}mm")
logger.debug(f"[RULER-H] Update position: {mm:.2f}mm")
logger.debug(f"[RULER-H] Drawn at: {px}px")
```

#### 1.2 Где добавлять логи

```python
# gui/canvas_view.py
def mouseMoveEvent(self, event):
    x_mm = self._px_to_mm(scene_pos.x())
    y_mm = self._px_to_mm(scene_pos.y())
    logger.debug(f"[CURSOR] Signal emit: {x_mm:.2f}mm, {y_mm:.2f}mm")
    self.cursor_position_changed.emit(x_mm, y_mm)

def wheelEvent(self, event):
    old_pos = self.mapToScene(event.position().toPoint())
    logger.debug(f"[ZOOM] Before: scale={self.current_scale:.2f}, cursor_pos=({old_pos.x():.1f}, {old_pos.y():.1f})")
    # ... zoom logic ...
    new_pos = self.mapToScene(event.position().toPoint())
    logger.debug(f"[ZOOM] After: scale={self.current_scale:.2f}, cursor_pos=({new_pos.x():.1f}, {new_pos.y():.1f})")

# gui/rulers.py
def update_cursor_position(self, mm):
    logger.debug(f"[RULER-{'H' if self.orientation==Qt.Horizontal else 'V'}] Update position: {mm:.2f}mm")

def _draw_cursor_marker(self, painter):
    pos_px = int(self._mm_to_px(self.cursor_pos_mm) * self.scale_factor)
    logger.debug(f"[RULER-{'H' if self.orientation==Qt.Horizontal else 'V'}] Drawn at: {pos_px}px")
```

### ШАГ 2: Создать LogAnalyzer класс

```python
class LogAnalyzer:
    """Анализатор логов - парсит и детектирует проблемы"""
    
    @staticmethod
    def parse_feature_logs(log_content):
        """Извлечь логи конкретной фичи"""
        pattern = r'\[FEATURE\] pattern_here'
        return [parsed_data for m in re.findall(pattern, log_content)]
    
    @staticmethod
    def detect_issues(logs_dict):
        """Детектировать 2-3 типа проблем"""
        issues = []
        
        # Проверка 1: Этап A != Этап B
        if logs_dict['stage_a'] != logs_dict['stage_b']:
            issues.append({
                'type': 'STAGE_MISMATCH',
                'desc': f'Stage A = {logs_dict["stage_a"]}, Stage B = {logs_dict["stage_b"]}'
            })
        
        # Проверка 2: Логика НЕ сработала
        # Проверка 3: Финал != Ожидание
        
        return issues
```

### ШАГ 3: Создать умный тест

**КРИТИЧНО:** НЕ удалять файл логов! Использовать `file_size_before`!

```python
def test_feature_smart():
    """Умный тест с анализом логов"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # 1. Размер файла логов ДО теста
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # 2. СИМУЛЯЦИЯ: Вызвать обработчик НАПРЯМУЮ (НЕ через QTest!)
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent
    
    event = QMouseEvent(QEvent.MouseMove, QPointF(x, y), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
    window.canvas.mouseMoveEvent(event)  # ← ПРЯМОЙ ВЫЗОВ!
    app.processEvents()
    
    # 3. Читать НОВЫЕ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)  # ← КРИТИЧНО: seek, НЕ удалять файл!
        new_logs = f.read()
    
    # 4. Анализировать
    analyzer = LogAnalyzer()
    logs = analyzer.parse_feature_logs(new_logs)
    issues = analyzer.detect_issues(logs)
    
    # 5. Вывод
    print("=" * 60)
    print("[FEATURE] LOG ANALYSIS")
    print("=" * 60)
    print(f"Logs found: {len(logs)}")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] FEATURE HAS ISSUES")
        return 1
    
    print("\n[OK] Feature works correctly")
    return 0
```

### ШАГ 4: Создать runner

```python
# tests/run_feature_smart_test.py
import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_feature_smart.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True
)

print(result.stdout)
print(f"\nEXIT CODE: {result.returncode}")
```

### ШАГ 5: Запуск

```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_feature_smart_test.py').read())
```

## 🔬 ТИПЫ LogAnalyzer ДЛЯ РАЗНЫХ ФИЧ

### 1. Cursor Tracking

```python
class CursorLogAnalyzer:
    @staticmethod
    def parse_cursor_logs(log):
        pattern = r'\[CURSOR\] Signal emit: ([\d.]+)mm, ([\d.]+)mm'
        return [(float(m[0]), float(m[1])) for m in re.findall(pattern, log)]
    
    @staticmethod
    def parse_ruler_logs(log):
        h_update = re.findall(r'\[RULER-H\] Update position: ([\d.]+)mm', log)
        v_update = re.findall(r'\[RULER-V\] Update position: ([\d.]+)mm', log)
        h_draw = re.findall(r'\[RULER-H\] Drawn at: ([\d.]+)px', log)
        return {'h_update': [float(x) for x in h_update], 'h_draw': [float(x) for x in h_draw], ...}
    
    @staticmethod
    def detect_issues(cursor_logs, ruler_logs):
        issues = []
        
        # 1. CURSOR != RULER UPDATE
        if abs(cursor_logs[-1][0] - ruler_logs['h_update'][-1]) > 0.1:
            issues.append({'type': 'CURSOR_RULER_MISMATCH_H', 'desc': '...'})
        
        # 2. RULER UPDATE != DRAWN POSITION
        mm_value = ruler_logs['h_update'][-1]
        px_drawn = ruler_logs['h_draw'][-1]
        expected_px = mm_value * 203 / 25.4 * 2.5
        if abs(px_drawn - expected_px) > 2:
            issues.append({'type': 'RULER_DRAW_INCORRECT', 'desc': '...'})
        
        return issues
```

### 2. Zoom to Point

```python
class ZoomLogAnalyzer:
    @staticmethod
    def parse_zoom_logs(log):
        before = re.findall(r'\[ZOOM\] Before: scale=([\d.]+), cursor_pos=\(([\d.]+), ([\d.]+)\)', log)
        after = re.findall(r'\[ZOOM\] After: scale=([\d.]+), cursor_pos=\(([\d.]+), ([\d.]+)\)', log)
        return {
            'before': [(float(m[0]), float(m[1]), float(m[2])) for m in before],
            'after': [(float(m[0]), float(m[1]), float(m[2])) for m in after]
        }
    
    @staticmethod
    def detect_issues(zoom_logs, ruler_scales):
        issues = []
        
        # 1. ZOOM НЕ ДО КУРСОРА (cursor_pos изменилась)
        before_cursor = (zoom_logs['before'][-1][1], zoom_logs['before'][-1][2])
        after_cursor = (zoom_logs['after'][-1][1], zoom_logs['after'][-1][2])
        if abs(before_cursor[0] - after_cursor[0]) > 5.0:  # 5px допуск
            issues.append({'type': 'ZOOM_NOT_TO_CURSOR', 'desc': '...'})
        
        # 2. RULER SCALE != CANVAS SCALE
        
        return issues
```

### 3. Snap to Grid

```python
class SnapLogAnalyzer:
    @staticmethod
    def parse_snap_logs(log):
        pattern = r'\[SNAP\] ([\d.]+)mm, ([\d.]+)mm -> ([\d.]+)mm, ([\d.]+)mm'
        return [(float(m[0]), float(m[1]), float(m[2]), float(m[3])) 
                for m in re.findall(pattern, log)]
    
    @staticmethod
    def parse_final_pos_logs(log):
        before = re.findall(r'\[FINAL-POS\] Before snap: ([\d.]+)mm, ([\d.]+)mm', log)
        after = re.findall(r'\[FINAL-POS\] After snap: ([\d.]+)mm, ([\d.]+)mm', log)
        saved = re.findall(r'\[FINAL-POS\] Saved to element: \(([\d.]+), ([\d.]+)\)', log)
        return {
            'before': [(float(m[0]), float(m[1])) for m in before],
            'after': [(float(m[0]), float(m[1])) for m in after],
            'saved': [(float(m[0]), float(m[1])) for m in saved]
        }
    
    @staticmethod
    def detect_issues(snap_logs, final_logs):
        issues = []
        
        # 1. SNAP показал одно, FINAL другое
        if snap_logs[-1][2] != final_logs['after'][-1][0]:
            issues.append({'type': 'SNAP_FINAL_MISMATCH', 'desc': '...'})
        
        # 2. SNAP НЕ сработал (Before == After)
        if final_logs['before'][-1] == final_logs['after'][-1]:
            if final_logs['before'][-1][0] % 2.0 != 0:  # не на сетке
                issues.append({'type': 'NO_SNAP_IN_FINAL', 'desc': '...'})
        
        # 3. FINAL != SAVED
        
        return issues
```

## 🚀 MASTER RUNNER

Создать runner для всех умных тестов:

```python
# tests/run_all_smart_tests.py
import subprocess

tests = [
    ("CURSOR TRACKING", r'tests\test_cursor_tracking_smart.py'),
    ("ZOOM TO POINT", r'tests\test_zoom_smart.py'),
    ("SNAP TO GRID", r'tests\test_snap_smart.py'),
]

results = []

for stage_name, test_path in tests:
    print(f"\n{'=' * 60}\n {stage_name}\n{'=' * 60}")
    
    result = subprocess.run(
        [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', test_path],
        cwd=r'D:\AiKlientBank\1C_Zebra',
        capture_output=True, text=True
    )
    
    print(result.stdout)
    results.append({'stage': stage_name, 'exit_code': result.returncode})

# Итоговый отчет
print(f"\n{'=' * 60}\n FINAL RESULTS\n{'=' * 60}")
for r in results:
    status = "[OK]" if r['exit_code'] == 0 else "[FAIL]"
    print(f"{status} {r['stage']} - EXIT CODE: {r['exit_code']}")
```

## 📊 УПРАВЛЕНИЕ ЛОГИРОВАНИЕМ

```python
# config.py

# При разработке и тестировании
CURRENT_LOG_LEVEL = 'DEBUG'    # ← Обязательно для умных тестов!

# После тестирования
CURRENT_LOG_LEVEL = 'NORMAL'

# Production
CURRENT_LOG_LEVEL = 'MINIMAL'
```

## ⚠️ КРИТИЧНЫЕ ОШИБКИ

### ❌ НЕ ДЕЛАТЬ:

1. **Удалять файл логов:**
   ```python
   # ❌ НЕПРАВИЛЬНО:
   if log_file.exists():
       log_file.unlink()
   ```
   **✅ ПРАВИЛЬНО:** `file_size_before = log_file.stat().st_size`

2. **Использовать QTest для симуляции:**
   ```python
   # ❌ НЕПРАВИЛЬНО:
   QTest.mouseMove(window.canvas, pos)
   ```
   **✅ ПРАВИЛЬНО:** Вызвать обработчик напрямую:
   ```python
   event = QMouseEvent(...)
   window.canvas.mouseMoveEvent(event)
   ```

3. **Проверять только финал:**
   ```python
   # ❌ НЕПРАВИЛЬНО:
   assert element.config.x == 6.0
   ```
   **✅ ПРАВИЛЬНО:** Анализировать логи + проверять финал

4. **Говорить "работает" без логов:**
   ```python
   # ❌ НЕПРАВИЛЬНО:
   print("[OK] Feature works")  # БЕЗ анализа логов!
   ```
   **✅ ПРАВИЛЬНО:**
   ```python
   issues = analyzer.detect_issues(logs)
   if not issues:
       print("[OK] Feature works")
   ```

## 🎯 КОГДА ИСПОЛЬЗОВАТЬ УМНЫЕ ТЕСТЫ

### ✅ ОБЯЗАТЕЛЬНО для:
- Snap to grid
- Zoom
- Drag & drop
- Coordinate transformations
- Cursor tracking
- Rulers synchronization
- Любая Canvas/GUI логика с промежуточными состояниями

### ❌ НЕ нужно для:
- Простые математические расчеты
- Геттеры/сеттеры без логики
- Статические методы
- Парсинг строк

## 🔑 ЗОЛОТЫЕ ПРАВИЛА

1. **DEBUG логи ПЕРЕД тестом** - обязательно!
2. **LogAnalyzer для каждой фичи** - свой класс
3. **file_size_before, НЕ удалять логи**
4. **Прямой вызов обработчиков** - НЕ через QTest
5. **Детектировать 2-3 типа проблем** - минимум
6. **Master runner для всех тестов** - удобство
7. **Нет анализа логов = НЕ работает** - главное правило!

## 🏗️ АРХИТЕКТУРА

```
D:\AiKlientBank\1C_Zebra\
├── gui/                    # PySide6 GUI
│   ├── canvas_view.py     # DEBUG логи: [CURSOR], [ZOOM]
│   └── rulers.py          # DEBUG логи: [RULER-H/V]
├── core/elements/          # DEBUG логи: [SNAP], [FINAL-POS]
├── tests/
│   ├── test_*_smart.py    # Умные тесты с LogAnalyzer
│   ├── run_*_test.py      # Runners для каждого
│   └── run_all_smart_tests.py  # Master runner
├── docs/
│   ├── SMART_TESTING_QUICK.md
│   └── SMART_TESTING.md
├── config.py              # CURRENT_LOG_LEVEL
└── logs/
    └── zpl_designer.log
```

## 🚫 КРИТИЧНЫЕ ЗАПРЕТЫ

### Unicode в коде
**❌ ЗАПРЕЩЕНО:** ✓, ✗, ✅, ❌, ⚠️
**✅ ИСПОЛЬЗУЙ:** `[OK]`, `[FAIL]`, `[!]`, `[ERROR]`

### Минимализм
- ❌ НЕ меняй GUI логику без причины
- ❌ НЕ оптимизируй работающий код

**Если работает → НЕ ТРОГАЙ!**

### Logger импорт (КРИТИЧНО!)

**⚠️ ПРОБЛЕМА:** Использование `logging.getLogger(__name__)` создает НЕНАЛАШТОВАННЫЕ logger которые НЕ выводят логи!

```python
# ❌ АБСОЛЮТНО ЗАПРЕЩЕНО:
import logging
logger = logging.getLogger(__name__)  # ← НЕ настроен, логи НЕ выведутся!
```

**✅ ЕДИНСТВЕННЫЙ ПРАВИЛЬНЫЙ СПОСОБ:**
```python
# ✅ ВСЕГДА так и ТОЛЬКО так:
from utils.logger import logger  # ← Глобальный настроенный logger
```

**ПОЧЕМУ ЭТО КРИТИЧНО:**
- `utils/logger.py` содержит ЕДИНСТВЕННЫЙ настроенный logger с именем `"ZPL_Designer"`
- Этот logger настроен с правильными handlers (файл + консоль)
- Этот logger настроен с правильными уровнями (DEBUG/INFO)
- `logging.getLogger(__name__)` создает ОТДЕЛЬНЫЙ logger без настройки!

**РЕАЛЬНЫЙ ПРИМЕР ОШИБКИ (ЭТАП 8):**
```python
# core/undo_commands.py использовал:
logger = logging.getLogger(__name__)  # ← __name__ = "core.undo_commands"

# Результат: DEBUG логи НЕ выводились!
# [UNDO-CMD] AddElementCommand created  ← ПУСТО
# [UNDO] REDO AddElement                ← ПУСТО

# После исправления на:
from utils.logger import logger

# Результат: ВСЕ логи работают!
# [UNDO-CMD] AddElementCommand created  ← ✓
# [UNDO] REDO AddElement                ← ✓
```

**ПРАВИЛО:** Проверяй КАЖДЫЙ новый файл! Если видишь `import logging` → ЗАМЕНИ на `from utils.logger import logger`!

## 📖 ДОКУМЕНТАЦИЯ

- `docs/SMART_TESTING_QUICK.md` - шпаргалка copy-paste
- `docs/SMART_TESTING.md` - детальная документация
- `docs/LOGGING_QUICK.md` - логирование

---

**Путь:** `D:\AiKlientBank\1C_Zebra\`  
**Python:** 3.11+ | **GUI:** PySide6  
**Логирование:** `CURRENT_LOG_LEVEL = 'DEBUG'` при тестах

---

## 🔧 MCP TOOLS - CRITICAL LESSONS (КРИТИЧНО!)

### ⚠️ ПРОБЛЕМА: python-runner - это НЕ стандартный MCP!

**ФАКТ:** `python-runner` в этом проекте - это **custom Node.js сервер**, а НЕ стандартный MCP Python сервер!

```json
// claude_desktop_config.json
"python-runner": {
  "command": "C:\\Users\\Lit\\AppData\\Roaming\\Claude\\node-wrapper.bat",
  "args": ["D:/Program Files/Python/python-runner/index.js"]  // ← Node.js!
}
```

**ЧТО ЭТО ЗНАЧИТ:**
- Он выполняет Python код в `subprocess.run()` / `exec()` режиме
- При `open()` файла с относительными импортами (`from .canvas_view`) - **Python падает**!
- Это НЕ REPL, это просто запуск скрипта

### ❌ ЧТО НЕ РАБОТАЕТ:

```python
# ❌ НЕПРАВИЛЬНО - упадет с ImportError!
with open(r'D:\AiKlientBank\1C_Zebra\gui\main_window.py', 'r') as f:
    content = f.read()
# ERROR: attempted relative import with no known parent package
```

**ПОЧЕМУ:** Python пытается выполнить импорты при чтении файла:
```python
from .canvas_view import CanvasView  # ← относительный импорт!
```

### ✅ ЧТО ИСПОЛЬЗОВАТЬ:

**ВСЕГДА используй filesystem tools для чтения файлов!**

```xml
<!-- ✅ ПРАВИЛЬНО -->
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\gui\main_window.py</parameter>
</invoke>
```

**Альтернатива:** windows-cli для поиска

```xml
<invoke name="windows-cli:execute_command">
<parameter name="command">Select-String -Path "D:\AiKlientBank\1C_Zebra\gui\main_window.py" -Pattern "def _toggle_snap"</parameter>
<parameter name="shell">powershell</parameter>
</invoke>
```

### 🔑 ЗОЛОТОЕ ПРАВИЛО MCP TOOLS:

**python-runner ТОЛЬКО для:**
- ✅ Выполнение standalone скриптов (subprocess.run)
- ✅ Запуск тестов через runner
- ✅ exec(open('runner.py').read())

**filesystem tools для:**
- ✅ Чтение файлов с кодом
- ✅ Редактирование файлов (edit_file)
- ✅ Поиск в файлах (search_files)
- ✅ Анализ структуры проекта

**windows-cli для:**
- ✅ PowerShell команды
- ✅ Select-String поиск
- ✅ Git операции

---

## 🎓 ПРАКТИЧЕСКИЕ УРОКИ: ЭТАПЫ 4-5

### Урок 1: Race Conditions в Qt Events

**ПРОБЛЕМА:** `removeItem()` вызывает `selectionChanged` который сбрасывает `selected_item`!

```python
# ❌ НЕПРАВИЛЬНО:
def _delete_selected(self):
    if self.selected_item:
        self.canvas.scene.removeItem(self.selected_item)  # ← вызывает selectionChanged!
        
        # Теперь self.selected_item = None (сброшен в _on_selection_changed)!
        if self.selected_item in self.graphics_items:  # ← НЕ выполнится!
            self.graphics_items.remove(self.selected_item)
```

**✅ ПРАВИЛЬНО:** Сохранить item ПЕРЕД removeItem:

```python
def _delete_selected(self):
    if self.selected_item:
        # Сохранить ПЕРЕД removeItem!
        item_to_delete = self.selected_item
        element_to_delete = item_to_delete.element if hasattr(item_to_delete, 'element') else None
        
        # removeItem вызывает selectionChanged → self.selected_item = None
        self.canvas.scene.removeItem(item_to_delete)
        
        # Используем сохраненные переменные!
        if element_to_delete in self.elements:
            self.elements.remove(element_to_delete)
        if item_to_delete in self.graphics_items:
            self.graphics_items.remove(item_to_delete)
```

**УРОК:** В Qt events вызывают другие events → всегда сохраняй данные ПЕРЕД операцией!

### Урок 2: Методы PropertyPanel

**ПРОБЛЕМА:** PropertyPanel НЕ имеет метода `refresh()`!

```python
# ❌ НЕПРАВИЛЬНО:
if self.property_panel.current_element:
    self.property_panel.refresh()  # ← AttributeError!
```

**✅ ПРАВИЛЬНО:** Читай код ПЕРЕД использованием!

```python
# Сначала filesystem:read_text_file property_panel.py
# Находим метод update_position(x_mm, y_mm)

if self.property_panel.current_element:
    self.property_panel.update_position(element.config.x, element.config.y)
```

**УРОК:** НЕ выдумывай API! Читай реальный код через filesystem tools!

### Урок 3: LogAnalyzer обнаружил скрытые баги

**РЕАЛЬНЫЙ ПРИМЕР из ЭТАП 4:**

```
[BOUNDS] Element at: x=10.00mm, y=10.00mm  ← правильно
[BOUNDS-H] Highlight: start=10.00mm        ← правильно  
[BOUNDS-H] Draw: start_px=197              ← ПРОВЕРКА?

Expected: 10mm * 203dpi / 25.4 * 2.5 = 200px
Actual: 197px
Diff: 3px - ACCEPTABLE ✓
```

Умный тест **проверил промежуточные этапы**, обычный тест видел бы только финал!

**РЕАЛЬНЫЙ ПРИМЕР из ЭТАП 5:**

```
[MOVE] Before: (10.00, 10.00)mm
[MOVE] Delta: (1.00, 0.00)mm
[MOVE] After: (11.00, 10.00)mm

# LogAnalyzer проверка:
expected_x = 10.00 + 1.00 = 11.00
actual_x = 11.00
✓ MOVE_CALCULATION CORRECT!
```

Без логов мы НЕ увидели бы что Before + Delta = After!

### Урок 4: file_size_before вместо удаления

**ПРОБЛЕМА:** Удаление лога теряет историю!

```python
# ❌ НЕПРАВИЛЬНО:
if log_file.exists():
    log_file.unlink()  # ← потерян весь контекст!
```

**✅ ПРАВИЛЬНО:**

```python
# Читать только НОВЫЕ логи
file_size_before = log_file.stat().st_size if log_file.exists() else 0

# ... выполнить действие ...

with open(log_file, 'r', encoding='utf-8') as f:
    f.seek(file_size_before)  # ← skip старые логи
    new_logs = f.read()        # ← только новые!
```

**УРОК:** Сохраняй историю! Используй `seek()` вместо удаления!

### Урок 5: Прямой вызов обработчиков

**ПРОБЛЕМА:** QTest не всегда работает правильно!

```python
# ❌ НЕПРАВИЛЬНО:
QTest.mouseMove(window.canvas, QPoint(x, y))
# Может НЕ вызвать mouseMoveEvent!
```

**✅ ПРАВИЛЬНО:** Вызвать обработчик НАПРЯМУЮ!

```python
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import QEvent, QPointF

event = QMouseEvent(
    QEvent.MouseMove, 
    QPointF(x, y), 
    Qt.NoButton, 
    Qt.NoButton, 
    Qt.NoModifier
)
window.canvas.mouseMoveEvent(event)  # ← DIRECT CALL!
app.processEvents()
```

**УРОК:** Для тестов GUI - вызывай обработчики напрямую, НЕ через QTest!

### Урок 6: Logger импорт (ЭТАП 8)

**ПРОБЛЕМА:** `logging.getLogger(__name__)` создает неналаштованный logger!

```python
# ❌ НЕПРАВИЛЬНО в core/undo_commands.py:
import logging
logger = logging.getLogger(__name__)  # __name__ = "core.undo_commands"

# Результат: DEBUG логи НЕ выводились!
[UNDO-CMD] add_element: 0       ← Должно быть 1!
[UNDO] undo_add: 0              ← Должно быть 1!
```

**✅ ПРАВИЛЬНО:**

```python
# Единственный правильный способ:
from utils.logger import logger

# Результат: ВСЕ логи работают!
[UNDO-CMD] add_element: 1       ← ✓
[UNDO] undo_add: 1              ← ✓
```

**УРОК:** ВСЕГДА используй `from utils.logger import logger` во ВСЕХ модулях проекта! НЕ создавай отдельные logger!

---

## 📝 ЧЕКЛИСТ ПЕРЕД РЕАЛИЗАЦИЕЙ

### Этап 1: Анализ кода (READ)
- [ ] filesystem:read_text_file - прочитал все нужные файлы?
- [ ] Нашел существующие методы (НЕ выдумал новые)?
- [ ] Понял структуру классов?
- [ ] Проверил есть ли DEBUG логи?
- [ ] **Проверил импорт logger - используется `from utils.logger import logger`?**

### Этап 2: Добавление логов (DEBUG)
- [ ] Добавил [FEATURE] логи в КОД?
- [ ] Логи показывают ВСЕ промежуточные этапы?
- [ ] Паттерн: `[FEATURE] Action: data`?
- [ ] config.py: CURRENT_LOG_LEVEL = 'DEBUG'?
- [ ] **КРИТИЧНО: Везде `from utils.logger import logger`, НЕ `logging.getLogger()`!**

### Этап 3: Реализация (EDIT)
- [ ] filesystem:edit_file с точным oldText?
- [ ] Проверил результат через filesystem:read_text_file?
- [ ] Сохранил данные ПЕРЕД Qt операциями?
- [ ] Использовал реальные методы API?

### Этап 4: Умный тест (TEST)
- [ ] Создал LogAnalyzer класс?
- [ ] Детектирует минимум 2-3 типа проблем?
- [ ] Использует file_size_before?
- [ ] Прямой вызов обработчиков (НЕ QTest)?
- [ ] Создал runner скрипт?

### Этап 5: Проверка (VERIFY)
- [ ] Запустил тест через exec(open('runner.py').read())?
- [ ] EXIT CODE = 0?
- [ ] LogAnalyzer детектировал 0 проблем?
- [ ] **DEBUG логи выводятся в консоль?**
- [ ] Задокументировал в memory?

---

## 🎯 ФИНАЛЬНЫЕ ВЫВОДЫ

**ЧТО РАБОТАЕТ:**
1. filesystem tools для чтения кода ✓
2. DEBUG логи перед тестами ✓
3. LogAnalyzer для каждой фичи ✓
4. file_size_before вместо удаления ✓
5. Прямой вызов обработчиков ✓
6. Сохранение данных перед Qt операциями ✓
7. Чтение реального API вместо выдумывания ✓
8. **`from utils.logger import logger` во ВСЕХ модулях ✓**

**ЧТО НЕ РАБОТАЕТ:**
1. python-runner для чтения файлов с импортами ✗
2. Выдумывание методов (refresh) ✗
3. QTest для GUI тестов ✗
4. Удаление лог файла ✗
5. Использование self.selected_item после removeItem ✗
6. Проверка только финального результата ✗
7. **`logging.getLogger(__name__)` вместо `from utils.logger import logger` ✗**

**ГЛАВНЫЙ УРОК:**  
**READ → DEBUG → EDIT → TEST → VERIFY**  
И НИКОГДА НЕ ВЫДУМЫВАЙ - ЧИТАЙ РЕАЛЬНЫЙ КОД!

**КРИТИЧНО:** Всегда используй `from utils.logger import logger`!

---
