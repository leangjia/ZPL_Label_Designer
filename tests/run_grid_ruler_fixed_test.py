# -*- coding: utf-8 -*-
"""Runner для test_grid_ruler_fixed.py"""

import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_grid_ruler_fixed.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, 
    text=True
)

print(result.stdout)

print(f"\nEXIT CODE: {result.returncode}")
