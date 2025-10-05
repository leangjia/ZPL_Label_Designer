import sys
import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'main.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True,
    text=True,
    timeout=None  # Без timeout - запуск GUI
)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
print(f"\nEXIT CODE: {result.returncode}")
