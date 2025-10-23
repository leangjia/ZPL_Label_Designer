# -*- coding: utf-8 -*-
"""工具栏"""

from PySide6.QtWidgets import QToolBar


class EditorToolbar(QToolBar):
    """编辑器工具栏"""

    def __init__(self, actions, menus, parent=None):
        super().__init__("工具", parent)

        self.actions = actions
        self.menus = menus

        # 添加文本
        self.add_text_action = self.actions['add_text']
        self.addAction(self.add_text_action)

        self.addSeparator()

        # 添加条码菜单
        self.barcode_menu_action = self.actions['barcode_menu']
        self.barcode_menu = self.menus['barcode']
        self.barcode_menu_action.setMenu(self.barcode_menu)

        # 添加到工具栏
        self.addAction(self.barcode_menu_action)

        self.addSeparator()

        # 添加形状菜单
        self.shape_menu_action = self.actions['shape_menu']
        self.shape_menu = self.menus['shape']
        self.shape_menu_action.setMenu(self.shape_menu)

        # 添加到工具栏
        self.addAction(self.shape_menu_action)

        self.addSeparator()

        # 添加图片
        self.add_image_action = self.actions['add_image']
        self.addAction(self.add_image_action)

        self.addSeparator()

        # 保存
        self.save_action = self.actions['save']
        self.addAction(self.save_action)

        # 加载
        self.load_action = self.actions['load']
        self.addAction(self.load_action)

        self.addSeparator()

        # 导出 ZPL
        self.export_action = self.actions['export']
        self.addAction(self.export_action)

        # 预览
        self.preview_action = self.actions['preview']
        self.addAction(self.preview_action)

        # 打开 JSON
        self.open_json_action = self.actions['open_json']
        self.addAction(self.open_json_action)