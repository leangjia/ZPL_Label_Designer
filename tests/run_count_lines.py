import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\count_lines.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True, encoding='utf-8'
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
