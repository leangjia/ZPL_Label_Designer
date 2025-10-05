# -*- coding: utf-8 -*-
"""Extract _load_template and _show_preview methods"""

with open(r'D:\AiKlientBank\1C_Zebra\gui\main_window.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find method line numbers
for i, line in enumerate(lines, 1):
    if 'def _load_template' in line:
        print(f"_load_template starts at line: {i}")
    elif 'def _show_preview' in line:
        print(f"_show_preview starts at line: {i}")
    elif 'def _highlight_element_bounds' in line:
        print(f"_highlight_element_bounds starts at line: {i}")

# Extract _load_template (approximately lines 487-575)
print("\n=== EXTRACTING _load_template ===\n")
for i in range(486, 576):  # lines 487-576
    print(lines[i], end='')

print("\n\n=== EXTRACTING _show_preview ===\n")
# Extract _show_preview (approximately lines 1084-1190)
for i in range(1083, 1191):  # lines 1084-1191
    print(lines[i], end='')
