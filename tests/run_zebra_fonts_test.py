# -*- coding: utf-8 -*-
"""Runner для ZEBRA fonts умного тесту"""

import subprocess

print("="*60)
print(" ZEBRA FONTS SUPPORT TEST RUNNER")
print("="*60)

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe',
     r'D:\AiKlientBank\1C_Zebra\tests\test_zebra_fonts_smart.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)

print(f"\nEXIT CODE: {result.returncode}")
print("0 = Success, 1 = Failure")
