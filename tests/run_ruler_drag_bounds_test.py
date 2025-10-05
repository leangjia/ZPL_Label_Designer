# -*- coding: utf-8 -*-
"""Runner для smart-теста ruler bounds drag"""

import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
TEST_SCRIPT = ROOT_DIR / 'tests' / 'test_ruler_drag_bounds_smart.py'

env = os.environ.copy()
env.setdefault('QT_QPA_PLATFORM', 'offscreen')

result = subprocess.run(
    [sys.executable, str(TEST_SCRIPT)],
    cwd=str(ROOT_DIR),
    capture_output=True,
    text=True,
    env=env,
)

print(result.stdout)
if result.stderr:
    print('STDERR:')
    print(result.stderr)

print(f"\nEXIT CODE: {result.returncode}")
