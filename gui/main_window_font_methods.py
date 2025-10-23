# 临时文件包含新方法 - 待合并到 main_window.py

def _toggle_bold(self):
    """切换选中元素的粗体样式"""
    if self.selected_item and hasattr(self.selected_item, 'element'):
        element = self.selected_item.element

        if hasattr(element, 'bold'):
            element.bold = not element.bold

            # 更新图形项
            if hasattr(self.selected_item, 'update_display'):
                self.selected_item.update_display()

            # 更新属性面板复选框
            if self.property_panel.current_element == element:
                self.property_panel.bold_checkbox.blockSignals(True)
                self.property_panel.bold_checkbox.setChecked(element.bold)
                self.property_panel.bold_checkbox.blockSignals(False)

            logger.debug(f"[快捷键] 粗体已切换: {element.bold}")


def _toggle_underline(self):
    """切换选中元素的下划线样式"""
    if self.selected_item and hasattr(self.selected_item, 'element'):
        element = self.selected_item.element

        if hasattr(element, 'underline'):
            element.underline = not element.underline

            # 更新图形项
            if hasattr(self.selected_item, 'update_display'):
                self.selected_item.update_display()

            # 更新属性面板复选框
            if self.property_panel.current_element == element:
                self.property_panel.underline_checkbox.blockSignals(True)
                self.property_panel.underline_checkbox.setChecked(element.underline)
                self.property_panel.underline_checkbox.blockSignals(False)

            logger.debug(f"[快捷键] 下划线已切换: {element.underline}")

# 在 _setup_shortcuts() 中添加的快捷键：
#
# # 字体样式 - 粗体
# bold_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
# bold_shortcut.activated.connect(self._toggle_bold)
#
# # 字体样式 - 下划线
# underline_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
# underline_shortcut.activated.connect(self._toggle_underline)