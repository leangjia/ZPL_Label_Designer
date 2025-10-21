中国大陆地区加速：

pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# ZPL Label Designer

Профессиональное приложение для создания и редактирования этикеток в формате ZPL (Zebra Programming Language) с графическим интерфейсом на основе PySide6.

## 🚀 Возможности

### Основные функции
- **Графический редактор этикеток** с интуитивным интерфейсом
- **Поддержка элементов:**
  - Текстовые поля с настройкой шрифтов и размеров
  - Штрих-коды: EAN-13, Code 128, QR Code
  - Изображения и графические элементы
- **ZPL генерация** с автоматической конвертацией в код для принтеров Zebra
- **Предварительный просмотр** через Labelary API
- **Системы измерений** (мм, дюймы, точки)
- **Шаблоны и плейсхолдеры** для переменных данных

### Canvas Features
- **Cursor Tracking** - отслеживание позиции курсора с координатами
- **Zoom to Point** - масштабирование к указанной точке
- **Snap to Grid** - привязка к сетке для точного позиционирования
- **Element Bounds** - подсветка границ выбранных элементов
- **Keyboard Shortcuts** - горячие клавиши для быстрой работы
- **Context Menu** - контекстное меню для операций с элементами
- **Smart Guides** - умные направляющие для выравнивания
- **Undo/Redo** - отмена и повтор действий
- **Multi-Select** - множественный выбор элементов

### Технические особенности
- **Smart Testing** - автоматизированное тестирование с LogAnalyzer
- **Modular Architecture** - модульная архитектура с миксинами
- **Unit Conversion** - автоматическое преобразование единиц измерения
- **Template System** - система шаблонов для повторного использования
- **API Integration** - интеграция с внешними API для предварительного просмотра

## 🛠️ Технический стек

- **Python 3.13** - основной язык разработки
- **PySide6** - графический интерфейс пользователя
- **Pillow** - обработка изображений
- **Requests** - HTTP-запросы к внешним API
- **Flask** - веб-сервер для API endpoints
- **python-barcode** - генерация штрих-кодов

## 📦 Установка

### Требования
- Python 3.13+
- Windows 10/11

### Быстрый старт
```powershell
# Клонировать репозиторий
git clone https://github.com/ваш-username/1C_Zebra.git
cd 1C_Zebra

# Создать виртуальное окружение
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
python main.py
```

## 🎯 Структура проекта

```
1C_Zebra/
├── main.py                 # Точка входа приложения
├── config.py              # Конфигурация приложения
├── requirements.txt       # Зависимости Python
├── gui/                   # Пользовательский интерфейс
│   ├── main_window.py     # Главное окно приложения
│   └── mixins/            # Модульные компоненты
├── core/                  # Основная логика
│   ├── elements/          # Элементы этикеток
│   └── generators/        # Генераторы ZPL кода
├── utils/                 # Утилиты
│   ├── logger.py          # Система логирования
│   └── unit_converter.py  # Конвертация единиц
├── integration/           # Внешние интеграции
│   └── labelary_client.py # Клиент Labelary API
├── tests/                 # Тестирование
│   └── *_smart.py         # Умные тесты с LogAnalyzer
└── docs/                  # Документация
```

## 🧪 Тестирование

Проект использует уникальную систему **Smart Testing** с LogAnalyzer для автоматического обнаружения проблем:

```powershell
# Запуск всех базовых тестов Canvas Features
python tests/run_stages_1_5_smart.py

# Запуск продвинутых тестов
python tests/run_stages_6_9_smart.py

# Запуск специфических тестов
python tests/test_cursor_tracking_smart.py
python tests/test_zoom_smart.py
python tests/test_snap_smart.py
```

## 📋 Использование

### Создание простой этикетки
1. Запустите приложение: `python main.py`
2. Настройте размер этикетки в панели свойств
3. Добавьте текстовые элементы через панель инструментов
4. Добавьте штрих-коды при необходимости
5. Используйте предварительный просмотр для проверки
6. Экспортируйте ZPL код для печати

### Работа с шаблонами
- Используйте плейсхолдеры `{{FIELD_NAME}}` для переменных данных
- Сохраняйте часто используемые макеты как шаблоны
- Импортируйте данные из внешних источников

## 🤝 Участие в разработке

### Разработка новых функций
1. Создайте feature branch
2. Добавьте DEBUG логи в код функции
3. Создайте умный тест с LogAnalyzer
4. Убедитесь, что все тесты проходят
5. Создайте Pull Request

### Отчеты об ошибках
Используйте систему логирования для диагностики:
- Включите DEBUG уровень в `utils/logger.py`
- Воспроизведите проблему
- Приложите логи к отчету об ошибке

## 📄 Лицензия

Этот проект разработан для внутреннего использования компании.

## 🔗 Полезные ссылки

- [Zebra Programming Language Guide](https://www.zebra.com/us/en/support-downloads/knowledge-articles/ZPL-Zebra-Programming-Language.html)
- [Labelary API Documentation](http://labelary.com/service.html)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)

---

**Автор:** Senior Software Engineer  
**Проект:** 1C_Zebra ZPL Label Designer  
**Версия:** 1.0.0
