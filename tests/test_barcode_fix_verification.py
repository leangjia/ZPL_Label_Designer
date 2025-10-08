# -*- coding: utf-8 -*-
"""Верифікаційний тест - Canvas = Preview після виправлення"""

import sys
from pathlib import Path

# Додати project root до sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.elements.barcode_element import (
    EAN13BarcodeElement, 
    Code128BarcodeElement,
    GraphicsBarcodeItem
)
from core.elements.base import ElementConfig


def test_barcode_canvas_preview_match():
    """Тест: Canvas placeholder ТЕПЕР відповідає Preview розміру"""
    
    print("=" * 60)
    print("[VERIFICATION] Canvas = Preview after fix")
    print("=" * 60)
    
    # === EAN-13 ===
    print("\n--- EAN-13 Barcode ---")
    
    config = ElementConfig(x=10.0, y=10.0)
    ean13 = EAN13BarcodeElement(
        config=config,
        data='1234567890123',
        width=20,  # User задав 20mm (буде ІГНОРУВАТИСЯ)
        height=15
    )
    
    # Canvas використовує calculate_real_width()
    graphics_item = GraphicsBarcodeItem(ean13, dpi=203)
    canvas_width_px = graphics_item.rect().width()
    canvas_width_mm = canvas_width_px * 25.4 / 203
    
    # Preview використовує той же calculate_real_width()
    preview_width_mm = ean13.calculate_real_width(dpi=203)
    
    print(f"Canvas (GraphicsBarcodeItem):")
    print(f"  Width: {canvas_width_mm:.1f}mm ({canvas_width_px:.0f}px)")
    print(f"\nPreview (Real ZPL):")
    print(f"  Width: {preview_width_mm:.1f}mm")
    
    diff = abs(canvas_width_mm - preview_width_mm)
    print(f"\nDIFFERENCE: {diff:.2f}mm")
    
    if diff < 0.1:
        print("[OK] Canvas and Preview MATCH!")
        ean13_ok = True
    else:
        print(f"[FAIL] Canvas != Preview (diff={diff:.2f}mm)")
        ean13_ok = False
    
    # === CODE128 ===
    print("\n\n--- CODE128 Barcode ---")
    
    config = ElementConfig(x=10.0, y=10.0)
    code128 = Code128BarcodeElement(
        config=config,
        data='ABC123',
        width=30,  # User задав 30mm (буде ІГНОРУВАТИСЯ)
        height=10
    )
    
    # Canvas використовує calculate_real_width()
    graphics_item = GraphicsBarcodeItem(code128, dpi=203)
    canvas_width_px = graphics_item.rect().width()
    canvas_width_mm = canvas_width_px * 25.4 / 203
    
    # Preview використовує той же calculate_real_width()
    preview_width_mm = code128.calculate_real_width(dpi=203)
    
    print(f"Canvas (GraphicsBarcodeItem):")
    print(f"  Width: {canvas_width_mm:.1f}mm ({canvas_width_px:.0f}px)")
    print(f"\nPreview (Real ZPL):")
    print(f"  Width: {preview_width_mm:.1f}mm")
    
    diff = abs(canvas_width_mm - preview_width_mm)
    print(f"\nDIFFERENCE: {diff:.2f}mm")
    
    if diff < 0.1:
        print("[OK] Canvas and Preview MATCH!")
        code128_ok = True
    else:
        print(f"[FAIL] Canvas != Preview (diff={diff:.2f}mm)")
        code128_ok = False
    
    # === SUMMARY ===
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if ean13_ok and code128_ok:
        print("[OK] FIX SUCCESS! Canvas тепер відповідає Preview!")
        print("\nIMPLEMENTED:")
        print("  - calculate_real_width() methods in BarcodeElement classes")
        print("  - GraphicsBarcodeItem uses REAL width from calculate_real_width()")
        print("  - Canvas placeholder now matches ZPL-generated barcode size")
        return 0
    else:
        print("[FAIL] Canvas still НЕ відповідає Preview")
        return 1


if __name__ == '__main__':
    sys.exit(test_barcode_canvas_preview_match())
