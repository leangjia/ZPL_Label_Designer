# -*- coding: utf-8 -*-
"""Undo/Redo команды для QUndoStack"""

from PySide6.QtGui import QUndoCommand
from utils.logger import logger


class AddElementCommand(QUndoCommand):
    """Команда додавання елемента"""
    
    def __init__(self, main_window, element, graphics_item):
        super().__init__("Add Element")
        self.main_window = main_window
        self.element = element
        self.graphics_item = graphics_item
        logger.debug(f"[UNDO-CMD] AddElementCommand created")
    
    def redo(self):
        """Виконати (додати елемент)"""
        logger.debug(f"[UNDO] REDO AddElement")
        self.main_window.canvas.scene.addItem(self.graphics_item)
        self.main_window.elements.append(self.element)
        self.main_window.graphics_items.append(self.graphics_item)
        logger.info(f"[UNDO] Element added")
    
    def undo(self):
        """Відмінити (видалити елемент)"""
        logger.debug(f"[UNDO] UNDO AddElement")
        self.main_window.canvas.scene.removeItem(self.graphics_item)
        self.main_window.elements.remove(self.element)
        self.main_window.graphics_items.remove(self.graphics_item)
        logger.info(f"[UNDO] Element removed")


class DeleteElementCommand(QUndoCommand):
    """Команда видалення елемента"""
    
    def __init__(self, main_window, element, graphics_item):
        super().__init__("Delete Element")
        self.main_window = main_window
        self.element = element
        self.graphics_item = graphics_item
        logger.debug(f"[UNDO-CMD] DeleteElementCommand created")
    
    def redo(self):
        """Виконати (видалити елемент)"""
        logger.debug(f"[UNDO] REDO DeleteElement")
        self.main_window.canvas.scene.removeItem(self.graphics_item)
        self.main_window.elements.remove(self.element)
        self.main_window.graphics_items.remove(self.graphics_item)
        logger.info(f"[UNDO] Element deleted")
    
    def undo(self):
        """Відмінити (додати елемент назад)"""
        logger.debug(f"[UNDO] UNDO DeleteElement")
        self.main_window.canvas.scene.addItem(self.graphics_item)
        self.main_window.elements.append(self.element)
        self.main_window.graphics_items.append(self.graphics_item)
        logger.info(f"[UNDO] Element restored")


class MoveElementCommand(QUndoCommand):
    """Команда переміщення елемента"""
    
    def __init__(self, element, graphics_item, old_x, old_y, new_x, new_y):
        super().__init__("Move Element")
        self.element = element
        self.graphics_item = graphics_item
        self.old_x = old_x
        self.old_y = old_y
        self.new_x = new_x
        self.new_y = new_y
        logger.debug(f"[UNDO-CMD] MoveElementCommand: ({old_x:.2f}, {old_y:.2f}) -> ({new_x:.2f}, {new_y:.2f})")
    
    def redo(self):
        """Виконати (перемістити до нової позиції)"""
        logger.debug(f"[UNDO] REDO MoveElement to ({self.new_x:.2f}, {self.new_y:.2f})")
        self.element.config.x = self.new_x
        self.element.config.y = self.new_y
        
        dpi = 203
        x_px = self.new_x * dpi / 25.4
        y_px = self.new_y * dpi / 25.4
        self.graphics_item.setPos(x_px, y_px)
        logger.info(f"[UNDO] Element moved to ({self.new_x}, {self.new_y})")
    
    def undo(self):
        """Відмінити (повернути до старої позиції)"""
        logger.debug(f"[UNDO] UNDO MoveElement to ({self.old_x:.2f}, {self.old_y:.2f})")
        self.element.config.x = self.old_x
        self.element.config.y = self.old_y
        
        dpi = 203
        x_px = self.old_x * dpi / 25.4
        y_px = self.old_y * dpi / 25.4
        self.graphics_item.setPos(x_px, y_px)
        logger.info(f"[UNDO] Element moved back to ({self.old_x}, {self.old_y})")


class ChangePropertyCommand(QUndoCommand):
    """Команда зміни властивості елемента"""
    
    def __init__(self, element, graphics_item, property_name, old_value, new_value):
        super().__init__(f"Change {property_name}")
        self.element = element
        self.graphics_item = graphics_item
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        logger.debug(f"[UNDO-CMD] ChangePropertyCommand: {property_name} = {old_value} -> {new_value}")
    
    def redo(self):
        """Виконати (встановити нове значення)"""
        logger.debug(f"[UNDO] REDO ChangeProperty: {self.property_name} = {self.new_value}")
        setattr(self.element.config, self.property_name, self.new_value)
        self.graphics_item.update_from_element()
        logger.info(f"[UNDO] Property {self.property_name} changed to {self.new_value}")
    
    def undo(self):
        """Відмінити (повернути старе значення)"""
        logger.debug(f"[UNDO] UNDO ChangeProperty: {self.property_name} = {self.old_value}")
        setattr(self.element.config, self.property_name, self.old_value)
        self.graphics_item.update_from_element()
        logger.info(f"[UNDO] Property {self.property_name} restored to {self.old_value}")
