# -*- coding: utf-8 -*-
"""Умний тест: ZPL Generation та Data Changes для Barcode"""

import sys
from pathlib import Path

# Додати project root до sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.elements.barcode_element import EAN13BarcodeElement, Code128BarcodeElement
from core.elements.base import ElementConfig
from tests.barcode_log_analyzer import BarcodeLogAnalyzer


def test_barcode_zpl_and_data_changes_smart():
    """Умний тест: ZPL generation та вплив Data Changes на width"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("[SMART TEST] Barcode ZPL Generation + Data Changes")
    print("=" * 60)
    
    # 1. Розмір файлу логів ДО тесту
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # 2. ТЕСТ-КЕЙСИ
    
    # === CASE 1: EAN-13 ZPL Generation ===
    print("\n[CASE 1] EAN-13 ZPL Generation")
    config = ElementConfig(x=10.0, y=10.0)
    ean13 = EAN13BarcodeElement(
        config=config,
        data='1234567890123',
        width=20,
        height=15
    )
    
    zpl_ean13 = ean13.to_zpl(dpi=203)
    print(f"  Data: '{ean13.data}'")
    print(f"  ZPL: {zpl_ean13.replace(chr(10), ' | ')}")
    
    # === CASE 2: CODE128 ZPL Generation (короткий) ===
    print("\n[CASE 2] CODE128 ZPL Generation (короткий)")
    code128_short = Code128BarcodeElement(
        config=config,
        data='ABC',  # 3 символи
        width=30,
        height=10
    )
    
    zpl_code128_short = code128_short.to_zpl(dpi=203)
    width_before = code128_short.calculate_real_width(dpi=203)
    
    print(f"  Data: '{code128_short.data}' (len={len(code128_short.data)})")
    print(f"  Real width BEFORE: {width_before:.1f}mm")
    print(f"  ZPL: {zpl_code128_short.replace(chr(10), ' | ')}")
    
    # === CASE 3: CODE128 Data Changes (довгий) ===
    print("\n[CASE 3] CODE128 Data Changes (довгий)")
    code128_short.data = 'ABCDEFGHIJ'  # 10 символів - ЗМІНИЛИ!
    
    zpl_code128_long = code128_short.to_zpl(dpi=203)
    width_after = code128_short.calculate_real_width(dpi=203)
    
    print(f"  Data: '{code128_short.data}' (len={len(code128_short.data)})")
    print(f"  Real width AFTER: {width_after:.1f}mm")
    print(f"  Width diff: {width_after - width_before:+.1f}mm")
    print(f"  ZPL: {zpl_code128_long.replace(chr(10), ' | ')}")
    
    # 3. Читати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # 4. Аналізувати логи
    analyzer = BarcodeLogAnalyzer()
    real_width_logs = analyzer.parse_real_width_logs(new_logs)
    zpl_logs = analyzer.parse_zpl_generation_logs(new_logs)
    
    print("\n" + "=" * 60)
    print("[LOG ANALYSIS]")
    print("=" * 60)
    print(f"Real width logs found: {len(real_width_logs)}")
    print(f"ZPL generation logs found: {len(zpl_logs)}")
    
    for i, log in enumerate(zpl_logs, 1):
        print(f"\n[ZPL LOG {i}] {log['type']}")
        print(f"  Position: {log['position_mm']}")
        print(f"  Height: {log['height_mm']:.1f}mm")
        print(f"  Data: '{log['data']}'")
        if 'data_len' in log:
            print(f"  Data len: {log['data_len']}")
        print(f"  Real width: {log['real_width_mm']:.1f}mm")
        print(f"  ZPL: {log['zpl']}")
    
    # 5. Детектувати проблеми
    issues = analyzer.detect_issues(real_width_logs, [], zpl_logs)
    
    print("\n" + "=" * 60)
    print("[ISSUE DETECTION]")
    print("=" * 60)
    
    if issues:
        print(f"DETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  [{issue['type']}] {issue['desc']}")
        print("\n[FAILURE] ZPL generation або Data changes HAS ISSUES")
        return 1
    else:
        print("[OK] No issues detected")
        print("\nVERIFICATION:")
        print(f"  EAN-13 ZPL: data present in ZPL ✓")
        print(f"  CODE128 ZPL: data present in ZPL ✓")
        print(f"  CODE128 data change: width increased {width_before:.1f}mm -> {width_after:.1f}mm ✓")
        
        # Додаткова перевірка: ZPL містить правильні дані
        if ean13.data not in zpl_ean13:
            print(f"\n[FAIL] EAN-13: data '{ean13.data}' NOT in ZPL")
            return 1
        
        if code128_short.data not in zpl_code128_long:
            print(f"\n[FAIL] CODE128: data '{code128_short.data}' NOT in ZPL")
            return 1
        
        # Додаткова перевірка: довший data = ширший barcode
        if width_after <= width_before:
            print(f"\n[FAIL] CODE128: longer data should produce wider barcode!")
            return 1
        
        print("\n[SUCCESS] ZPL generation та Data changes працюють правильно!")
        return 0


if __name__ == '__main__':
    sys.exit(test_barcode_zpl_and_data_changes_smart())
