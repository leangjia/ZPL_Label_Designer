# -*- coding: utf-8 -*-
"""Тест Rectangle rounding параметр"""

import sys
from pathlib import Path

# Додати project root до sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.elements.shape_element import RectangleElement, ShapeConfig


def test_rectangle_rounding():
    """Перевірити що Rectangle генерує rounding=0"""
    
    print("=" * 60)
    print("[TEST] Rectangle Rounding Parameter")
    print("=" * 60)
    
    # Створити Rectangle як на скріншоті
    config = ShapeConfig(
        x=2.9,
        y=3.9,
        width=20.0,
        height=10.0,
        fill=False,
        border_thickness=1.0
    )
    
    rect = RectangleElement(config)
    
    # Згенерувати ZPL
    zpl = rect.to_zpl(dpi=203)
    
    print("\n[GENERATED ZPL]")
    print(zpl)
    
    # Перевірити параметр rounding
    print("\n" + "=" * 60)
    print("[ANALYSIS]")
    print("=" * 60)
    
    lines = zpl.split('\n')
    gb_line = None
    for line in lines:
        if line.startswith('^GB'):
            gb_line = line
            break
    
    if gb_line:
        print(f"^GB command: {gb_line}")
        
        # Розпарсити параметри ^GB{width},{height},{thickness},{color},{rounding}
        params = gb_line.replace('^GB', '').split(',')
        
        if len(params) >= 5:
            width = params[0]
            height = params[1]
            thickness = params[2]
            color = params[3]
            rounding = params[4]
            
            print(f"\nParameters:")
            print(f"  Width: {width} dots")
            print(f"  Height: {height} dots")
            print(f"  Thickness: {thickness} dots")
            print(f"  Color: {color}")
            print(f"  Rounding: {rounding}")
            
            if rounding == '0':
                print("\n[OK] Rounding = 0 (NO rounding)")
                print("Issue: Labelary preview BUG or browser rendering issue")
                return 0
            else:
                print(f"\n[FAIL] Rounding = {rounding} (should be 0)")
                print("Fix: Set rounding=0 in RectangleElement.to_zpl()")
                return 1
        else:
            print(f"[ERROR] ^GB має тільки {len(params)} параметрів")
            return 1
    else:
        print("[ERROR] ^GB команда НЕ знайдена!")
        return 1


if __name__ == '__main__':
    sys.exit(test_rectangle_rounding())
