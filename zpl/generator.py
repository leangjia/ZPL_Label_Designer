# -*- coding: utf-8 -*-
"""ZPL 代码生成器"""

from typing import List, Dict
from core.elements.base import BaseElement
from utils.logger import logger


class ZPLGenerator:
    """从元素生成 ZPL 代码"""

    def __init__(self, dpi=203):
        self.dpi = dpi
        logger.info(f"ZPL生成器已初始化，DPI: {dpi}")

    def generate(self, elements: List[BaseElement],
                 label_config: Dict,
                 data: Dict = None) -> str:
        """
        生成 ZPL 代码

        Args:
            elements: 标签元素列表
            label_config: 标签配置 (width, height, dpi)
            data: 用于替换占位符的数据

        Returns:
            ZPL 代码 (str)
        """
        logger.info("=" * 60)
        logger.info("开始生成 ZPL 代码")
        logger.info("=" * 60)
        logger.info(f"元素数量: {len(elements)}")
        logger.info(f"标签配置: {label_config}")
        if data:
            logger.info(f"替换数据: {data}")

        zpl_lines = []

        # 标签开始
        zpl_lines.append("^XA")
        logger.debug("已添加: ^XA (标签开始)")

        # 西里尔字符编码
        zpl_lines.append("^CI28")
        logger.debug("已添加: ^CI28 (UTF-8 编码)")

        # 标签宽度
        width_dots = self._mm_to_dots(label_config['width'])
        zpl_lines.append(f"^PW{width_dots}")
        logger.info(f"标签宽度: {label_config['width']}mm = {width_dots} 点 (^PW{width_dots})")

        # 标签高度
        height_dots = self._mm_to_dots(label_config['height'])
        zpl_lines.append(f"^LL{height_dots}")
        logger.info(f"标签高度: {label_config['height']}mm = {height_dots} 点 (^LL{height_dots})")

        # 生成元素
        logger.info("正在生成元素...")
        for i, element in enumerate(elements):
            logger.info(f"处理元素 {i + 1}/{len(elements)}: {element.__class__.__name__}")

            # 记录元素参数
            if hasattr(element, 'text'):
                logger.debug(f"  文本: '{element.text}'")
            if hasattr(element, 'font_size'):
                logger.debug(f"  字体大小: {element.font_size}")
            if hasattr(element, 'data_field'):
                logger.debug(f"  数据字段: {element.data_field}")
            logger.debug(f"  位置: ({element.config.x:.2f}mm, {element.config.y:.2f}mm)")

            # 生成元素的 ZPL 代码
            element_zpl = element.to_zpl(self.dpi)
            logger.debug(f"  生成的 ZPL: {element_zpl}")

            # 数据替换
            if data:
                original_zpl = element_zpl
                element_zpl = self._substitute_placeholders(element_zpl, data)
                if original_zpl != element_zpl:
                    logger.info(f"  已应用占位符替换")
                    logger.debug(f"  替换前: {original_zpl}")
                    logger.debug(f"  替换后: {element_zpl}")

            zpl_lines.append(element_zpl)

        # 标签结束
        zpl_lines.append("^XZ")
        logger.debug("已添加: ^XZ (标签结束)")

        zpl_code = "\n".join(zpl_lines)
        logger.info(f"ZPL 生成完成: {len(zpl_code)} 字节, {len(zpl_lines)} 行")
        logger.info("=" * 60)

        return zpl_code

    def _mm_to_dots(self, mm: float) -> int:
        """毫米 -> 点 转换"""
        dots = int(mm * self.dpi / 25.4)
        logger.debug(f"单位转换: {mm:.2f}mm = {dots} 点 (DPI={self.dpi})")
        return dots

    def _substitute_placeholders(self, zpl: str, data: Dict) -> str:
        """将 {{FIELD}} 替换为实际数据"""
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in zpl:
                logger.debug(f"替换占位符 '{placeholder}' 为 '{value}'")
                zpl = zpl.replace(placeholder, str(value))
        return zpl