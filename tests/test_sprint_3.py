# -*- coding: utf-8 -*-
"""Комплексный тест штрихкодов для Спринта 3"""

import sys
sys.path.insert(0, r'D:\AiKlientBank\1C_Zebra')

from core.elements.barcode_element import (
    EAN13BarcodeElement,
    Code128BarcodeElement,
    QRCodeElement
)
from core.elements.base import ElementConfig
from zpl.generator import ZPLGenerator


def test_all_barcodes():
    """Комплексный тест всех штрихкодов"""
    
    results = []
    results.append("="*60)
    results.append("SPRINT 3 COMPREHENSIVE BARCODE TEST")
    results.append("="*60)
    
    # ========== TEST 1: EAN-13 ==========
    results.append("\n[TEST 1] EAN-13 Barcode")
    config1 = ElementConfig(x=10, y=10)
    ean13 = EAN13BarcodeElement(config1, data='1234567890123', width=50, height=30)
    
    results.append(f"[+] Created: {ean13.barcode_type}")
    results.append(f"    Data: {ean13.data}")
    results.append(f"    Size: {ean13.width}x{ean13.height}mm")
    
    zpl1 = ean13.to_zpl(dpi=203)
    assert '^BEN' in zpl1, "EAN-13 ZPL missing ^BEN"
    results.append("[+] ZPL generation: OK")
    
    dict1 = ean13.to_dict()
    assert dict1['type'] == 'barcode', "to_dict type wrong"
    assert dict1['barcode_type'] == 'EAN13', "barcode_type wrong"
    results.append("[+] Serialization: OK")
    
    # ========== TEST 2: Code 128 ==========
    results.append("\n[TEST 2] Code 128 Barcode")
    config2 = ElementConfig(x=10, y=50)
    code128 = Code128BarcodeElement(config2, data='SAMPLE128', width=60, height=30)
    
    results.append(f"[+] Created: {code128.barcode_type}")
    results.append(f"    Data: {code128.data}")
    
    zpl2 = code128.to_zpl(dpi=203)
    assert '^BCN' in zpl2, "Code128 ZPL missing ^BCN"
    results.append("[+] ZPL generation: OK")
    
    dict2 = code128.to_dict()
    assert dict2['barcode_type'] == 'CODE128', "barcode_type wrong"
    results.append("[+] Serialization: OK")
    
    # ========== TEST 3: QR Code ==========
    results.append("\n[TEST 3] QR Code")
    config3 = ElementConfig(x=70, y=10)
    qr = QRCodeElement(config3, data='https://example.com', size=25)
    
    results.append(f"[+] Created: {qr.barcode_type}")
    results.append(f"    Data: {qr.data}")
    results.append(f"    Size: {qr.size}x{qr.size}mm")
    
    zpl3 = qr.to_zpl(dpi=203)
    assert '^BQN' in zpl3, "QR ZPL missing ^BQN"
    results.append("[+] ZPL generation: OK")
    
    dict3 = qr.to_dict()
    assert dict3['barcode_type'] == 'QRCODE', "barcode_type wrong"
    assert 'magnification' in dict3, "missing magnification"
    results.append("[+] Serialization: OK")
    
    # ========== TEST 4: Placeholder Support ==========
    results.append("\n[TEST 4] Placeholder Support")
    
    ean13.data_field = "{{PRODUCT_BARCODE}}"
    zpl_p = ean13.to_zpl(dpi=203)
    assert "{{PRODUCT_BARCODE}}" in zpl_p, "Placeholder not in ZPL"
    results.append("[+] EAN-13 placeholder: OK")
    
    code128.data_field = "{{ORDER_ID}}"
    zpl_p2 = code128.to_zpl(dpi=203)
    assert "{{ORDER_ID}}" in zpl_p2, "Placeholder not in ZPL"
    results.append("[+] Code 128 placeholder: OK")
    
    qr.data_field = "{{URL}}"
    zpl_p3 = qr.to_zpl(dpi=203)
    assert "{{URL}}" in zpl_p3, "Placeholder not in ZPL"
    results.append("[+] QR Code placeholder: OK")
    
    # ========== TEST 5: Complete ZPL Generation ==========
    results.append("\n[TEST 5] Complete Label with All Barcodes")
    
    label_config = {
        'width': 100,
        'height': 100,
        'dpi': 203
    }
    
    generator = ZPLGenerator(dpi=203)
    
    # Сбросить placeholders для теста
    ean13.data_field = None
    code128.data_field = None
    qr.data_field = None
    
    elements = [ean13, code128, qr]
    
    full_zpl = generator.generate(elements, label_config)
    
    # Проверить структуру ZPL
    assert '^XA' in full_zpl, "Missing ^XA start"
    assert '^XZ' in full_zpl, "Missing ^XZ end"
    assert '^CI28' in full_zpl, "Missing ^CI28 encoding"
    assert '^BEN' in full_zpl, "Missing EAN-13"
    assert '^BCN' in full_zpl, "Missing Code 128"
    assert '^BQN' in full_zpl, "Missing QR Code"
    
    results.append("[+] Complete ZPL structure: OK")
    results.append(f"    Total length: {len(full_zpl)} chars")
    
    # Показать ZPL
    results.append("\n[ZPL CODE]:")
    results.append("-"*60)
    results.append(full_zpl)
    results.append("-"*60)
    
    # ========== TEST 6: from_dict Restoration ==========
    results.append("\n[TEST 6] from_dict() Restoration")
    
    # EAN-13
    ean13_restored = EAN13BarcodeElement.from_dict(dict1)
    assert ean13_restored.barcode_type == 'EAN13', "EAN-13 restore failed"
    assert ean13_restored.data == '1234567890123', "EAN-13 data restore failed"
    results.append("[+] EAN-13 from_dict: OK")
    
    # Code 128
    code128_restored = Code128BarcodeElement.from_dict(dict2)
    assert code128_restored.barcode_type == 'CODE128', "Code128 restore failed"
    results.append("[+] Code 128 from_dict: OK")
    
    # QR Code
    qr_restored = QRCodeElement.from_dict(dict3)
    assert qr_restored.barcode_type == 'QRCODE', "QR restore failed"
    assert qr_restored.magnification == 3, "QR magnification restore failed"
    results.append("[+] QR Code from_dict: OK")
    
    # ========== FINAL RESULTS ==========
    results.append("\n" + "="*60)
    results.append("ALL TESTS PASSED!")
    results.append("="*60)
    results.append("\nSummary:")
    results.append("[+] 3 barcode types implemented: EAN-13, Code 128, QR Code")
    results.append("[+] ZPL generation working for all types")
    results.append("[+] Placeholder support working")
    results.append("[+] Serialization (to_dict/from_dict) working")
    results.append("[+] Complete label generation working")
    results.append("\n[SUCCESS] Sprint 3 Implementation Complete!")
    
    # Сохранить результат
    output = '\n'.join(results)
    with open(r'D:\AiKlientBank\1C_Zebra\tests\sprint_3_test_result.txt', 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(output)
    return True


if __name__ == '__main__':
    try:
        success = test_all_barcodes()
        sys.exit(0 if success else 1)
    except Exception as e:
        error_msg = f"[ERROR] {e}\n"
        import traceback
        error_msg += traceback.format_exc()
        
        with open(r'D:\AiKlientBank\1C_Zebra\tests\sprint_3_test_result.txt', 'w', encoding='utf-8') as f:
            f.write(error_msg)
        
        print(error_msg)
        sys.exit(1)
