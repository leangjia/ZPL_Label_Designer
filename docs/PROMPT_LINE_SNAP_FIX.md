# 🔴 ПРОМПТ: Line Element - Snap to Grid для ОБОИХ концов + Умные тесты

**КОНТЕКСТ ПРОБЛЕМЫ:**

Проект: 1C_Zebra - ZPL Label Designer (`D:\AiKlientBank\1C_Zebra\`)

**BUG:** Line элемент НЕ snap'ит end point (x2, y2) к сетке при drag. Только start point snap'ится!

**СКРИНШОТ:** Line от x=10mm до x=25mm визуально НЕ на grid пересечениях.

**КОД ПРОБЛЕМЫ:**
```python
# core/elements/shape_element.py, GraphicsLineItem.itemChange()
# Line має складнішу логіку snap - snap обох кінців
# Тут спрощена версія - snap тільки start point  ← УПРОЩЕНИЕ = БАГ!
```

---

## 🎯 ЦЕЛЬ

Исправить Line snap to grid чтобы:
1. **Start point (x, y) snap'ится** ✓ (уже работает)
2. **End point (x2, y2) snap'ится** ✗ (НЕ работает - исправить)
3. **PropertyPanel показывает snapped координаты**
4. **ZPL генерация точная** с snapped координатами

---

## 📋 ПОШАГОВЫЙ ПЛАН (5 ЭТАПОВ)

### ✅ ЭТАП 0: ОБЯЗАТЕЛЬНО - READ MEMORY

**ДЕЙСТВИЕ:**
```xml
<invoke name="memory:read_graph"/>
<invoke name="memory:search_nodes">
<parameter name="query">1C_Zebra Critical Rules Line Smart Testing Logger</parameter>
</invoke>
```

**ПРИМЕНИТЬ CRITICAL RULES:**
- Logger ТОЛЬКО `from utils.logger import logger` (НЕ logging.getLogger!)
- Filesystem tools для чтения/записи файлов
- Умный тест с LogAnalyzer ОБЯЗАТЕЛЬНО
- file_size_before вместо удаления логов
- exec(open('runner.py').read()) для запуска тестов

---

### ✅ ЭТАП 1: ИСПРАВЛЕНИЕ SNAP - ОБОИХ КОНЦОВ

**ШАГ 1.1: Читай КОД перед изменением**

```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\core\elements\shape_element.py</parameter>
</invoke>
```

**Найди:** `class GraphicsLineItem` → `def itemChange()`

**ШАГ 1.2: Исправь itemChange() - snap ОБОИХ концов**

**НОВАЯ ЛОГИКА:**
1. `ItemPositionChange`: snap start (x1, y1) AND end (x2, y2) к сетке
2. Пересчитать line vector = snapped_end - snapped_start (RELATIVE)
3. `setLine(0, 0, new_vector_x, new_vector_y)` обновить vector
4. `ItemPositionHasChanged`: сохранить snapped координаты в element.config

**КЛЮЧЕВОЙ КОД (для edit_file):**

```python
def itemChange(self, change, value):
    """Snap to grid для ОБОИХ концов линии"""
    if change == QGraphicsItem.ItemPositionChange:
        new_pos = value
        
        # Start point mm
        x1_mm = self._px_to_mm(new_pos.x())
        y1_mm = self._px_to_mm(new_pos.y())
        
        logger.debug(f"[LINE-DRAG] Start before snap: ({x1_mm:.2f}, {y1_mm:.2f})mm")
        
        # End point mm (absolute = start + vector)
        line_vector = self.line()
        x2_mm = self._px_to_mm(new_pos.x() + line_vector.x2())
        y2_mm = self._px_to_mm(new_pos.y() + line_vector.y2())
        
        logger.debug(f"[LINE-DRAG] End before snap: ({x2_mm:.2f}, {y2_mm:.2f})mm")
        
        # EMIT cursor
        if self.canvas:
            self.canvas.cursor_position_changed.emit(x1_mm, y1_mm)
        
        if self.snap_enabled:
            # SNAP ОБОИХ КОНЦОВ!
            snapped_x1 = self._snap_to_grid(x1_mm, 'x')
            snapped_y1 = self._snap_to_grid(y1_mm, 'y')
            snapped_x2 = self._snap_to_grid(x2_mm, 'x')
            snapped_y2 = self._snap_to_grid(y2_mm, 'y')
            
            logger.debug(f"[LINE-SNAP] Start: ({x1_mm:.2f}, {y1_mm:.2f}) -> ({snapped_x1:.2f}, {snapped_y1:.2f})mm")
            logger.debug(f"[LINE-SNAP] End: ({x2_mm:.2f}, {y2_mm:.2f}) -> ({snapped_x2:.2f}, {snapped_y2:.2f})mm")
            
            # Новая позиция start
            snapped_pos = QPointF(
                self._mm_to_px(snapped_x1),
                self._mm_to_px(snapped_y1)
            )
            
            # Новый вектор линии RELATIVE (snapped_end - snapped_start)
            new_vector_x_px = self._mm_to_px(snapped_x2 - snapped_x1)
            new_vector_y_px = self._mm_to_px(snapped_y2 - snapped_y1)
            
            # КРИТИЧНО: обновить line vector!
            self.setLine(0, 0, new_vector_x_px, new_vector_y_px)
            
            logger.debug(f"[LINE-SNAP] New vector: ({new_vector_x_px:.2f}, {new_vector_y_px:.2f})px")
            
            return snapped_pos
        
        return new_pos
    
    elif change == QGraphicsItem.ItemPositionHasChanged:
        # Сохранить snapped координаты
        line_vector = self.line()
        x1_mm = self._px_to_mm(self.pos().x())
        y1_mm = self._px_to_mm(self.pos().y())
        x2_mm = self._px_to_mm(self.pos().x() + line_vector.x2())
        y2_mm = self._px_to_mm(self.pos().y() + line_vector.y2())
        
        logger.debug(f"[LINE-FINAL] Start: ({x1_mm:.2f}, {y1_mm:.2f})mm")
        logger.debug(f"[LINE-FINAL] End: ({x2_mm:.2f}, {y2_mm:.2f})mm")
        
        self.element.config.x = x1_mm
        self.element.config.y = y1_mm
        self.element.config.x2 = x2_mm
        self.element.config.y2 = y2_mm
        
        logger.debug(f"[LINE-FINAL] Saved: start=({x1_mm:.2f}, {y1_mm:.2f}), end=({x2_mm:.2f}, {y2_mm:.2f})mm")
        
        if self.canvas and getattr(self.canvas, 'bounds_update_callback', None) and self.isSelected():
            self.canvas.bounds_update_callback(self)
    
    return super().itemChange(change, value)
```

**ПРИМЕНИТЬ:**
```xml
<invoke name="filesystem:edit_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\core\elements\shape_element.py</parameter>
<parameter name="edits">[{
  "oldText": "[ТОЧНЫЙ СТАРЫЙ КОД itemChange из файла]",
  "newText": "[НОВЫЙ КОД ВЫШЕ]"
}]</parameter>
</invoke>
```

**ШАГ 1.3: VERIFY изменения**

```xml
<invoke name="filesystem:read_text_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\core\elements\shape_element.py</parameter>
<parameter name="head">50</parameter>
</invoke>
```

**КРИТЕРИЙ УСПЕХА:**
- ✅ `[LINE-DRAG] Start before snap` логи
- ✅ `[LINE-DRAG] End before snap` логи
- ✅ `[LINE-SNAP] Start: ...` логи
- ✅ `[LINE-SNAP] End: ...` логи
- ✅ `setLine(0, 0, new_vector_x, new_vector_y)` код
- ✅ `[LINE-FINAL] Saved` логи

---

### ✅ ЭТАП 2: УМНЫЙ ТЕСТ - LINE SNAP BOTH ENDS

**ШАГ 2.1: Создать LogAnalyzer**

**ФАЙЛ:** `tests/test_line_snap_both_ends_smart.py`

```python
# -*- coding: utf-8 -*-
"""Умный тест Line snap to grid для ОБОИХ концов"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent, QEvent
from gui.main_window import MainWindow
from core.elements.shape_element import LineElement, LineConfig
from utils.logger import logger
import re


class LineSnapBothEndsAnalyzer:
    """Анализатор логов Line snap для обоих концов"""
    
    @staticmethod
    def parse_line_snap_logs(log_content):
        """Парсить логи snap для Line"""
        
        # [LINE-DRAG] Start before snap: (10.45, 10.23)mm
        start_before = re.findall(
            r'\[LINE-DRAG\] Start before snap: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-DRAG] End before snap: (25.67, 10.89)mm
        end_before = re.findall(
            r'\[LINE-DRAG\] End before snap: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-SNAP] Start: (10.45, 10.23) -> (10.00, 10.00)mm
        start_snap = re.findall(
            r'\[LINE-SNAP\] Start: \(([\d.]+), ([\d.]+)\) -> \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-SNAP] End: (25.67, 10.89) -> (25.00, 11.00)mm
        end_snap = re.findall(
            r'\[LINE-SNAP\] End: \(([\d.]+), ([\d.]+)\) -> \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-FINAL] Start: (10.00, 10.00)mm
        final_start = re.findall(
            r'\[LINE-FINAL\] Start: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        # [LINE-FINAL] End: (25.00, 11.00)mm
        final_end = re.findall(
            r'\[LINE-FINAL\] End: \(([\d.]+), ([\d.]+)\)mm',
            log_content
        )
        
        return {
            'start_before': [(float(m[0]), float(m[1])) for m in start_before],
            'end_before': [(float(m[0]), float(m[1])) for m in end_before],
            'start_snap': [
                {'before': (float(m[0]), float(m[1])), 'after': (float(m[2]), float(m[3]))}
                for m in start_snap
            ],
            'end_snap': [
                {'before': (float(m[0]), float(m[1])), 'after': (float(m[2]), float(m[3]))}
                for m in end_snap
            ],
            'final_start': [(float(m[0]), float(m[1])) for m in final_start],
            'final_end': [(float(m[0]), float(m[1])) for m in final_end]
        }
    
    @staticmethod
    def detect_issues(logs_dict, grid_size=1.0):
        """Детектировать 5 типов проблем"""
        issues = []
        
        # 1. END SNAP НЕ ПРОИЗОШЕЛ (логи end_snap пустые)
        if not logs_dict['end_snap']:
            issues.append({
                'type': 'END_SNAP_NOT_APPLIED',
                'desc': f"End snap логи отсутствуют - snap работает только для start point!"
            })
            return issues  # Дальше проверять нет смысла
        
        # 2. START SNAP INCORRECT (snapped координата НЕ кратна grid_size)
        if logs_dict['start_snap']:
            start_snapped = logs_dict['start_snap'][-1]['after']
            if start_snapped[0] % grid_size > 0.01 or start_snapped[1] % grid_size > 0.01:
                issues.append({
                    'type': 'START_SNAP_NOT_ON_GRID',
                    'desc': f"Start snapped to ({start_snapped[0]}, {start_snapped[1]}) но НЕ кратно {grid_size}mm"
                })
        
        # 3. END SNAP INCORRECT (snapped координата НЕ кратна grid_size)
        if logs_dict['end_snap']:
            end_snapped = logs_dict['end_snap'][-1]['after']
            if end_snapped[0] % grid_size > 0.01 or end_snapped[1] % grid_size > 0.01:
                issues.append({
                    'type': 'END_SNAP_NOT_ON_GRID',
                    'desc': f"End snapped to ({end_snapped[0]}, {end_snapped[1]}) но НЕ кратно {grid_size}mm"
                })
        
        # 4. SNAP != FINAL (snap показал одно, final другое)
        if logs_dict['start_snap'] and logs_dict['final_start']:
            start_snap_result = logs_dict['start_snap'][-1]['after']
            final_start_result = logs_dict['final_start'][-1]
            if abs(start_snap_result[0] - final_start_result[0]) > 0.01 or \
               abs(start_snap_result[1] - final_start_result[1]) > 0.01:
                issues.append({
                    'type': 'START_SNAP_FINAL_MISMATCH',
                    'desc': f"Start snap={start_snap_result}, final={final_start_result} - НЕ совпадают!"
                })
        
        if logs_dict['end_snap'] and logs_dict['final_end']:
            end_snap_result = logs_dict['end_snap'][-1]['after']
            final_end_result = logs_dict['final_end'][-1]
            if abs(end_snap_result[0] - final_end_result[0]) > 0.01 or \
               abs(end_snap_result[1] - final_end_result[1]) > 0.01:
                issues.append({
                    'type': 'END_SNAP_FINAL_MISMATCH',
                    'desc': f"End snap={end_snap_result}, final={final_end_result} - НЕ совпадают!"
                })
        
        # 5. FINAL НЕ НА GRID (финальные координаты НЕ кратны grid_size)
        if logs_dict['final_start']:
            final_s = logs_dict['final_start'][-1]
            if final_s[0] % grid_size > 0.01 or final_s[1] % grid_size > 0.01:
                issues.append({
                    'type': 'FINAL_START_NOT_ON_GRID',
                    'desc': f"Final start ({final_s[0]}, {final_s[1]}) НЕ на grid {grid_size}mm"
                })
        
        if logs_dict['final_end']:
            final_e = logs_dict['final_end'][-1]
            if final_e[0] % grid_size > 0.01 or final_e[1] % grid_size > 0.01:
                issues.append({
                    'type': 'FINAL_END_NOT_ON_GRID',
                    'desc': f"Final end ({final_e[0]}, {final_e[1]}) НЕ на grid {grid_size}mm"
                })
        
        return issues


def test_line_snap_both_ends():
    """Умный тест Line snap для обоих концов"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    print("=" * 60)
    print("[TEST] Line Snap to Grid - BOTH ENDS")
    print("=" * 60)
    
    # ТЕСТ: Создать Line и сдвинуть чтобы вызвать snap
    print("\n[TEST 1] Create Line and drag to trigger snap")
    
    # Создать Line элемент: start (9.55, 9.67), end (24.89, 10.23)
    config = LineConfig(x=9.55, y=9.67, x2=24.89, y2=10.23, thickness=1.0, color='black')
    line = LineElement(config)
    
    # Добавить в canvas
    from core.elements.shape_element import GraphicsLineItem
    graphics_line = GraphicsLineItem(line, dpi=203, canvas=window.canvas)
    window.canvas.scene.addItem(graphics_line)
    window.elements.append(line)
    window.graphics_items.append(graphics_line)
    
    app.processEvents()
    
    print(f"  Before drag: start=({line.config.x:.2f}, {line.config.y:.2f}), end=({line.config.x2:.2f}, {line.config.y2:.2f})mm")
    
    # Симулировать drag через itemChange (сдвиг на 1px чтобы вызвать snap)
    from PySide6.QtWidgets import QGraphicsItem
    new_pos = QPointF(graphics_line.pos().x() + 1.0, graphics_line.pos().y() + 1.0)
    snapped_pos = graphics_line.itemChange(QGraphicsItem.ItemPositionChange, new_pos)
    
    if snapped_pos != new_pos:
        graphics_line.setPos(snapped_pos)
        graphics_line.itemChange(QGraphicsItem.ItemPositionHasChanged, None)
    
    app.processEvents()
    
    print(f"  After drag: start=({line.config.x:.2f}, {line.config.y:.2f}), end=({line.config.x2:.2f}, {line.config.y2:.2f})mm")
    
    # Читать логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализ
    analyzer = LineSnapBothEndsAnalyzer()
    logs = analyzer.parse_line_snap_logs(new_logs)
    issues = analyzer.detect_issues(logs, grid_size=1.0)
    
    # Результат
    print("\n" + "=" * 60)
    print("[LINE SNAP BOTH ENDS] LOG ANALYSIS")
    print("=" * 60)
    print(f"Start snap logs: {len(logs['start_snap'])}")
    print(f"End snap logs: {len(logs['end_snap'])}")
    print(f"Final start logs: {len(logs['final_start'])}")
    print(f"Final end logs: {len(logs['final_end'])}")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] LINE SNAP HAS ISSUES")
        return 1
    
    print("\n[OK] Line snap for BOTH ends works correctly")
    
    # Финальные проверки
    assert line.config.x % 1.0 < 0.01, f"Start X {line.config.x} должно быть кратно 1mm"
    assert line.config.y % 1.0 < 0.01, f"Start Y {line.config.y} должно быть кратно 1mm"
    assert line.config.x2 % 1.0 < 0.01, f"End X {line.config.x2} должно быть кратно 1mm"
    assert line.config.y2 % 1.0 < 0.01, f"End Y {line.config.y2} должно быть кратно 1mm"
    
    print(f"\nFinal verification:")
    print(f"  Start: ({line.config.x:.2f}, {line.config.y:.2f})mm on grid ✓")
    print(f"  End: ({line.config.x2:.2f}, {line.config.y2:.2f})mm on grid ✓")
    
    return 0


if __name__ == "__main__":
    exit(test_line_snap_both_ends())
```

**СОЗДАТЬ ФАЙЛ:**
```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\test_line_snap_both_ends_smart.py</parameter>
<parameter name="content">[КОД ВЫШЕ]</parameter>
</invoke>
```

**ШАГ 2.2: Создать runner**

**ФАЙЛ:** `tests/run_line_snap_both_ends_test.py`

```python
# -*- coding: utf-8 -*-
"""Runner для test_line_snap_both_ends_smart.py"""

import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_line_snap_both_ends_smart.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
print(f"\nEXIT CODE: {result.returncode}")
```

**СОЗДАТЬ:**
```xml
<invoke name="filesystem:write_file">
<parameter name="path">D:\AiKlientBank\1C_Zebra\tests\run_line_snap_both_ends_test.py</parameter>
<parameter name="content">[КОД ВЫШЕ]</parameter>
</invoke>
```

---

### ✅ ЭТАП 3: ЗАПУСК ТЕСТА

```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_line_snap_both_ends_test.py').read())
```

**КРИТЕРИЙ УСПЕХА:**
- ✅ EXIT CODE = 0
- ✅ End snap logs > 0
- ✅ 0 issues detected
- ✅ Final coordinates on grid (кратны 1mm)

**ЕСЛИ FAILED:**
1. Читай STDERR логи - смотри где проблема
2. Исправь itemChange() код
3. Повтори тест

---

### ✅ ЭТАП 4: VERIFY В GUI (мануальный тест)

**ДЕЙСТВИЯ:**
1. Запустить `python main.py`
2. Добавить Line элемент (Sidebar → Line)
3. Drag Line - проверить что ОБЕИХ концов snap'ятся к grid
4. Property Panel - проверить координаты кратны 1mm

---

### ✅ ЭТАП 5: ДОКУМЕНТАЦИЯ

**Обновить memory:**
```xml
<invoke name="memory:add_observations">
<parameter name="observations">[{
  "entityName": "1C_Zebra Project",
  "contents": [
    "Line Element Snap Fix completed 2025-10-06 - EXIT CODE 0",
    "GraphicsLineItem.itemChange() теперь snap'ит ОБОИХ концов: start (x, y) AND end (x2, y2)",
    "Snap formula: nearest = offset + round((value-offset)/size)*size применяется к start и end отдельно",
    "Line vector пересчитывается после snap: new_vector = snapped_end - snapped_start (RELATIVE)",
    "DEBUG логи: [LINE-DRAG], [LINE-SNAP], [LINE-FINAL] показывают все этапы snap",
    "Smart test test_line_snap_both_ends_smart.py with LineSnapBothEndsAnalyzer - EXIT CODE 0",
    "LogAnalyzer detects 5 issue types: END_SNAP_NOT_APPLIED, *_SNAP_NOT_ON_GRID, SNAP_FINAL_MISMATCH, FINAL_NOT_ON_GRID",
    "Test results: Start AND End snap to grid correctly, all coordinates multiples of grid_size",
    "Files modified: core/elements/shape_element.py (GraphicsLineItem.itemChange method)"
  ]
}]</parameter>
</invoke>
```

---

## 🎯 ФИНАЛЬНЫЙ ЧЕКЛИСТ

- [ ] Memory прочитан через read_graph()
- [ ] Critical Rules применены (logger import, filesystem tools)
- [ ] itemChange() исправлен - snap ОБОИХ концов
- [ ] DEBUG логи добавлены: [LINE-DRAG], [LINE-SNAP], [LINE-FINAL]
- [ ] Умный тест создан с LineSnapBothEndsAnalyzer
- [ ] Runner создан
- [ ] Тест запущен через exec() - EXIT CODE = 0
- [ ] LogAnalyzer НЕ нашел проблем (0 issues)
- [ ] GUI мануальный тест - Line snap'ится правильно
- [ ] Memory обновлен через add_observations
- [ ] config.py: CURRENT_LOG_LEVEL = 'DEBUG' во время теста

---

**КРИТИЧНО:**
- НЕ выдумывай - читай РЕАЛЬНЫЙ код через filesystem:read_text_file
- Умный тест ОБЯЗАТЕЛЬНО с LogAnalyzer
- file_size_before вместо удаления логов
- `from utils.logger import logger` во ВСЕХ модулях
