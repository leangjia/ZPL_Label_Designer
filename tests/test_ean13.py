# -*- coding: utf-8 -*-
"""Тест EAN-13 штрихкода"""

import sys
sys.path.insert(0, r'D:\AiKlientBank\1C_Zebra')

from core.elements.barcode_element import EAN13BarcodeElement
from core.elements.base import ElementConfig


def test_ean13():
    """Тест создания и генерации ZPL для EAN-13"""
    
    results = []
    
    results.append("=== TEST EAN-13 BARCODE ===\n")
    
    # Создать элемент
    config = ElementConfig(x=10, y=10)
    ean13 = EAN13BarcodeElement(
        config=config,
        data='1234567890123',
        width=50,
        height=30
    )
    
    results.append(f"[+] EAN13BarcodeElement created")
    results.append(f"    Type: {ean13.barcode_type}")
    results.append(f"    Data: {ean13.data}")
    results.append(f"    Size: {ean13.width}x{ean13.height}mm")
    results.append(f"    Position: ({ean13.config.x}, {ean13.config.y})mm")
    
    # Генерация ZPL с DPI 203
    results.append("\n[TEST] ZPL Generation (DPI=203)")
    zpl = ean13.to_zpl(dpi=203)
    results.append("[+] ZPL generated:")
    results.append(zpl)
    
    # Проверить формат
    assert "^FO" in zpl, "Missing ^FO command"
    assert "^BY" in zpl, "Missing ^BY command"
    assert "^BEN" in zpl, "Missing ^BEN command"
    assert "^FD1234567890123^FS" in zpl, "Missing data"
    results.append("\n[+] ZPL format validation passed")
    
    # Проверить координаты (10mm = 10 * 203 / 25.4 ≈ 80 dots)
    expected_x = int(10 * 203 / 25.4)
    expected_y = int(10 * 203 / 25.4)
    expected_height = int(30 * 203 / 25.4)
    
    results.append(f"\n[INFO] Coordinate conversion:")
    results.append(f"  X: 10mm -> {expected_x} dots")
    results.append(f"  Y: 10mm -> {expected_y} dots")
    results.append(f"  Height: 30mm -> {expected_height} dots")
    
    assert f"^FO{expected_x},{expected_y}" in zpl, "Wrong coordinates"
    assert f"^BEN,{expected_height}" in zpl, "Wrong height"
    results.append("[+] Coordinate conversion correct")
    
    # Тест с placeholder
    results.append("\n[TEST] Placeholder Support")
    ean13.data_field = "{{PRODUCT_BARCODE}}"
    zpl_with_placeholder = ean13.to_zpl(dpi=203)
    
    assert "{{PRODUCT_BARCODE}}" in zpl_with_placeholder, "Placeholder not in ZPL"
    results.append(f"[+] Placeholder in ZPL: {{{{PRODUCT_BARCODE}}}}")
    
    # Тест to_dict / from_dict
    results.append("\n[TEST] Serialization")
    ean13_dict = ean13.to_dict()
    
    assert ean13_dict['type'] == 'barcode', "Wrong type"
    assert ean13_dict['barcode_type'] == 'EAN13', "Wrong barcode_type"
    assert ean13_dict['data'] == '1234567890123', "Wrong data"
    results.append("[+] to_dict() works")
    
    ean13_restored = EAN13BarcodeElement.from_dict(ean13_dict)
    assert ean13_restored.barcode_type == 'EAN13', "from_dict failed"
    assert ean13_restored.data == '1234567890123', "from_dict data failed"
    results.append("[+] from_dict() works")
    
    results.append("\n[SUCCESS] All EAN-13 tests passed!")
    
    # Сохранить результат
    output = '\n'.join(results)
    with open(r'D:\AiKlientBank\1C_Zebra\tests\step_3_2_result.txt', 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(output)
    return True


if __name__ == '__main__':
    try:
        success = test_ean13()
        sys.exit(0 if success else 1)
    except Exception as e:
        error_msg = f"[ERROR] {e}\n"
        import traceback
        error_msg += traceback.format_exc()
        
        with open(r'D:\AiKlientBank\1C_Zebra\tests\step_3_2_result.txt', 'w', encoding='utf-8') as f:
            f.write(error_msg)
        
        print(error_msg)
        sys.exit(1)
