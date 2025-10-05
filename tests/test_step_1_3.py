# -*- coding: utf-8 -*-
"""Тест Step 1.3 - проверка импортов и создания элементов"""

import sys
from pathlib import Path

# Добавить корневую папку в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Проверка импортов"""
    print("[TEST] Проверка импортов...")
    
    try:
        from core.elements.base import ElementConfig, BaseElement
        print("[+] core.elements.base - OK")
    except Exception as e:
        print(f"[-] core.elements.base - FAIL: {e}")
        return False
    
    try:
        from core.elements.text_element import TextElement
        print("[+] core.elements.text_element - OK")
    except Exception as e:
        print(f"[-] core.elements.text_element - FAIL: {e}")
        return False
    
    try:
        from gui.toolbar import EditorToolbar
        print("[+] gui.toolbar - OK")
    except Exception as e:
        print(f"[-] gui.toolbar - FAIL: {e}")
        return False
    
    return True

def test_element_creation():
    """Проверка создания элемента"""
    print("\n[TEST] Создание TextElement...")
    
    try:
        from core.elements.base import ElementConfig
        from core.elements.text_element import TextElement
        
        config = ElementConfig(x=10.0, y=15.0)
        element = TextElement(config, "Test Text", font_size=25)
        
        print(f"[+] Element created: pos=({element.config.x}, {element.config.y}), text='{element.text}'")
        
        # Проверка to_dict
        data = element.to_dict()
        print(f"[+] to_dict(): {data}")
        
        # Проверка to_zpl
        zpl = element.to_zpl(dpi=203)
        print(f"[+] to_zpl(): {zpl}")
        
        return True
    except Exception as e:
        print(f"[-] FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("STEP 1.3 TEST")
    print("=" * 50)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_element_creation():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("[OK] All tests passed!")
    else:
        print("[FAIL] Some tests failed!")
    print("=" * 50)
    
    sys.exit(0 if success else 1)
