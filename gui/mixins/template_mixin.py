# -*- coding: utf-8 -*-
"""模板操作的混入类"""

from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QFileDialog, QLabel
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from io import BytesIO
from datetime import datetime
import json
from pathlib import Path
from utils.logger import logger
from utils.unit_converter import MeasurementUnit
from core.elements.text_element import TextElement, GraphicsTextItem
from core.elements.image_element import ImageElement, GraphicsImageItem
from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem


class TemplateMixin:
    """模板保存/加载和 ZPL 导出操作"""

    def _load_template_from_file(self, filepath):
        """从文件加载模板（用于 1C 集成）- 加载到画布"""
        try:
            logger.info(f"[1C-导入] 从文件加载模板: {filepath}")

            # 使用 TemplateManager 进行解析（类似于 _load_template）
            template_data = self.template_manager.load_template(filepath)
            logger.info(f"[1C-导入] 模板已加载: {template_data.get('name', '未命名')}")

            # 应用网格配置（向后兼容）
            label_config = template_data['label_config']
            if 'grid' in label_config:
                from config import GridConfig, SnapMode
                grid_data = label_config['grid']
                grid_config = GridConfig(
                    size_x_mm=grid_data.get('size_x_mm', 1.0),
                    size_y_mm=grid_data.get('size_y_mm', 1.0),
                    offset_x_mm=grid_data.get('offset_x_mm', 0.0),
                    offset_y_mm=grid_data.get('offset_y_mm', 0.0),
                    visible=grid_data.get('visible', True),
                    snap_mode=SnapMode(grid_data.get('snap_mode', 'grid'))
                )
                self.canvas.set_grid_config(grid_config)
                logger.debug(f"[1C-导入] 已加载网格: 尺寸 X={grid_config.size_x_mm}mm")
            else:
                # 没有网格的旧模板 - 使用默认值
                from config import GridConfig
                self.canvas.set_grid_config(GridConfig())

            # 清除画布
            self.canvas.clear_and_redraw_grid()
            self.elements.clear()
            self.graphics_items.clear()
            logger.info("[1C-导入] 画布已清除")

            # 设置单位
            display_unit = template_data.get('display_unit', MeasurementUnit.MM)
            index = self.units_combobox.findData(display_unit)
            if index >= 0:
                self.units_combobox.setCurrentIndex(index)
            logger.info(f"[1C-导入] 应用显示单位: {display_unit.value}")

            # 设置标签尺寸
            width_mm = label_config.get('width_mm', 28)
            height_mm = label_config.get('height_mm', 28)

            if width_mm != self.canvas.width_mm or height_mm != self.canvas.height_mm:
                self.canvas.set_label_size(width_mm, height_mm)
                self.width_spinbox.blockSignals(True)
                self.height_spinbox.blockSignals(True)
                self.width_spinbox.setValue(width_mm)
                self.height_spinbox.setValue(height_mm)
                self.width_spinbox.blockSignals(False)
                self.height_spinbox.blockSignals(False)
                logger.info(f"[1C-导入] 标签尺寸已设置: {width_mm}x{height_mm}mm")

            # 加载元素
            for element in template_data['elements']:
                if isinstance(element, TextElement):
                    graphics_item = GraphicsTextItem(element, dpi=self.canvas.dpi)
                elif isinstance(element, BarcodeElement):
                    graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
                elif isinstance(element, ImageElement):
                    graphics_item = GraphicsImageItem(element, dpi=self.canvas.dpi)
                else:
                    continue

                self.canvas.scene.addItem(graphics_item)
                self.elements.append(element)
                self.graphics_items.append(graphics_item)

            logger.info(f"[1C-导入] 模板加载成功: {len(self.elements)} 个元素")

        except Exception as e:
            logger.error(f"[1C-导入] 加载失败: {e}", exc_info=True)
            QMessageBox.critical(self, "导入错误", f"加载错误:\n{e}")

    def _export_zpl(self):
        """导出为 ZPL"""
        if not self.elements:
            logger.warning("导出 ZPL: 没有要导出的元素")
            QMessageBox.warning(self, "导出", "没有要导出的元素")
            return

        # 生成 ZPL
        label_config = {
            'width': self.canvas.width_mm,
            'height': self.canvas.height_mm,
            'dpi': self.canvas.dpi
        }

        zpl_code = self.zpl_generator.generate(self.elements, label_config)
        logger.info("已生成 ZPL 代码用于导出")

        # 在对话框中显示
        dialog = QDialog(self)
        dialog.setWindowTitle("ZPL 代码")
        dialog.resize(600, 400)

        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setPlainText(zpl_code)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        dialog.setLayout(layout)

        dialog.exec()

        logger.info("ZPL 导出对话框已显示")

    def _open_json(self):
        """在对话框中显示模板 JSON"""
        if not self.elements:
            logger.warning("打开 JSON: 没有要显示的元素")
            QMessageBox.warning(self, "打开 JSON", "画布上没有元素")
            return

        try:
            # 生成 JSON（复制 _save_template 的逻辑）
            from datetime import datetime
            import json

            template_data = {
                "name": "当前模板",
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "label_config": {
                    "width_mm": self.canvas.width_mm,
                    "height_mm": self.canvas.height_mm,
                    "dpi": self.canvas.dpi,
                    "display_unit": self.current_unit.value,
                    "grid": {
                        "size_x_mm": self.canvas.grid_config.size_x_mm,
                        "size_y_mm": self.canvas.grid_config.size_y_mm,
                        "offset_x_mm": self.canvas.grid_config.offset_x_mm,
                        "offset_y_mm": self.canvas.grid_config.offset_y_mm,
                        "visible": self.canvas.grid_config.visible,
                        "snap_mode": self.canvas.grid_config.snap_mode.value
                    }
                },
                "elements": [element.to_dict() for element in self.elements],
                "metadata": {
                    "elements_count": len(self.elements),
                    "application": "ZPL 标签设计器 1.0"
                }
            }

            # 格式化 JSON
            json_str = json.dumps(template_data, indent=2, ensure_ascii=False)
            logger.info(f"[打开-JSON] 生成的 JSON: {len(json_str)} 字符")

            # 显示对话框（类似于导出 ZPL！）
            dialog = QDialog(self)
            dialog.setWindowTitle("模板 JSON")
            dialog.resize(700, 500)

            layout = QVBoxLayout()
            text_edit = QTextEdit()
            text_edit.setPlainText(json_str)
            text_edit.setReadOnly(True)

            # JSON 使用等宽字体
            font = QFont("Courier New", 10)
            text_edit.setFont(font)

            layout.addWidget(text_edit)
            dialog.setLayout(layout)

            dialog.exec()
            logger.info("[打开-JSON] 对话框已显示")

        except Exception as e:
            logger.error(f"[打开-JSON] 错误: {e}", exc_info=True)
            QMessageBox.critical(self, "打开 JSON 错误", f"生成 JSON 失败:\n{e}")

    def _save_template(self):
        """将模板保存为 JSON"""
        if not self.elements:
            logger.warning("保存模板: 没有要保存的元素")
            QMessageBox.warning(self, "保存", "没有要保存的元素")
            return

        # 选择保存路径的对话框
        default_path = str(self.template_manager.templates_dir / "my_template.json")
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "保存模板",
            default_path,
            "JSON 文件 (*.json)"
        )

        if not filepath:
            return

        # 确保扩展名为 .json
        if not filepath.endswith('.json'):
            filepath += '.json'

        # 从路径中提取模板名称
        from pathlib import Path
        template_name = Path(filepath).stem

        # 准备配置
        label_config = {
            'width': self.canvas.width_mm,
            'height': self.canvas.height_mm,
            'dpi': self.canvas.dpi
        }

        # 元数据
        metadata = {
            'elements_count': len(self.elements),
            'application': 'ZPL 标签设计器 1.0'
        }

        try:
            # 直接创建 JSON 结构
            from datetime import datetime
            import json

            template_data = {
                "name": template_name,
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "label_config": {
                    "width_mm": label_config.get('width', 28),
                    "height_mm": label_config.get('height', 28),
                    "dpi": label_config.get('dpi', 203),
                    "display_unit": self.current_unit.value  # ← 保存显示单位
                },
                "elements": [element.to_dict() for element in self.elements],
                "metadata": metadata
            }

            logger.info(f"[模板] 使用显示单位保存: {self.current_unit.value}")

            # 保存到选择的文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            logger.info(f"模板已保存: {filepath}")
            QMessageBox.information(
                self,
                "保存",
                f"模板保存成功!\n{filepath}"
            )

        except Exception as e:
            logger.error(f"保存模板失败: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "保存错误",
                f"保存模板失败:\n{e}"
            )

    def _load_template(self):
        """从 JSON 加载模板"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "加载模板",
            str(self.template_manager.templates_dir),
            "JSON 文件 (*.json)"
        )

        if not filepath:
            return

        try:
            template_data = self.template_manager.load_template(filepath)

            # 应用网格配置（向后兼容）
            label_config = template_data['label_config']
            if 'grid' in label_config:
                from config import GridConfig, SnapMode
                grid_data = label_config['grid']
                grid_config = GridConfig(
                    size_x_mm=grid_data.get('size_x_mm', 1.0),
                    size_y_mm=grid_data.get('size_y_mm', 1.0),
                    offset_x_mm=grid_data.get('offset_x_mm', 0.0),
                    offset_y_mm=grid_data.get('offset_y_mm', 0.0),
                    visible=grid_data.get('visible', True),
                    snap_mode=SnapMode(grid_data.get('snap_mode', 'grid'))
                )
                self.canvas.set_grid_config(grid_config)
                logger.debug(
                    f"[模板加载] 已加载网格: 尺寸 X={grid_config.size_x_mm}mm, 偏移 Y={grid_config.offset_y_mm}mm")
            else:
                # 没有网格的旧模板 - 使用默认值
                logger.debug("[模板加载] 无网格配置 - 使用默认值")
                from config import GridConfig
                self.canvas.set_grid_config(GridConfig())

            self.canvas.clear_and_redraw_grid()
            self.elements.clear()
            self.graphics_items.clear()

            display_unit = template_data.get('display_unit', MeasurementUnit.MM)

            index = self.units_combobox.findData(display_unit)
            if index >= 0:
                self.units_combobox.setCurrentIndex(index)

            logger.info(f"[模板] 应用显示单位: {display_unit.value}")

            label_config = template_data['label_config']
            width_mm = label_config.get('width_mm', 28)
            height_mm = label_config.get('height_mm', 28)

            logger.debug(f"[加载模板] 模板中的标签尺寸: {width_mm}x{height_mm}mm")

            if width_mm != self.canvas.width_mm or height_mm != self.canvas.height_mm:
                logger.info(f"[加载模板] 应用新标签尺寸: {width_mm}x{height_mm}mm")
                self.canvas.set_label_size(width_mm, height_mm)

                self.width_spinbox.blockSignals(True)
                self.height_spinbox.blockSignals(True)
                self.width_spinbox.setValue(width_mm)
                self.height_spinbox.setValue(height_mm)
                self.width_spinbox.blockSignals(False)
                self.height_spinbox.blockSignals(False)

                logger.debug(f"[加载模板] 微调框已更新: 宽={width_mm}, 高={height_mm}")

            for element in template_data['elements']:
                if isinstance(element, TextElement):
                    graphics_item = GraphicsTextItem(element, dpi=self.canvas.dpi)
                elif isinstance(element, BarcodeElement):
                    graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
                elif isinstance(element, ImageElement):
                    graphics_item = GraphicsImageItem(element, dpi=self.canvas.dpi)
                else:
                    continue

                self.canvas.scene.addItem(graphics_item)
                self.elements.append(element)
                self.graphics_items.append(graphics_item)

            logger.info(f"模板已加载: {filepath} ({len(self.elements)} 个元素)")
            QMessageBox.information(
                self,
                "加载",
                f"模板加载成功!\n{len(self.elements)} 个元素"
            )

        except Exception as e:
            logger.error(f"加载模板失败: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "加载错误",
                f"加载模板失败:\n{e}"
            )

    def _show_preview(self):
        """通过 Labelary 显示预览"""
        logger.info("=" * 60)
        logger.info("预览请求已启动")
        logger.info("=" * 60)

        if not self.elements:
            logger.warning("预览中止: 画布上没有元素")
            QMessageBox.warning(self, "预览", "没有要预览的元素")
            return

        # 元素信息
        logger.info(f"元素数量: {len(self.elements)}")
        for i, element in enumerate(self.elements):
            element_info = f"元素 {i + 1}: 类型={element.__class__.__name__}"
            if hasattr(element, 'text'):
                element_info += f", 文本='{element.text}'"
            if hasattr(element, 'font_size'):
                element_info += f", 字体大小={element.font_size}"
            element_info += f", 位置=({element.config.x:.1f}, {element.config.y:.1f})"
            if hasattr(element, 'data_field') and element.data_field:
                element_info += f", 占位符='{element.data_field}'"
            logger.info(element_info)

        # 生成 ZPL
        label_config = {
            'width': self.canvas.width_mm,
            'height': self.canvas.height_mm,
            'dpi': self.canvas.dpi
        }
        logger.info(f"标签配置: {label_config}")

        # 为预览将占位符替换为测试数据
        test_data = {}
        for element in self.elements:
            if hasattr(element, 'data_field') and element.data_field:
                # 从 {{字段名}} 中提取字段名称
                field_name = element.data_field.replace('{{', '').replace('}}', '')
                test_data[field_name] = '[测试数据]'

        if test_data:
            logger.info(f"占位符的测试数据: {test_data}")
        else:
            logger.info("没有占位符，使用实际文本值")

        logger.info("正在生成 ZPL 代码...")
        zpl_code = self.zpl_generator.generate(self.elements, label_config, test_data)

        # 在 DEBUG 模式下显示 ZPL
        logger.debug("=" * 60)
        logger.debug("生成的 ZPL 代码:")
        logger.debug("=" * 60)
        for line in zpl_code.split('\n'):
            logger.debug(line)
        logger.debug("=" * 60)

        # 获取预览
        logger.info("正在从 Labelary API 请求预览...")
        try:
            image = self.labelary_client.preview(
                zpl_code,
                self.canvas.width_mm,
                self.canvas.height_mm
            )

            if image:
                logger.info("收到预览图片，显示对话框")

                # 显示预览
                dialog = QDialog(self)
                dialog.setWindowTitle("预览")

                layout = QVBoxLayout()
                label = QLabel()

                # 转换 PIL Image -> QPixmap
                image_bytes = BytesIO()
                image.save(image_bytes, format='PNG')
                pixmap = QPixmap()
                pixmap.loadFromData(image_bytes.getvalue())

                logger.info(f"图片尺寸: {pixmap.width()}x{pixmap.height()}px")

                # 缩放以显示
                pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(pixmap)

                layout.addWidget(label)
                dialog.setLayout(layout)
                dialog.resize(450, 450)
                dialog.exec()

                logger.info("预览对话框已关闭")
                logger.info("=" * 60)
            else:
                logger.error("预览失败: Labelary 客户端返回 None")
                logger.info("=" * 60)
                QMessageBox.critical(self, "预览", "生成预览失败。请检查日志了解详情。")

        except Exception as e:
            logger.error("=" * 60)
            logger.error("预览异常")
            logger.error("=" * 60)
            logger.error(f"异常类型: {type(e).__name__}")
            logger.error(f"异常消息: {e}", exc_info=True)
            logger.error("=" * 60)
            QMessageBox.critical(self, "预览", f"生成预览失败: {e}")