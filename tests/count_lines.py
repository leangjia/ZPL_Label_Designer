# Count lines in all files
from pathlib import Path

project_root = Path(r'D:\AiKlientBank\1C_Zebra')

files = {
    'main_window.py': project_root / 'gui' / 'main_window.py',
    'element_creation_mixin.py': project_root / 'gui' / 'mixins' / 'element_creation_mixin.py',
    'selection_mixin.py': project_root / 'gui' / 'mixins' / 'selection_mixin.py',
    'template_mixin.py': project_root / 'gui' / 'mixins' / 'template_mixin.py',
    'clipboard_mixin.py': project_root / 'gui' / 'mixins' / 'clipboard_mixin.py',
    'shortcuts_mixin.py': project_root / 'gui' / 'mixins' / 'shortcuts_mixin.py',
    'label_config_mixin.py': project_root / 'gui' / 'mixins' / 'label_config_mixin.py',
    'ui_helpers_mixin.py': project_root / 'gui' / 'mixins' / 'ui_helpers_mixin.py',
}

print("=" * 60)
print("LINE COUNT AFTER REFACTORING")
print("=" * 60)

total_lines = 0
for name, path in files.items():
    with open(path, 'r', encoding='utf-8') as f:
        lines = len(f.readlines())
    print(f"{name:30} {lines:4} lines")
    total_lines += lines

print("-" * 60)
print(f"{'TOTAL:':30} {total_lines:4} lines")
print("=" * 60)

# Compare with backup
backup_file = project_root / 'gui' / 'main_window_backup.py'
with open(backup_file, 'r', encoding='utf-8') as f:
    backup_lines = len(f.readlines())

print(f"\nBefore refactoring: {backup_lines} lines (main_window.py only)")
print(f"After refactoring:  {total_lines} lines (main_window.py + 7 mixins)")
print(f"Difference:         {total_lines - backup_lines:+} lines")
print(f"\nmain_window.py:     {len(open(files['main_window.py'], 'r', encoding='utf-8').readlines())} lines (was {backup_lines})")
