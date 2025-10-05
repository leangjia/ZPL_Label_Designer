# -*- coding: utf-8 -*-
"""Runner для умного snap теста с анализом логов"""

import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_snap_smart.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True,
    text=True
)

print(result.stdout)
print("\nSTDERR (last 500 chars):")
print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
print(f"\nEXIT CODE: {result.returncode}")
