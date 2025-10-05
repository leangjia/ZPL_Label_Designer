# -*- coding: utf-8 -*-
"""Analyze main_window.py structure"""

import re

file_path = r'D:\AiKlientBank\1C_Zebra\gui\main_window.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

total_lines = len(lines)
print(f"Total lines: {total_lines}")
print("\nMethods found:")

methods = []
for i, line in enumerate(lines, 1):
    if re.match(r'^\s{4}def\s+\w+\(', line):
        method_name = re.search(r'def\s+(\w+)\(', line).group(1)
        methods.append((i, method_name))

# Group methods by category
categories = {
    'Init': [],
    'Element Creation': [],
    'Selection': [],
    'Template': [],
    'Clipboard': [],
    'Shortcuts': [],
    'Label Config': [],
    'UI Helpers': [],
    'Other': []
}

for line_num, method_name in methods:
    if method_name == '__init__':
        categories['Init'].append((line_num, method_name))
    elif method_name.startswith('_add_'):
        categories['Element Creation'].append((line_num, method_name))
    elif 'selection' in method_name or 'highlight' in method_name or method_name.startswith('event'):
        categories['Selection'].append((line_num, method_name))
    elif 'template' in method_name or 'save' in method_name or 'load' in method_name or 'export' in method_name or 'preview' in method_name:
        categories['Template'].append((line_num, method_name))
    elif 'copy' in method_name or 'paste' in method_name or 'duplicate' in method_name or 'delete' in method_name or method_name == '_move_selected':
        categories['Clipboard'].append((line_num, method_name))
    elif 'shortcut' in method_name or method_name == 'keyPressEvent' or 'toggle' in method_name:
        categories['Shortcuts'].append((line_num, method_name))
    elif 'label' in method_name or 'unit' in method_name or 'spinbox' in method_name or '_apply_' in method_name:
        categories['Label Config'].append((line_num, method_name))
    elif 'context' in method_name or 'front' in method_name or 'back' in method_name or 'undo' in method_name or 'redo' in method_name:
        categories['UI Helpers'].append((line_num, method_name))
    else:
        categories['Other'].append((line_num, method_name))

print("\n=== METHODS BY CATEGORY ===\n")
for category, methods_list in categories.items():
    if methods_list:
        print(f"{category} ({len(methods_list)} methods):")
        for line_num, method in methods_list:
            print(f"  Line {line_num}: {method}")
        print()

print(f"\n=== SUMMARY ===")
print(f"Total lines: {total_lines}")
print(f"Total methods: {len(methods)}")
for category, methods_list in categories.items():
    if methods_list:
        print(f"{category}: {len(methods_list)} methods")
