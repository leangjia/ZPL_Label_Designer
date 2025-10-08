# -*- coding: utf-8 -*-
"""Швидка перевірка ZPL генерації з різними fonts"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.elements.text_element import TextElement, ZplFont
from core.elements.base import ElementConfig

print("="*60)
print("ZPL FONT GENERATION CHECK")
print("="*60)

# Створити Text Element з Font E (OCR-B)
config = ElementConfig(x=10.0, y=10.0)
element = TextElement(config, text="Test", font_size=50, font_family=ZplFont.FONT_E)

print(f"\nElement Font: {element.font_family.zpl_code} ({element.font_family.display_name})")
print(f"Font Size: {element.font_size} dots")

# Генерувати ZPL
zpl = element.to_zpl(dpi=203)

print("\nGENERATED ZPL:")
print(zpl)

# Перевірити чи є ^AEN (Font E)
if "^AEN" in zpl:
    print("\n[OK] Font E (OCR-B) correctly used in ZPL!")
else:
    print("\n[ERROR] Expected ^AEN command not found!")
    print(f"ZPL contains: {zpl}")

# Тест Font A
print("\n" + "="*60)
element_a = TextElement(config, text="Test", font_size=40, font_family=ZplFont.FONT_A)
zpl_a = element_a.to_zpl(dpi=203)

print(f"Font A ZPL:\n{zpl_a}")

if "^AAN" in zpl_a:
    print("[OK] Font A correctly used!")
else:
    print("[ERROR] Font A not found!")

print("\n" + "="*60)
print("NOTE: Canvas shows Arial (Qt limitation)")
print("Real font visible ONLY in Preview or Print!")
print("="*60)
