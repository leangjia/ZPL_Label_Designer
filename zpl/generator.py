# -*- coding: utf-8 -*-
"""Генератор ZPL кода"""

from typing import List, Dict
from core.elements.base import BaseElement
from utils.logger import logger

class ZPLGenerator:
    """Генератор ZPL кода из элементов"""
    
    def __init__(self, dpi=203):
        self.dpi = dpi
        logger.info(f"ZPLGenerator initialized with DPI {dpi}")
    
    def generate(self, elements: List[BaseElement], 
                 label_config: Dict,
                 data: Dict = None) -> str:
        """
        Генерировать ZPL код
        
        Args:
            elements: Список элементов этикетки
            label_config: Конфигурация (width, height, dpi)
            data: Данные для подстановки в placeholder
        
        Returns:
            ZPL код (str)
        """
        logger.info("="*60)
        logger.info("ZPL GENERATION STARTED")
        logger.info("="*60)
        logger.info(f"Elements count: {len(elements)}")
        logger.info(f"Label config: {label_config}")
        if data:
            logger.info(f"Data for substitution: {data}")
        
        zpl_lines = []
        
        # Начало этикетки
        zpl_lines.append("^XA")
        logger.debug("Added: ^XA (start of label)")
        
        # Кодировка кириллицы
        zpl_lines.append("^CI28")
        logger.debug("Added: ^CI28 (UTF-8 encoding)")
        
        # Ширина этикетки
        width_dots = self._mm_to_dots(label_config['width'])
        zpl_lines.append(f"^PW{width_dots}")
        logger.info(f"Label width: {label_config['width']}mm = {width_dots} dots (^PW{width_dots})")
        
        # Высота этикетки
        height_dots = self._mm_to_dots(label_config['height'])
        zpl_lines.append(f"^LL{height_dots}")
        logger.info(f"Label height: {label_config['height']}mm = {height_dots} dots (^LL{height_dots})")
        
        # Генерация элементов
        logger.info("Generating elements...")
        for i, element in enumerate(elements):
            logger.info(f"Processing element {i+1}/{len(elements)}: {element.__class__.__name__}")
            
            # Логировать параметры элемента
            if hasattr(element, 'text'):
                logger.debug(f"  Text: '{element.text}'")
            if hasattr(element, 'font_size'):
                logger.debug(f"  Font size: {element.font_size}")
            if hasattr(element, 'data_field'):
                logger.debug(f"  Data field: {element.data_field}")
            logger.debug(f"  Position: ({element.config.x:.2f}mm, {element.config.y:.2f}mm)")
            
            # Генерация ZPL для элемента
            element_zpl = element.to_zpl(self.dpi)
            logger.debug(f"  Generated ZPL: {element_zpl}")
            
            # Подстановка данных
            if data:
                original_zpl = element_zpl
                element_zpl = self._substitute_placeholders(element_zpl, data)
                if original_zpl != element_zpl:
                    logger.info(f"  Placeholder substitution applied")
                    logger.debug(f"  Before: {original_zpl}")
                    logger.debug(f"  After: {element_zpl}")
            
            zpl_lines.append(element_zpl)
        
        # Конец этикетки
        zpl_lines.append("^XZ")
        logger.debug("Added: ^XZ (end of label)")
        
        zpl_code = "\n".join(zpl_lines)
        logger.info(f"ZPL generation completed: {len(zpl_code)} bytes, {len(zpl_lines)} lines")
        logger.info("="*60)
        
        return zpl_code
    
    def _mm_to_dots(self, mm: float) -> int:
        """Конвертация мм -> dots"""
        dots = int(mm * self.dpi / 25.4)
        logger.debug(f"Conversion: {mm:.2f}mm = {dots} dots (DPI={self.dpi})")
        return dots
    
    def _substitute_placeholders(self, zpl: str, data: Dict) -> str:
        """Замена {{FIELD}} на реальные данные"""
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in zpl:
                logger.debug(f"Substituting placeholder '{placeholder}' with '{value}'")
                zpl = zpl.replace(placeholder, str(value))
        return zpl
