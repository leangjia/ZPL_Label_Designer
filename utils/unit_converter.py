# -*- coding: utf-8 -*-
"""Конвертер одиниць вимірювання"""

from enum import Enum
from typing import Tuple


class MeasurementUnit(Enum):
    """Одиниці вимірювання"""
    MM = "mm"
    CM = "cm"
    INCH = "inch"


class UnitConverter:
    """
    Конвертер між одиницями вимірювання.
    
    БАЗОВА ОДИНИЦЯ: MM (міліметри)
    Всі елементи зберігають координати і розміри в MM.
    Units використовуються ТІЛЬКИ для відображення в GUI.
    """
    
    # === КОНСТАНТИ КОНВЕРТАЦІЇ ===
    
    # Конвертація ДО mm (базова одиниця)
    TO_MM = {
        MeasurementUnit.MM: 1.0,
        MeasurementUnit.CM: 10.0,
        MeasurementUnit.INCH: 25.4
    }
    
    # Конвертація З mm
    FROM_MM = {
        MeasurementUnit.MM: 1.0,
        MeasurementUnit.CM: 0.1,
        MeasurementUnit.INCH: 1.0 / 25.4  # 0.0393701
    }
    
    # === ПУБЛІЧНІ МЕТОДИ ===
    
    @classmethod
    def unit_to_mm(cls, value: float, unit: MeasurementUnit) -> float:
        """
        Конвертувати з заданої одиниці в mm.
        
        Examples:
            >>> UnitConverter.unit_to_mm(1.0, MeasurementUnit.INCH)
            25.4
            >>> UnitConverter.unit_to_mm(1.0, MeasurementUnit.CM)
            10.0
        """
        return value * cls.TO_MM[unit]
    
    @classmethod
    def mm_to_unit(cls, mm: float, unit: MeasurementUnit) -> float:
        """
        Конвертувати з mm в задану одиницю.
        
        Examples:
            >>> UnitConverter.mm_to_unit(25.4, MeasurementUnit.INCH)
            1.0
            >>> UnitConverter.mm_to_unit(10.0, MeasurementUnit.CM)
            1.0
        """
        return mm * cls.FROM_MM[unit]
    
    @classmethod
    def convert_between(cls, value: float, 
                       from_unit: MeasurementUnit, 
                       to_unit: MeasurementUnit) -> float:
        """
        Конвертувати між двома одиницями.
        
        Examples:
            >>> UnitConverter.convert_between(1.0, MeasurementUnit.INCH, MeasurementUnit.MM)
            25.4
        """
        mm = cls.unit_to_mm(value, from_unit)
        return cls.mm_to_unit(mm, to_unit)
    
    @classmethod
    def format_value(cls, mm: float, unit: MeasurementUnit, 
                    decimals: int = 1) -> str:
        """
        Форматувати значення в заданих units.
        
        Examples:
            >>> UnitConverter.format_value(25.4, MeasurementUnit.INCH)
            '1.0 inch'
            >>> UnitConverter.format_value(10.0, MeasurementUnit.CM, decimals=2)
            '1.00 cm'
        """
        value = cls.mm_to_unit(mm, unit)
        return f"{value:.{decimals}f} {unit.value}"
    
    @classmethod
    def get_range_in_unit(cls, min_mm: float, max_mm: float, 
                         unit: MeasurementUnit) -> Tuple[float, float]:
        """
        Отримати діапазон в заданих units.
        
        Returns:
            (min_value, max_value) в обраних units
        """
        min_value = cls.mm_to_unit(min_mm, unit)
        max_value = cls.mm_to_unit(max_mm, unit)
        return (min_value, max_value)
    
    @classmethod
    def get_step_in_unit(cls, step_mm: float, unit: MeasurementUnit) -> float:
        """
        Отримати крок для SpinBox в заданих units.
        
        Examples:
            >>> UnitConverter.get_step_in_unit(0.1, MeasurementUnit.INCH)
            0.004  # 0.1mm ≈ 0.004 inch
        """
        return cls.mm_to_unit(step_mm, unit)
