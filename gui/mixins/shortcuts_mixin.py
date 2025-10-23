# -*- coding: utf-8 -*-
"""键盘快捷键混入类"""

from PySide6.QtWidgets import QCheckBox
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt
from utils.logger import logger


class ShortcutsMixin:
    """键盘快捷键设置和处理程序"""

    def _setup_shortcuts(self):
        """设置键盘快捷键"""
        # 放大
        zoom_in = QShortcut(QKeySequence("Ctrl++"), self)
        zoom_in.activated.connect(self.canvas.zoom_in)

        # 放大 (替代按键)
        zoom_in2 = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in2.activated.connect(self.canvas.zoom_in)

        # 缩小
        zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out.activated.connect(self.canvas.zoom_out)

        # 重置缩放
        zoom_reset = QShortcut(QKeySequence("Ctrl+0"), self)
        zoom_reset.activated.connect(self.canvas.reset_zoom)

        # 网格显示切换
        grid_toggle = QShortcut(QKeySequence("Ctrl+Shift+G"), self)
        grid_toggle.activated.connect(
            lambda: self.grid_checkbox.toggle()
            if hasattr(self, "grid_checkbox")
            else self._toggle_grid_visibility(
                0 if getattr(self, "grid_visible", True) else 2  # 0=未选中, 2=选中
            )
        )

        # 对齐切换
        snap_toggle = QShortcut(QKeySequence("Ctrl+G"), self)
        snap_toggle.activated.connect(
            lambda: self.snap_checkbox.toggle()
            if hasattr(self, "snap_checkbox")
            else self._toggle_snap(0 if self.snap_enabled else 2)
        )

        # 字体样式 - 粗体
        bold_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_shortcut.activated.connect(self._toggle_bold)

        # 字体样式 - 下划线
        underline_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        underline_shortcut.activated.connect(self._toggle_underline)

        # 粗体切换
        bold_toggle = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_toggle.activated.connect(self._toggle_bold)

        # 下划线切换
        underline_toggle = QShortcut(QKeySequence("Ctrl+U"), self)
        underline_toggle.activated.connect(self._toggle_underline)

        # 删除快捷键
        delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        delete_shortcut.activated.connect(self._delete_selected)
        logger.debug("[SHORTCUT] 删除快捷键已创建")

        # 退格快捷键
        backspace_shortcut = QShortcut(QKeySequence(Qt.Key_Backspace), self)
        backspace_shortcut.activated.connect(self._delete_selected)
        logger.debug("[SHORTCUT] 退格快捷键已创建")

        logger.debug("缩放快捷键: Ctrl+加号, Ctrl+减号, Ctrl+0")
        logger.debug("网格显示快捷键: Ctrl+Shift+G")
        logger.debug("对齐快捷键: Ctrl+G")
        logger.debug("删除快捷键: Delete, Backspace")

    def _toggle_guides(self, state):
        """智能参考线切换器"""
        self.guides_enabled = (state == 2)
        self.smart_guides.set_enabled(self.guides_enabled)
        logger.debug(f"[GUIDES-TOGGLE] 已启用: {self.guides_enabled}")
        if hasattr(self, "_persist_toolbar_settings"):
            self._persist_toolbar_settings()

    def _create_snap_toggle(self):
        """创建网格显示、对齐和智能参考线的切换控件"""
        self.toolbar.addSeparator()

        # 网格显示复选框
        self.grid_checkbox = QCheckBox("显示网格")
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.stateChanged.connect(self._toggle_grid_visibility)
        self.toolbar.addWidget(self.grid_checkbox)

        # 对齐复选框
        self.snap_checkbox = QCheckBox("对齐网格")
        self.snap_checkbox.setChecked(True)
        self.snap_checkbox.stateChanged.connect(self._toggle_snap)
        self.toolbar.addWidget(self.snap_checkbox)

        # 智能参考线复选框
        self.guides_checkbox = QCheckBox("智能参考线")
        self.guides_checkbox.setChecked(True)
        self.guides_checkbox.stateChanged.connect(self._toggle_guides)
        self.toolbar.addWidget(self.guides_checkbox)

        self.grid_visible = True

        logger.info("已创建显示网格、对齐网格和智能参考线切换控件")
        logger.debug("[CREATE-SNAP-TOGGLE] 复选框已创建，等待 _apply_persisted_toolbar_settings()")

    def _toggle_grid_visibility(self, state):
        """网格显示切换器"""
        self.grid_visible = (state == 2)  # QCheckBox 发送 int: 0=未选中, 2=选中

        if hasattr(self, "canvas") and hasattr(self.canvas, "set_grid_visible"):
            self.canvas.set_grid_visible(self.grid_visible)
            logger.debug(f"[GRID-TOGGLE] 可见: {self.grid_visible}")
        else:
            logger.warning("画布不支持 set_grid_visible")

        if hasattr(self, "_persist_toolbar_settings"):
            self._persist_toolbar_settings()

    def _toggle_snap(self, state):
        """启用/禁用对齐"""
        # state 是 int: 0=未选中, 2=选中
        self.snap_enabled = (state == 2)  # Qt.Checked = 2

        # 更新所有元素
        for item in self.graphics_items:
            if hasattr(item, 'snap_enabled'):
                item.snap_enabled = self.snap_enabled

        logger.info(f"对齐网格: {'开启' if self.snap_enabled else '关闭'} (元素数量: {len(self.graphics_items)})")
        if hasattr(self, "_persist_toolbar_settings"):
            self._persist_toolbar_settings()

    def _toggle_bold(self):
        """切换选中元素的粗体样式"""
        if self.selected_item and hasattr(self.selected_item, 'element'):
            element = self.selected_item.element

            if hasattr(element, 'bold'):
                element.bold = not element.bold

                # 更新图形元素
                if hasattr(self.selected_item, 'update_display'):
                    self.selected_item.update_display()

                # 更新属性面板复选框
                if self.property_panel.current_element == element:
                    self.property_panel.bold_checkbox.blockSignals(True)
                    self.property_panel.bold_checkbox.setChecked(element.bold)
                    self.property_panel.bold_checkbox.blockSignals(False)

                logger.debug(f"[SHORTCUT] 粗体已切换: {element.bold}")

    def _toggle_underline(self):
        """切换选中元素的下划线样式"""
        if self.selected_item and hasattr(self.selected_item, 'element'):
            element = self.selected_item.element

            if hasattr(element, 'underline'):
                element.underline = not element.underline

                # 更新图形元素
                if hasattr(self.selected_item, 'update_display'):
                    self.selected_item.update_display()

                # 更新属性面板复选框
                if self.property_panel.current_element == element:
                    self.property_panel.underline_checkbox.blockSignals(True)
                    self.property_panel.underline_checkbox.setChecked(element.underline)
                    self.property_panel.underline_checkbox.blockSignals(False)

                logger.debug(f"[SHORTCUT] 下划线已切换: {element.underline}")

    def keyPressEvent(self, event):
        """键盘快捷键处理"""
        modifiers = event.modifiers()
        key = event.key()

        # === 缩放 ===
        if modifiers == Qt.ControlModifier:
            if key in (Qt.Key_Plus, Qt.Key_Equal):
                logger.debug("[SHORTCUT] Ctrl+加号 - 放大")
                self.canvas.zoom_in()
            elif key == Qt.Key_Minus:
                logger.debug("[SHORTCUT] Ctrl+减号 - 缩小")
                self.canvas.zoom_out()
            elif key == Qt.Key_0:
                logger.debug("[SHORTCUT] Ctrl+0 - 重置缩放")
                self.canvas.reset_zoom()
            # === 对齐 ===
            elif key == Qt.Key_G:
                logger.debug("[SHORTCUT] Ctrl+G - 切换对齐")
                if hasattr(self, "snap_checkbox"):
                    self.snap_checkbox.toggle()
                else:
                    self.snap_enabled = not self.snap_enabled
                    self._toggle_snap(Qt.Checked if self.snap_enabled else Qt.Unchecked)
            # === 剪贴板 ===
            elif key == Qt.Key_C:
                logger.debug("[SHORTCUT] Ctrl+C - 复制")
                self._copy_selected()
            elif key == Qt.Key_V:
                logger.debug("[SHORTCUT] Ctrl+V - 粘贴")
                self._paste_from_clipboard()
            elif key == Qt.Key_D:
                logger.debug("[SHORTCUT] Ctrl+D - 复制")
                self._duplicate_selected()
            # === 撤销/重做 ===
            elif key == Qt.Key_Z:
                logger.debug("[SHORTCUT] Ctrl+Z - 撤销")
                self._undo()
            elif key == Qt.Key_Y:
                logger.debug("[SHORTCUT] Ctrl+Y - 重做")
                self._redo()

        # === 删除 ===
        elif key in (Qt.Key_Delete, Qt.Key_Backspace):
            logger.debug(f"[SHORTCUT] {event.key()} - 删除元素")
            self._delete_selected()

        # === 精确移动 (Shift + 方向键) ===
        elif modifiers == Qt.ShiftModifier:
            if key == Qt.Key_Left:
                logger.debug("[SHORTCUT] Shift+左 - 向左移动 -0.1mm")
                self._move_selected(-0.1, 0)
            elif key == Qt.Key_Right:
                logger.debug("[SHORTCUT] Shift+右 - 向右移动 +0.1mm")
                self._move_selected(0.1, 0)
            elif key == Qt.Key_Up:
                logger.debug("[SHORTCUT] Shift+上 - 向上移动 -0.1mm")
                self._move_selected(0, -0.1)
            elif key == Qt.Key_Down:
                logger.debug("[SHORTCUT] Shift+下 - 向下移动 +0.1mm")
                self._move_selected(0, 0.1)

        # === 正常移动 (方向键) ===
        elif modifiers == Qt.NoModifier:
            if key == Qt.Key_Left:
                logger.debug("[SHORTCUT] 左 - 向左移动 -1mm")
                self._move_selected(-1, 0)
            elif key == Qt.Key_Right:
                logger.debug("[SHORTCUT] 右 - 向右移动 +1mm")
                self._move_selected(1, 0)
            elif key == Qt.Key_Up:
                logger.debug("[SHORTCUT] 上 - 向上移动 -1mm")
                self._move_selected(0, -1)
            elif key == Qt.Key_Down:
                logger.debug("[SHORTCUT] 下 - 向下移动 +1mm")
                self._move_selected(0, 1)

        super().keyPressEvent(event)