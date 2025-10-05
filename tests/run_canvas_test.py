import subprocess
import sys

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests/test_canvas_stages_1_2_3_automated.py'],
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
print(result.stderr)
print("\n" + "=" * 60)
print(f"EXIT CODE: {result.returncode}")
print("=" * 60)
