# -*- coding: utf-8 -*-
"""Master runner - ЕТАПИ 1-5 умні тести"""

import subprocess

print("=" * 70)
print(" MASTER TEST RUNNER - STAGES 1-5 BASIC CANVAS FEATURES")
print("=" * 70)

tests = [
    ("STAGE 1: CURSOR TRACKING", r'tests\test_cursor_tracking_smart.py'),
    ("STAGE 2: ZOOM TO POINT", r'tests\test_zoom_smart.py'),
    ("STAGE 3: SNAP TO GRID", r'tests\test_snap_smart.py'),
    ("STAGE 4: ELEMENT BOUNDS", r'tests\test_bounds_smart.py'),
    ("STAGE 5: KEYBOARD SHORTCUTS", r'tests\test_shortcuts_smart.py'),
]

results = []

for stage_name, test_path in tests:
    print(f"\n{'=' * 70}")
    print(f" {stage_name}")
    print('=' * 70)
    
    result = subprocess.run(
        [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', test_path],
        cwd=r'D:\AiKlientBank\1C_Zebra',
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    results.append({
        'stage': stage_name,
        'exit_code': result.returncode,
        'success': result.returncode == 0
    })

# Підсумковий звіт
print("\n" + "=" * 70)
print(" FINAL RESULTS - STAGES 1-5")
print("=" * 70)

all_passed = True
for r in results:
    status = "[OK]" if r['success'] else "[FAIL]"
    print(f"{status} {r['stage']} - EXIT CODE: {r['exit_code']}")
    if not r['success']:
        all_passed = False

print("\n" + "=" * 70)
if all_passed:
    print(" ALL STAGES 1-5 PASSED!")
    print(" Basic Canvas Features Ready for Production")
else:
    print(" SOME STAGES FAILED!")
    print(" Fix issues before proceeding")
print("=" * 70)
