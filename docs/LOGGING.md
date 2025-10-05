# Система логування ZPL Label Designer

## Рівні деталізації

У `config.py` налаштовано 4 рівні деталізації логування:

### 1. MINIMAL (тільки помилки)
```python
CURRENT_LOG_LEVEL = 'MINIMAL'
```
- Логуються тільки критичні помилки (ERROR)
- Рекомендується для production

### 2. NORMAL (стандартний режим)
```python
CURRENT_LOG_LEVEL = 'NORMAL'  # ← ЗА ЗАМОВЧУВАННЯМ
```
- Важлива інформація + помилки (INFO, ERROR)
- ZPL генерація, API запити, робота з шаблонами
- Рекомендується для повсякденної роботи

### 3. DEBUG (відладка)
```python
CURRENT_LOG_LEVEL = 'DEBUG'
```
- Додатково: Canvas події, Rulers, координати
- Використовуй при розробці GUI компонентів

### 4. VERBOSE (максимально детально)
```python
CURRENT_LOG_LEVEL = 'VERBOSE'
```
- Все включено, навіть елементи і внутрішня логіка
- Використовуй тільки при глибокій відладці

## Категорії логування

Можна керувати окремими категоріями в `config.py`:

```python
LOG_CATEGORIES = {
    'canvas': True/False,     # Canvas події (координати, cursor)
    'rulers': True/False,     # Лінійки (відрисовка, cursor markers)
    'elements': True/False,   # Елементи (створення, зміни)
    'zpl': True,              # ZPL генерація (завжди активно)
    'api': True,              # API запити (завжди активно)
    'template': True          # Робота з шаблонами (завжди активно)
}
```

## Формати виводу

### Консоль (коротко)
```
[INFO] zpl.generator: Generated ZPL for label 28x28mm
[DEBUG] canvas_view: Mouse at x=12.5mm, y=8.3mm
[ERROR] api.server: Connection failed
```

### Файл (детально)
```
2025-10-04 15:30:45 - zpl.generator - INFO - Generated ZPL for label 28x28mm
2025-10-04 15:30:46 - canvas_view - DEBUG - Mouse at x=12.5mm, y=8.3mm
2025-10-04 15:30:47 - api.server - ERROR - Connection failed
```

## Швидке перемикання

**Для нормальної роботи:**
```python
CURRENT_LOG_LEVEL = 'NORMAL'
```

**Щось не працює? Увімкни debug:**
```python
CURRENT_LOG_LEVEL = 'DEBUG'
```

**Потрібна максимальна деталізація:**
```python
CURRENT_LOG_LEVEL = 'VERBOSE'
```

**Production (мінімум логів):**
```python
CURRENT_LOG_LEVEL = 'MINIMAL'
```

## Файли логів

Всі логи зберігаються в: `D:\AiKlientBank\1C_Zebra\logs\`

- `app.log` - головний лог файл
- Ротація: 5MB макс, 3 backup файли
