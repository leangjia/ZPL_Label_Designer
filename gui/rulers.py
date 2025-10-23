# -*- coding: utf-8 -*-
"""标尺 - 用于元素精确定位"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from utils.logger import logger
from utils.unit_converter import MeasurementUnit, UnitConverter


class RulerWidget(QWidget):
    """带有毫米刻度的标尺"""

    def __init__(self, orientation, length_mm, dpi, scale=2.5, unit=MeasurementUnit.MM):
        """
        Args:
            orientation: Qt.Horizontal 或 Qt.Vertical
            length_mm: 标尺长度（毫米）
            dpi: 用于转换的 canvas DPI
            scale: canvas 缩放比例（用于同步）
            unit: 显示用的测量单位
        """
        super().__init__()

        self.orientation = orientation
        self.length_mm = length_mm
        self.dpi = dpi
        self.scale_factor = scale
        self.unit = unit

        # 标尺尺寸
        self.ruler_thickness = 25
        self.length_px = round(self._mm_to_px(length_mm) * scale)

        # 设置 widget 尺寸
        if orientation == Qt.Horizontal:
            self.setFixedHeight(self.ruler_thickness)
            self.setMinimumWidth(self.length_px)
        else:
            self.setFixedWidth(self.ruler_thickness)
            self.setMinimumHeight(self.length_px)

        # 颜色
        self.bg_color = QColor(240, 240, 240)
        self.major_tick_color = QColor(0, 0, 0)
        self.minor_tick_color = QColor(100, 100, 100)
        self.text_color = QColor(0, 0, 0)

        # 刻度尺寸
        self.major_tick_length = 10
        self.minor_tick_length = 5

        # 字体
        self.font = QFont("Arial", 8)

        # 光标追踪
        self.cursor_pos_mm = None
        self.show_cursor = False

        # 元素边界高亮
        self.highlighted_bounds = None  # (start_mm, width_mm)

    def _mm_to_px(self, mm):
        """毫米 -> 像素转换（不考虑缩放）"""
        return mm * self.dpi / 25.4  # 保持浮点数精度

    def set_unit(self, unit: MeasurementUnit):
        """更改显示单位"""
        logger.debug(
            f"[RULER-{'H' if self.orientation == Qt.Horizontal else 'V'}] 设置单位: {self.unit.value} -> {unit.value}")

        self.unit = unit
        self.update()

    def paintEvent(self, event):
        """绘制标尺"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 背景
        painter.fillRect(self.rect(), self.bg_color)

        # 刻度
        self._draw_ticks(painter)

        # 绘制高亮边界
        if self.highlighted_bounds:
            self._draw_bounds_highlight(painter)

        # 绘制光标标记
        if self.show_cursor and self.cursor_pos_mm is not None:
            self._draw_cursor_marker(painter)

        painter.end()

    def _draw_ticks(self, painter):
        """绘制刻度和标签"""
        # === 根据单位设置网格参数 ===
        if self.unit == MeasurementUnit.MM:
            major_step_mm = 5.0  # 主刻度（带标签）每 5mm → 0, 5, 10, 15, 20, 25
            minor_step_mm = 2.0  # 次刻度每 2mm（与 canvas 网格一致）
            decimals = 0  # 标签无小数

        elif self.unit == MeasurementUnit.CM:
            major_step_mm = 10.0  # 主刻度每 1cm
            minor_step_mm = 5.0  # 次刻度每 0.5cm
            decimals = 1  # 标签带 1 位小数

        elif self.unit == MeasurementUnit.INCH:
            major_step_mm = 25.4  # 主刻度每 1 inch
            minor_step_mm = 25.4 / 8  # 次刻度每 1/8 inch
            decimals = 2  # 标签带 2 位小数

        # === 绘制刻度 ===
        # 收集所有刻度位置（主刻度 + 次刻度）
        tick_positions = set()

        # 添加主刻度位置（每 5mm）
        mm = 0.0
        while mm <= self.length_mm:
            tick_positions.add(mm)
            mm += major_step_mm

        # 添加次刻度位置（每 2mm）
        mm = 0.0
        while mm <= self.length_mm:
            tick_positions.add(mm)
            mm += minor_step_mm

        # 绘制所有刻度
        for pos_mm in sorted(tick_positions):
            # 确定是否为主刻度（带标签）
            is_major = (abs(pos_mm % major_step_mm) < 0.01)

            # 刻度在像素中的位置
            pos_px = round(self._mm_to_px(pos_mm) * self.scale_factor)

            if is_major:
                # 带标签的主刻度
                tick_length = self.major_tick_length

                # 以选定单位显示标签
                label_mm = pos_mm
                label_value = UnitConverter.mm_to_unit(label_mm, self.unit)

                if decimals == 0:
                    label_text = f"{int(label_value)}"
                else:
                    label_text = f"{label_value:.{decimals}f}"

                # 绘制刻度
                self._draw_tick_at_px(painter, pos_px, tick_length, self.major_tick_color, width=2)
                self._draw_label_at_px(painter, pos_px, label_text)

            else:
                # 不带标签的次刻度
                tick_length = self.minor_tick_length
                self._draw_tick_at_px(painter, pos_px, tick_length, self.minor_tick_color, width=1)

    def _draw_tick_at_px(self, painter, pos_px, tick_length, color, width=1):
        """在像素位置绘制一个刻度"""
        pen = QPen(color, width)
        painter.setPen(pen)

        if self.orientation == Qt.Horizontal:
            # 水平标尺
            x = pos_px
            y1 = self.ruler_thickness - tick_length
            y2 = self.ruler_thickness
            painter.drawLine(x, y1, x, y2)
        else:
            # 垂直标尺
            x1 = self.ruler_thickness - tick_length
            x2 = self.ruler_thickness
            y = pos_px
            painter.drawLine(x1, y, x2, y)

    def _draw_label_at_px(self, painter, pos_px, text):
        """在像素位置绘制标签"""
        painter.setFont(self.font)
        painter.setPen(self.text_color)

        # 文本尺寸
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        text_height = fm.height()

        if self.orientation == Qt.Horizontal:
            # 水平标尺 - 文本在上方居中
            x = pos_px - text_width // 2
            y = self.ruler_thickness - self.major_tick_length - 2

            rect = QRect(x, 0, text_width, y)
            painter.drawText(rect, Qt.AlignCenter, text)
        else:
            # 垂直标尺 - 文本在左侧
            x = 2
            y = pos_px - text_height // 2

            rect = QRect(x, y, self.ruler_thickness - self.major_tick_length - 4, text_height)
            painter.drawText(rect, Qt.AlignRight | Qt.AlignVCenter, text)

    def update_cursor_position(self, mm):
        """更新标尺上的光标位置"""
        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        logger.debug(f"[RULER-{orientation_name}] 更新位置: {mm:.2f}mm")
        self.cursor_pos_mm = mm
        self.show_cursor = True
        self.update()  # 重新绘制

    def hide_cursor(self):
        """隐藏光标"""
        self.show_cursor = False
        self.update()

    def _draw_cursor_marker(self, painter):
        """在光标位置绘制红线"""
        pen = QPen(QColor(255, 0, 0), 2, Qt.SolidLine)
        painter.setPen(pen)

        pos_px = round(self._mm_to_px(self.cursor_pos_mm) * self.scale_factor)

        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        logger.debug(f"[RULER-{orientation_name}] 绘制位置: {pos_px}px")

        if self.orientation == Qt.Horizontal:
            # 水平标尺上的垂直线
            painter.drawLine(pos_px, 0, pos_px, self.ruler_thickness)
        else:
            # 垂直标尺上的水平线
            painter.drawLine(0, pos_px, self.ruler_thickness, pos_px)

    def highlight_bounds(self, start_mm, width_mm):
        """高亮元素边界"""
        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        end_mm = start_mm + width_mm
        logger.debug(
            f"[RULER-{orientation_name}] 边界已更新: 起始={start_mm:.2f}mm, "
            f"结束={end_mm:.2f}mm, 宽度={width_mm:.2f}mm"
        )
        self.highlighted_bounds = (start_mm, width_mm)
        self.update()

    def clear_highlight(self):
        """清除高亮"""
        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        logger.debug(f"[BOUNDS-{orientation_name}] 清除高亮")
        self.highlighted_bounds = None
        self.update()

    def _draw_bounds_highlight(self, painter):
        """绘制边界高亮"""
        start_mm, width_mm = self.highlighted_bounds

        start_px = round(self._mm_to_px(start_mm) * self.scale_factor)
        width_px = round(self._mm_to_px(width_mm) * self.scale_factor)

        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        logger.debug(f"[BOUNDS-{orientation_name}] 绘制: start_px={start_px}, width_px={width_px}")

        # 半透明蓝色矩形
        color = QColor(100, 150, 255, 80)

        if self.orientation == Qt.Horizontal:
            rect = QRect(start_px, 0, width_px, self.ruler_thickness)
        else:
            rect = QRect(0, start_px, self.ruler_thickness, width_px)

        painter.fillRect(rect, color)

        # 边框
        pen = QPen(QColor(50, 100, 255), 1)
        painter.setPen(pen)
        painter.drawRect(rect)

    def update_scale(self, scale_factor):
        """更新标尺缩放比例"""
        self.scale_factor = scale_factor

        # 重新计算长度
        self.length_px = round(self._mm_to_px(self.length_mm) * scale_factor)

        # 更新 widget 尺寸
        if self.orientation == Qt.Horizontal:
            self.setMinimumWidth(self.length_px)
        else:
            self.setMinimumHeight(self.length_px)

        # 重新绘制
        self.update()

    def set_length(self, length_mm):
        """更改标尺长度"""
        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        logger.debug(f"[RULER-{orientation_name}] set_length: {self.length_mm}mm -> {length_mm}mm")

        self.length_mm = length_mm
        self.length_px = round(self._mm_to_px(length_mm) * self.scale_factor)

        logger.debug(
            f"[RULER-{orientation_name}] 新长度: {length_mm}mm = {self.length_px}px (scale={self.scale_factor})")

        # 更新 widget 尺寸
        if self.orientation == Qt.Horizontal:
            self.setMinimumWidth(self.length_px)
        else:
            self.setMinimumHeight(self.length_px)

        # 重新绘制
        self.update()
        logger.debug(f"[RULER-{orientation_name}] 标尺已更新")


class HorizontalRuler(RulerWidget):
    """水平标尺（便捷别名）"""

    def __init__(self, length_mm, dpi, scale=2.5):
        super().__init__(Qt.Horizontal, length_mm, dpi, scale)


class VerticalRuler(RulerWidget):
    """垂直标尺（便捷别名）"""

    def __init__(self, length_mm, dpi, scale=2.5):
        super().__init__(Qt.Vertical, length_mm, dpi, scale)