# -*- coding: utf-8 -*-
"""Верифікаційний тест: Module Width Control"""

import sys
from pathlib import Path

# Додати project root до sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.elements.barcode_element import EAN13BarcodeElement
from core.elements.base import ElementConfig


def test_module_width_control():
    """Тест: зміна module_width впливає на ширину"""
    
    print("=" * 60)
    print("[VERIFICATION] Module Width Control")
    print("=" * 60)
    
    config = ElementConfig(x=10.0, y=10.0)
    ean13 = EAN13BarcodeElement(
        config=config,
        data='1234567890123',
        width=20,  # ІГНОРУЄТЬСЯ
        height=10
    )
    
    # === TEST 1: module_width = 1 (для маленьких етикеток) ===
    print("\n[TEST 1] module_width = 1 dot")
    ean13.module_width = 1
    width_1 = ean13.calculate_real_width(dpi=203)
    print(f"  Real width: {width_1:.1f}mm")
    print(f"  Fits 28mm label: {'YES' if width_1 < 26 else 'NO'}")
    
    # === TEST 2: module_width = 2 (default) ===
    print("\n[TEST 2] module_width = 2 dots (default)")
    ean13.module_width = 2
    width_2 = ean13.calculate_real_width(dpi=203)
    print(f"  Real width: {width_2:.1f}mm")
    print(f"  Fits 28mm label: {'YES' if width_2 < 26 else 'NO'}")
    
    # === TEST 3: module_width = 3 ===
    print("\n[TEST 3] module_width = 3 dots")
    ean13.module_width = 3
    width_3 = ean13.calculate_real_width(dpi=203)
    print(f"  Real width: {width_3:.1f}mm")
    print(f"  Fits 28mm label: {'YES' if width_3 < 26 else 'NO'}")
    
    # === VERIFICATION ===
    print("\n" + "=" * 60)
    print("[VERIFICATION]")
    print("=" * 60)
    
    # Scaling: width має бути пропорційним module_width
    ratio_2_1 = width_2 / width_1
    ratio_3_2 = width_3 / width_2
    
    print(f"Width ratio (module=2 / module=1): {ratio_2_1:.2f} (expected ~2.0)")
    print(f"Width ratio (module=3 / module=2): {ratio_3_2:.2f} (expected ~1.5)")
    
    if abs(ratio_2_1 - 2.0) > 0.01:
        print("\n[FAIL] Width scaling incorrect!")
        return 1
    
    if abs(ratio_3_2 - 1.5) > 0.01:
        print("\n[FAIL] Width scaling incorrect!")
        return 1
    
    # 28mm етикетка перевірка
    if width_1 >= 26:
        print(f"\n[FAIL] module=1 should fit 28mm label (width={width_1:.1f}mm)")
        return 1
    
    print("\n" + "=" * 60)
    print("[SUCCESS]")
    print("=" * 60)
    print(f"module_width=1: {width_1:.1f}mm - fits 28mm label ✓")
    print(f"module_width=2: {width_2:.1f}mm - barely fits ⚠")
    print(f"module_width=3: {width_3:.1f}mm - does NOT fit ✗")
    print("\nRECOMMENDATION:")
    print("  For 28x28mm labels → use module_width=1")
    print("  For 58x40mm labels → use module_width=2 (default)")
    return 0


if __name__ == '__main__':
    sys.exit(test_module_width_control())
