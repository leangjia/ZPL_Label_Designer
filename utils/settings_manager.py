# -*- coding: utf-8 -*-
"""设置管理器 - 用于保存用户设置"""

from PySide6.QtCore import QSettings

from utils.logger import logger
from config import SnapMode


class SettingsManager:
    """通过 QSettings 管理应用程序设置。"""

    def __init__(self):
        # Windows: HKEY_CURRENT_USER\Software\Anthropic\ZPL_Designer
        # Linux: ~/.config/Anthropic/ZPL_Designer.conf
        # macOS: ~/Library/Preferences/com.Anthropic.ZPL_Designer.plist
        self.settings = QSettings("Anthropic", "ZPL_Designer")
        logger.debug("[SETTINGS] 设置管理器已初始化")

    # ========== 网格设置 ==========

    def save_grid_settings(self, settings_dict):
        """保存网格设置。"""
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
        logger.debug(f"[SETTINGS] 网格设置已保存: {settings_dict}")

    def load_grid_settings(self):
        """加载网格设置。"""
        settings = {
            "size_x": self.settings.value("grid/size_x", defaultValue=1.0, type=float),
            "size_y": self.settings.value("grid/size_y", defaultValue=1.0, type=float),
            "offset_x": self.settings.value("grid/offset_x", defaultValue=0.0, type=float),
            "offset_y": self.settings.value("grid/offset_y", defaultValue=0.0, type=float),
            "show_gridlines": self.settings.value("grid/show_gridlines", defaultValue=True, type=bool),
            "snap_mode": self._load_snap_mode(),
        }

        logger.debug(f"[SETTINGS] 网格设置已加载: {settings}")
        return settings

    # ========== 工具栏设置 ==========

    def save_toolbar_settings(self, settings_dict):
        """保存工具栏设置。"""
        self.settings.setValue("toolbar/show_grid", settings_dict.get("show_grid", True))
        self.settings.setValue("toolbar/snap_to_grid", settings_dict.get("snap_to_grid", True))
        self.settings.setValue("toolbar/smart_guides", settings_dict.get("smart_guides", True))
        self.settings.setValue("toolbar/label_width", settings_dict.get("label_width", 28.0))
        self.settings.setValue("toolbar/label_height", settings_dict.get("label_height", 28.0))
        self.settings.setValue("toolbar/unit", settings_dict.get("unit", "mm"))

        self.settings.sync()
        logger.debug(f"[SETTINGS] 工具栏设置已保存: {settings_dict}")

    def load_toolbar_settings(self):
        """加载工具栏设置。"""
        settings = {
            "show_grid": self.settings.value("toolbar/show_grid", defaultValue=True, type=bool),
            "snap_to_grid": self.settings.value("toolbar/snap_to_grid", defaultValue=True, type=bool),
            "smart_guides": self.settings.value("toolbar/smart_guides", defaultValue=True, type=bool),
            "label_width": self.settings.value("toolbar/label_width", defaultValue=28.0, type=float),
            "label_height": self.settings.value("toolbar/label_height", defaultValue=28.0, type=float),
            "unit": self.settings.value("toolbar/unit", defaultValue="mm", type=str),
        }

        logger.debug(f"[SETTINGS] 工具栏设置已加载: {settings}")
        return settings

    def clear_all_settings(self):
        """清除所有设置（用于测试）。"""
        self.settings.clear()
        self.settings.sync()
        logger.debug("[SETTINGS] 所有设置已清除")

    def _load_snap_mode(self):
        """加载 SnapMode 的辅助方法。"""
        snap_mode_value = self.settings.value(
            "grid/snap_mode",
            defaultValue=SnapMode.GRID.value,
            type=str,
        )

        try:
            snap_mode = SnapMode(snap_mode_value)
        except ValueError:
            logger.warning(
                f"[SETTINGS] 未知的吸附模式 '{snap_mode_value}'，回退到 {SnapMode.GRID.value}"
            )
            snap_mode = SnapMode.GRID

        return snap_mode


settings_manager = SettingsManager()