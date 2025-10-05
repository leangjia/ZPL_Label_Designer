# -*- coding: utf-8 -*-
"""Mixin для обробки selection та events"""

from PySide6.QtWidgets import QToolTip
from PySide6.QtCore import QEvent
from PySide6.QtGui import QCursor
from utils.logger import logger


class SelectionMixin:
    """Selection & event handling"""
    
    def _on_selection_changed(self):
        """Обработка изменения выделения"""
        try:
            selected = self.canvas.scene.selectedItems()
        except RuntimeError:
            # Scene уже удален при закрытии приложения
            return
        
        if len(selected) == 1:
            graphics_item = selected[0]
            
            if hasattr(graphics_item, 'element'):
                element = graphics_item.element
                self.selected_item = graphics_item
                self.property_panel.set_element(element, graphics_item)
                self._highlight_element_bounds(graphics_item)
                logger.info(f"Selected element at ({element.config.x:.1f}, {element.config.y:.1f})")
        
        elif len(selected) > 1:
            logger.debug(f"[MULTI-SELECT] {len(selected)} items selected")
            self.selected_item = None
            self.property_panel.set_element(None, None)
            self.h_ruler.clear_highlight()
            self.v_ruler.clear_highlight()
            logger.info(f"Multi-select: {len(selected)} elements")
        
        else:
            self.h_ruler.clear_highlight()
            self.v_ruler.clear_highlight()
            self.selected_item = None
            self.property_panel.set_element(None, None)
            logger.debug("Selection cleared")
    
    def _highlight_element_bounds(self, item):
        """Підсвітити межі елемента на лінейках"""
        if hasattr(item, 'element'):
            element = item.element
            x = element.config.x
            y = element.config.y
            
            bounds = item.boundingRect()
            width_px = bounds.width()
            height_px = bounds.height()
            
            dpi = 203
            width_mm = width_px * 25.4 / dpi
            height_mm = height_px * 25.4 / dpi
            
            logger.debug(f"[BOUNDS] Element at: x={x:.2f}mm, y={y:.2f}mm")
            logger.debug(f"[BOUNDS] Size: width={width_mm:.2f}mm, height={height_mm:.2f}mm")
            
            self.h_ruler.highlight_bounds(x, width_mm)
            self.v_ruler.highlight_bounds(y, height_mm)
            logger.info(f"Highlighted bounds: X={x}mm W={width_mm:.1f}mm, Y={y}mm H={height_mm:.1f}mm")
    
    def _update_ruler_cursor(self, x_mm, y_mm):
        """Оновити cursor markers на лінейках"""
        self.h_ruler.update_cursor_position(x_mm)
        self.v_ruler.update_cursor_position(y_mm)
        self._show_cursor_tooltip(x_mm, y_mm)
    
    def _show_cursor_tooltip(self, x_mm, y_mm):
        """Показати tooltip з координатами"""
        tooltip_text = f"X: {x_mm:.1f} mm\nY: {y_mm:.1f} mm"
        QToolTip.showText(QCursor.pos(), tooltip_text)
    
    def eventFilter(self, obj, event):
        """Обробка подій canvas та scene"""
        if obj == self.canvas.viewport():
            if event.type() == QEvent.Leave:
                self.h_ruler.hide_cursor()
                self.v_ruler.hide_cursor()
            elif event.type() == QEvent.Wheel:
                return False
        
        elif obj == self.canvas.scene:
            if event.type() == QEvent.GraphicsSceneMousePress:
                items = self.canvas.scene.items(event.scenePos())
                item = items[0] if items else None
                
                if item and hasattr(item, 'element'):
                    self.drag_start_pos = (item.element.config.x, item.element.config.y)
                    logger.debug(f"[DRAG-START] Pos: ({self.drag_start_pos[0]:.2f}, {self.drag_start_pos[1]:.2f})")
                else:
                    self.drag_start_pos = None
            
            elif event.type() == QEvent.GraphicsSceneMouseMove:
                items = self.canvas.scene.items(event.scenePos())
                dragged_item = items[0] if items else None
                
                if self.guides_enabled and dragged_item and hasattr(dragged_item, 'element'):
                    snap_pos = self.smart_guides.check_alignment(
                        dragged_item,
                        self.graphics_items,
                        dpi=203
                    )
                    if snap_pos:
                        logger.debug(f"[SMART-GUIDE] Snap to: ({snap_pos[0]:.2f}, {snap_pos[1]:.2f})")
            
            elif event.type() == QEvent.GraphicsSceneMouseRelease:
                self.smart_guides.clear()
                
                if self.drag_start_pos and self.selected_item:
                    from core.undo_commands import MoveElementCommand
                    element = self.selected_item.element
                    end_pos = (element.config.x, element.config.y)
                    
                    if self.drag_start_pos != end_pos:
                        command = MoveElementCommand(
                            element,
                            self.drag_start_pos,
                            end_pos,
                            self.selected_item
                        )
                        self.undo_stack.push(command)
                        logger.debug(f"[MOVE-CMD] Added to undo stack")
                    
                    self.drag_start_pos = None
        
        return super().eventFilter(obj, event)
