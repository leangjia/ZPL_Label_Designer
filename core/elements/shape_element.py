# -*- coding: utf-8 -*-
"""ZPL 标签设计器的形状元素"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF, QRectF, QLineF
from PySide6.QtGui import QPen, QBrush, QColor

from core.elements.base import BaseElement, ElementConfig
from utils.logger import logger


class ShapeConfig(ElementConfig):
    """形状元素的基础配置"""

    def __init__(self, x=0, y=0, width=50, height=50,
                 fill=False, border_thickness=2, color='black'):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.fill = fill
        self.border_thickness = border_thickness
        self.color = color


class RectangleElement(BaseElement):
    """矩形元素"""

    def __init__(self, config=None):
        if config is None:
            config = ShapeConfig()
        super().__init__(config)
        logger.debug(f"[形状-矩形] 已创建: 尺寸=({config.width}x{config.height})mm, 填充={config.fill}")

    def to_dict(self):
        """序列化到 dict"""
        return {
            'type': 'rectangle',
            'x': self.config.x,
            'y': self.config.y,
            'width': self.config.width,
            'height': self.config.height,
            'fill': self.config.fill,
            'border_thickness': self.config.border_thickness,
            'color': self.config.color
        }

    @classmethod
    def from_dict(cls, data):
        """从 dict 反序列化"""
        config = ShapeConfig(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height'],
            fill=data.get('fill', False),
            border_thickness=data.get('border_thickness', 2),
            color=data.get('color', 'black')
        )
        return cls(config)

    def to_zpl(self, dpi=203):
        """生成矩形的 ZPL 命令

        格式: ^GB{宽度},{高度},{厚度},{颜色},{圆角}
        """
        # 转换坐标 mm -> dots
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        width_dots = int(self.config.width * dpi / 25.4)
        height_dots = int(self.config.height * dpi / 25.4)

        logger.debug(f"[形状-ZPL-矩形] 位置: ({x_dots}, {y_dots}) 点")
        logger.debug(f"[形状-ZPL-矩形] 尺寸: ({width_dots}x{height_dots}) 点")

        # 确定填充的厚度
        if self.config.fill:
            # 填充: 厚度 = 高度
            thickness = height_dots
        else:
            # 边框: 厚度（点）
            thickness = int(self.config.border_thickness * dpi / 25.4)

        logger.debug(f"[形状-ZPL-矩形] 填充={self.config.fill}, 厚度={thickness}")

        # 颜色 (B=黑色, W=白色)
        color = 'B' if self.config.color == 'black' else 'W'

        # 圆角 (0 = 无圆角)
        rounding = 0

        zpl_commands = [
            f"^FO{x_dots},{y_dots}",
            f"^GB{width_dots},{height_dots},{thickness},{color},{rounding}",
            "^FS"
        ]

        logger.debug(f"[形状-ZPL-矩形] 已生成 ZPL")
        return "\n".join(zpl_commands)


class CircleElement(BaseElement):
    """圆形元素，支持直径和自动切换到椭圆"""

    def __init__(self, config=None):
        if config is None:
            config = ShapeConfig(width=50, height=50)
        super().__init__(config)
        logger.debug(f"[形状-圆形] 已创建: 尺寸=({config.width}x{config.height})mm, 填充={config.fill}")

    @property
    def is_circle(self):
        """如果 width == height 则为 True（容差 0.1mm）"""
        is_circ = abs(self.config.width - self.config.height) < 0.1
        logger.debug(f"[圆形] is_circle 检查: 宽={self.config.width:.2f}, 高={self.config.height:.2f}, 结果={is_circ}")
        return is_circ

    @property
    def diameter(self):
        """圆的直径（如果是圆）"""
        if self.is_circle:
            return self.config.width
        return None

    @diameter.setter
    def diameter(self, value):
        """设置直径 → 同步 width/height"""
        logger.debug(f"[圆形] 设置直径: {value:.2f}mm")
        self.config.width = value
        self.config.height = value
        logger.debug(
            f"[圆形] 设置直径后: 宽={self.config.width:.2f}, 高={self.config.height:.2f}, is_circle={self.is_circle}")

    def set_width(self, width_mm):
        """更改宽度时检查 is_circle"""
        old_is_circle = self.is_circle
        self.config.width = width_mm
        new_is_circle = self.is_circle

        logger.debug(f"[圆形] 设置宽度: {width_mm:.2f}mm")
        logger.debug(f"[圆形] 形状变化: {old_is_circle} -> {new_is_circle}")

        if old_is_circle and not new_is_circle:
            logger.info(f"[圆形] 形状已改变: 圆形 -> 椭圆")
        elif not old_is_circle and new_is_circle:
            logger.info(f"[圆形] 形状已改变: 椭圆 -> 圆形")

    def set_height(self, height_mm):
        """更改高度时检查 is_circle"""
        old_is_circle = self.is_circle
        self.config.height = height_mm
        new_is_circle = self.is_circle

        logger.debug(f"[圆形] 设置高度: {height_mm:.2f}mm")
        logger.debug(f"[圆形] 形状变化: {old_is_circle} -> {new_is_circle}")

        if old_is_circle and not new_is_circle:
            logger.info(f"[圆形] 形状已改变: 圆形 -> 椭圆")
        elif not old_is_circle and new_is_circle:
            logger.info(f"[圆形] 形状已改变: 椭圆 -> 圆形")

    def to_dict(self):
        """序列化到 dict"""
        return {
            'type': 'circle',
            'x': self.config.x,
            'y': self.config.y,
            'width': self.config.width,
            'height': self.config.height,
            'fill': self.config.fill,
            'border_thickness': self.config.border_thickness,
            'color': self.config.color
        }

    @classmethod
    def from_dict(cls, data):
        """从 dict 反序列化"""
        config = ShapeConfig(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height'],
            fill=data.get('fill', False),
            border_thickness=data.get('border_thickness', 2),
            color=data.get('color', 'black')
        )
        return cls(config)

    def to_zpl(self, dpi=203):
        """生成圆形或椭圆的 ZPL 命令

        格式: ^GC{直径},{厚度},{颜色} - 用于圆形
        格式: ^GE{宽度},{高度},{厚度},{颜色} - 用于椭圆
        """
        # 转换坐标 mm -> dots
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        width_dots = int(self.config.width * dpi / 25.4)
        height_dots = int(self.config.height * dpi / 25.4)

        logger.debug(f"[形状-ZPL-圆形] 位置: ({x_dots}, {y_dots}) 点")
        logger.debug(f"[形状-ZPL-圆形] 尺寸: {width_dots}x{height_dots} 点, is_circle={self.is_circle}")

        # 确定厚度
        thickness_mm = self.config.border_thickness
        thickness_dots = int(thickness_mm * dpi / 25.4)

        # 颜色 (B=黑色, W=白色)
        color = 'B' if self.config.color == 'black' else 'W'

        if self.is_circle:
            # 圆形: ^GC{直径},{厚度},{颜色}
            diameter_dots = width_dots  # width == height

            # 测试日志: mm -> dots
            logger.debug(f"[ZPL-圆形] 圆形: 直径={self.diameter:.2f}mm -> {diameter_dots}点")

            if self.config.fill:
                # 填充: 厚度 = 直径
                thickness = diameter_dots
            else:
                # 边框: 厚度（点）
                thickness = thickness_dots

            logger.debug(f"[形状-ZPL-圆形] ^GC 格式: 直径={diameter_dots}, 厚度={thickness}, 填充={self.config.fill}")

            zpl_commands = [
                f"^FO{x_dots},{y_dots}",
                f"^GC{diameter_dots},{thickness},{color}",
                "^FS"
            ]

            # 测试日志: 生成的 ZPL
            logger.debug(f"[ZPL-圆形] 生成的圆形: {''.join(zpl_commands)}")
        else:
            # 椭圆: ^GE{宽度},{高度},{厚度},{颜色}

            # 测试日志: mm -> dots
            logger.debug(
                f"[ZPL-圆形] 椭圆: 宽={self.config.width:.2f}mm, 高={self.config.height:.2f}mm -> {width_dots}x{height_dots}点")

            if self.config.fill:
                # 填充: 厚度 = 高度
                thickness = height_dots
            else:
                # 边框: 厚度（点）
                thickness = thickness_dots

            logger.debug(
                f"[形状-ZPL-椭圆] ^GE 格式: 宽度={width_dots}, 高度={height_dots}, 厚度={thickness}, 填充={self.config.fill}")

            zpl_commands = [
                f"^FO{x_dots},{y_dots}",
                f"^GE{width_dots},{height_dots},{thickness},{color}",
                "^FS"
            ]

            # 测试日志: 生成的 ZPL
            logger.debug(f"[ZPL-圆形] 生成的椭圆: {''.join(zpl_commands)}")

        logger.debug(f"[形状-ZPL] 已生成 {'圆形' if self.is_circle else '椭圆'} 的 ZPL")
        return "\n".join(zpl_commands)


class LineConfig(ElementConfig):
    """线条元素的配置"""

    def __init__(self, x=0, y=0, x2=50, y2=50, thickness=2, color='black'):
        super().__init__(x, y)
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness
        self.color = color


class LineElement(BaseElement):
    """线条元素"""

    def __init__(self, config=None):
        if config is None:
            config = LineConfig()
        super().__init__(config)
        logger.debug(f"[形状-线条] 已创建: 从 ({config.x},{config.y}) 到 ({config.x2},{config.y2})mm")

    def to_dict(self):
        """序列化到 dict"""
        return {
            'type': 'line',
            'x': self.config.x,
            'y': self.config.y,
            'x2': self.config.x2,
            'y2': self.config.y2,
            'thickness': self.config.thickness,
            'color': self.config.color
        }

    @classmethod
    def from_dict(cls, data):
        """从 dict 反序列化"""
        config = LineConfig(
            x=data['x'],
            y=data['y'],
            x2=data['x2'],
            y2=data['y2'],
            thickness=data.get('thickness', 2),
            color=data.get('color', 'black')
        )
        return cls(config)

    def to_zpl(self, dpi=203):
        """生成线条的 ZPL 命令

        水平/垂直: ^GB{宽度},{高度},{厚度}
        对角线: ^GD{宽度},{高度},{厚度},{颜色},{方向}
        """
        # 转换坐标 mm -> dots
        x1_dots = int(self.config.x * dpi / 25.4)
        y1_dots = int(self.config.y * dpi / 25.4)
        x2_dots = int(self.config.x2 * dpi / 25.4)
        y2_dots = int(self.config.y2 * dpi / 25.4)

        # 计算宽度和高度
        width_dots = abs(x2_dots - x1_dots)
        height_dots = abs(y2_dots - y1_dots)

        logger.debug(f"[形状-ZPL-线条] 从: ({x1_dots}, {y1_dots}) 点")
        logger.debug(f"[形状-ZPL-线条] 到: ({x2_dots}, {y2_dots}) 点")
        logger.debug(f"[形状-ZPL-线条] 宽度: {width_dots}, 高度: {height_dots} 点")

        # 厚度（点）
        thickness = int(self.config.thickness * dpi / 25.4)

        # 颜色 (B=黑色, W=白色)
        color = 'B' if self.config.color == 'black' else 'W'

        # 关键: 确定线条类型
        is_horizontal = (height_dots == 0)
        is_vertical = (width_dots == 0)

        if is_horizontal:
            # 水平线: ^GB{宽度},{厚度},{厚度}
            logger.debug(f"[形状-ZPL-线条] 类型: 水平, 使用 ^GB")
            zpl_commands = [
                f"^FO{x1_dots},{y1_dots}",
                f"^GB{width_dots},{thickness},{thickness},{color},0",
                "^FS"
            ]
        elif is_vertical:
            # 垂直线: ^GB{厚度},{高度},{厚度}
            logger.debug(f"[形状-ZPL-线条] 类型: 垂直, 使用 ^GB")
            zpl_commands = [
                f"^FO{x1_dots},{y1_dots}",
                f"^GB{thickness},{height_dots},{thickness},{color},0",
                "^FS"
            ]
        else:
            # 对角线: ^GD
            # 方向: L (左斜 \), R (右斜 /)
            dx = x2_dots - x1_dots
            dy = y2_dots - y1_dots

            if dx * dy < 0:  # 不同符号 = /
                orientation = 'R'
            else:  # 相同符号 = \
                orientation = 'L'

            logger.debug(f"[形状-ZPL-线条] 类型: 对角线, 方向={orientation}, 使用 ^GD")

            zpl_commands = [
                f"^FO{x1_dots},{y1_dots}",
                f"^GD{width_dots},{height_dots},{thickness},{color},{orientation}",
                "^FS"
            ]

        logger.debug(f"[形状-ZPL-线条] 已生成 ZPL: {zpl_commands[1]}")
        return "\n".join(zpl_commands)


# === 图形项 ===

class GraphicsRectangleItem(QGraphicsRectItem):
    """画布上矩形的图形项"""

    def __init__(self, element, dpi=203, canvas=None, parent=None):
        super().__init__(parent)
        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # 引用 canvas 用于 GridConfig

        # 关键: 在 setPos() 之前创建！
        self.snap_enabled = True
        self.grid_step_mm = 1.0
        self.snap_threshold_mm = 1.0

        # 设置尺寸
        width_px = self._mm_to_px(element.config.width)
        height_px = self._mm_to_px(element.config.height)
        self.setRect(0, 0, width_px, height_px)

        # 设置样式
        self._update_style()

        # 设置位置
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)

        # 拖放标志
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        logger.debug(f"[形状项-矩形] 已创建于: ({element.config.x:.2f}, {element.config.y:.2f})mm")

    def _update_style(self):
        """更新样式（填充/边框）"""
        color = QColor('black') if self.element.config.color == 'black' else QColor('white')

        if self.element.config.fill:
            # 填充
            self.setBrush(QBrush(color))
            self.setPen(QPen(Qt.NoPen))
        else:
            # 边框
            thickness_px = self._mm_to_px(self.element.config.border_thickness)
            self.setBrush(QBrush(Qt.NoBrush))
            # 关键: 设置 MiterJoin 用于锐角！
            pen = QPen(color, thickness_px)
            pen.setJoinStyle(Qt.MiterJoin)
            self.setPen(pen)

        logger.debug(f"[形状项-矩形] 样式已更新: 填充={self.element.config.fill}")

    def itemChange(self, change, value):
        """重写用于网格对齐"""
        if change == QGraphicsItem.ItemPositionChange:
            new_pos = value

            # 转换为毫米
            x_mm = self._px_to_mm(new_pos.x())
            y_mm = self._px_to_mm(new_pos.y())

            logger.debug(
                f"[项目拖拽] 位置变化中: ({new_pos.x():.2f}, {new_pos.y():.2f})px -> "
                f"({x_mm:.2f}, {y_mm:.2f})mm"
            )

            # 拖拽时发送光标位置给标尺
            if self.canvas:
                logger.debug(f"[项目拖拽] 发送光标: ({x_mm:.2f}, {y_mm:.2f})mm")
                self.canvas.cursor_position_changed.emit(x_mm, y_mm)

            if self.snap_enabled:
                # 对齐到网格（分别处理 X 和 Y）
                snapped_x = self._snap_to_grid(x_mm, 'x')
                snapped_y = self._snap_to_grid(y_mm, 'y')

                # 转换回像素
                snapped_pos = QPointF(
                    self._mm_to_px(snapped_x),
                    self._mm_to_px(snapped_y)
                )

                return snapped_pos

            return new_pos

        elif change == QGraphicsItem.ItemPositionHasChanged:
            # 移动后更新配置
            x_mm = self._px_to_mm(self.pos().x())
            y_mm = self._px_to_mm(self.pos().y())

            logger.debug(
                f"[项目拖拽] 位置已改变（原始）: ({self.pos().x():.2f}, {self.pos().y():.2f})px -> "
                f"({x_mm:.2f}, {y_mm:.2f})mm"
            )

            self.element.config.x = x_mm
            self.element.config.y = y_mm

            if (
                    self.canvas
                    and getattr(self.canvas, 'bounds_update_callback', None)
                    and self.isSelected()
            ):
                logger.debug(
                    f"[项目拖拽] 位置已改变: 需要边界更新 "
                    f"({self.element.config.x:.2f}, {self.element.config.y:.2f})mm"
                )
                self.canvas.bounds_update_callback(self)

        return super().itemChange(change, value)

    def _snap_to_grid(self, value_mm, axis='x'):
        """使用 GridConfig（大小、偏移量）对齐到网格"""
        from config import SnapMode

        # 回退用于没有 canvas 的旧元素
        if not self.canvas:
            logger.debug(f"[对齐回退] 使用默认值: 大小=1.0mm, 偏移=0.0mm")
            size = 1.0
            offset = 0.0
            threshold = 1.0
        else:
            config = self.canvas.grid_config

            # 检查对齐模式
            if config.snap_mode != SnapMode.GRID:
                logger.debug(f"[对齐] 模式={config.snap_mode.value}, 跳过网格对齐")
                return value_mm

            size = config.size_x_mm if axis == 'x' else config.size_y_mm
            offset = config.offset_x_mm if axis == 'x' else config.offset_y_mm
            threshold = size / 2

            logger.debug(f"[对齐-{axis.upper()}] 值: {value_mm:.2f}mm, 偏移: {offset:.2f}mm, 大小: {size:.2f}mm")

        # 对齐公式: nearest = offset + round((value - offset) / size) * size
        relative = value_mm - offset
        rounded = round(relative / size) * size + offset

        logger.debug(f"[对齐-{axis.upper()}] 相对: {relative:.2f}mm, 四舍五入: {rounded:.2f}mm")

        if abs(value_mm - rounded) <= threshold:
            logger.debug(f"[对齐-{axis.upper()}] 结果: {value_mm:.2f}mm -> {rounded:.2f}mm")
            return rounded

        logger.debug(f"[对齐-{axis.upper()}] 未对齐（距离 > 阈值）")
        return value_mm

    def _mm_to_px(self, mm):
        """转换毫米 -> 像素"""
        return mm * self.dpi / 25.4

    def _px_to_mm(self, px):
        """转换像素 -> 毫米"""
        return px * 25.4 / self.dpi

    def update_from_element(self):
        """从元素配置更新图形项"""
        width_px = self._mm_to_px(self.element.config.width)
        height_px = self._mm_to_px(self.element.config.height)
        self.setRect(0, 0, width_px, height_px)

        self._update_style()

        x_px = self._mm_to_px(self.element.config.x)
        y_px = self._mm_to_px(self.element.config.y)
        self.setPos(x_px, y_px)

        logger.debug(f"[形状项-矩形] 从元素更新")


class GraphicsCircleItem(QGraphicsEllipseItem):
    """画布上圆形的图形项"""

    def __init__(self, element, dpi=203, canvas=None, parent=None):
        super().__init__(parent)
        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # 引用 canvas 用于 GridConfig

        # 关键: 在 setPos() 之前创建！
        self.snap_enabled = True
        self.grid_step_mm = 1.0
        self.snap_threshold_mm = 1.0

        # 设置尺寸（椭圆）
        width_px = self._mm_to_px(element.config.width)
        height_px = self._mm_to_px(element.config.height)
        self.setRect(0, 0, width_px, height_px)

        # 设置样式
        self._update_style()

        # 设置位置
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)

        # 拖放标志
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        logger.debug(f"[形状项-圆形] 已创建于: ({element.config.x:.2f}, {element.config.y:.2f})mm")

    def _update_style(self):
        """更新样式（填充/边框）"""
        color = QColor('black') if self.element.config.color == 'black' else QColor('white')

        if self.element.config.fill:
            # 填充
            self.setBrush(QBrush(color))
            self.setPen(QPen(Qt.NoPen))
        else:
            # 边框
            thickness_px = self._mm_to_px(self.element.config.border_thickness)
            self.setBrush(QBrush(Qt.NoBrush))
            # 关键: 设置 MiterJoin 用于锐角！
            pen = QPen(color, thickness_px)
            pen.setJoinStyle(Qt.MiterJoin)
            self.setPen(pen)

        logger.debug(f"[形状项-圆形] 样式已更新: 填充={self.element.config.fill}")

    def itemChange(self, change, value):
        """重写用于网格对齐 - 类似于矩形"""
        if change == QGraphicsItem.ItemPositionChange:
            new_pos = value

            x_mm = self._px_to_mm(new_pos.x())
            y_mm = self._px_to_mm(new_pos.y())

            logger.debug(
                f"[项目拖拽] 位置变化中: ({new_pos.x():.2f}, {new_pos.y():.2f})px -> "
                f"({x_mm:.2f}, {y_mm:.2f})mm"
            )

            # 拖拽时发送光标位置给标尺
            if self.canvas:
                logger.debug(f"[项目拖拽] 发送光标: ({x_mm:.2f}, {y_mm:.2f})mm")
                self.canvas.cursor_position_changed.emit(x_mm, y_mm)

            if self.snap_enabled:
                snapped_x = self._snap_to_grid(x_mm, 'x')
                snapped_y = self._snap_to_grid(y_mm, 'y')

                snapped_pos = QPointF(
                    self._mm_to_px(snapped_x),
                    self._mm_to_px(snapped_y)
                )

                return snapped_pos

            return new_pos

        elif change == QGraphicsItem.ItemPositionHasChanged:
            x_mm = self._px_to_mm(self.pos().x())
            y_mm = self._px_to_mm(self.pos().y())

            logger.debug(
                f"[项目拖拽] 位置已改变（原始）: ({self.pos().x():.2f}, {self.pos().y():.2f})px -> "
                f"({x_mm:.2f}, {y_mm:.2f})mm"
            )

            self.element.config.x = x_mm
            self.element.config.y = y_mm

            if (
                    self.canvas
                    and getattr(self.canvas, 'bounds_update_callback', None)
                    and self.isSelected()
            ):
                logger.debug(
                    f"[项目拖拽] 位置已改变: 需要边界更新 "
                    f"({self.element.config.x:.2f}, {self.element.config.y:.2f})mm"
                )
                self.canvas.bounds_update_callback(self)

        return super().itemChange(change, value)

    def _snap_to_grid(self, value_mm, axis='x'):
        """使用 GridConfig（大小、偏移量）对齐到网格"""
        from config import SnapMode

        # 回退用于没有 canvas 的旧元素
        if not self.canvas:
            logger.debug(f"[对齐回退] 使用默认值: 大小=1.0mm, 偏移=0.0mm")
            size = 1.0
            offset = 0.0
            threshold = 1.0
        else:
            config = self.canvas.grid_config

            # 检查对齐模式
            if config.snap_mode != SnapMode.GRID:
                logger.debug(f"[对齐] 模式={config.snap_mode.value}, 跳过网格对齐")
                return value_mm

            size = config.size_x_mm if axis == 'x' else config.size_y_mm
            offset = config.offset_x_mm if axis == 'x' else config.offset_y_mm
            threshold = size / 2

            logger.debug(f"[对齐-{axis.upper()}] 值: {value_mm:.2f}mm, 偏移: {offset:.2f}mm, 大小: {size:.2f}mm")

        # 对齐公式: nearest = offset + round((value - offset) / size) * size
        relative = value_mm - offset
        rounded = round(relative / size) * size + offset

        logger.debug(f"[对齐-{axis.upper()}] 相对: {relative:.2f}mm, 四舍五入: {rounded:.2f}mm")

        if abs(value_mm - rounded) <= threshold:
            logger.debug(f"[对齐-{axis.upper()}] 结果: {value_mm:.2f}mm -> {rounded:.2f}mm")
            return rounded

        logger.debug(f"[对齐-{axis.upper()}] 未对齐（距离 > 阈值）")
        return value_mm

    def _mm_to_px(self, mm):
        """转换毫米 -> 像素"""
        return mm * self.dpi / 25.4

    def _px_to_mm(self, px):
        """转换像素 -> 毫米"""
        return px * 25.4 / self.dpi

    def update_from_element(self):
        """从元素配置更新图形项"""
        width_px = self._mm_to_px(self.element.config.width)
        height_px = self._mm_to_px(self.element.config.height)
        self.setRect(0, 0, width_px, height_px)

        self._update_style()

        x_px = self._mm_to_px(self.element.config.x)
        y_px = self._mm_to_px(self.element.config.y)
        self.setPos(x_px, y_px)

        logger.debug(f"[形状项-圆形] 从元素更新")


class GraphicsLineItem(QGraphicsLineItem):
    """画布上线条的图形项"""

    def __init__(self, element, dpi=203, canvas=None, parent=None):
        super().__init__(parent)
        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # 引用 canvas 用于 GridConfig

        # 关键: 在 setPos() 之前创建！
        self.snap_enabled = True
        self.grid_step_mm = 1.0
        self.snap_threshold_mm = 1.0

        # 设置线条 - 使用相对坐标
        x1_px = self._mm_to_px(element.config.x)
        y1_px = self._mm_to_px(element.config.y)
        x2_px = self._mm_to_px(element.config.x2)
        y2_px = self._mm_to_px(element.config.y2)

        # 关键: setPos() = 起点（绝对坐标）, setLine() = 线条向量（相对坐标）
        self.setPos(x1_px, y1_px)
        self.setLine(0, 0, x2_px - x1_px, y2_px - y1_px)

        logger.debug(
            f"[线条坐标] 元素: ({element.config.x:.2f}, {element.config.y:.2f}) -> ({element.config.x2:.2f}, {element.config.y2:.2f})mm")
        logger.debug(f"[线条坐标] setPos: ({x1_px:.2f}, {y1_px:.2f})px")
        logger.debug(f"[线条坐标] setLine: (0, 0) -> ({x2_px - x1_px:.2f}, {y2_px - y1_px:.2f})px")

        # 设置样式
        self._update_style()

        # 拖放标志
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        logger.debug(
            f"[形状项-线条] 已创建: 从 ({element.config.x:.2f},{element.config.y:.2f}) 到 ({element.config.x2:.2f},{element.config.y2:.2f})mm")

    def _update_style(self):
        """更新样式（厚度、颜色）"""
        color = QColor('black') if self.element.config.color == 'black' else QColor('white')
        thickness_px = self._mm_to_px(self.element.config.thickness)

        # 关键: 设置 MiterJoin 用于锐角！
        pen = QPen(color, thickness_px)
        pen.setJoinStyle(Qt.MiterJoin)
        pen.setCapStyle(Qt.SquareCap)  # 线条的方形端点
        self.setPen(pen)

        logger.debug(f"[形状项-线条] 样式已更新: 厚度={self.element.config.thickness}mm")

    def itemChange(self, change, value):
        """两个端点的网格对齐"""
        if change == QGraphicsItem.ItemPositionChange:
            new_pos = value

            # 起点毫米
            x1_mm = self._px_to_mm(new_pos.x())
            y1_mm = self._px_to_mm(new_pos.y())

            logger.debug(f"[线条拖拽] 对齐前起点: ({x1_mm:.2f}, {y1_mm:.2f})mm")

            # 终点毫米（绝对坐标 = 起点 + 向量）
            line_vector = self.line()
            x2_mm = self._px_to_mm(new_pos.x() + line_vector.x2())
            y2_mm = self._px_to_mm(new_pos.y() + line_vector.y2())

            logger.debug(f"[线条拖拽] 对齐前终点: ({x2_mm:.2f}, {y2_mm:.2f})mm")

            # 发送光标
            if self.canvas:
                self.canvas.cursor_position_changed.emit(x1_mm, y1_mm)

            if self.snap_enabled:
                # 对齐两个端点！
                snapped_x1 = self._snap_to_grid(x1_mm, 'x')
                snapped_y1 = self._snap_to_grid(y1_mm, 'y')
                snapped_x2 = self._snap_to_grid(x2_mm, 'x')
                snapped_y2 = self._snap_to_grid(y2_mm, 'y')

                logger.debug(f"[线条对齐] 起点: ({x1_mm:.2f}, {y1_mm:.2f}) -> ({snapped_x1:.2f}, {snapped_y1:.2f})mm")
                logger.debug(f"[线条对齐] 终点: ({x2_mm:.2f}, {y2_mm:.2f}) -> ({snapped_x2:.2f}, {snapped_y2:.2f})mm")

                # 新的起点位置
                snapped_pos = QPointF(
                    self._mm_to_px(snapped_x1),
                    self._mm_to_px(snapped_y1)
                )

                # 新的线条向量 RELATIVE (对齐终点 - 对齐起点)
                new_vector_x_px = self._mm_to_px(snapped_x2 - snapped_x1)
                new_vector_y_px = self._mm_to_px(snapped_y2 - snapped_y1)

                # 关键: 更新线条向量！
                self.setLine(0, 0, new_vector_x_px, new_vector_y_px)

                logger.debug(f"[线条对齐] 新向量: ({new_vector_x_px:.2f}, {new_vector_y_px:.2f})px")

                return snapped_pos

            return new_pos

        elif change == QGraphicsItem.ItemPositionHasChanged:
            # 保存对齐后的坐标
            line_vector = self.line()
            x1_mm = self._px_to_mm(self.pos().x())
            y1_mm = self._px_to_mm(self.pos().y())
            x2_mm = self._px_to_mm(self.pos().x() + line_vector.x2())
            y2_mm = self._px_to_mm(self.pos().y() + line_vector.y2())

            logger.debug(f"[线条最终] 起点: ({x1_mm:.2f}, {y1_mm:.2f})mm")
            logger.debug(f"[线条最终] 终点: ({x2_mm:.2f}, {y2_mm:.2f})mm")

            self.element.config.x = x1_mm
            self.element.config.y = y1_mm
            self.element.config.x2 = x2_mm
            self.element.config.y2 = y2_mm

            logger.debug(f"[线条最终] 已保存: 起点=({x1_mm:.2f}, {y1_mm:.2f}), 终点=({x2_mm:.2f}, {y2_mm:.2f})mm")

            if self.canvas and getattr(self.canvas, 'bounds_update_callback', None) and self.isSelected():
                self.canvas.bounds_update_callback(self)

        return super().itemChange(change, value)

    def _snap_to_grid(self, value_mm, axis='x'):
        """使用 GridConfig（大小、偏移量）对齐到网格"""
        from config import SnapMode

        # 回退用于没有 canvas 的旧元素
        if not self.canvas:
            logger.debug(f"[对齐回退] 使用默认值: 大小=1.0mm, 偏移=0.0mm")
            size = 1.0
            offset = 0.0
            threshold = 1.0
        else:
            config = self.canvas.grid_config

            # 检查对齐模式
            if config.snap_mode != SnapMode.GRID:
                logger.debug(f"[对齐] 模式={config.snap_mode.value}, 跳过网格对齐")
                return value_mm

            size = config.size_x_mm if axis == 'x' else config.size_y_mm
            offset = config.offset_x_mm if axis == 'x' else config.offset_y_mm
            threshold = size / 2

            logger.debug(f"[对齐-{axis.upper()}] 值: {value_mm:.2f}mm, 偏移: {offset:.2f}mm, 大小: {size:.2f}mm")

        # 对齐公式: nearest = offset + round((value - offset) / size) * size
        relative = value_mm - offset
        rounded = round(relative / size) * size + offset

        logger.debug(f"[对齐-{axis.upper()}] 相对: {relative:.2f}mm, 四舍五入: {rounded:.2f}mm")

        if abs(value_mm - rounded) <= threshold:
            logger.debug(f"[对齐-{axis.upper()}] 结果: {value_mm:.2f}mm -> {rounded:.2f}mm")
            return rounded

        logger.debug(f"[对齐-{axis.upper()}] 未对齐（距离 > 阈值）")
        return value_mm

    def _mm_to_px(self, mm):
        """转换毫米 -> 像素"""
        return mm * self.dpi / 25.4

    def _px_to_mm(self, px):
        """转换像素 -> 毫米"""
        return px * 25.4 / self.dpi

    def update_from_element(self):
        """从元素配置更新图形项"""
        x1_px = self._mm_to_px(self.element.config.x)
        y1_px = self._mm_to_px(self.element.config.y)
        x2_px = self._mm_to_px(self.element.config.x2)
        y2_px = self._mm_to_px(self.element.config.y2)

        # 关键: 使用 RELATIVE 坐标用于 setLine
        self.setPos(x1_px, y1_px)
        self.setLine(0, 0, x2_px - x1_px, y2_px - y1_px)
        self._update_style()

        logger.debug(
            f"[线条更新] 元素: ({self.element.config.x:.2f}, {self.element.config.y:.2f}) -> ({self.element.config.x2:.2f}, {self.element.config.y2:.2f})mm")
        logger.debug(f"[线条更新] setPos: ({x1_px:.2f}, {y1_px:.2f})px")
        logger.debug(f"[线条更新] setLine: (0, 0) -> ({x2_px - x1_px:.2f}, {y2_px - y1_px:.2f})px")
        logger.debug(f"[形状项-线条] 从元素更新")