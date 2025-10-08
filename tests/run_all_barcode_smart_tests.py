# -*- coding: utf-8 -*-
"""Master Runner для всіх Barcode Smart Tests"""

import subprocess

tests = [
    ("BARCODE REAL WIDTH CALCULATION", r'tests\test_barcode_real_width_smart.py'),
    ("BARCODE CANVAS = PREVIEW", r'tests\test_barcode_canvas_preview_smart.py'),
    ("BARCODE ZPL + DATA CHANGES", r'tests\test_barcode_zpl_and_data_changes_smart.py'),
]

results = []

print("=" * 70)
print(" BARCODE SMART TESTS - MASTER RUNNER")
print("=" * 70)

for stage_name, test_path in tests:
    print(f"\n{'=' * 70}\n {stage_name}\n{'=' * 70}")
    
    result = subprocess.run(
        [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', test_path],
        cwd=r'D:\AiKlientBank\1C_Zebra',
        capture_output=True, text=True
    )
    
    print(result.stdout)
    results.append({'stage': stage_name, 'exit_code': result.returncode})

# Підсумковий звіт
print(f"\n{'=' * 70}\n FINAL RESULTS\n{'=' * 70}")

total_tests = len(results)
passed_tests = sum(1 for r in results if r['exit_code'] == 0)
failed_tests = total_tests - passed_tests

for r in results:
    status = "[OK]" if r['exit_code'] == 0 else "[FAIL]"
    print(f"{status} {r['stage']} - EXIT CODE: {r['exit_code']}")

print(f"\n{'=' * 70}")
print(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
print("=" * 70)

if failed_tests > 0:
    print(f"\n[FAILURE] {failed_tests} test(s) failed")
    exit(1)
else:
    print("\n[SUCCESS] All Barcode tests passed!")
    exit(0)
