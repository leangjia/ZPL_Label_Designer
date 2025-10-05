# -*- coding: utf-8 -*-
"""Settings Manager для збереження користувацьких налаштувань"""

from PySide6.QtCore import QSettings

from utils.logger import logger
from config import SnapMode


class SettingsManager:
    """Управління налаштуваннями застосунку через QSettings."""

    def __init__(self):
        # Windows: HKEY_CURRENT_USER\Software\Anthropic\ZPL_Designer
        # Linux: ~/.config/Anthropic/ZPL_Designer.conf
        # macOS: ~/Library/Preferences/com.Anthropic.ZPL_Designer.plist
        self.settings = QSettings("Anthropic", "ZPL_Designer")
        logger.debug("[SETTINGS] SettingsManager initialized")

    # ========== GRID SETTINGS ==========

    def save_grid_settings(self, settings_dict):
        """Зберегти налаштування сітки."""
        self.settings.setValue("grid/size_x", settings_dict.get("size_x", 1.0))
        self.settings.setValue("grid/size_y", settings_dict.get("size_y", 1.0))
        self.settings.setValue("grid/offset_x", settings_dict.get("offset_x", 0.0))
        self.settings.setValue("grid/offset_y", settings_dict.get("offset_y", 0.0))
        self.settings.setValue("grid/show_gridlines", settings_dict.get("show_gridlines", True))
        snap_mode_value = settings_dict.get("snap_mode", SnapMode.GRID)
        if isinstance(snap_mode_value, SnapMode):
            snap_mode_to_store = snap_mode_value.value
        else:
            snap_mode_to_store = str(snap_mode_value)

        self.settings.setValue("grid/snap_mode", snap_mode_to_store)

        self.settings.sync()
        logger.debug(f"[SETTINGS] Grid settings saved: {settings_dict}")

    def load_grid_settings(self):
        """Завантажити налаштування сітки."""
        settings = {
            "size_x": self.settings.value("grid/size_x", defaultValue=1.0, type=float),
            "size_y": self.settings.value("grid/size_y", defaultValue=1.0, type=float),
            "offset_x": self.settings.value("grid/offset_x", defaultValue=0.0, type=float),
            "offset_y": self.settings.value("grid/offset_y", defaultValue=0.0, type=float),
            "show_gridlines": self.settings.value("grid/show_gridlines", defaultValue=True, type=bool),
            "snap_mode": self._load_snap_mode(),
        }

        logger.debug(f"[SETTINGS] Grid settings loaded: {settings}")
        return settings

    # ========== TOOLBAR SETTINGS ==========

    def save_toolbar_settings(self, settings_dict):
        """Зберегти налаштування toolbar."""
        self.settings.setValue("toolbar/show_grid", settings_dict.get("show_grid", True))
        self.settings.setValue("toolbar/snap_to_grid", settings_dict.get("snap_to_grid", True))
        self.settings.setValue("toolbar/smart_guides", settings_dict.get("smart_guides", True))
        self.settings.setValue("toolbar/label_width", settings_dict.get("label_width", 28.0))
        self.settings.setValue("toolbar/label_height", settings_dict.get("label_height", 28.0))
        self.settings.setValue("toolbar/unit", settings_dict.get("unit", "mm"))

        self.settings.sync()
        logger.debug(f"[SETTINGS] Toolbar settings saved: {settings_dict}")

    def load_toolbar_settings(self):
        """Завантажити налаштування toolbar."""
        settings = {
            "show_grid": self.settings.value("toolbar/show_grid", defaultValue=True, type=bool),
            "snap_to_grid": self.settings.value("toolbar/snap_to_grid", defaultValue=True, type=bool),
            "smart_guides": self.settings.value("toolbar/smart_guides", defaultValue=True, type=bool),
            "label_width": self.settings.value("toolbar/label_width", defaultValue=28.0, type=float),
            "label_height": self.settings.value("toolbar/label_height", defaultValue=28.0, type=float),
            "unit": self.settings.value("toolbar/unit", defaultValue="mm", type=str),
        }

        logger.debug(f"[SETTINGS] Toolbar settings loaded: {settings}")
        return settings

    def clear_all_settings(self):
        """Очистити всі налаштування (для тестів)."""
        self.settings.clear()
        self.settings.sync()
        logger.debug("[SETTINGS] All settings cleared")

    def _load_snap_mode(self):
        """Допоміжний метод для завантаження SnapMode."""
        snap_mode_value = self.settings.value(
            "grid/snap_mode",
            defaultValue=SnapMode.GRID.value,
            type=str,
        )

        try:
            snap_mode = SnapMode(snap_mode_value)
        except ValueError:
            logger.warning(
                f"[SETTINGS] Unknown snap mode '{snap_mode_value}', fallback to {SnapMode.GRID.value}"
            )
            snap_mode = SnapMode.GRID

        return snap_mode


settings_manager = SettingsManager()
