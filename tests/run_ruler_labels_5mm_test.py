# -*- coding: utf-8 -*-
"""Runner для test_ruler_labels_5mm.py"""

import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_ruler_labels_5mm.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, 
    text=True
)

print(result.stdout)

print(f"\nEXIT CODE: {result.returncode}")
