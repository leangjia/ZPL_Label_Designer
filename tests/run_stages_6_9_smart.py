# -*- coding: utf-8 -*-
"""Master runner - ЕТАПИ 6-9 умні тести"""

import subprocess

print("=" * 70)
print(" MASTER TEST RUNNER - STAGES 6-9 ADVANCED CANVAS FEATURES")
print("=" * 70)

tests = [
    ("STAGE 6: CONTEXT MENU", r'tests\test_context_menu_smart.py'),
    ("STAGE 7: SMART GUIDES", r'tests\test_smart_guides_smart.py'),
    ("STAGE 8: UNDO/REDO", r'tests\test_undo_redo_smart.py'),
    ("STAGE 9: MULTI-SELECT", r'tests\test_multi_select_smart.py'),
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
    
    results.append({
        'stage': stage_name,
        'exit_code': result.returncode,
        'success': result.returncode == 0
    })

# Підсумковий звіт
print("\n" + "=" * 70)
print(" FINAL RESULTS - STAGES 6-9")
print("=" * 70)

all_passed = True
for r in results:
    status = "[OK]" if r['success'] else "[FAIL]"
    print(f"{status} {r['stage']} - EXIT CODE: {r['exit_code']}")
    if not r['success']:
        all_passed = False

print("\n" + "=" * 70)
if all_passed:
    print(" ALL STAGES 6-9 PASSED!")
    print(" Advanced Canvas Features Ready for Production")
else:
    print(" SOME STAGES FAILED!")
    print(" Fix issues before proceeding")
print("=" * 70)
