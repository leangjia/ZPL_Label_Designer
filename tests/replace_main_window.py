# Backup old main_window.py and replace with new
import shutil
from pathlib import Path

project_root = Path(r'D:\AiKlientBank\1C_Zebra')
old_file = project_root / 'gui' / 'main_window.py'
backup_file = project_root / 'gui' / 'main_window_backup.py'
new_file = project_root / 'gui' / 'main_window_new.py'

# Create backup
print(f"Creating backup: {backup_file}")
shutil.copy2(old_file, backup_file)
print("[OK] Backup created")

# Replace with new
print(f"\nReplacing {old_file} with {new_file}")
shutil.copy2(new_file, old_file)
print("[OK] File replaced")

print("\n[SUCCESS] main_window.py updated with mixins!")
