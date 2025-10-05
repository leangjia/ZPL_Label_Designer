"""
Master Runner для всех тестов исправления Settings Persistence
Запускает все 6 тестов последовательно и выводит финальный отчет
"""
import subprocess

tests = [
    ("STEP 1: Remove Hardcode", r'tests\test_step1_no_hardcode.py'),
    ("STEP 2: Show Grid Works", r'tests\test_step2_show_grid_works.py'),
    ("STEP 3: Snap to Grid Works", r'tests\test_step3_snap_works.py'),
    ("STEP 4: Smart Guides Work", r'tests\test_step4_guides_work.py'),
    ("STEP 5: Units Applied to Rulers", r'tests\test_step5_units_work.py'),
    ("STEP 6: Full Persistence Cycle", r'tests\test_step6_full_persistence_cycle.py'),
]

results = []

print("=" * 80)
print(" SETTINGS PERSISTENCE FIX - FULL TEST SUITE")
print("=" * 80)

for stage_name, test_path in tests:
    print(f"\n{'=' * 80}\n{stage_name}\n{'=' * 80}")
    
    result = subprocess.run(
        [r'D:\AiKlientBank\1C_Zebra\.venv\Scripts\python.exe', test_path],
        cwd=r'D:\AiKlientBank\1C_Zebra',
        capture_output=True, text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    results.append({'stage': stage_name, 'exit_code': result.returncode})

# Финальный отчет
print(f"\n{'=' * 80}\nFINAL RESULTS\n{'=' * 80}")
for r in results:
    status = "[OK]" if r['exit_code'] == 0 else "[FAIL]"
    print(f"{status} {r['stage']} - EXIT CODE: {r['exit_code']}")

# Общий результат
all_passed = all(r['exit_code'] == 0 for r in results)
print(f"\n{'=' * 80}")
if all_passed:
    print("[SUCCESS] ALL PERSISTENCE FIX TESTS PASSED!")
    print("Settings are now correctly saved AND applied on startup!")
else:
    failed = [r['stage'] for r in results if r['exit_code'] != 0]
    print(f"[FAILURE] {len(failed)} test(s) failed:")
    for stage in failed:
        print(f"  - {stage}")

print("=" * 80)
