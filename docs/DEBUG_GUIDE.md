# Руководство по диагностике проблем через логи

## Введение

Система логирования 1C_Zebra создана для детальной диагностики проблем. Каждый процесс логируется с полной информацией, что позволяет точно определить источник проблемы.

## Уровни логирования

По умолчанию активирован **DEBUG** режим:
```python
# config.py
LOG_LEVEL = "DEBUG"           # Всё в файл
CONSOLE_LOG_LEVEL = "DEBUG"   # Всё в консоль
```

Это означает максимальную детализацию при диагностике.

## Структура логов при Preview

При нажатии кнопки "Preview" логируется полная цепочка:

### 1. Инициация запроса (MainWindow)

```
============================================================
PREVIEW REQUEST INITIATED
============================================================
[INFO] Elements count: 1
[INFO] Element 1: type=TextElement, text='New Text', font_size=25, position=(9.9, 9.9)
[INFO] Label config: {'width': 28, 'height': 28, 'dpi': 203}
[INFO] No placeholders, using actual text values
[INFO] Generating ZPL code...
```

**Что проверять:**
- ✅ Количество элементов соответствует тому что на canvas
- ✅ Координаты элементов корректные
- ✅ Label config правильный (28x28mm, DPI 203)

### 2. Генерация ZPL (ZPLGenerator)

```
============================================================
ZPL GENERATION STARTED
============================================================
[INFO] Elements count: 1
[INFO] Label config: {'width': 28, 'height': 28, 'dpi': 203}
[DEBUG] Added: ^XA (start of label)
[DEBUG] Added: ^CI28 (UTF-8 encoding)
[INFO] Label width: 28mm = 223 dots (^PW223)
[INFO] Label height: 28mm = 223 dots (^LL223)
[INFO] Processing element 1/1: TextElement
[DEBUG]   Text: 'New Text'
[DEBUG]   Font size: 25
[DEBUG]   Position: (9.90mm, 9.90mm)
[DEBUG]   Generated ZPL: ^FO79,79^A0N,25,25^FDNew Text^FS
[DEBUG] Added: ^XZ (end of label)
[INFO] ZPL generation completed: 67 bytes, 7 lines
============================================================
```

**Что проверять:**
- ✅ Конвертация mm -> dots правильная (28mm = 223 dots при 203 DPI)
- ✅ Позиция элемента правильная (^FO79,79)
- ✅ Команды ZPL корректные (^A0N для шрифта, ^FD для данных)

**Формулы проверки:**
```
dots = mm * DPI / 25.4
223 = 28 * 203 / 25.4 ✓
79 = 9.9 * 203 / 25.4 ✓
```

### 3. Финальный ZPL код (DEBUG режим)

```
============================================================
GENERATED ZPL CODE:
============================================================
[DEBUG] ^XA
[DEBUG] ^CI28
[DEBUG] ^PW223
[DEBUG] ^LL223
[DEBUG] ^FO79,79^A0N,25,25^FDNew Text^FS
[DEBUG] ^XZ
============================================================
```

**Что проверять:**
- ✅ Начинается с ^XA, заканчивается ^XZ
- ✅ Есть ^CI28 для поддержки UTF-8
- ✅ Команды не разорваны (каждая команда на своей строке или слитно)

### 4. Запрос к Labelary API (LabelaryClient)

```
============================================================
LABELARY PREVIEW REQUEST
============================================================
[INFO] Input dimensions: 28mm x 28mm
[INFO] Converted to inches: 1.10 x 1.10
[INFO] DPI: 203 -> dpmm: 8
[INFO] API URL: http://api.labelary.com/v1/printers/8dpmm/labels/1.10x1.10/0/
[INFO] ZPL code length: 67 bytes
[DEBUG] ZPL code content:
[DEBUG] ----------------------------------------
[DEBUG] ^XA
[DEBUG] ^CI28
[DEBUG] ^PW223
[DEBUG] ^LL223
[DEBUG] ^FO79,79^A0N,25,25^FDNew Text^FS
[DEBUG] ^XZ
[DEBUG] ----------------------------------------
[INFO] Request headers: {'Accept': 'image/png'}
[INFO] Sending POST request to Labelary API...
```

**Что проверять:**
- ✅ Конвертация в дюймы: 28mm / 25.4 = 1.10 inch ✓
- ✅ dpmm правильный: 203 / 25.4 = 8 ✓
- ✅ URL сформирован правильно
- ✅ ZPL код совпадает с сгенерированным

### 5. Ответ от API

#### Успешный ответ (200):

```
[INFO] Response status code: 200
[INFO] Response headers: {'Content-Type': 'image/png', ...}
[INFO] Response content length: 1523 bytes
[INFO] Preview generated successfully [+]
============================================================
```

#### Ошибка (400):

```
[ERROR] Labelary API returned error code: 400
[ERROR] Response content type: text/plain
[ERROR] Response body length: 156 bytes
[ERROR] Response body:
[ERROR] ----------------------------------------
[ERROR] ZPL Error: Invalid command ^A0N,25,25
[ERROR] Expected format: ^A0N,height,width
[ERROR] ----------------------------------------
============================================================
```

**Что проверять при 400:**
- ❌ Текст ошибки от Labelary - что именно не так
- ❌ Формат команды ZPL - соответствует ли спецификации
- ❌ Кодировка данных - нет ли невалидных символов

## Типичные проблемы и их диагностика

### Проблема 1: Ошибка 400 - Invalid ZPL command

**Логи покажут:**
```
[ERROR] Response body:
[ERROR] ZPL Error: Invalid command ^A0N,25,25
```

**Причина:** Неправильный формат команды ZPL

**Решение:**
1. Проверить спецификацию команды на zebra.com
2. Исправить формат в `core/elements/text_element.py`
3. Проверить, что параметры команды в правильном порядке

### Проблема 2: Элемент не виден на preview

**Логи покажут:**
```
[DEBUG]   Position: (0.50mm, 0.50mm)
[DEBUG]   Generated ZPL: ^FO4,4^A0N,25,25^FDText^FS
```

**Причина:** Элемент слишком близко к краю (за полем печати)

**Решение:** Минимальная позиция должна быть ~2-3mm от края

### Проблема 3: Кодировка кириллицы

**Логи покажут:**
```
[DEBUG] ^CI28
[DEBUG] ^FDПривет^FS
```

**Проверка:** 
- ✅ Есть команда ^CI28 перед текстом
- ✅ Текст в UTF-8

### Проблема 4: Неправильный размер этикетки

**Логи покажут:**
```
[INFO] API URL: http://api.labelary.com/v1/printers/8dpmm/labels/0.50x0.50/0/
[ERROR] Labelary API returned error code: 400
[ERROR] Response body: Label size too small
```

**Причина:** Минимальный размер этикетки в Labelary - 1x1 дюйм (~25x25mm)

### Проблема 5: Timeout

**Логи покажут:**
```
[ERROR] Request timeout (>10 seconds)
```

**Причина:** Проблемы с сетью или Labelary API недоступен

**Решение:** Проверить интернет соединение

## Полный пример успешного Preview

```
============================================================
PREVIEW REQUEST INITIATED
============================================================
[INFO] Elements count: 1
[INFO] Element 1: type=TextElement, text='Hello', font_size=30, position=(10.0, 10.0)
[INFO] Label config: {'width': 28, 'height': 28, 'dpi': 203}
[INFO] No placeholders, using actual text values
[INFO] Generating ZPL code...

============================================================
ZPL GENERATION STARTED
============================================================
[INFO] Elements count: 1
[INFO] Label config: {'width': 28, 'height': 28, 'dpi': 203}
[INFO] Label width: 28mm = 223 dots (^PW223)
[INFO] Label height: 28mm = 223 dots (^LL223)
[INFO] Processing element 1/1: TextElement
[DEBUG]   Text: 'Hello'
[DEBUG]   Font size: 30
[DEBUG]   Position: (10.00mm, 10.00mm)
[DEBUG]   Generated ZPL: ^FO80,80^A0N,30,30^FDHello^FS
[INFO] ZPL generation completed: 65 bytes, 7 lines
============================================================

============================================================
LABELARY PREVIEW REQUEST
============================================================
[INFO] Input dimensions: 28mm x 28mm
[INFO] Converted to inches: 1.10 x 1.10
[INFO] DPI: 203 -> dpmm: 8
[INFO] API URL: http://api.labelary.com/v1/printers/8dpmm/labels/1.10x1.10/0/
[INFO] ZPL code length: 65 bytes
[INFO] Sending POST request to Labelary API...
[INFO] Response status code: 200
[INFO] Response content length: 1842 bytes
[INFO] Preview generated successfully [+]
============================================================

[INFO] Preview image received, displaying dialog
[INFO] Image size: 223x223px
[INFO] Preview dialog closed
============================================================
```

## Как использовать логи для отладки

### 1. Воспроизвести проблему

```bash
cd D:\AiKlientBank\1C_Zebra
.venv\Scripts\activate
python main.py
```

Выполнить действия до ошибки.

### 2. Открыть лог-файл

```bash
type logs\zpl_designer.log
```

или

```powershell
notepad logs\zpl_designer.log
```

### 3. Найти секцию с ошибкой

Искать по ключевым словам:
- `ERROR` - ошибки
- `PREVIEW REQUEST` - начало процесса preview
- `LABELARY PREVIEW REQUEST` - запрос к API
- `Response status code: 400` - ошибка API

### 4. Анализировать последовательность

Читать логи последовательно от `PREVIEW REQUEST INITIATED` до ошибки:
1. Проверить элементы
2. Проверить ZPL генерацию
3. Проверить URL и параметры API
4. Читать текст ошибки от Labelary

### 5. Сравнить с рабочим примером

Сравнить свой лог с примером выше - где отличие?

## Настройка детализации логов

### Максимальная детализация (по умолчанию)

```python
# config.py
LOG_LEVEL = "DEBUG"
CONSOLE_LOG_LEVEL = "DEBUG"
```

Показывает **ВСЁ**: каждую строку ZPL, каждую конвертацию, каждый параметр.

### Только ошибки

```python
# config.py
LOG_LEVEL = "INFO"           # Всё в файл
CONSOLE_LOG_LEVEL = "ERROR"  # Только ошибки в консоль
```

Тихая работа, но полный лог в файле.

### Баланс (рекомендуется после отладки)

```python
# config.py
LOG_LEVEL = "INFO"
CONSOLE_LOG_LEVEL = "INFO"
```

Основные события без деталей конвертации.

## Мониторинг в реальном времени

### Windows PowerShell

```powershell
# Следить за логом
Get-Content logs\zpl_designer.log -Wait -Tail 50
```

### Фильтрация по уровню

```powershell
# Только ошибки
Get-Content logs\zpl_designer.log | Select-String "ERROR"

# Секция preview
Get-Content logs\zpl_designer.log | Select-String -Context 5 "PREVIEW REQUEST"
```

## Отправка логов для помощи

При запросе помощи отправляй:
1. Полный лог-файл `logs/zpl_designer.log`
2. Скриншот canvas с проблемным элементом
3. Описание действий до ошибки

## Заключение

Детальные логи позволяют:
- ✅ Точно определить на каком этапе ошибка
- ✅ Увидеть все параметры и преобразования
- ✅ Понять что именно не так с ZPL кодом
- ✅ Получить текст ошибки от Labelary API
- ✅ Быстро исправить проблему

**Помни:** Логи пишутся для того чтобы их читать! Не игнорируй детали в логах - там ответ на вопрос "почему не работает".

---

**Версия:** 1.0  
**Дата:** 2025-10-03
