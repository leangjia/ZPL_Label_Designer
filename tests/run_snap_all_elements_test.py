# -*- coding: utf-8 -*-
"""Runner для Master тесту - всі типи елементів"""
import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_snap_all_elements_smart.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr[-2000:])  # Last 2000 chars to avoid flood
print(f"\nEXIT CODE: {result.returncode}")
