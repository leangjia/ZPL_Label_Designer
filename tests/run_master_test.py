"""Runner для запуска Master Test Suite"""
import subprocess

result = subprocess.run(
    [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', 
     r'tests\run_all_persistence_fix_tests.py'],
    cwd=r'D:\AiKlientBank\1C_Zebra',
    capture_output=True, text=True
)

print(result.stdout)
if result.stderr:
    print("\n" + "=" * 80)
    print("STDERR OUTPUT (INFO/DEBUG logs):")
    print("=" * 80)
    print(result.stderr)

print(f"\nFINAL EXIT CODE: {result.returncode}")
