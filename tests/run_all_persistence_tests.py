import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PYTHON = sys.executable

TESTS = [
    ("STEP 1: Default Grid 1mm", 'tests/test_step1_default_grid.py'),
    ("STEP 2: Settings Manager", 'tests/test_step2_settings_manager.py'),
    ("STEP 3: Grid Dialog Persistence", 'tests/test_step3_grid_dialog_persistence.py'),
    ("STEP 4: Toolbar Persistence", 'tests/test_step4_toolbar_persistence.py'),
    ("STEP 5: Canvas Grid Persistence", 'tests/test_step5_canvas_grid_persistence.py'),
    ("STEP 6: Full Persistence Cycle", 'tests/test_step6_full_persistence_cycle.py'),
]


def main():
    env = os.environ.copy()
    env.setdefault('QT_QPA_PLATFORM', 'offscreen')

    results = []

    for stage_name, test_path in TESTS:
        print("\n" + "=" * 60)
        print(stage_name)
        print("=" * 60)

        process = subprocess.run(
            [PYTHON, test_path],
            cwd=BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
        )

        print(process.stdout)
        if process.stderr:
            print(process.stderr)

        results.append((stage_name, process.returncode))

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    all_passed = True
    for stage_name, code in results:
        status = "[OK]" if code == 0 else "[FAIL]"
        print(f"{status} {stage_name} - EXIT CODE: {code}")
        all_passed &= code == 0

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL PERSISTENCE TESTS PASSED!")
    else:
        print("[FAILURE] Some tests failed")

    return 0 if all_passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
