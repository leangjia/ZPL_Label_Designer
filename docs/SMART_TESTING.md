# УМНОЕ ТЕСТИРОВАНИЕ CANVAS/GUI

## Проблема с обычными тестами

**Обычные тесты НЕ ВИДЯТ внутренних проблем:**
```python
# Тест проверяет только финальный результат
assert element.config.x == 6.0  # PASSED ✓

# НО НЕ ВИДИТ что внутри snap НЕ работал!
# Логи показывают:
#   [SNAP] 6.55mm -> 6.6mm  (во время drag)
#   [FINAL-POS] Before: 6.55mm
#   [FINAL-POS] After: 6.55mm  ← НЕ СНЕПНУЛО!
#   [FINAL-POS] Saved: 6.55mm
```

## Решение: Анализ логов

**Умный тест анализирует логи и детектирует:**

1. **SNAP_FINAL_MISMATCH** - последний [SNAP] не совпадает с [FINAL-POS After]
   ```
   [SNAP] 6.55mm -> 6.0mm  (показал что снепнуло)
   [FINAL-POS] After: 6.55mm  (но НЕ снепнуло!)
   ```

2. **NO_SNAP_IN_FINAL** - [FINAL-POS Before] == [FINAL-POS After]
   ```
   [FINAL-POS] Before: 6.55mm
   [FINAL-POS] After: 6.55mm  (snap НЕ применился!)
   ```

3. **FINAL_SAVED_MISMATCH** - [FINAL-POS After] != [FINAL-POS Saved]
   ```
   [FINAL-POS] After: 6.0mm
   [FINAL-POS] Saved: 6.55mm  (сохранили неснепленное!)
   ```

## Структура умного теста

```python
class LogAnalyzer:
    """Анализирует логи на проблемы"""
    
    @staticmethod
    def parse_snap_logs(log_content):
        """Извлечь все [SNAP] записи"""
        pattern = r'\[SNAP\] ([\d.]+)mm, ([\d.]+)mm -> ([\d.]+)mm, ([\d.]+)mm'
        # Возвращает: [(from_x, from_y, to_x, to_y), ...]
    
    @staticmethod
    def parse_final_pos_logs(log_content):
        """Извлечь все [FINAL-POS] записи"""
        # Возвращает: {'before': [...], 'after': [...], 'saved': [...]}
    
    @staticmethod
    def detect_snap_issues(snap_logs, final_logs):
        """Детектировать проблемы"""
        # Проверка 1: SNAP vs FINAL-POS After
        # Проверка 2: FINAL-POS Before vs After
        # Проверка 3: FINAL-POS After vs Saved
```

## Алгоритм тестирования

1. **Запомнить размер лог-файла ДО теста**
2. **Выполнить действие** (например, перетащить элемент)
3. **Прочитать НОВЫЕ логи** (от запомненной позиции)
4. **Распарсить логи** (найти [SNAP], [FINAL-POS])
5. **Детектировать проблемы** (несоответствия)
6. **Вывести детальный отчет**

## Пример использования

```python
def test_snap_with_log_analysis():
    log_file = Path('logs/zpl_designer.log')
    file_size_before = log_file.stat().st_size
    
    # Выполнить действие
    item.setPos(QPointF(x, y))
    app.processEvents()
    
    # Прочитать новые логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализировать
    analyzer = LogAnalyzer()
    snap_logs = analyzer.parse_snap_logs(new_logs)
    final_logs = analyzer.parse_final_pos_logs(new_logs)
    issues = analyzer.detect_snap_issues(snap_logs, final_logs)
    
    # Проверить
    if issues:
        for issue in issues:
            print(f"[!] {issue['type']}: {issue['desc']}")
        return 1  # FAIL
    
    return 0  # SUCCESS
```

## Преимущества

✅ **Детектирует внутренние проблемы** - видит что происходит внутри логики
✅ **Не зависит от финального результата** - может найти баг даже если результат случайно правильный
✅ **Детальная диагностика** - показывает ЧТО именно сломано
✅ **Предотвращает регрессии** - поймает если кто-то сломает snap

## Примеры детекции

### Пример 1: Threshold слишком мал (старый баг)
```
DETECTED 1 ISSUE(S):
1. NO_SNAP_IN_FINAL
   FINAL-POS Before=6.55mm, After=6.55mm (не снепнуло!)
   threshold=0.5 слишком мал для distance=0.55
```

### Пример 2: Snap в ItemPositionHasChanged не работает
```
DETECTED 1 ISSUE(S):
1. SNAP_FINAL_MISMATCH
   SNAP показал 6.0mm, но FINAL-POS After = 6.55mm
   Snap применился в ItemPositionChange, но НЕ в ItemPositionHasChanged
```

## Файлы

- `tests/test_snap_smart_v2.py` - умный тест с анализом логов
- `tests/run_snap_smart_v2_test.py` - runner для умного теста

## Когда использовать

**ВСЕГДА** для Canvas/GUI функций где важна внутренняя логика:
- Snap to grid
- Zoom
- Drag & drop
- Coordinate transformations
- Любая логика с промежуточными состояниями

**НЕ нужно** для простых функций без логов:
- Математические расчеты
- Простые геттеры/сеттеры
- Статические методы
