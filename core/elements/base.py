# -*- coding: utf-8 -*-
"""Базовый класс для всех элементов этикетки"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ElementConfig:
    """Конфигурация позиции элемента"""
    x: float  # Позиция X в мм
    y: float  # Позиция Y в мм
    rotation: int = 0  # Поворот в градусах

class BaseElement:
    """Базовый класс элемента этикетки"""
    
    def __init__(self, config: ElementConfig):
        self.config = config
        self.id = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в JSON"""
        raise NotImplementedError
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Десериализация из JSON"""
        raise NotImplementedError
    
    def to_zpl(self, dpi: int) -> str:
        """Генерация ZPL кода"""
        raise NotImplementedError
