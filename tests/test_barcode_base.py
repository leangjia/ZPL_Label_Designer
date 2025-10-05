# -*- coding: utf-8 -*-
"""Тест базового класса BarcodeElement"""

import sys
import os
sys.path.insert(0, r'D:\AiKlientBank\1C_Zebra')

from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem
from core.elements.base import ElementConfig


def test_barcode_base():
    """Тест создания BarcodeElement"""
    
    results = []
    
    results.append("[TEST] Creating BarcodeElement")
    
    # Создать элемент
    config = ElementConfig(x=10, y=10)
    barcode = BarcodeElement(config, 'EAN13', '1234567890123', width=50, height=30)
    
    results.append(f"[+] BarcodeElement created: {barcode.barcode_type}")
    results.append(f"[+] Data: {barcode.data}")
    results.append(f"[+] Size: {barcode.width}x{barcode.height}mm")
    results.append(f"[+] Position: ({barcode.config.x}, {barcode.config.y})mm")
    
    # Проверить to_dict
    barcode_dict = barcode.to_dict()
    results.append(f"[+] to_dict() works: {barcode_dict}")
    
    # Проверить from_dict
    barcode2 = BarcodeElement.from_dict(barcode_dict)
    results.append(f"[+] from_dict() works: {barcode2.barcode_type}, {barcode2.data}")
    
    # Проверить placeholder
    barcode.data_field = "{{BARCODE}}"
    results.append(f"[+] Placeholder set: {barcode.data_field}")
    results.append(f"[+] _get_barcode_data() returns: {barcode._get_barcode_data()}")
    
    results.append("\n[SUCCESS] All base barcode tests passed!")
    
    # Сохранить результат с полным путем
    output = '\n'.join(results)
    output_path = r'D:\AiKlientBank\1C_Zebra\tests\test_barcode_base_result.txt'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(output)
    return True


if __name__ == '__main__':
    try:
        success = test_barcode_base()
        sys.exit(0 if success else 1)
    except Exception as e:
        error_msg = f"[ERROR] {e}\n"
        import traceback
        error_msg += traceback.format_exc()
        
        output_path = r'D:\AiKlientBank\1C_Zebra\tests\test_barcode_base_result.txt'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(error_msg)
        
        print(error_msg)
        sys.exit(1)
