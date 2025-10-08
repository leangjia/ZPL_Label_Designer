# -*- coding: utf-8 -*-
"""Умний тест: Real Width Calculation для Barcode"""

import sys
from pathlib import Path

# Додати project root до sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.elements.barcode_element import EAN13BarcodeElement, Code128BarcodeElement
from core.elements.base import ElementConfig
from tests.barcode_log_analyzer import BarcodeLogAnalyzer


def test_barcode_real_width_smart():
    """Умний тест: перевірка calculate_real_width() через LogAnalyzer"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("[SMART TEST] Barcode Real Width Calculation")
    print("=" * 60)
    
    # 1. Розмір файлу логів ДО тесту
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # 2. ТЕСТ-КЕЙСИ: створити Barcode та викликати calculate_real_width()
    
    # === EAN-13 ===
    print("\n[CASE 1] EAN-13 with module_width=2")
    config = ElementConfig(x=10.0, y=10.0)
    ean13 = EAN13BarcodeElement(config=config, data='1234567890123', width=20, height=15)
    ean13.module_width = 2
    
    real_width_ean13 = ean13.calculate_real_width(dpi=203)
    print(f"  Calculated width: {real_width_ean13:.1f}mm")
    
    # === EAN-13 with module_width=3 ===
    print("\n[CASE 2] EAN-13 with module_width=3")
    ean13_wide = EAN13BarcodeElement(config=config, data='9876543210987', width=20, height=15)
    ean13_wide.module_width = 3
    
    real_width_ean13_wide = ean13_wide.calculate_real_width(dpi=203)
    print(f"  Calculated width: {real_width_ean13_wide:.1f}mm")
    
    # === CODE128 - 6 chars ===
    print("\n[CASE 3] CODE128 with 6 chars")
    code128_short = Code128BarcodeElement(config=config, data='ABC123', width=30, height=10)
    code128_short.module_width = 2
    
    real_width_code128_short = code128_short.calculate_real_width(dpi=203)
    print(f"  Data: '{code128_short.data}' (len={len(code128_short.data)})")
    print(f"  Calculated width: {real_width_code128_short:.1f}mm")
    
    # === CODE128 - 12 chars ===
    print("\n[CASE 4] CODE128 with 12 chars")
    code128_long = Code128BarcodeElement(config=config, data='ABCDEF123456', width=30, height=10)
    code128_long.module_width = 2
    
    real_width_code128_long = code128_long.calculate_real_width(dpi=203)
    print(f"  Data: '{code128_long.data}' (len={len(code128_long.data)})")
    print(f"  Calculated width: {real_width_code128_long:.1f}mm")
    
    # 3. Читати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # 4. Аналізувати логи
    analyzer = BarcodeLogAnalyzer()
    real_width_logs = analyzer.parse_real_width_logs(new_logs)
    
    print("\n" + "=" * 60)
    print("[LOG ANALYSIS]")
    print("=" * 60)
    print(f"Real width logs found: {len(real_width_logs)}")
    
    for i, log in enumerate(real_width_logs, 1):
        print(f"\n[LOG {i}] {log['type']}")
        print(f"  Width: {log['width_mm']:.1f}mm")
        print(f"  Modules: {log['modules']}")
        print(f"  Module width: {log['module_width_dots']} dots")
        if log['data_len']:
            print(f"  Data len: {log['data_len']}")
    
    # 5. Детектувати проблеми
    issues = analyzer.detect_issues(real_width_logs, [], [])
    
    print("\n" + "=" * 60)
    print("[ISSUE DETECTION]")
    print("=" * 60)
    
    if issues:
        print(f"DETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  [{issue['type']}] {issue['desc']}")
        print("\n[FAILURE] Real width calculation HAS ISSUES")
        return 1
    else:
        print("[OK] No issues detected")
        print("\nVERIFICATION:")
        print(f"  EAN-13 (module=2): {real_width_ean13:.1f}mm")
        print(f"  EAN-13 (module=3): {real_width_ean13_wide:.1f}mm (should be 1.5x wider)")
        print(f"  CODE128 (6 chars):  {real_width_code128_short:.1f}mm")
        print(f"  CODE128 (12 chars): {real_width_code128_long:.1f}mm (should be wider)")
        
        # Додаткова перевірка: module_width=3 має бути 1.5x ширше
        expected_ratio = 3.0 / 2.0
        actual_ratio = real_width_ean13_wide / real_width_ean13
        
        if abs(actual_ratio - expected_ratio) > 0.01:
            print(f"\n[FAIL] Module width scaling incorrect: ratio {actual_ratio:.2f}, expected {expected_ratio:.2f}")
            return 1
        
        # Додаткова перевірка: CODE128 довший = ширший
        if real_width_code128_long <= real_width_code128_short:
            print(f"\n[FAIL] CODE128: longer data should be wider!")
            return 1
        
        print("\n[SUCCESS] Real width calculation works correctly!")
        return 0


if __name__ == '__main__':
    sys.exit(test_barcode_real_width_smart())
