# -*- coding: utf-8 -*-
"""Script to extract remaining mixins from main_window.py"""

import re
from pathlib import Path

main_window_path = r'D:\AiKlientBank\1C_Zebra\gui\main_window.py'
mixins_dir = Path(r'D:\AiKlientBank\1C_Zebra\gui\mixins')

# Read main_window.py
with open(main_window_path, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Extract method ranges
method_ranges = {
    'template': [(373, 485), (1084, 1190)],  # _export_zpl, _save_template, _load_template, _show_preview
    'clipboard': [(806, 914)],  # _move_selected, _copy_selected, _paste, _duplicate
    'shortcuts': [(686, 805), (1008, 1082)],  # _setup_shortcuts, _toggle*, keyPressEvent
    'label_config': [(1192, 1359)],  # _create_label_size_controls, _apply_label_size, units methods
    'ui_helpers': [(156, 170), (916, 1006)]  # _undo, _redo, _bring_to_front, _send_to_back, _show_context_menu, _delete
}

# Helper to extract lines
def extract_lines(ranges):
    result = []
    for start, end in ranges:
        result.extend(lines[start-1:end])
    return '\n'.join(result)

# Create each mixin
print("Creating mixins...")

# 1. TemplateMixin
template_code = extract_lines(method_ranges['template'])
template_mixin = f'''# -*- coding: utf-8 -*-
"""Mixin для template операцій"""

from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QFileDialog, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from io import BytesIO
from datetime import datetime
import json
from pathlib import Path
from utils.logger import logger
from utils.unit_converter import MeasurementUnit
from core.elements.text_element import TextElement, GraphicsTextItem
from core.elements.image_element import ImageElement, GraphicsImageItem
from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem


class TemplateMixin:
    """Template save/load and ZPL export operations"""
    
{template_code}
'''

with open(mixins_dir / 'template_mixin.py', 'w', encoding='utf-8') as f:
    f.write(template_mixin)
print("Created template_mixin.py")

# 2. ClipboardMixin
clipboard_code = extract_lines(method_ranges['clipboard'])
clipboard_mixin = f'''# -*- coding: utf-8 -*-
"""Mixin для clipboard операцій"""

from utils.logger import logger
import copy


class ClipboardMixin:
    """Copy/paste/duplicate/move operations"""
    
{clipboard_code}
'''

with open(mixins_dir / 'clipboard_mixin.py', 'w', encoding='utf-8') as f:
    f.write(clipboard_mixin)
print("Created clipboard_mixin.py")

# 3. ShortcutsMixin
shortcuts_code = extract_lines(method_ranges['shortcuts'])
shortcuts_mixin = f'''# -*- coding: utf-8 -*-
"""Mixin для keyboard shortcuts"""

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt
from utils.logger import logger


class ShortcutsMixin:
    """Keyboard shortcuts setup and handlers"""
    
{shortcuts_code}
'''

with open(mixins_dir / 'shortcuts_mixin.py', 'w', encoding='utf-8') as f:
    f.write(shortcuts_mixin)
print("Created shortcuts_mixin.py")

# 4. LabelConfigMixin  
label_config_code = extract_lines(method_ranges['label_config'])
label_config_mixin = f'''# -*- coding: utf-8 -*-
"""Mixin для label size та units configuration"""

from PySide6.QtWidgets import QDoubleSpinBox, QPushButton, QHBoxLayout, QLabel, QComboBox
from utils.logger import logger
from utils.unit_converter import MeasurementUnit, UnitConverter
from config import DEFAULT_UNIT, UNIT_DECIMALS, UNIT_STEPS, CONFIG


class LabelConfigMixin:
    """Label size & units configuration"""
    
{label_config_code}
'''

with open(mixins_dir / 'label_config_mixin.py', 'w', encoding='utf-8') as f:
    f.write(label_config_mixin)
print("Created label_config_mixin.py")

# 5. UIHelpersMixin
ui_helpers_code = extract_lines(method_ranges['ui_helpers'])
ui_helpers_mixin = f'''# -*- coding: utf-8 -*-
"""Mixin для UI helper методів"""

from PySide6.QtWidgets import QMenu
from utils.logger import logger
from core.undo_commands import DeleteElementCommand


class UIHelpersMixin:
    """UI helper methods"""
    
{ui_helpers_code}
'''

with open(mixins_dir / 'ui_helpers_mixin.py', 'w', encoding='utf-8') as f:
    f.write(ui_helpers_mixin)
print("Created ui_helpers_mixin.py")

print("\nAll mixins created successfully!")
print(f"Location: {mixins_dir}")
