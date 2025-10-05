# -*- coding: utf-8 -*-
"""
Тест для ШАГ 1.4: Property Panel

Этот тест проверяет:
1. Создание Property Panel
2. Интеграцию с MainWindow
3. Изменение свойств элементов через Property Panel

ВАЖНО: GUI нельзя запустить через python-runner!
Тест нужно выполнять ВРУЧНУЮ!
"""

print("=" * 60)
print("ТЕСТ ШАГ 1.4: Property Panel")
print("=" * 60)
print()
print("ИНСТРУКЦИЯ ДЛЯ РУЧНОГО ТЕСТИРОВАНИЯ:")
print()
print("1. Запустить приложение:")
print("   cd D:\\AiKlientBank\\1C_Zebra")
print("   .venv\\Scripts\\activate")
print("   python main.py")
print()
print("2. Проверить что Property Panel отображается справа")
print("   [OK] Property Panel виден в правой части окна")
print()
print("3. Нажать 'Add Text' или Ctrl+T")
print("   [OK] Текст 'New Text' появился на canvas")
print("   [OK] В консоли: [INFO] Text added at (10.0, 10.0)")
print()
print("4. Кликнуть на текст чтобы выделить его")
print("   [OK] Текст выделен")
print("   [OK] Property Panel активирован")
print("   [OK] В консоли: [INFO] Selected element at (10.0, 10.0)")
print("   [OK] В Property Panel видны значения X=10, Y=10")
print()
print("5. Изменить X в Property Panel на 15")
print("   [OK] Текст переместился по горизонтали")
print("   [OK] В консоли: [INFO] Property 'x' changed to '15'")
print()
print("6. Изменить Y в Property Panel на 15")
print("   [OK] Текст переместился по вертикали")
print("   [OK] В консоли: [INFO] Property 'y' changed to '15'")
print()
print("7. Изменить Text в Property Panel на 'Hello World'")
print("   [OK] Текст на canvas изменился на 'Hello World'")
print("   [OK] В консоли: [INFO] Property 'text' changed to 'Hello World'")
print()
print("8. Изменить Font Size на 30")
print("   [OK] В консоли: [INFO] Property 'font_size' changed to '30'")
print()
print("9. Добавить несколько текстов и проверить переключение")
print("   [OK] При клике на разные тексты Property Panel обновляется")
print()
print("10. Кликнуть на пустое место canvas")
print("    [OK] Property Panel деактивирован (серый)")
print()
print("=" * 60)
print("ЕСЛИ ВСЕ ТЕСТЫ ПРОШЛИ - ШАГ 1.4 ЗАВЕРШЕН!")
print("=" * 60)
