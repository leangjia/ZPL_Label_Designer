# -*- coding: utf-8 -*-
"""Runner для test_font_shortcuts_checkboxes.py"""

import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_font_shortcuts_checkboxes.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True
)

print(result.stdout)
if result.stderr:
    print("\nSTDERR (INFO logs):")
    # Показувати тільки критичні помилки, не INFO логи
    stderr_lines = result.stderr.split('\n')
    for line in stderr_lines:
        if '[ERROR]' in line or '[CRITICAL]' in line or 'Traceback' in line or 'Error' in line:
            print(line)

print(f"\nEXIT CODE: {result.returncode}")
