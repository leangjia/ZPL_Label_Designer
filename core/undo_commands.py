# -*- coding: utf-8 -*-
"""用于 QUndoStack 的撤销/重做命令"""

from PySide6.QtGui import QUndoCommand
from utils.logger import logger


class AddElementCommand(QUndoCommand):
    """添加元素命令"""

    def __init__(self, main_window, element, graphics_item):
        super().__init__("添加元素")
        self.main_window = main_window
        self.element = element
        self.graphics_item = graphics_item
        logger.debug(f"[撤销命令] AddElementCommand 已创建")

    def redo(self):
        """执行（添加元素）"""
        logger.debug(f"[撤销] 重做 添加元素")
        self.main_window.canvas.scene.addItem(self.graphics_item)
        self.main_window.elements.append(self.element)
        self.main_window.graphics_items.append(self.graphics_item)
        logger.info(f"[撤销] 元素已添加")

    def undo(self):
        """撤销（删除元素）"""
        logger.debug(f"[撤销] 撤销 添加元素")
        self.main_window.canvas.scene.removeItem(self.graphics_item)
        self.main_window.elements.remove(self.element)
        self.main_window.graphics_items.remove(self.graphics_item)
        logger.info(f"[撤销] 元素已移除")


class DeleteElementCommand(QUndoCommand):
    """删除元素命令"""

    def __init__(self, main_window, element, graphics_item):
        super().__init__("删除元素")
        self.main_window = main_window
        self.element = element
        self.graphics_item = graphics_item
        logger.debug(f"[撤销命令] DeleteElementCommand 已创建")

    def redo(self):
        """执行（删除元素）"""
        logger.debug(f"[撤销] 重做 删除元素")
        self.main_window.canvas.scene.removeItem(self.graphics_item)
        self.main_window.elements.remove(self.element)
        self.main_window.graphics_items.remove(self.graphics_item)
        logger.info(f"[撤销] 元素已删除")

    def undo(self):
        """撤销（重新添加元素）"""
        logger.debug(f"[撤销] 撤销 删除元素")
        self.main_window.canvas.scene.addItem(self.graphics_item)
        self.main_window.elements.append(self.element)
        self.main_window.graphics_items.append(self.graphics_item)
        logger.info(f"[撤销] 元素已恢复")


class MoveElementCommand(QUndoCommand):
    """移动元素命令"""

    def __init__(self, element, graphics_item, old_x, old_y, new_x, new_y):
        super().__init__("移动元素")
        self.element = element
        self.graphics_item = graphics_item
        self.old_x = old_x
        self.old_y = old_y
        self.new_x = new_x
        self.new_y = new_y
        logger.debug(f"[撤销命令] MoveElementCommand: ({old_x:.2f}, {old_y:.2f}) -> ({new_x:.2f}, {new_y:.2f})")

    def redo(self):
        """执行（移动到新位置）"""
        logger.debug(f"[撤销] 重做 移动元素到 ({self.new_x:.2f}, {self.new_y:.2f})")
        self.element.config.x = self.new_x
        self.element.config.y = self.new_y

        dpi = 203
        x_px = self.new_x * dpi / 25.4
        y_px = self.new_y * dpi / 25.4
        self.graphics_item.setPos(x_px, y_px)
        logger.info(f"[撤销] 元素已移动到 ({self.new_x}, {self.new_y})")

    def undo(self):
        """撤销（返回到旧位置）"""
        logger.debug(f"[撤销] 撤销 移动元素到 ({self.old_x:.2f}, {self.old_y:.2f})")
        self.element.config.x = self.old_x
        self.element.config.y = self.old_y

        dpi = 203
        x_px = self.old_x * dpi / 25.4
        y_px = self.old_y * dpi / 25.4
        self.graphics_item.setPos(x_px, y_px)
        logger.info(f"[撤销] 元素已移回到 ({self.old_x}, {self.old_y})")


class ChangePropertyCommand(QUndoCommand):
    """更改元素属性命令"""

    def __init__(self, element, graphics_item, property_name, old_value, new_value):
        super().__init__(f"更改 {property_name}")
        self.element = element
        self.graphics_item = graphics_item
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        logger.debug(f"[撤销命令] ChangePropertyCommand: {property_name} = {old_value} -> {new_value}")

    def redo(self):
        """执行（设置新值）"""
        logger.debug(f"[撤销] 重做 更改属性: {self.property_name} = {self.new_value}")
        setattr(self.element.config, self.property_name, self.new_value)
        self.graphics_item.update_from_element()
        logger.info(f"[撤销] 属性 {self.property_name} 已更改为 {self.new_value}")

    def undo(self):
        """撤销（恢复旧值）"""
        logger.debug(f"[撤销] 撤销 更改属性: {self.property_name} = {self.old_value}")
        setattr(self.element.config, self.property_name, self.old_value)
        self.graphics_item.update_from_element()
        logger.info(f"[撤销] 属性 {self.property_name} 已恢复到 {self.old_value}")