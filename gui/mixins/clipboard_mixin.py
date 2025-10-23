# -*- coding: utf-8 -*-
"""剪贴板操作混入类"""

from utils.logger import logger
import copy


class ClipboardMixin:
    """复制/粘贴/复制/移动操作"""

    def _move_selected(self, dx_mm, dy_mm):
        """移动选中的元素（支持多选）"""
        selected = self.canvas.scene.selectedItems()

        if len(selected) > 1:
            # 群组移动
            logger.debug(f"[群组移动] 正在移动 {len(selected)} 个项目，偏移量 ({dx_mm:.2f}, {dy_mm:.2f})mm")

            for item in selected:
                if hasattr(item, 'element'):
                    element = item.element
                    old_x, old_y = element.config.x, element.config.y

                    element.config.x += dx_mm
                    element.config.y += dy_mm

                    # 更新图形项位置
                    dpi = 203
                    new_x = element.config.x * dpi / 25.4
                    new_y = element.config.y * dpi / 25.4
                    item.setPos(new_x, new_y)

                    # 为撤销创建移动命令
                    command = MoveElementCommand(element, item, old_x, old_y, element.config.x, element.config.y)
                    self.undo_stack.push(command)

            logger.info(f"已移动 {len(selected)} 个元素，偏移量 ({dx_mm}, {dy_mm})mm")

        elif self.selected_item and hasattr(self.selected_item, 'element'):
            # 单个移动
            element = self.selected_item.element
            old_x, old_y = element.config.x, element.config.y

            element.config.x += dx_mm
            element.config.y += dy_mm

            logger.debug(f"[移动] 之前: ({old_x:.2f}, {old_y:.2f})mm")
            logger.debug(f"[移动] 增量: ({dx_mm:.2f}, {dy_mm:.2f})mm")
            logger.debug(f"[移动] 之后: ({element.config.x:.2f}, {element.config.y:.2f})mm")

            # 更新图形项位置
            dpi = 203
            new_x = element.config.x * dpi / 25.4
            new_y = element.config.y * dpi / 25.4
            self.selected_item.setPos(new_x, new_y)

            # 更新属性面板和边界
            if self.property_panel.current_element:
                self.property_panel.update_position(element.config.x, element.config.y)
            self._highlight_element_bounds(self.selected_item)

            logger.info(f"元素已移动: dx={dx_mm}mm, dy={dy_mm}mm -> ({element.config.x}, {element.config.y})")

    def _copy_selected(self):
        """复制选中元素到剪贴板"""
        if self.selected_item and hasattr(self.selected_item, 'element'):
            import copy
            self.clipboard_element = copy.deepcopy(self.selected_item.element)
            logger.debug(f"[剪贴板] 已复制: {self.clipboard_element.__class__.__name__}")
            logger.info(f"元素已复制到剪贴板")

    def _paste_from_clipboard(self):
        """从剪贴板粘贴元素"""
        if not self.clipboard_element:
            logger.debug(f"[剪贴板] 为空 - 无内容可粘贴")
            return

        import copy
        new_element = copy.deepcopy(self.clipboard_element)

        # 偏移量用于视觉区分
        new_element.config.x += 5.0
        new_element.config.y += 5.0

        logger.debug(f"[剪贴板] 粘贴位置: ({new_element.config.x:.2f}, {new_element.config.y:.2f})mm")

        # 添加到画布
        graphics_item = self._create_graphics_item(new_element)
        self.canvas.scene.addItem(graphics_item)
        self.elements.append(new_element)
        self.graphics_items.append(graphics_item)

        # 选中新项
        self.canvas.scene.clearSelection()
        graphics_item.setSelected(True)

        logger.info(f"已从剪贴板粘贴元素")

    def _create_graphics_item(self, element):
        """为元素创建图形项"""
        if isinstance(element, TextElement):
            graphics_item = GraphicsTextItem(element, dpi=self.canvas.dpi)
        else:
            from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem
            if isinstance(element, BarcodeElement):
                graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
            else:
                return None

        graphics_item.snap_enabled = self.snap_enabled
        return graphics_item

    def _duplicate_selected(self):
        """复制选中的元素（复制 + 粘贴）"""
        if self.selected_item:
            logger.debug(f"[复制] 开始")
            self._copy_selected()
            self._paste_from_clipboard()
            logger.info(f"元素已复制")