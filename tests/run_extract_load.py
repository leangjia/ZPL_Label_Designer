import subprocess
import sys

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\extract_load_template.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True, encoding='utf-8'
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print(f"\nEXIT CODE: {result.returncode}")
