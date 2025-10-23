# -*- coding: utf-8 -*-
"""UI 辅助方法的混入类"""

from PySide6.QtWidgets import QMenu
from utils.logger import logger
from core.undo_commands import DeleteElementCommand


class UIHelpersMixin:
    """UI 辅助方法"""

    def _undo(self):
        """撤销最后一次操作"""
        if self.undo_stack.canUndo():
            logger.debug(f"[撤销操作] 撤销: {self.undo_stack.undoText()}")
            self.undo_stack.undo()
        else:
            logger.debug(f"[撤销操作] 没有可撤销的操作")

    def _redo(self):
        """重做已撤销的操作"""
        if self.undo_stack.canRedo():
            logger.debug(f"[撤销操作] 重做: {self.undo_stack.redoText()}")
            self.undo_stack.redo()
        else:
            logger.debug(f"[撤销操作] 没有可重做的操作")

    def _bring_to_front(self):
        """移到最前面（z 顺序）"""
        if self.selected_item:
            max_z = max([item.zValue() for item in self.graphics_items], default=0)
            self.selected_item.setZValue(max_z + 1)
            logger.debug(f"[Z顺序] 移到最前面: z={max_z + 1}")
            logger.info(f"元素已移到最前面")

    def _send_to_back(self):
        """移到最后面（z 顺序）"""
        if self.selected_item:
            min_z = min([item.zValue() for item in self.graphics_items], default=0)
            self.selected_item.setZValue(min_z - 1)
            logger.debug(f"[Z顺序] 移到最后面: z={min_z - 1}")
            logger.info(f"元素已移到最后面")

    def _show_context_menu(self, item, global_pos):
        """显示上下文菜单"""
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)

        if item:  # 项目上下文菜单
            logger.debug(f"[上下文菜单] 创建项目菜单")

            copy_action = menu.addAction("复制 (Ctrl+C)")
            copy_action.triggered.connect(self._copy_selected)

            duplicate_action = menu.addAction("复制 (Ctrl+D)")
            duplicate_action.triggered.connect(self._duplicate_selected)

            menu.addSeparator()

            front_action = menu.addAction("移到最前面")
            front_action.triggered.connect(self._bring_to_front)

            back_action = menu.addAction("移到最后面")
            back_action.triggered.connect(self._send_to_back)

            menu.addSeparator()

            delete_action = menu.addAction("删除 (Del)")
            delete_action.triggered.connect(self._delete_selected)
        else:  # 画布上下文菜单
            logger.debug(f"[上下文菜单] 创建画布菜单")

            paste_action = menu.addAction("粘贴 (Ctrl+V)")
            paste_action.triggered.connect(self._paste_from_clipboard)
            paste_action.setEnabled(self.clipboard_element is not None)

        logger.debug(f"[上下文菜单] 显示位置: {global_pos}")
        menu.exec(global_pos)

    def _delete_selected(self):
        """删除选中的元素（支持多选）"""
        selected = self.canvas.scene.selectedItems()

        if len(selected) > 1:
            # 组删除
            logger.debug(f"[组删除] 删除 {len(selected)} 个项目")

            for item in selected:
                if hasattr(item, 'element'):
                    element = item.element
                    command = DeleteElementCommand(self, element, item)
                    self.undo_stack.push(command)

            # 清除 UI
            self.selected_item = None
            self.h_ruler.clear_highlight()
            self.v_ruler.clear_highlight()
            self.property_panel.set_element(None, None)
            logger.info(f"删除了 {len(selected)} 个元素")

        elif self.selected_item:
            # 单元素删除
            # 在 removeItem 之前保存（竞态条件！）
            item_to_delete = self.selected_item
            element_to_delete = item_to_delete.element if hasattr(item_to_delete, 'element') else None

            if element_to_delete:
                logger.debug(f"[删除] 创建删除命令")
                command = DeleteElementCommand(self, element_to_delete, item_to_delete)
                self.undo_stack.push(command)

                # 清除 UI
                self.selected_item = None
                self.h_ruler.clear_highlight()
                self.v_ruler.clear_highlight()
                self.property_panel.set_element(None, None)
                logger.debug(f"[删除] UI 已清除")