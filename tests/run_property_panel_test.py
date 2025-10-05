# -*- coding: utf-8 -*-
"""Runner для теста PropertyPanel + Snap"""

import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\test_property_panel_snap.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True,
    text=True
)

print("=" * 60)
print("STDOUT:")
print("=" * 60)
print(result.stdout)
print("\n" + "=" * 60)
print("STDERR:")
print("=" * 60)
print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)  # Последние 2000 символов
print("\n" + "=" * 60)
print(f"EXIT CODE: {result.returncode}")
print("=" * 60)
