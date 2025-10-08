# -*- coding: utf-8 -*-
"""Умний тест: Canvas = Preview для Barcode"""

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
from tests.barcode_log_analyzer import BarcodeLogAnalyzer


def test_barcode_canvas_preview_smart():
    """Умний тест: Canvas placeholder має відповідати Preview розміру"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("[SMART TEST] Barcode Canvas = Preview")
    print("=" * 60)
    
    # 1. Розмір файлу логів ДО тесту
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # 2. ТЕСТ-КЕЙСИ: створити Barcode та GraphicsItem
    
    # === EAN-13 ===
    print("\n[CASE 1] EAN-13 Barcode")
    config = ElementConfig(x=10.0, y=10.0)
    ean13 = EAN13BarcodeElement(
        config=config,
        data='1234567890123',
        width=20,  # User задав 20mm (буде ІГНОРУВАТИСЯ)
        height=15
    )
    
    # Canvas використовує calculate_real_width()
    graphics_ean13 = GraphicsBarcodeItem(ean13, dpi=203)
    canvas_width_ean13 = graphics_ean13.rect().width() * 25.4 / 203
    
    # Preview використовує той же calculate_real_width()
    preview_width_ean13 = ean13.calculate_real_width(dpi=203)
    
    print(f"  Canvas:  {canvas_width_ean13:.1f}mm")
    print(f"  Preview: {preview_width_ean13:.1f}mm")
    print(f"  Diff:    {abs(canvas_width_ean13 - preview_width_ean13):.2f}mm")
    
    # === CODE128 ===
    print("\n[CASE 2] CODE128 Barcode")
    code128 = Code128BarcodeElement(
        config=config,
        data='ABC123',
        width=30,  # User задав 30mm (буде ІГНОРУВАТИСЯ)
        height=10
    )
    
    # Canvas використовує calculate_real_width()
    graphics_code128 = GraphicsBarcodeItem(code128, dpi=203)
    canvas_width_code128 = graphics_code128.rect().width() * 25.4 / 203
    
    # Preview використовує той же calculate_real_width()
    preview_width_code128 = code128.calculate_real_width(dpi=203)
    
    print(f"  Canvas:  {canvas_width_code128:.1f}mm")
    print(f"  Preview: {preview_width_code128:.1f}mm")
    print(f"  Diff:    {abs(canvas_width_code128 - preview_width_code128):.2f}mm")
    
    # 3. Читати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # 4. Аналізувати логи
    analyzer = BarcodeLogAnalyzer()
    real_width_logs = analyzer.parse_real_width_logs(new_logs)
    canvas_logs = analyzer.parse_canvas_item_logs(new_logs)
    
    print("\n" + "=" * 60)
    print("[LOG ANALYSIS]")
    print("=" * 60)
    print(f"Real width logs found: {len(real_width_logs)}")
    print(f"Canvas item logs found: {len(canvas_logs)}")
    
    for i, log in enumerate(canvas_logs, 1):
        print(f"\n[CANVAS LOG {i}]")
        print(f"  Source: {log['source']}")
        print(f"  Width: {log['width_mm']:.1f}mm")
        print(f"  Uses real width: {log['uses_real_width']}")
    
    # 5. Детектувати проблеми
    issues = analyzer.detect_issues(real_width_logs, canvas_logs, [])
    
    print("\n" + "=" * 60)
    print("[ISSUE DETECTION]")
    print("=" * 60)
    
    if issues:
        print(f"DETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  [{issue['type']}] {issue['desc']}")
        print("\n[FAILURE] Canvas НЕ відповідає Preview")
        return 1
    else:
        print("[OK] No issues detected")
        print("\nVERIFICATION:")
        print(f"  EAN-13:  Canvas {canvas_width_ean13:.1f}mm = Preview {preview_width_ean13:.1f}mm")
        print(f"  CODE128: Canvas {canvas_width_code128:.1f}mm = Preview {preview_width_code128:.1f}mm")
        
        # Додаткова перевірка: різниця має бути < 0.1mm
        diff_ean13 = abs(canvas_width_ean13 - preview_width_ean13)
        diff_code128 = abs(canvas_width_code128 - preview_width_code128)
        
        if diff_ean13 > 0.1 or diff_code128 > 0.1:
            print(f"\n[FAIL] Canvas and Preview do NOT match (tolerance 0.1mm)")
            return 1
        
        print("\n[SUCCESS] Canvas відповідає Preview!")
        return 0


if __name__ == '__main__':
    sys.exit(test_barcode_canvas_preview_smart())
