# -*- coding: utf-8 -*-
"""
Простий тест імпортів для Template Manager
"""

import sys
sys.path.insert(0, r'D:\AiKlientBank\1C_Zebra')

try:
    from core.template_manager import TemplateManager
    from core.elements.text_element import TextElement
    from core.elements.base import ElementConfig
    
    with open(r'D:\AiKlientBank\1C_Zebra\tests\import_test_result.txt', 'w', encoding='utf-8') as f:
        f.write("[SUCCESS] All imports worked!\n")
        f.write("TemplateManager imported OK\n")
        f.write("TextElement imported OK\n")
        f.write("ElementConfig imported OK\n")
    
    print("[SUCCESS] All imports worked!")
    sys.exit(0)
    
except Exception as e:
    with open(r'D:\AiKlientBank\1C_Zebra\tests\import_test_result.txt', 'w', encoding='utf-8') as f:
        f.write(f"[FAILED] Import error: {e}\n")
        import traceback
        f.write(traceback.format_exc())
    
    print(f"[FAILED] Import error: {e}")
    sys.exit(1)
