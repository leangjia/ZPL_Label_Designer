import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\extract_methods.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
