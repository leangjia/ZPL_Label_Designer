# -*- coding: utf-8 -*-
"""MainWindow Mixins для розділення функціоналу"""

from .element_creation_mixin import ElementCreationMixin
from .selection_mixin import SelectionMixin
from .template_mixin import TemplateMixin
from .clipboard_mixin import ClipboardMixin
from .shortcuts_mixin import ShortcutsMixin
from .label_config_mixin import LabelConfigMixin
from .ui_helpers_mixin import UIHelpersMixin

__all__ = [
    'ElementCreationMixin',
    'SelectionMixin',
    'TemplateMixin',
    'ClipboardMixin',
    'ShortcutsMixin',
    'LabelConfigMixin',
    'UIHelpersMixin',
]
