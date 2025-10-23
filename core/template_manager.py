# -*- coding: utf-8 -*-
"""模板管理器 - JSON 保存/加载"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .elements.base import BaseElement
from .elements.text_element import TextElement
from utils.unit_converter import MeasurementUnit


class TemplateManager:
    """标签模板管理器"""

    def __init__(self, templates_dir: str = "templates/library"):
        """
        初始化管理器

        Args:
            templates_dir: 保存模板的目录
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def save_template(self,
                      name: str,
                      elements: List[BaseElement],
                      label_config: Dict[str, Any],
                      display_unit: MeasurementUnit = MeasurementUnit.MM,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        保存模板到 JSON

        Args:
            name: 模板名称
            elements: 标签元素列表
            label_config: 标签配置 (width, height, dpi)
            display_unit: 显示用的测量单位
            metadata: 额外元数据 (作者, 描述等)

        Returns:
            保存的文件路径
        """
        # 创建 JSON 结构
        template_data = {
            "name": name,
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "label_config": {
                "width_mm": label_config.get('width', 28),
                "height_mm": label_config.get('height', 28),
                "dpi": label_config.get('dpi', 203),
                "display_unit": display_unit.value,  # ← 保存为 string
                "grid": label_config.get('grid', {
                    'size_x_mm': 1.0,
                    'size_y_mm': 1.0,
                    'offset_x_mm': 0.0,
                    'offset_y_mm': 0.0,
                    'visible': True,
                    'snap_mode': 'grid'
                })
            },
            "elements": [element.to_dict() for element in elements],
            "metadata": metadata or {}
        }

        # 格式化文件名
        safe_name = self._sanitize_filename(name)
        filepath = self.templates_dir / f"{safe_name}.json"

        # 写入 JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)

        print(f"[INFO] 模板已保存: {filepath}")
        return str(filepath)

    def load_template(self, filepath: str) -> Dict[str, Any]:
        """
        从 JSON 加载模板

        Args:
            filepath: JSON 文件路径

        Returns:
            包含 label_config 和 elements 的字典
        """
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            template_data = json.load(f)

        # 将元素从 dict → objects 转换
        elements = []
        for elem_data in template_data.get('elements', []):
            element = self._element_from_dict(elem_data)
            if element:
                elements.append(element)

        label_config = template_data.get('label_config', {})

        # 加载 display_unit (默认: MM)
        unit_str = label_config.get('display_unit', 'mm')
        try:
            display_unit = MeasurementUnit(unit_str)
        except ValueError:
            from utils.logger import logger
            logger.warning(f"[模板] 无效的 display_unit '{unit_str}'，使用 MM")
            display_unit = MeasurementUnit.MM

        from utils.logger import logger
        logger.info(f"[模板] 加载的 display_unit: {display_unit.value}")

        print(f"[INFO] 模板已加载: {filepath} ({len(elements)} 个元素)")

        return {
            "name": template_data.get('name', '未命名'),
            "label_config": label_config,
            "display_unit": display_unit,  # ← 返回 enum
            "elements": elements,
            "metadata": template_data.get('metadata', {})
        }

    def list_templates(self) -> List[Dict[str, str]]:
        """
        获取所有模板列表

        Returns:
            包含 'name' 和 'path' 的字典列表
        """
        templates = []

        for filepath in self.templates_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    templates.append({
                        "name": data.get('name', filepath.stem),
                        "path": str(filepath),
                        "created_at": data.get('created_at', ''),
                        "updated_at": data.get('updated_at', '')
                    })
            except Exception as e:
                print(f"[ERROR] 读取模板失败 {filepath}: {e}")

        return templates

    def delete_template(self, filepath: str) -> bool:
        """
        删除模板

        Args:
            filepath: JSON 文件路径

        Returns:
            如果成功删除则为 True
        """
        try:
            os.remove(filepath)
            print(f"[INFO] 模板已删除: {filepath}")
            return True
        except Exception as e:
            print(f"[ERROR] 删除模板失败 {filepath}: {e}")
            return False

    def _element_from_dict(self, data: Dict[str, Any]) -> Optional[BaseElement]:
        """
        转换 dict → BaseElement

        Args:
            data: 包含元素数据的字典

        Returns:
            元素对象或 None
        """
        elem_type = data.get('type')

        if elem_type == 'text':
            return TextElement.from_dict(data)

        elif elem_type == 'barcode':
            from .elements.barcode_element import (
                EAN13BarcodeElement,
                Code128BarcodeElement,
                QRCodeElement
            )

            barcode_type = data.get('barcode_type')

            if barcode_type == 'EAN13':
                return EAN13BarcodeElement.from_dict(data)
            elif barcode_type == 'CODE128':
                return Code128BarcodeElement.from_dict(data)
            elif barcode_type == 'QRCODE':
                return QRCodeElement.from_dict(data)

        elif elem_type == 'rectangle':
            from .elements.shape_element import RectangleElement
            return RectangleElement.from_dict(data)

        elif elem_type == 'circle':
            from .elements.shape_element import CircleElement
            return CircleElement.from_dict(data)

        elif elem_type == 'line':
            from .elements.shape_element import LineElement
            return LineElement.from_dict(data)

        elif elem_type == 'image':
            from .elements.image_element import ImageElement
            return ImageElement.from_dict(data)

        print(f"[WARNING] 未知元素类型: {elem_type}")
        return None

    def _sanitize_filename(self, name: str) -> str:
        """
        清理文件名中的危险字符

        Args:
            name: 原始名称

        Returns:
            安全的文件名
        """
        # 将危险字符替换为 _
        safe_chars = []
        for char in name:
            if char.isalnum() or char in ('-', '_', ' '):
                safe_chars.append(char)
            else:
                safe_chars.append('_')

        safe_name = ''.join(safe_chars).strip()

        # 如果为空 - 给默认名称
        if not safe_name:
            safe_name = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return safe_name