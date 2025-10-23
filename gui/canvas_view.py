# -*- coding: utf-8 -*-
"""用于标签视觉编辑的画布"""

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPen, QColor, QPainter

from config import GridConfig
from utils.logger import logger
from utils.settings_manager import settings_manager


class CanvasView(QGraphicsView):
    """带网格的标签设计画布"""

    # 光标追踪信号
    cursor_position_changed = Signal(float, float)  # x_mm, y_mm
    context_menu_requested = Signal(object, QPoint)  # (item, global_pos)

    def __init__(self, width_mm=28, height_mm=28, dpi=203):
        super().__init__()

        self.dpi = dpi
        self.width_mm = width_mm
        self.height_mm = height_mm

        # 毫米 -> 像素转换
        self.width_px = round(self._mm_to_px(width_mm))
        self.height_px = round(self._mm_to_px(height_mm))

        # 创建场景
        self.scene = QGraphicsScene(0, 0, self.width_px, self.height_px)
        self.setScene(self.scene)

        # 将场景对齐到左上角（类似于 ZebraDesigner）
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # 禁用滚动条，使画布始终在位置 (0,0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 显示设置
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setBackgroundBrush(QColor(255, 255, 255))

        # 连接多选信号
        self.scene.selectionChanged.connect(self._on_selection_changed)

        # 网格设置
        saved_grid = settings_manager.load_grid_settings()
        self.grid_config = GridConfig(
            size_x_mm=saved_grid["size_x"],
            size_y_mm=saved_grid["size_y"],
            offset_x_mm=saved_grid["offset_x"],
            offset_y_mm=saved_grid["offset_y"],
            visible=saved_grid["show_gridlines"],
            snap_mode=saved_grid["snap_mode"],
        )
        logger.debug(
            "[网格] 默认尺寸已初始化: "
            f"{self.grid_config.size_x_mm}mm x {self.grid_config.size_y_mm}mm"
        )
        self.grid_items = []

        # 绘制网格
        self._draw_grid()

        # 缩放参数
        self.current_scale = 2.5
        self.min_scale = 0.5
        self.max_scale = 10.0

        # 应用初始缩放
        self.scale(self.current_scale, self.current_scale)

        # 标尺引用（将从主窗口设置）
        self.h_ruler = None
        self.v_ruler = None
        # 拖拽期间更新边界高亮的回调
        self.bounds_update_callback = None

        # 启用鼠标追踪
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)

        # 为视口安装事件过滤器以拦截滚轮事件
        self.viewport().installEventFilter(self)

    def _mm_to_px(self, mm):
        """毫米 -> 像素转换"""
        return mm * self.dpi / 25.4  # 浮点数以提高精度

    def _draw_grid(self):
        """使用 GridConfig 绘制网格（尺寸 X/Y，偏移 X/Y）"""
        config = self.grid_config
        logger.debug(f"[网格绘制] 配置: 尺寸 X={config.size_x_mm}mm, Y={config.size_y_mm}mm")
        logger.debug(f"[网格绘制] 配置: 偏移 X={config.offset_x_mm}mm, Y={config.offset_y_mm}mm")

        pen = QPen(QColor(200, 200, 200), 1, Qt.SolidLine)

        # 移除之前的网格
        for item in self.grid_items:
            try:
                self.scene.removeItem(item)
            except RuntimeError:
                pass
        self.grid_items = []

        # 垂直线 - 从 offset_x 开始，步长为 size_x
        mm = config.offset_x_mm
        while mm <= self.width_mm:
            x_px = round(self._mm_to_px(mm))
            logger.debug(f"[网格绘制] 垂直线: mm={mm:.2f}, px={x_px}")
            line = self.scene.addLine(x_px, 0, x_px, self.height_px, pen)
            line.setVisible(config.visible)
            self.grid_items.append(line)
            mm += config.size_x_mm

        # 水平线 - 从 offset_y 开始，步长为 size_y
        mm = config.offset_y_mm
        while mm <= self.height_mm:
            y_px = round(self._mm_to_px(mm))
            logger.debug(f"[网格绘制] 水平线: mm={mm:.2f}, px={y_px}")
            line = self.scene.addLine(0, y_px, self.width_px, y_px, pen)
            line.setVisible(config.visible)
            self.grid_items.append(line)
            mm += config.size_y_mm

        # 边框
        border_pen = QPen(QColor(0, 0, 0), 2, Qt.SolidLine)
        border = self.scene.addRect(0, 0, self.width_px, self.height_px, border_pen)
        self.grid_items.append(border)

        # 在创建所有项目后设置可见性
        for item in self.grid_items:
            item.setVisible(self.grid_config.visible)

        logger.debug(f"[网格绘制] 创建了 {len(self.grid_items)} 个项目，可见性: {self.grid_config.visible}")

    def set_grid_config(self, grid_config):
        """设置网格配置"""
        logger.debug(f"[网格配置] 设置: 尺寸 X={grid_config.size_x_mm}mm, Y={grid_config.size_y_mm}mm")
        logger.debug(f"[网格配置] 设置: 偏移 X={grid_config.offset_x_mm}mm, Y={grid_config.offset_y_mm}mm")
        self.grid_config = grid_config
        settings_manager.save_grid_settings(
            {
                "size_x": grid_config.size_x_mm,
                "size_y": grid_config.size_y_mm,
                "offset_x": grid_config.offset_x_mm,
                "offset_y": grid_config.offset_y_mm,
                "show_gridlines": grid_config.visible,
                "snap_mode": grid_config.snap_mode,
            }
        )

    def get_grid_config(self):
        """获取网格配置"""
        return self.grid_config

    def _redraw_grid(self):
        """使用新设置重新绘制网格"""
        logger.debug(f"[网格重绘] 使用配置重新绘制: {self.grid_config}")
        self._draw_grid()

    def set_grid_visible(self, visible: bool):
        """控制网格可见性"""
        self.grid_config.visible = visible
        logger.debug(f"[网格可见性] 设置为: {visible}")

        # 检查 grid_items 是否有效
        if not self.grid_items:
            logger.debug(f"[网格可见性] grid_items 为空，重新绘制")
            self._draw_grid()
            return

        # 检查项目是否仍在场景中
        items_valid = True
        for item in self.grid_items:
            if item is None or item.scene() is None:
                items_valid = False
                logger.debug(f"[网格可见性] grid_items 无效，重新绘制")
                break

        if not items_valid:
            self.grid_items = []
            self._draw_grid()
            return

        # 项目有效 → 只需更改可见性
        logger.debug(f"[网格可见性] 在 {len(self.grid_items)} 个项目上设置可见性")
        for item in self.grid_items:
            try:
                item.setVisible(visible)  # ← 已修复：使用参数 visible
            except RuntimeError:
                logger.debug(f"[网格可见性] RuntimeError，重新绘制")
                self.grid_items = []
                self._draw_grid()
                return

        logger.debug(f"[网格可见性] 成功将可见性设置为 {visible}")
        settings_manager.save_grid_settings(
            {
                "size_x": self.grid_config.size_x_mm,
                "size_y": self.grid_config.size_y_mm,
                "offset_x": self.grid_config.offset_x_mm,
                "offset_y": self.grid_config.offset_y_mm,
                "show_gridlines": visible,
                "snap_mode": self.grid_config.snap_mode,
            }
        )

    def _on_selection_changed(self):
        """处理选择变化（用于多选）"""
        try:
            selected = self.scene.selectedItems()
        except RuntimeError:
            # 应用程序关闭时场景已被删除
            return

        logger.debug(f"[选择] 选择的项目: {len(selected)}")

        if len(selected) > 1:
            logger.debug(f"[选择] 多选: {len(selected)} 个项目")

    def contextMenuEvent(self, event):
        """画布上的上下文菜单"""
        # 获取光标下的项目
        pos = self.mapToScene(event.pos())
        item = self.scene.itemAt(pos, self.transform())

        logger.debug(f"[上下文] 菜单位置: ({pos.x():.1f}, {pos.y():.1f})px")

        if item and hasattr(item, 'element'):
            logger.debug(f"[上下文] 找到项目: {item.element.__class__.__name__}")
            self.context_menu_requested.emit(item, event.globalPos())
        else:
            logger.debug(f"[上下文] 无项目 - 画布菜单")
            # 画布上下文菜单（如果有剪贴板内容可以是粘贴）
            self.context_menu_requested.emit(None, event.globalPos())

    def mouseMoveEvent(self, event):
        """追踪光标位置"""
        # 将位置转换为毫米
        scene_pos = self.mapToScene(event.pos())
        x_mm = self._px_to_mm(scene_pos.x())
        y_mm = self._px_to_mm(scene_pos.y())

        # 调试：光标追踪
        logger.debug(f"[光标] 信号发出: {x_mm:.2f}mm, {y_mm:.2f}mm")

        # 发出信号
        self.cursor_position_changed.emit(x_mm, y_mm)

        # 调用父类方法
        super().mouseMoveEvent(event)

    def _px_to_mm(self, px):
        """像素 -> 毫米转换"""
        return px * 25.4 / self.dpi

    def eventFilter(self, obj, event):
        """用于拦截滚轮事件的事件过滤器"""
        from PySide6.QtCore import QEvent

        if obj == self.viewport() and event.type() == QEvent.Wheel:
            self.wheelEvent(event)
            return True  # 停止进一步处理

        return super().eventFilter(obj, event)

    def wheelEvent(self, event):
        """缩放到光标下的点"""
        logger.debug(f"[缩放] wheelEvent 触发, angleDelta={event.angleDelta().y()}")

        # 获取场景坐标中的光标位置
        old_pos = self.mapToScene(event.position().toPoint())
        logger.debug(f"[缩放] 之前: 缩放={self.current_scale:.2f}, 光标位置=({old_pos.x():.1f}, {old_pos.y():.1f})")

        # 计算新缩放比例
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            # 放大
            new_scale = self.current_scale * zoom_factor
            logger.debug(f"[缩放] 放大: {self.current_scale:.2f} -> {new_scale:.2f}")
        else:
            # 缩小
            new_scale = self.current_scale / zoom_factor
            logger.debug(f"[缩放] 缩小: {self.current_scale:.2f} -> {new_scale:.2f}")

        # 限制缩放比例
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))

        # 应用缩放
        scale_ratio = new_scale / self.current_scale
        self.scale(scale_ratio, scale_ratio)
        self.current_scale = new_scale
        logger.debug(f"[缩放] 应用的缩放: {self.current_scale:.2f}x")

        # 调整位置使缩放到光标
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
        logger.debug(f"[缩放] 之后: 缩放={self.current_scale:.2f}, 光标位置=({new_pos.x():.1f}, {new_pos.y():.1f})")
        logger.debug(f"[缩放] 位置校正: 增量=({delta.x():.1f}, {delta.y():.1f})")

        # 更新标尺
        self._update_rulers_scale()

        event.accept()

    def _update_rulers_scale(self):
        """更新标尺缩放比例"""
        updated = False

        if self.h_ruler:
            self.h_ruler.update_scale(self.current_scale)
            updated = True

        if self.v_ruler:
            self.v_ruler.update_scale(self.current_scale)
            updated = True

        if updated:
            logger.debug(f"[标尺缩放] 更新为: {self.current_scale:.2f}")

    def zoom_in(self):
        """相对于视口中心放大"""
        center = self.viewport().rect().center()
        self._zoom_at_point(center, 1.15)

    def zoom_out(self):
        """相对于视口中心缩小"""
        center = self.viewport().rect().center()
        self._zoom_at_point(center, 1 / 1.15)

    def reset_zoom(self):
        """重置缩放到 100%"""
        self.resetTransform()
        self.current_scale = 1.0
        self._update_rulers_scale()

    def _zoom_at_point(self, point, factor):
        """缩放到特定点"""
        old_pos = self.mapToScene(point)

        new_scale = self.current_scale * factor
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))

        scale_ratio = new_scale / self.current_scale
        self.scale(scale_ratio, scale_ratio)
        self.current_scale = new_scale

        new_pos = self.mapToScene(point)
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

        self._update_rulers_scale()

    def clear_and_redraw_grid(self):
        """清除场景并重新绘制网格"""
        grid_visible_state = self.grid_config.visible

        self.scene.clear()
        self.grid_items = []

        self.grid_config.visible = grid_visible_state
        self._draw_grid()

        logger.debug(f"[清除重绘] 网格已重新绘制，可见性: {self.grid_config.visible}")

    def set_label_size(self, width_mm, height_mm):
        """更改标签尺寸"""
        logger.debug(f"[标签尺寸] 之前: {self.width_mm}x{self.height_mm}mm")
        logger.debug(f"[标签尺寸] 请求: {width_mm}x{height_mm}mm")

        # 保存旧尺寸
        old_width = self.width_mm
        old_height = self.height_mm

        # 更新尺寸
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.width_px = round(self._mm_to_px(width_mm))
        self.height_px = round(self._mm_to_px(height_mm))

        # 如果标尺附加到画布，则更新标尺
        if self.h_ruler:
            self.h_ruler.set_length(width_mm)
        if self.v_ruler:
            self.v_ruler.set_length(height_mm)

        # 确保标尺缩放与画布同步
        self._update_rulers_scale()

        logger.debug(f"[标签尺寸] 宽度: {width_mm}mm = {self.width_px}px")
        logger.debug(f"[标签尺寸] 高度: {height_mm}mm = {self.height_px}px")

        # 更新场景矩形
        self.scene.setSceneRect(0, 0, self.width_px, self.height_px)
        logger.debug(f"[标签尺寸] 场景矩形已更新: {self.width_px}x{self.height_px}px")

        # 重新绘制网格和边框
        # 在清除前保存元素和 grid_visible
        items_to_preserve = [item for item in self.scene.items()
                             if hasattr(item, 'element')]
        grid_visible_state = self.grid_config.visible
        logger.debug(f"[标签尺寸] 保留 {len(items_to_preserve)} 个元素, grid_visible={grid_visible_state}")

        # 清除场景
        self.scene.clear()
        self.grid_items = []

        # 使用保存的状态重新绘制网格
        self.grid_config.visible = grid_visible_state
        self._draw_grid()

        # 恢复元素
        for item in items_to_preserve:
            self.scene.addItem(item)

        logger.debug(
            f"[标签尺寸] 网格已重新绘制，可见性: {self.grid_config.visible}, 恢复了 {len(items_to_preserve)} 个元素")
        logger.debug(f"[标签尺寸] 之后: {self.width_mm}x{self.height_mm}mm")