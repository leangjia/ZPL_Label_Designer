# -*- coding: utf-8 -*-
"""选择与事件处理混入类"""

from PySide6.QtWidgets import QToolTip
from PySide6.QtCore import QEvent
from PySide6.QtGui import QCursor
from utils.logger import logger


class SelectionMixin:
    """选择与事件处理"""

    def _on_selection_changed(self):
        """处理选择变化"""
        try:
            selected = self.canvas.scene.selectedItems()
        except RuntimeError:
            # 应用程序关闭时场景已被删除
            return

        if len(selected) == 1:
            graphics_item = selected[0]

            if hasattr(graphics_item, 'element'):
                element = graphics_item.element
                self.selected_item = graphics_item
                self.property_panel.set_element(element, graphics_item)
                self._highlight_element_bounds(graphics_item)
                logger.info(f"已选择位于 ({element.config.x:.1f}, {element.config.y:.1f}) 的元素")

        elif len(selected) > 1:
            logger.debug(f"[多选] 已选择 {len(selected)} 个项目")
            self.selected_item = None
            self.property_panel.set_element(None, None)
            self.h_ruler.clear_highlight()
            self.v_ruler.clear_highlight()
            logger.info(f"多选: {len(selected)} 个元素")

        else:
            self.h_ruler.clear_highlight()
            self.v_ruler.clear_highlight()
            self.selected_item = None
            self.property_panel.set_element(None, None)
            logger.debug("选择已清除")

    def _highlight_element_bounds(self, item):
        """在标尺上高亮显示元素边界"""
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

            logger.debug(f"[边界更新] 位置: x={x:.2f}mm, y={y:.2f}mm")
            logger.debug(f"[边界更新] 尺寸: 宽度={width_mm:.2f}mm, 高度={height_mm:.2f}mm")

            self.h_ruler.highlight_bounds(x, width_mm)
            self.v_ruler.highlight_bounds(y, height_mm)
            logger.info(f"已高亮边界: X={x}mm 宽度={width_mm:.1f}mm, Y={y}mm 高度={height_mm:.1f}mm")

    def _update_ruler_cursor(self, x_mm, y_mm):
        """更新标尺上的光标标记"""
        self.h_ruler.update_cursor_position(x_mm)
        self.v_ruler.update_cursor_position(y_mm)
        self._show_cursor_tooltip(x_mm, y_mm)

    def _show_cursor_tooltip(self, x_mm, y_mm):
        """显示坐标提示框"""
        tooltip_text = f"X: {x_mm:.1f} mm\nY: {y_mm:.1f} mm"
        QToolTip.showText(QCursor.pos(), tooltip_text)

    def _delete_selected(self):
        """删除选中的元素或元素组"""
        # 获取所有选中的项目
        selected = self.canvas.scene.selectedItems()

        if not selected:
            logger.debug("[删除] 没有选中的项目")
            return

        logger.debug(f"[删除] 正在删除 {len(selected)} 个项目")

        # 关键：在 removeItem 之前保存列表！
        # removeItem() 会触发 selectionChanged 从而改变 selected
        items_to_delete = []
        for item in selected:
            if hasattr(item, 'element'):
                items_to_delete.append((item, item.element))
                logger.debug(
                    f"[删除] 标记: {item.__class__.__name__} 位于 ({item.element.config.x:.2f}, {item.element.config.y:.2f})mm")

        # 删除所有项目
        for item, element in items_to_delete:
            # removeItem 会触发 selectionChanged
            self.canvas.scene.removeItem(item)

            # 使用保存的变量！
            if element in self.elements:
                self.elements.remove(element)
                logger.debug(f"[删除] 已从列表中移除元素")

            if item in self.graphics_items:
                self.graphics_items.remove(item)
                logger.debug(f"[删除] 已从列表中移除图形项目")

        # 清除属性面板
        self.property_panel.set_element(None, None)

        logger.info(f"已删除 {len(items_to_delete)} 个元素。剩余: {len(self.elements)} 个")

    def eventFilter(self, obj, event):
        """处理画布和场景事件"""
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
                    logger.debug(f"[拖拽开始] 位置: ({self.drag_start_pos[0]:.2f}, {self.drag_start_pos[1]:.2f})")
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
                        logger.debug(f"[智能参考线] 对齐到: ({snap_pos[0]:.2f}, {snap_pos[1]:.2f})")

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
                        logger.debug(f"[移动命令] 已添加到撤销栈")

                    self.drag_start_pos = None

        return super().eventFilter(obj, event)