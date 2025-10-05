# -*- coding: utf-8 -*-
"""Runner для умного snap теста v2"""

import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_snap_smart_v2.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True,
    text=True
)

print(result.stdout)
print(f"\nEXIT CODE: {result.returncode}")
