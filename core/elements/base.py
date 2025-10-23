# -*- coding: utf-8 -*-
"""所有标签元素的基础类"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ElementConfig:
    """元素位置配置"""
    x: float  # X 位置（毫米）
    y: float  # Y 位置（毫米）
    rotation: int = 0  # 旋转角度（度）


class BaseElement:
    """标签元素基础类"""

    def __init__(self, config: ElementConfig):
        self.config = config
        self.id = None

    def to_dict(self) -> Dict[str, Any]:
        """序列化到 JSON"""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从 JSON 反序列化"""
        raise NotImplementedError

    def to_zpl(self, dpi: int) -> str:
        """生成 ZPL 代码"""
        raise NotImplementedError