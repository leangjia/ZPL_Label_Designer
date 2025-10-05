# -*- coding: utf-8 -*-
"""
Тест Шага 1.5: ZPL Generator и Preview

ИНСТРУКЦИЯ ДЛЯ РУЧНОГО ТЕСТИРОВАНИЯ:
1. Запустить: python main.py
2. Нажать "Add Text" несколько раз
3. Переместить элементы на canvas
4. Нажать "Export ZPL" (Ctrl+E) - проверить что открылся диалог с ZPL кодом
5. Проверить что ZPL содержит: ^XA, ^CI28, ^PW, ^LL, ^FO команды
6. Нажать "Preview" (Ctrl+P) - проверить что отобразилось изображение этикетки
7. Проверить что preview соответствует расположению элементов на canvas

ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:
[OK] Export ZPL показывает диалог с кодом
[OK] ZPL код содержит правильные команды
[OK] Preview показывает изображение этикетки
[OK] Preview соответствует дизайну на canvas
[INFO] ZPL exported
[INFO] Preview shown
"""

import sys
sys.path.insert(0, r'D:\AiKlientBank\1C_Zebra')

from core.elements.text_element import TextElement
from core.elements.base import ElementConfig
from zpl.generator import ZPLGenerator
from integration.labelary_client import LabelaryClient

def test_zpl_generation():
    """Тест генерации ZPL кода"""
    print("\n=== TEST ZPL GENERATION ===\n")
    
    # Создать элементы
    elements = []
    
    # Элемент 1
    config1 = ElementConfig(x=10, y=10)
    element1 = TextElement(config1, "Test Label", font_size=30)
    elements.append(element1)
    
    # Элемент 2 с placeholder
    config2 = ElementConfig(x=10, y=15)
    element2 = TextElement(config2, "Product", font_size=25)
    element2.data_field = "{{PRODUCT_NAME}}"
    elements.append(element2)
    
    # Генератор
    generator = ZPLGenerator(dpi=203)
    
    # Конфигурация этикетки
    label_config = {
        'width': 28,
        'height': 28,
        'dpi': 203
    }
    
    # Генерировать без данных
    print("[+] Generating ZPL without data...")
    zpl_code = generator.generate(elements, label_config)
    print("\nGenerated ZPL:\n")
    print(zpl_code)
    print()
    
    # Проверки
    assert "^XA" in zpl_code, "Missing ^XA"
    assert "^CI28" in zpl_code, "Missing ^CI28"
    assert "^PW" in zpl_code, "Missing ^PW"
    assert "^LL" in zpl_code, "Missing ^LL"
    assert "^FO" in zpl_code, "Missing ^FO"
    assert "^FD" in zpl_code, "Missing ^FD"
    assert "^XZ" in zpl_code, "Missing ^XZ"
    assert "{{PRODUCT_NAME}}" in zpl_code, "Missing placeholder"
    
    print("[OK] ZPL structure is correct")
    
    # Генерировать с данными
    print("\n[+] Generating ZPL with data substitution...")
    data = {
        'PRODUCT_NAME': 'Apple iPhone 15'
    }
    zpl_code_with_data = generator.generate(elements, label_config, data)
    print("\nGenerated ZPL with data:\n")
    print(zpl_code_with_data)
    print()
    
    assert "Apple iPhone 15" in zpl_code_with_data, "Data substitution failed"
    assert "{{PRODUCT_NAME}}" not in zpl_code_with_data, "Placeholder not replaced"
    
    print("[OK] Data substitution works")
    
    return zpl_code

def test_labelary_preview():
    """Тест preview через Labelary API"""
    print("\n=== TEST LABELARY PREVIEW ===\n")
    
    # Простой ZPL код для теста
    zpl_code = """^XA
^CI28
^PW221
^LL221
^FO80,80^A0N,30^FDTest Preview^FS
^XZ"""
    
    print("[+] Requesting preview from Labelary API...")
    print(f"ZPL Code:\n{zpl_code}\n")
    
    client = LabelaryClient(dpi=203)
    image = client.preview(zpl_code, width_mm=28, height_mm=28)
    
    if image:
        print(f"[OK] Preview received: {image.size[0]}x{image.size[1]} pixels")
        
        # Сохранить для проверки
        output_path = r'D:\AiKlientBank\1C_Zebra\tests\preview_test.png'
        image.save(output_path)
        print(f"[OK] Preview saved to: {output_path}")
        
        return True
    else:
        print("[ERROR] Failed to get preview")
        return False

if __name__ == '__main__':
    print("="*60)
    print("STEP 1.5 TEST: ZPL Generator and Preview")
    print("="*60)
    
    try:
        # Тест генерации ZPL
        zpl_code = test_zpl_generation()
        
        # Тест preview
        preview_ok = test_labelary_preview()
        
        print("\n" + "="*60)
        if preview_ok:
            print("[OK] ALL TESTS PASSED")
            print("\nNext step: Run GUI and test manually:")
            print("  cd D:\\AiKlientBank\\1C_Zebra")
            print("  .venv\\Scripts\\activate")
            print("  python main.py")
        else:
            print("[FAILED] Preview test failed")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
