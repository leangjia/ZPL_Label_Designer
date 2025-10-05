# -*- coding: utf-8 -*-
"""Master Runner для всіх тестів default thickness"""
import subprocess

tests = [
    ("Line Thickness", r'tests\test_default_thickness_line.py'),
    ("Master Test - All Elements", r'tests\test_all_default_thickness.py'),
]

results = []

print("=" * 80)
print(" DEFAULT THICKNESS FIX - FULL TEST SUITE")
print("=" * 80)

for stage_name, test_path in tests:
    print(f"\n{'=' * 80}\n{stage_name}\n{'=' * 80}")
    
    result = subprocess.run(
        [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', test_path],
        cwd=r'D:\AiKlientBank\1C_Zebra',
        capture_output=True, text=True
    )
    
    print(result.stdout)
    results.append({'stage': stage_name, 'exit_code': result.returncode})

# Фінальний звіт
print(f"\n{'=' * 80}\nFINAL RESULTS\n{'=' * 80}")
for r in results:
    status = "[OK]" if r['exit_code'] == 0 else "[FAIL]"
    print(f"{status} {r['stage']} - EXIT CODE: {r['exit_code']}")

all_passed = all(r['exit_code'] == 0 for r in results)
print(f"\n{'=' * 80}")
if all_passed:
    print("[SUCCESS] ALL DEFAULT THICKNESS TESTS PASSED!")
    print("Rectangle, Circle, Line now have default thickness: 1 mm")
else:
    failed = [r['stage'] for r in results if r['exit_code'] != 0]
    print(f"[FAILURE] {len(failed)} test(s) failed:")
    for stage in failed:
        print(f"  - {stage}")

print("=" * 80)
