# Find and extract _load_template
import re

with open(r'D:\AiKlientBank\1C_Zebra\gui\main_window.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find _load_template start
start_line = None
for i, line in enumerate(lines):
    if 'def _load_template(self):' in line:
        start_line = i
        print(f"Found _load_template at line {i+1}")
        break

if start_line:
    # Extract method (look for next 'def ' at same indentation)
    method_lines = [lines[start_line]]
    for i in range(start_line + 1, min(start_line + 100, len(lines))):
        line = lines[i]
        # Check if we reached next method
        if line.strip().startswith('def ') and not line.startswith('        '):
            break
        method_lines.append(line)
    
    print("\n_load_template method:")
    print(''.join(method_lines))
