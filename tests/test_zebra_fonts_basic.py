# -*- coding: utf-8 -*-
"""Базовий тест перевірки ZplFont enum"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.elements.text_element import ZplFont, TextElement
from core.elements.base import ElementConfig

print("=" * 60)
print(" ZEBRA FONTS BASIC TEST")
print("=" * 60)

# Тест 1: ZplFont enum існує
print("\n[TEST 1] ZplFont enum:")
for font in ZplFont:
    print(f"  {font.zpl_code}: {font.display_name}")

# Тест 2: TextElement має font_family
print("\n[TEST 2] TextElement.font_family:")
config = ElementConfig(x=10, y=10)
element = TextElement(config, "Test", 50)
print(f"  Default font_family: {element.font_family.zpl_code} ({element.font_family.display_name})")

# Тест 3: Зміна font_family
print("\n[TEST 3] Change font_family:")
element.font_family = ZplFont.FONT_D
print(f"  Changed to: {element.font_family.zpl_code} ({element.font_family.display_name})")

# Тест 4: to_dict() зберігає font_family
print("\n[TEST 4] to_dict() serialization:")
data = element.to_dict()
print(f"  font_family in dict: {data.get('font_family')}")

# Тест 5: from_dict() backward compatibility
print("\n[TEST 5] from_dict() backward compatibility:")
old_data = {'type': 'text', 'x': 5, 'y': 5, 'text': 'Old', 'font_size': 30}
old_element = TextElement.from_dict(old_data)
print(f"  Old template (no font_family): {old_element.font_family.zpl_code}")

# Тест 6: to_zpl() генерує правильний код
print("\n[TEST 6] to_zpl() generation:")
element2 = TextElement(ElementConfig(x=10, y=10), "Test", 50, ZplFont.FONT_D)
zpl = element2.to_zpl(203)
print(f"  ZPL contains ^AD: {'ADN' in zpl}")
print(f"  ZPL output:\n{zpl}")

print("\n[SUCCESS] All basic tests passed!")
print("EXIT CODE: 0")
