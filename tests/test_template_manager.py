# -*- coding: utf-8 -*-
"""
Тест ШАГ 2.1-2.2: Template Manager - Save/Load JSON

Перевірка:
1. Створення TemplateManager
2. Збереження шаблону в JSON
3. Завантаження шаблону з JSON
4. Перевірка структури JSON файлу
"""

import sys
import os

# Додати шлях до проекту
sys.path.insert(0, r'D:\AiKlientBank\1C_Zebra')

from pathlib import Path
import json
from core.template_manager import TemplateManager
from core.elements.text_element import TextElement
from core.elements.base import ElementConfig


# Відкрити файл для запису результатів
result_file = open('tests/test_template_manager_result.txt', 'w', encoding='utf-8')

def log(msg):
    """Логування в файл і консоль"""
    print(msg)
    result_file.write(msg + '\n')
    result_file.flush()


def test_template_manager():
    """Тест Template Manager"""
    log("[INFO] Starting Template Manager test...")
    log("="*60)
    
    # 1. Створити TemplateManager
    log("\n[TEST 1] Creating TemplateManager...")
    templates_dir = "templates/library_test"
    manager = TemplateManager(templates_dir=templates_dir)
    
    # Перевірити що директорія створена
    if Path(templates_dir).exists():
        log(f"[+] Templates directory created: {templates_dir}")
    else:
        log(f"[-] FAILED: Directory not created")
        return False
    
    # 2. Створити тестові елементи
    log("\n[TEST 2] Creating test elements...")
    elements = []
    
    # Текстовий елемент 1
    config1 = ElementConfig(x=10, y=10)
    text1 = TextElement(config1, "Product Name", font_size=30)
    text1.data_field = "{{PRODUCT_NAME}}"
    elements.append(text1)
    
    # Текстовий елемент 2
    config2 = ElementConfig(x=10, y=20)
    text2 = TextElement(config2, "Price: 100", font_size=20)
    text2.data_field = "{{PRICE}}"
    elements.append(text2)
    
    log(f"[+] Created {len(elements)} test elements")
    
    # 3. Зберегти шаблон
    log("\n[TEST 3] Saving template to JSON...")
    label_config = {
        'width': 28,
        'height': 28,
        'dpi': 203
    }
    
    metadata = {
        'description': 'Test template for product labels',
        'author': 'Test Script'
    }
    
    try:
        filepath = manager.save_template(
            name="test_product_label",
            elements=elements,
            label_config=label_config,
            metadata=metadata
        )
        log(f"[+] Template saved: {filepath}")
    except Exception as e:
        log(f"[-] FAILED to save template: {e}")
        import traceback
        log(traceback.format_exc())
        return False
    
    # 4. Перевірити структуру JSON файлу
    log("\n[TEST 4] Verifying JSON structure...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Перевірити ключі
        required_keys = ['name', 'version', 'created_at', 'updated_at', 
                        'label_config', 'elements', 'metadata']
        
        for key in required_keys:
            if key in data:
                log(f"[+] Key '{key}' present")
            else:
                log(f"[-] FAILED: Missing key '{key}'")
                return False
        
        # Перевірити кількість елементів
        if len(data['elements']) == 2:
            log(f"[+] Correct number of elements: {len(data['elements'])}")
        else:
            log(f"[-] FAILED: Expected 2 elements, got {len(data['elements'])}")
            return False
        
        # Показати структуру першого елемента
        log("\n[INFO] First element structure:")
        log(json.dumps(data['elements'][0], indent=2, ensure_ascii=False))
        
    except Exception as e:
        log(f"[-] FAILED to verify JSON: {e}")
        import traceback
        log(traceback.format_exc())
        return False
    
    # 5. Завантажити шаблон
    log("\n[TEST 5] Loading template from JSON...")
    try:
        loaded_data = manager.load_template(filepath)
        
        # Перевірити дані
        if loaded_data['name'] == 'test_product_label':
            log(f"[+] Template name correct: {loaded_data['name']}")
        else:
            log(f"[-] FAILED: Wrong template name")
            return False
        
        if len(loaded_data['elements']) == 2:
            log(f"[+] Loaded {len(loaded_data['elements'])} elements")
        else:
            log(f"[-] FAILED: Expected 2 elements, got {len(loaded_data['elements'])}")
            return False
        
        # Перевірити перший елемент
        elem1 = loaded_data['elements'][0]
        if elem1.text == "Product Name" and elem1.config.x == 10:
            log(f"[+] First element data correct")
        else:
            log(f"[-] FAILED: First element data incorrect")
            return False
        
        # Перевірити placeholder
        if elem1.data_field == "{{PRODUCT_NAME}}":
            log(f"[+] Placeholder preserved: {elem1.data_field}")
        else:
            log(f"[-] FAILED: Placeholder incorrect")
            return False
        
    except Exception as e:
        log(f"[-] FAILED to load template: {e}")
        import traceback
        log(traceback.format_exc())
        return False
    
    # 6. Тест list_templates
    log("\n[TEST 6] Listing templates...")
    try:
        templates = manager.list_templates()
        log(f"[+] Found {len(templates)} templates")
        
        for template in templates:
            log(f"  - {template['name']} ({template['path']})")
    
    except Exception as e:
        log(f"[-] FAILED to list templates: {e}")
        import traceback
        log(traceback.format_exc())
        return False
    
    log("\n" + "="*60)
    log("[SUCCESS] All Template Manager tests passed!")
    log("="*60)
    return True


if __name__ == '__main__':
    try:
        success = test_template_manager()
        result_file.close()
        sys.exit(0 if success else 1)
    except Exception as e:
        log(f"\nEXCEPTION: {e}")
        import traceback
        log(traceback.format_exc())
        result_file.close()
        sys.exit(1)
