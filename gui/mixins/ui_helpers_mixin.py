# -*- coding: utf-8 -*-
"""Mixin для UI helper методів"""

from PySide6.QtWidgets import QMenu
from utils.logger import logger
from core.undo_commands import DeleteElementCommand


class UIHelpersMixin:
    """UI helper methods"""
    
    def _undo(self):
        """Отменить последнюю операцию"""
        if self.undo_stack.canUndo():
            logger.debug(f"[UNDO-ACTION] Undo: {self.undo_stack.undoText()}")
            self.undo_stack.undo()
        else:
            logger.debug(f"[UNDO-ACTION] Nothing to undo")
    
    def _redo(self):
        """Повторить отмененную операцию"""
        if self.undo_stack.canRedo():
            logger.debug(f"[UNDO-ACTION] Redo: {self.undo_stack.redoText()}")
            self.undo_stack.redo()
        else:
            logger.debug(f"[UNDO-ACTION] Nothing to redo")
    def _bring_to_front(self):
        """Перемістити на передній план (z-order)"""
        if self.selected_item:
            max_z = max([item.zValue() for item in self.graphics_items], default=0)
            self.selected_item.setZValue(max_z + 1)
            logger.debug(f"[Z-ORDER] Bring to front: z={max_z + 1}")
            logger.info(f"Element brought to front")
    
    def _send_to_back(self):
        """Перемістити на задній план (z-order)"""
        if self.selected_item:
            min_z = min([item.zValue() for item in self.graphics_items], default=0)
            self.selected_item.setZValue(min_z - 1)
            logger.debug(f"[Z-ORDER] Send to back: z={min_z - 1}")
            logger.info(f"Element sent to back")
    
    def _show_context_menu(self, item, global_pos):
        """Показати context menu"""
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        if item:  # Item context menu
            logger.debug(f"[CONTEXT-MENU] Creating item menu")
            
            copy_action = menu.addAction("Copy (Ctrl+C)")
            copy_action.triggered.connect(self._copy_selected)
            
            duplicate_action = menu.addAction("Duplicate (Ctrl+D)")
            duplicate_action.triggered.connect(self._duplicate_selected)
            
            menu.addSeparator()
            
            front_action = menu.addAction("Bring to Front")
            front_action.triggered.connect(self._bring_to_front)
            
            back_action = menu.addAction("Send to Back")
            back_action.triggered.connect(self._send_to_back)
            
            menu.addSeparator()
            
            delete_action = menu.addAction("Delete (Del)")
            delete_action.triggered.connect(self._delete_selected)
        else:  # Canvas context menu
            logger.debug(f"[CONTEXT-MENU] Creating canvas menu")
            
            paste_action = menu.addAction("Paste (Ctrl+V)")
            paste_action.triggered.connect(self._paste_from_clipboard)
            paste_action.setEnabled(self.clipboard_element is not None)
        
        logger.debug(f"[CONTEXT-MENU] Show at: {global_pos}")
        menu.exec(global_pos)
    
    def _delete_selected(self):
        """Видалити виділені елементи (підтримка multi-select)"""
        selected = self.canvas.scene.selectedItems()
        
        if len(selected) > 1:
            # Групове видалення
            logger.debug(f"[DELETE-GROUP] Deleting {len(selected)} items")
            
            for item in selected:
                if hasattr(item, 'element'):
                    element = item.element
                    command = DeleteElementCommand(self, element, item)
                    self.undo_stack.push(command)
            
            # Очистити UI
            self.selected_item = None
            self.h_ruler.clear_highlight()
            self.v_ruler.clear_highlight()
            self.property_panel.set_element(None, None)
            logger.info(f"Deleted {len(selected)} elements")
        
        elif self.selected_item:
            # Одиночне видалення
            # Зберегти ПЕРЕД removeItem (race condition!)
            item_to_delete = self.selected_item
            element_to_delete = item_to_delete.element if hasattr(item_to_delete, 'element') else None
            
            if element_to_delete:
                logger.debug(f"[DELETE] Creating DeleteCommand")
                command = DeleteElementCommand(self, element_to_delete, item_to_delete)
                self.undo_stack.push(command)
                
                # Очистити UI
                self.selected_item = None
                self.h_ruler.clear_highlight()
                self.v_ruler.clear_highlight()
                self.property_panel.set_element(None, None)
                logger.debug(f"[DELETE] UI cleared")
