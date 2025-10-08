# -*- coding: utf-8 -*-
"""Тест границ Barcode - Canvas vs Preview"""

import sys
from pathlib import Path

# Додати project root до sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.elements.barcode_element import EAN13BarcodeElement, Code128BarcodeElement
from core.elements.base import ElementConfig


def calculate_ean13_real_width(module_width_dots=2, dpi=203):
    """Розрахувати РЕАЛЬНУ ширину EAN-13 barcode
    
    EAN-13 structure:
    - 3 quiet zone modules (left)
    - 3 start guard (101)
    - 42 left half (6 digits * 7 modules)
    - 5 middle guard (01010)
    - 42 right half (6 digits * 7 modules)  
    - 3 end guard (101)
    - 7 quiet zone modules (right)
    Total: 3 + 3 + 42 + 5 + 42 + 3 + 7 = 105 modules
    """
    total_modules = 105
    width_dots = total_modules * module_width_dots
    width_mm = width_dots * 25.4 / dpi
    return width_mm


def calculate_code128_real_width(data_length, module_width_dots=2, dpi=203):
    """Розрахувати РЕАЛЬНУ ширину Code128 barcode
    
    Code128 structure:
    - 10 quiet zone modules (left)
    - 11 start character
    - data_length * 11 (average per character)
    - 13 stop character (includes 2-bar stop pattern)
    - 10 quiet zone modules (right)
    """
    total_modules = 10 + 11 + (data_length * 11) + 13 + 10
    width_dots = total_modules * module_width_dots
    width_mm = width_dots * 25.4 / dpi
    return width_mm


def test_barcode_boundaries():
    """Тест: Canvas placeholder vs РЕАЛЬНИЙ розмір Barcode"""
    
    print("=" * 60)
    print("[TEST] Barcode Boundaries - Canvas vs Preview")
    print("=" * 60)
    
    # === EAN-13 ===
    print("\n--- EAN-13 Barcode ---")
    
    config = ElementConfig(x=10.0, y=10.0)
    ean13 = EAN13BarcodeElement(
        config=config,
        data='1234567890123',
        width=20,  # User задав 20mm
        height=15
    )
    
    # Canvas placeholder
    canvas_width = ean13.width
    canvas_height = ean13.height
    
    # РЕАЛЬНА ширина (згенерована ZPL)
    real_width = calculate_ean13_real_width(module_width_dots=2, dpi=203)
    
    print(f"Canvas Placeholder:")
    print(f"  Width:  {canvas_width:.1f}mm")
    print(f"  Height: {canvas_height:.1f}mm")
    print(f"\nReal Barcode (from ZPL ^BY2):")
    print(f"  Width:  {real_width:.1f}mm")
    print(f"  Height: {canvas_height:.1f}mm (same)")
    
    diff_width = real_width - canvas_width
    print(f"\nDIFFERENCE:")
    print(f"  Width:  {diff_width:+.1f}mm ({abs(diff_width)/canvas_width*100:.1f}%)")
    
    if abs(diff_width) > 1.0:
        print(f"\n[FAIL] Barcode on Preview {'WIDER' if diff_width > 0 else 'NARROWER'} than Canvas placeholder!")
        print(f"  Canvas shows: {canvas_width}mm")
        print(f"  Preview shows: {real_width:.1f}mm")
        ean13_fail = True
    else:
        print(f"\n[OK] Canvas and Preview match (diff < 1mm)")
        ean13_fail = False
    
    # === CODE128 ===
    print("\n\n--- CODE128 Barcode ---")
    
    config = ElementConfig(x=10.0, y=10.0)
    code128 = Code128BarcodeElement(
        config=config,
        data='ABC123',  # 6 characters
        width=30,  # User задав 30mm
        height=10
    )
    
    # Canvas placeholder
    canvas_width = code128.width
    canvas_height = code128.height
    
    # РЕАЛЬНА ширина (згенерована ZPL)
    real_width = calculate_code128_real_width(len(code128.data), module_width_dots=2, dpi=203)
    
    print(f"Data: '{code128.data}' ({len(code128.data)} chars)")
    print(f"Canvas Placeholder:")
    print(f"  Width:  {canvas_width:.1f}mm")
    print(f"  Height: {canvas_height:.1f}mm")
    print(f"\nReal Barcode (from ZPL ^BY2):")
    print(f"  Width:  {real_width:.1f}mm")
    print(f"  Height: {canvas_height:.1f}mm (same)")
    
    diff_width = real_width - canvas_width
    print(f"\nDIFFERENCE:")
    print(f"  Width:  {diff_width:+.1f}mm ({abs(diff_width)/canvas_width*100:.1f}%)")
    
    if abs(diff_width) > 1.0:
        print(f"\n[FAIL] Barcode on Preview {'WIDER' if diff_width > 0 else 'NARROWER'} than Canvas placeholder!")
        print(f"  Canvas shows: {canvas_width}mm")
        print(f"  Preview shows: {real_width:.1f}mm")
        code128_fail = True
    else:
        print(f"\n[OK] Canvas and Preview match (diff < 1mm)")
        code128_fail = False
    
    # === SUMMARY ===
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if ean13_fail or code128_fail:
        print("[FAIL] Canvas placeholder НЕ відповідає реальному розміру Barcode!")
        print("\nROOT CAUSE:")
        print("  - GraphicsBarcodeItem uses element.width for placeholder")
        print("  - to_zpl() IGNORES element.width and uses ^BY module width")
        print("  - Real width = data_length * modules_per_char * module_width")
        print("\nSOLUTION:")
        print("  1. Calculate real width based on barcode type and data")
        print("  2. Update GraphicsBarcodeItem to show REAL width")
        print("  3. OR add width scaling parameter to ZPL generation")
        return 1
    else:
        print("[OK] Canvas and Preview boundaries match")
        return 0


if __name__ == '__main__':
    sys.exit(test_barcode_boundaries())
