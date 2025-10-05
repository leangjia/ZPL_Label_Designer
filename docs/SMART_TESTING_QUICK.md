# УМНОЕ ТЕСТИРОВАНИЕ - БЫСТРЫЙ СТАРТ

## 🎯 Проблема обычных тестов

```python
# ❌ ОБЫЧНЫЙ (СЛЕПОЙ) ТЕСТ:
assert element.config.x == 6.0  # PASSED ✓

# АЛЕ НЕ ВИДИТ:
# [SNAP] 6.55mm -> 6.6mm  (показал что снепнуло)
# [FINAL-POS] Before: 6.55mm
# [FINAL-POS] After: 6.55mm  ← НЕ СНЕПНУЛО!
```

**Результат случайно правильный, но логика сломана!**

## 🔬 Решение: LogAnalyzer

Умные тесты парсят DEBUG логи и детектируют 3 типа проблем:
- `SNAP_FINAL_MISMATCH` - SNAP показал одно, FINAL другое
- `NO_SNAP_IN_FINAL` - Before == After (snap НЕ применился)
- `FINAL_SAVED_MISMATCH` - After != Saved

## 📋 Структура умного теста

### 1. Анализатор логов

```python
class LogAnalyzer:
    @staticmethod
    def parse_snap_logs(log):
        """Извлечь [SNAP] записи"""
        pattern = r'\[SNAP\] ([\d.]+)mm, ([\d.]+)mm -> ([\d.]+)mm, ([\d.]+)mm'
        return [(float(m[0]), float(m[1]), float(m[2]), float(m[3])) 
                for m in re.findall(pattern, log)]
    
    @staticmethod
    def detect_issues(snap_logs, final_logs):
        """Детектировать проблемы"""
        issues = []
        
        # Проверка 1: SNAP vs FINAL
        if snap_logs[-1][2] != final_logs['after'][-1][0]:
            issues.append({
                'type': 'SNAP_FINAL_MISMATCH',
                'desc': f'SNAP показал {snap_logs[-1][2]}, но FINAL = {final_logs["after"][-1][0]}'
            })
        
        return issues
```

### 2. Тест с анализом логов

```python
def test_feature_smart():
    log_file = Path('logs/zpl_designer.log')
    file_size_before = log_file.stat().st_size  # Размер ДО
    
    # Выполнить действие
    item.setPos(QPointF(x, y))
    app.processEvents()
    
    # Прочитать НОВЫЕ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализировать
    analyzer = LogAnalyzer()
    snap_logs = analyzer.parse_snap_logs(new_logs)
    issues = analyzer.detect_issues(snap_logs, final_logs)
    
    if issues:
        print(f"DETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        return 1
    
    return 0
```

## 🚀 Запуск тестов

### Отдельный тест
```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_cursor_smart_test.py').read())
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_zoom_smart_test.py').read())
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_snap_smart_test.py').read())
```

### Все тесты
```python
exec(open(r'D:\AiKlientBank\1C_Zebra\tests\run_all_smart_tests.py').read())
```

## 📊 Добавление DEBUG логов

### Canvas View
```python
def mouseMoveEvent(self, event):
    logger.debug(f"[CURSOR] Signal emit: {x_mm:.2f}mm, {y_mm:.2f}mm")

def wheelEvent(self, event):
    logger.debug(f"[ZOOM] Before: scale={self.current_scale:.2f}, cursor_pos=({old_pos.x():.1f}, {old_pos.y():.1f})")
    # ... zoom logic ...
    logger.debug(f"[ZOOM] After: scale={self.current_scale:.2f}, cursor_pos=({new_pos.x():.1f}, {new_pos.y():.1f})")
```

### Rulers
```python
def update_cursor_position(self, mm):
    logger.debug(f"[RULER-{orientation_name}] Update position: {mm:.2f}mm")

def _draw_cursor_marker(self, painter):
    logger.debug(f"[RULER-{orientation_name}] Drawn at: {pos_px}px")
```

## 🎯 3 Этапа Canvas Features

| Этап | Тест | Детектирует |
|------|------|-------------|
| **1. Cursor Tracking** | `test_cursor_tracking_smart.py` | Cursor != Ruler Update<br>Ruler Update != Draw |
| **2. Zoom to Point** | `test_zoom_smart.py` | Cursor shifted<br>Ruler scale mismatch |
| **3. Snap to Grid** | `test_snap_smart.py` | Snap != Final<br>No snap applied<br>Final != Saved |

## ✅ Когда использовать

**ОБЯЗАТЕЛЬНО:**
- ✅ Snap to grid
- ✅ Zoom
- ✅ Drag & drop
- ✅ Coordinate transformations
- ✅ Любая логика с промежуточными состояниями

**НЕ нужно:**
- ❌ Простые математические расчеты
- ❌ Геттеры/сеттеры без логики

## 🔑 Ключевое правило

**Нет анализа логов = НЕ работает!**
