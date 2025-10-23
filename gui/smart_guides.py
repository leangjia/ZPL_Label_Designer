# -*- coding: utf-8 -*-
"""智能参考线 - 画布对齐辅助工具"""

from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QColor
from utils.logger import logger


class SmartGuides:
    """管理智能参考线（对齐辅助工具）"""

    SNAP_THRESHOLD = 2.0  # 毫米 - 显示参考线的阈值

    def __init__(self, scene):
        self.scene = scene
        self.guides = []  # QGraphicsLineItem 列表
        self.enabled = True
        logger.debug("[GUIDES] 智能参考线已初始化")

    def clear_guides(self):
        """清除所有参考线"""
        for guide in self.guides:
            self.scene.removeItem(guide)
        self.guides.clear()
        logger.debug("[GUIDES] 已清除所有参考线")

    def check_alignment(self, dragged_item, all_items, dpi=203):
        """检查与其他元素的对齐情况"""
        if not self.enabled:
            return None

        self.clear_guides()

        if not hasattr(dragged_item, 'element'):
            return None

        dragged_element = dragged_item.element
        dragged_x = dragged_element.config.x
        dragged_y = dragged_element.config.y

        # 拖拽元素的边界
        dragged_bounds = dragged_item.boundingRect()
        dragged_width_mm = dragged_bounds.width() * 25.4 / dpi
        dragged_height_mm = dragged_bounds.height() * 25.4 / dpi

        dragged_center_x = dragged_x + dragged_width_mm / 2
        dragged_center_y = dragged_y + dragged_height_mm / 2
        dragged_right = dragged_x + dragged_width_mm
        dragged_bottom = dragged_y + dragged_height_mm

        logger.debug(f"[GUIDES] 检查对齐: x={dragged_x:.2f}, y={dragged_y:.2f}, "
                     f"中心=({dragged_center_x:.2f}, {dragged_center_y:.2f})")

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

            # 检查 X 轴对齐
            # 左边缘
            if abs(dragged_x - x) < self.SNAP_THRESHOLD:
                snap_x = x
                self._draw_vertical_guide(x, dpi)
                logger.debug(f"[GUIDES] 垂直参考线在 x={x:.2f}mm (左边缘)")

            # X 中心
            elif abs(dragged_center_x - center_x) < self.SNAP_THRESHOLD:
                snap_x = center_x - dragged_width_mm / 2
                self._draw_vertical_guide(center_x, dpi)
                logger.debug(f"[GUIDES] 垂直参考线在 x={center_x:.2f}mm (中心)")

            # 右边缘
            elif abs(dragged_right - right) < self.SNAP_THRESHOLD:
                snap_x = right - dragged_width_mm
                self._draw_vertical_guide(right, dpi)
                logger.debug(f"[GUIDES] 垂直参考线在 x={right:.2f}mm (右边缘)")

            # 检查 Y 轴对齐
            # 上边缘
            if abs(dragged_y - y) < self.SNAP_THRESHOLD:
                snap_y = y
                self._draw_horizontal_guide(y, dpi)
                logger.debug(f"[GUIDES] 水平参考线在 y={y:.2f}mm (上边缘)")

            # Y 中心
            elif abs(dragged_center_y - center_y) < self.SNAP_THRESHOLD:
                snap_y = center_y - dragged_height_mm / 2
                self._draw_horizontal_guide(center_y, dpi)
                logger.debug(f"[GUIDES] 水平参考线在 y={center_y:.2f}mm (中心)")

            # 下边缘
            elif abs(dragged_bottom - bottom) < self.SNAP_THRESHOLD:
                snap_y = bottom - dragged_height_mm
                self._draw_horizontal_guide(bottom, dpi)
                logger.debug(f"[GUIDES] 水平参考线在 y={bottom:.2f}mm (下边缘)")

        if snap_x is not None or snap_y is not None:
            logger.debug(f"[GUIDES] 检测到吸附: x={snap_x}, y={snap_y}")
            return (snap_x, snap_y)

        return None

    def _draw_vertical_guide(self, x_mm, dpi):
        """绘制垂直参考线"""
        x_px = x_mm * dpi / 25.4

        # 创建从画布顶部到底部的线条
        line = QGraphicsLineItem(x_px, 0, x_px, 1000)

        # 红色虚线
        pen = QPen(QColor(255, 0, 0), 1, Qt.DashLine)
        line.setPen(pen)

        # 不可选择，在元素上方
        line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        line.setZValue(1000)

        self.scene.addItem(line)
        self.guides.append(line)

        logger.debug(f"[GUIDES] 绘制垂直参考线在 {x_px:.1f}px")

    def _draw_horizontal_guide(self, y_mm, dpi):
        """绘制水平参考线"""
        y_px = y_mm * dpi / 25.4

        # 创建从画布左侧到右侧的线条
        line = QGraphicsLineItem(0, y_px, 1000, y_px)

        # 红色虚线
        pen = QPen(QColor(255, 0, 0), 1, Qt.DashLine)
        line.setPen(pen)

        # 不可选择，在元素上方
        line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        line.setZValue(1000)

        self.scene.addItem(line)
        self.guides.append(line)

        logger.debug(f"[GUIDES] 绘制水平参考线在 {y_px:.1f}px")

    def set_enabled(self, enabled):
        """启用/禁用智能参考线"""
        self.enabled = enabled
        if not enabled:
            self.clear_guides()
        logger.debug(f"[GUIDES] 启用状态: {enabled}")