# -*- coding: utf-8 -*-
"""Runner для test_perfect_grid_ruler.py"""

import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_perfect_grid_ruler.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, 
    text=True
)

print(result.stdout)

print(f"\nEXIT CODE: {result.returncode}")
