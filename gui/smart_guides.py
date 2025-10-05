# -*- coding: utf-8 -*-
"""Smart Guides - alignment helpers для canvas"""

from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QColor
from utils.logger import logger


class SmartGuides:
    """Управління smart guides (alignment helpers)"""
    
    SNAP_THRESHOLD = 2.0  # мм - поріг для показу guide
    
    def __init__(self, scene):
        self.scene = scene
        self.guides = []  # Список QGraphicsLineItem
        self.enabled = True
        logger.debug("[GUIDES] SmartGuides initialized")
    
    def clear_guides(self):
        """Очистити всі guides"""
        for guide in self.guides:
            self.scene.removeItem(guide)
        self.guides.clear()
        logger.debug("[GUIDES] Cleared all guides")
    
    def check_alignment(self, dragged_item, all_items, dpi=203):
        """Перевірити вирівнювання з іншими елементами"""
        if not self.enabled:
            return None
        
        self.clear_guides()
        
        if not hasattr(dragged_item, 'element'):
            return None
        
        dragged_element = dragged_item.element
        dragged_x = dragged_element.config.x
        dragged_y = dragged_element.config.y
        
        # Межі dragged item
        dragged_bounds = dragged_item.boundingRect()
        dragged_width_mm = dragged_bounds.width() * 25.4 / dpi
        dragged_height_mm = dragged_bounds.height() * 25.4 / dpi
        
        dragged_center_x = dragged_x + dragged_width_mm / 2
        dragged_center_y = dragged_y + dragged_height_mm / 2
        dragged_right = dragged_x + dragged_width_mm
        dragged_bottom = dragged_y + dragged_height_mm
        
        logger.debug(f"[GUIDES] Check alignment for: x={dragged_x:.2f}, y={dragged_y:.2f}, "
                    f"center=({dragged_center_x:.2f}, {dragged_center_y:.2f})")
        
        snap_x = None
        snap_y = None
        
        for item in all_items:
            if item == dragged_item or not hasattr(item, 'element'):
                continue
            
            element = item.element
            x = element.config.x
            y = element.config.y
            
            bounds = item.boundingRect()
            width_mm = bounds.width() * 25.4 / dpi
            height_mm = bounds.height() * 25.4 / dpi
            
            center_x = x + width_mm / 2
            center_y = y + height_mm / 2
            right = x + width_mm
            bottom = y + height_mm
            
            # Перевірка вирівнювання по X
            # Left edges
            if abs(dragged_x - x) < self.SNAP_THRESHOLD:
                snap_x = x
                self._draw_vertical_guide(x, dpi)
                logger.debug(f"[GUIDES] Vertical guide at x={x:.2f}mm (left edges)")
            
            # Center X
            elif abs(dragged_center_x - center_x) < self.SNAP_THRESHOLD:
                snap_x = center_x - dragged_width_mm / 2
                self._draw_vertical_guide(center_x, dpi)
                logger.debug(f"[GUIDES] Vertical guide at x={center_x:.2f}mm (centers)")
            
            # Right edges
            elif abs(dragged_right - right) < self.SNAP_THRESHOLD:
                snap_x = right - dragged_width_mm
                self._draw_vertical_guide(right, dpi)
                logger.debug(f"[GUIDES] Vertical guide at x={right:.2f}mm (right edges)")
            
            # Перевірка вирівнювання по Y
            # Top edges
            if abs(dragged_y - y) < self.SNAP_THRESHOLD:
                snap_y = y
                self._draw_horizontal_guide(y, dpi)
                logger.debug(f"[GUIDES] Horizontal guide at y={y:.2f}mm (top edges)")
            
            # Center Y
            elif abs(dragged_center_y - center_y) < self.SNAP_THRESHOLD:
                snap_y = center_y - dragged_height_mm / 2
                self._draw_horizontal_guide(center_y, dpi)
                logger.debug(f"[GUIDES] Horizontal guide at y={center_y:.2f}mm (centers)")
            
            # Bottom edges
            elif abs(dragged_bottom - bottom) < self.SNAP_THRESHOLD:
                snap_y = bottom - dragged_height_mm
                self._draw_horizontal_guide(bottom, dpi)
                logger.debug(f"[GUIDES] Horizontal guide at y={bottom:.2f}mm (bottom edges)")
        
        if snap_x is not None or snap_y is not None:
            logger.debug(f"[GUIDES] Snap detected: x={snap_x}, y={snap_y}")
            return (snap_x, snap_y)
        
        return None
    
    def _draw_vertical_guide(self, x_mm, dpi):
        """Малювати вертикальну guide лінію"""
        x_px = x_mm * dpi / 25.4
        
        # Створити лінію від top до bottom canvas
        line = QGraphicsLineItem(x_px, 0, x_px, 1000)
        
        # Червона пунктирна лінія
        pen = QPen(QColor(255, 0, 0), 1, Qt.DashLine)
        line.setPen(pen)
        
        # Не селектабельна, над елементами
        line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        line.setZValue(1000)
        
        self.scene.addItem(line)
        self.guides.append(line)
        
        logger.debug(f"[GUIDES] Drew vertical guide at {x_px:.1f}px")
    
    def _draw_horizontal_guide(self, y_mm, dpi):
        """Малювати горизонтальну guide лінію"""
        y_px = y_mm * dpi / 25.4
        
        # Створити лінію від left до right canvas
        line = QGraphicsLineItem(0, y_px, 1000, y_px)
        
        # Червона пунктирна лінія
        pen = QPen(QColor(255, 0, 0), 1, Qt.DashLine)
        line.setPen(pen)
        
        # Не селектабельна, над елементами
        line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        line.setZValue(1000)
        
        self.scene.addItem(line)
        self.guides.append(line)
        
        logger.debug(f"[GUIDES] Drew horizontal guide at {y_px:.1f}px")
    
    def set_enabled(self, enabled):
        """Увімкнути/вимкнути smart guides"""
        self.enabled = enabled
        if not enabled:
            self.clear_guides()
        logger.debug(f"[GUIDES] Enabled: {enabled}")
