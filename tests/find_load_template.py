# -*- coding: utf-8 -*-
"""Simple script to find _load_template method"""

with open(r'D:\AiKlientBank\1C_Zebra\gui\main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find _load_template method
start = content.find('def _load_template(self):')
if start != -1:
    # Find next method (next 'def ' at same indentation level)
    next_def = content.find('\n    def ', start + 1)
    if next_def != -1:
        method_content = content[start:next_def]
    else:
        # If no next method, take until end
        method_content = content[start:start+3000]  # reasonable limit
    
    print(method_content)
else:
    print("Method _load_template not found!")
