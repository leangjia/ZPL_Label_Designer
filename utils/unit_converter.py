# -*- coding: utf-8 -*-
"""测量单位转换器"""

from enum import Enum
from typing import Tuple


class MeasurementUnit(Enum):
    """测量单位"""
    MM = "mm"
    CM = "cm"
    INCH = "inch"


class UnitConverter:
    """
    测量单位转换器。

    基本单位: MM (毫米)
    所有元素以 MM 为单位存储坐标和尺寸。
    单位仅用于 GUI 显示。
    """

    # === 转换常量 ===

    # 转换为 mm (基本单位)
    TO_MM = {
        MeasurementUnit.MM: 1.0,
        MeasurementUnit.CM: 10.0,
        MeasurementUnit.INCH: 25.4
    }

    # 从 mm 转换
    FROM_MM = {
        MeasurementUnit.MM: 1.0,
        MeasurementUnit.CM: 0.1,
        MeasurementUnit.INCH: 1.0 / 25.4  # 0.0393701
    }

    # === 公共方法 ===

    @classmethod
    def unit_to_mm(cls, value: float, unit: MeasurementUnit) -> float:
        """
        从指定单位转换为毫米。

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
        从毫米转换为指定单位。

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
        在两个单位之间进行转换。

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
        格式化指定单位的值。

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
        获取指定单位的范围。

        Returns:
            (最小值, 最大值) 以选定单位表示
        """
        min_value = cls.mm_to_unit(min_mm, unit)
        max_value = cls.mm_to_unit(max_mm, unit)
        return (min_value, max_value)

    @classmethod
    def get_step_in_unit(cls, step_mm: float, unit: MeasurementUnit) -> float:
        """
        获取 SpinBox 在指定单位中的步长。

        Examples:
            >>> UnitConverter.get_step_in_unit(0.1, MeasurementUnit.INCH)
            0.004  # 0.1mm ≈ 0.004 inch
        """
        return cls.mm_to_unit(step_mm, unit)