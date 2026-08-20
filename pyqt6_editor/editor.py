"""
TACZ Lua 状态机编辑器 - NodeForge
基于 PyQt6 的可视化节点编辑器
"""

import json
import sys
import os
from typing import Optional, List, Tuple
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTextEdit,
    QMenuBar, QMenu, QToolBar, QDialog, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFileDialog, QScrollArea,
    QFrame, QGraphicsView, QGraphicsScene, QGraphicsItem,
    QGraphicsSceneMouseEvent, QInputDialog, QFormLayout, QPlainTextEdit,
    QApplication, QMenu, QTabWidget, QGroupBox, QCheckBox, QSpinBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QMimeData, QSize, QRect
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPath, QAction, QKeySequence, QDrag, QKeyEvent, QFontMetrics, QFont, QTextCursor

from .node import Node, Port
from .connection import Connection
from .registry import NodeRegistry
from .codegen import LuaCodeGenerator
from .tacz_nodes import *


class ConfigManager:
    """配置文件管理器"""
    CONFIG_FILE = "config.json"

    @staticmethod
    def get_config_path():
        # 使用用户数据目录（AppData），兼容打包后的exe
        if getattr(sys, 'frozen', False):
            # 打包后的exe：使用 AppData\Local\TLM编辑器\
            app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            config_dir = os.path.join(app_data, 'TLM编辑器')
        else:
            # 开发时：使用项目根目录
            editor_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_dir = editor_dir
        
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, ConfigManager.CONFIG_FILE)

    @staticmethod
    def load_config():
        """加载配置文件"""
        config_path = ConfigManager.get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        # 如果配置文件不存在，尝试创建一个
        ConfigManager._create_config_file()
        return ConfigManager.get_default_config()

    @staticmethod
    def _create_config_file():
        """创建配置文件"""
        config_path = ConfigManager.get_config_path()
        if os.path.exists(config_path):
            return True
        try:
            config = ConfigManager.get_default_config()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            print(f"配置文件已创建: {config_path}")
            return True
        except Exception as e:
            print(f"创建配置文件失败: {e}")
            return False

    @staticmethod
    def save_config(config):
        """保存配置文件"""
        config_path = ConfigManager.get_config_path()
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    @staticmethod
    def get_default_config():
        """获取默认配置"""
        return {
            "grid_size": 20,
            "show_grid": True,
            "auto_save": False,
            "auto_save_interval": 60,
            "last_project": "",
            "recent_projects": [],
            "window_geometry": None,
            "splitter_sizes": None,
            "shortcuts": {},
            "editor_word_wrap": False,
            "editor_font_size": 12,
            "editor_tab_size": 4
        }


class PortGraphicsItem(QGraphicsItem):
    """端口图形项"""

    def __init__(self, port: Port, node_item: 'NodeGraphicsItem', is_output: bool, index: int):
        super().__init__()
        self.port = port
        self.node_item = node_item
        self.is_output = is_output
        self.index = index
        self.radius = 6
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setSelected(False)
        self.setZValue(100)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton)
        self.setPos(0, 0)
        self.port.graphics_item = self

    def update_position(self):
        """更新端口位置"""
        y = self.node_item.title_height + 10 + self.index * 20
        if self.is_output:
            x = self.node_item.width - 6
        else:
            x = -6
        self.setPos(x, y)

    def boundingRect(self) -> QRectF:
        return QRectF(-3, -3, self.radius * 2 + 6, self.radius * 2 + 6)

    def paint(self, painter: QPainter, option, widget=None):
        if self.isSelected():
            color = QColor(255, 107, 107)
        elif self.port.connections:
            color = QColor(74, 144, 226)
        elif self.isUnderMouse():
            color = QColor(255, 215, 0)
        else:
            color = QColor(220, 220, 220)

        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.drawEllipse(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

    def get_port_position(self) -> Tuple[float, float]:
        """获取端口在场景中的绝对坐标"""
        pos = self.scenePos()
        return (pos.x(), pos.y())

    def mousePressEvent(self, event):
        """按下端口：开始拖拽连接"""
        if event.button() == Qt.MouseButton.LeftButton and self.is_output:
            self.node_item.editor.start_connection_drag(self)
        elif event.button() == Qt.MouseButton.LeftButton:
            pass
        else:
            event.ignore()


class DraggableTreeWidget(QTreeWidget):
    """可拖拽的节点树形控件"""

    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setDragDropMode(QTreeWidget.DragDropMode.DragOnly)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            node_name = item.data(0, Qt.ItemDataRole.UserRole)
            if node_name:
                mimeData = QMimeData()
                mimeData.setText(node_name)
                drag = QDrag(self)
                drag.setMimeData(mimeData)
                drag.exec(supportedActions)


class NodeGraphicsItem(QGraphicsItem):
    """节点图形项"""

    def __init__(self, node: Node, editor: 'NodeEditor'):
        super().__init__()
        self.node = node
        self.editor = editor
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setPos(node.x, node.y)

        self.title_height = 30
        self.port_spacing = 20
        self.is_hovered = False
        self.is_error = False
        self.error_message = ""
        self.progress = 0.0  # 0.0 到 1.0
        self.preview_data = None

        config = node._get_config()
        config_lines = len(config) if config else 0

        input_count = len(node.inputs)
        output_count = len(node.outputs)
        port_count = max(input_count, output_count)

        fm_title = QFontMetrics(QFont("Segoe UI", 10, QFont.Weight.Bold))
        fm_config = QFontMetrics(QFont("Segoe UI", 8))
        title = getattr(self.node, 'title', self.node.name)
        title_width = fm_title.horizontalAdvance(title)

        # 计算所需的最大宽度（先不考虑换行）
        max_width = 150  # 最小宽度

        # 标题宽度
        title_width = fm_title.horizontalAdvance(title) + 20  # 20 = 左右边距

        # 端口名称宽度（左边端口名称 + 右边端口名称需要的空间）
        port_max_width = 0
        for port in node.inputs:
            w = fm_config.horizontalAdvance(port.name)
            port_max_width = max(port_max_width, w + 20)
        for port in node.outputs:
            w = fm_config.horizontalAdvance(port.name)
            port_max_width = max(port_max_width, w + 20)
        
        # 配置项宽度（key: value）
        config_max_width = 0
        if config:
            for key, value in config.items():
                if isinstance(value, (list, dict)):
                    value_text = str(value)
                else:
                    value_text = str(value)
                config_text = f"{key}: {value_text}"
                w = fm_config.horizontalAdvance(config_text)
                config_max_width = max(config_max_width, w + 20)
        
        # 取所有宽度的最大值
        max_width = max(150, title_width, port_max_width, config_max_width)
        self.width = max_width

        # 高度 = 标题高度 + 端口区域 + 配置项高度
        config_height = (config_lines * 18) if config else 0

        # 确保高度足够容纳所有元素
        min_height = self.title_height + 15 + port_count * self.port_spacing + 15
        if config:
            min_height = max(min_height, self.title_height + 15 + port_count * self.port_spacing + config_height + 15)

        self.height = min_height

        self.setAcceptHoverEvents(True)
        if hasattr(node, 'description') and node.description:
            self.setToolTip(node.description)

        # 通知 Qt 几何形状即将改变
        self.prepareGeometryChange()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None):
        # 错误状态高亮
        if self.is_error:
            glow_color = QColor(255, 107, 107)
            glow_pen = QPen(glow_color, 3)
            painter.setPen(glow_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(-3, -3, self.width + 6, self.height + 6, 10, 10)
        elif self.isSelected() or self.is_hovered:
            glow_color = QColor(255, 215, 0)
            glow_pen = QPen(glow_color, 3)
            painter.setPen(glow_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(-3, -3, self.width + 6, self.height + 6, 10, 10)

        color = QColor(self.node.color)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(), 2))
        painter.drawRoundedRect(0, 0, self.width, self.height, 8, 8)

        painter.setPen(QPen(Qt.GlobalColor.white))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)

        title = getattr(self.node, 'title', self.node.name)
        # 标题不再截断，节点已自适应大小
        painter.drawText(10, 22, title)

        # 错误图标
        if self.is_error:
            painter.setPen(QPen(QColor(255, 107, 107)))
            painter.drawText(self.width - 25, 22, "!")

        # 进度指示器
        if self.progress > 0 and self.progress < 1:
            painter.setBrush(QBrush(QColor(74, 144, 226)))
            painter.setPen(Qt.PenStyle.NoPen)
            progress_width = self.width * self.progress
            painter.drawRect(0, self.height - 3, progress_width, 3)

        # 实时预览
        if self.preview_data:
            painter.setBrush(QBrush(QColor(102, 187, 106, 100)))
            painter.setPen(QPen(QColor(102, 187, 106), 1))
            painter.drawRect(10, self.height - 40, self.width - 20, 30)
            painter.setPen(QPen(Qt.GlobalColor.white))
            font.setPointSize(7)
            painter.setFont(font)
            preview_text = str(self.preview_data)
            if len(preview_text) > 20:
                preview_text = preview_text[:20] + '...'
            painter.drawText(15, self.height - 20, preview_text)

        config = self.node._get_config()
        if config:
            font.setBold(False)
            font.setPointSize(8)
            painter.setFont(font)
            painter.setPen(QPen(QColor(240, 240, 240)))

            y_offset = self.title_height + 15
            for key, value in config.items():
                # 直接显示完整文本，节点已自适应宽度
                if isinstance(value, (list, dict)):
                    text = f"{key}: {str(value)}"
                else:
                    text = f"{key}: {value}"
                painter.drawText(10, y_offset, text)
                y_offset += 18

        self._draw_ports(painter)

    def _draw_ports(self, painter: QPainter):
        font = QFont("Segoe UI", 7)
        painter.setFont(font)
        fm = QFontMetrics(font)

        for i, port in enumerate(self.node.inputs):
            y = self.title_height + 10 + i * self.port_spacing
            painter.setBrush(QBrush(QColor(220, 220, 220)))
            painter.setPen(QPen(QColor(80, 80, 80), 2))
            painter.drawEllipse(-2, y - 5, 10, 10)
            painter.setPen(QPen(Qt.GlobalColor.white))
            # 输入端口名称在圆圈右边
            name_x = 14
            # 确保名称不会超出节点
            text_width = fm.horizontalAdvance(port.name)
            if name_x + text_width > self.width - 10:
                # 名称太长，截断
                max_chars = int((self.width - 24) / fm.horizontalAdvance('W'))
                display_name = port.name[:max_chars] + '..'
            else:
                display_name = port.name
            painter.drawText(name_x, y + 3, display_name)

        for i, port in enumerate(self.node.outputs):
            y = self.title_height + 10 + i * self.port_spacing
            painter.setBrush(QBrush(QColor(220, 220, 220)))
            painter.setPen(QPen(QColor(80, 80, 80), 2))
            painter.drawEllipse(self.width - 8, y - 5, 10, 10)
            painter.setPen(QPen(Qt.GlobalColor.white))
            # 输出端口名称在圆圈左边，向左排列
            text_width = fm.horizontalAdvance(port.name)
            name_x = self.width - 14 - text_width
            # 确保名称不会超出节点
            if name_x < 10:
                name_x = 10
                max_chars = int((self.width - 24) / fm.horizontalAdvance('W'))
                display_name = '..' + port.name[-max_chars:]
            else:
                display_name = port.name
            painter.drawText(name_x, y + 3, display_name)

    def mousePressEvent(self, event):
        # 记录鼠标按下时的位置
        self._mouse_press_pos = event.scenePos()
        # 记录 Alt 键状态
        self._is_alt_pressed = event.modifiers() & Qt.KeyboardModifier.AltModifier
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_alt_pressed:
            # Alt+拖拽：复制节点
            delta = event.scenePos() - self._mouse_press_pos
            if delta.length() > 5:  # 防止误操作
                # 创建节点副本
                node_data = self.node.to_dict()
                new_node = NodeRegistry.create(node_data['class'], x=self.node.x + delta.x(), y=self.node.y + delta.y())
                if new_node:
                    # 恢复节点属性
                    new_node.id = node_data['id']
                    for i, input_data in enumerate(node_data.get('inputs', [])):
                        if i < len(new_node.inputs):
                            new_node.inputs[i].id = input_data.get('id', new_node.inputs[i].id)
                    for i, output_data in enumerate(node_data.get('outputs', [])):
                        if i < len(new_node.outputs):
                            new_node.outputs[i].id = output_data.get('id', new_node.outputs[i].id)
                    # 恢复配置
                    config = self.node._get_config()
                    if config:
                        for key, value in config.items():
                            node_config = new_node._get_config()
                            if key in node_config:
                                node_config[key] = value
                    # 添加到场景
                    self.editor.scene.add_node(new_node)
                    # 自动生成代码
                    self.editor.auto_generate_code()
                # 重置状态
                self._is_alt_pressed = False
        else:
            # 正常移动节点
            super().mouseMoveEvent(event)
            # 确保节点位置与图形项位置同步
            old_x, old_y = self.node.x, self.node.y
            new_x, new_y = self.pos().x(), self.pos().y()
            
            if old_x != new_x or old_y != new_y:
                self.node.x = new_x
                self.node.y = new_y

                # 更新当前节点的端口位置
                if hasattr(self, 'input_port_items'):
                    for port_item in self.input_port_items:
                        port_item.update_position()
                if hasattr(self, 'output_port_items'):
                    for port_item in self.output_port_items:
                        port_item.update_position()

                # 更新所有选中节点的端口位置（多选拖动）
                selected_items = self.editor.scene.selectedItems()
                for item in selected_items:
                    if isinstance(item, NodeGraphicsItem) and item != self:
                        # 同步选中节点的位置
                        if hasattr(item.node, 'x') and hasattr(item.node, 'y'):
                            item.node.x = item.pos().x()
                            item.node.y = item.pos().y()
                        # 更新端口位置
                        if hasattr(item, 'input_port_items'):
                            for port_item in item.input_port_items:
                                port_item.update_position()
                        if hasattr(item, 'output_port_items'):
                            for port_item in item.output_port_items:
                                port_item.update_position()

                # 更新所有连接图形项
                for conn_item in self.editor.scene.connection_items:
                    conn_item.update()
                
                self.editor.scene.update()
                # 记录操作
                self.editor.record_operation()

    def mouseDoubleClickEvent(self, event):
        """双击编辑节点属性"""
        self.editor.edit_node_properties(self.node)

    def hoverEnterEvent(self, event):
        self.is_hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self.update()


class ConnectionGraphicsItem(QGraphicsItem):
    """连接线图形项"""

    def __init__(self, connection: Connection, node_scene):
        super().__init__()
        self.connection = connection
        self.node_scene = node_scene
        self.setZValue(-1)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.is_hovered = False

    def boundingRect(self) -> QRectF:
        start = self.connection.get_start_point()
        end = self.connection.get_end_point()
        return QRectF(
            min(start[0], end[0]) - 20,
            min(start[1], end[1]) - 20,
            abs(end[0] - start[0]) + 40,
            abs(end[1] - start[1]) + 40
        )

    def paint(self, painter: QPainter, option, widget=None):
        start = self.connection.get_start_point()
        end = self.connection.get_end_point()

        # 根据端口类型设置不同的颜色
        port_type = getattr(self.connection.input_port, 'port_type', 'EXEC')
        if port_type == 'EXEC':
            base_color = QColor(74, 144, 226)  # 蓝色
        elif port_type == 'BOOL':
            base_color = QColor(102, 187, 106)  # 绿色
        elif port_type == 'NUMBER':
            base_color = QColor(255, 193, 7)  # 黄色
        elif port_type == 'STRING':
            base_color = QColor(233, 30, 99)  # 粉色
        else:
            base_color = QColor(74, 144, 226)  # 默认蓝色

        if self.isSelected():
            pen = QPen(QColor(255, 107, 107), 4)
        elif self.is_hovered:
            pen = QPen(QColor(255, 215, 0), 3)
        else:
            pen = QPen(base_color, 3)
        painter.setPen(pen)

        path = QPainterPath()
        path.moveTo(start[0], start[1])

        sign = 1 if end[0] >= start[0] else -1
        dx = abs(end[0] - start[0])
        control_offset = max(40, dx * 0.5)

        path.cubicTo(
            start[0] + sign * control_offset, start[1],
            end[0] - sign * control_offset, end[1],
            end[0], end[1]
        )

        painter.drawPath(path)

    def hoverEnterEvent(self, event):
        self.is_hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self.update()

    def mouseDoubleClickEvent(self, event):
        """双击删除连线"""
        self.node_scene.remove_connection(self.connection)

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("删除连接")
        delete_action.triggered.connect(lambda: self.node_scene.remove_connection(self.connection))
        menu.exec(event.screenPos())


class TempConnectionLine(QGraphicsItem):
    """临时连接线"""

    def __init__(self, start_x: float, start_y: float):
        super().__init__()
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = start_x
        self.end_y = start_y
        self.setZValue(1000)

    def set_end_point(self, x: float, y: float):
        self.end_x = x
        self.end_y = y
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(
            min(self.start_x, self.end_x) - 20,
            min(self.start_y, self.end_y) - 20,
            abs(self.end_x - self.start_x) + 40,
            abs(self.end_y - self.start_y) + 40
        )

    def paint(self, painter: QPainter, option, widget=None):
        pen = QPen(QColor(74, 144, 226), 2)
        pen.setDashPattern([5, 5])
        painter.setPen(pen)

        path = QPainterPath()
        path.moveTo(self.start_x, self.start_y)

        # 根据终点相对位置决定控制点方向
        sign = 1 if self.end_x >= self.start_x else -1
        dx = abs(self.end_x - self.start_x) * 0.5

        path.cubicTo(
            self.start_x + sign * dx, self.start_y,
            self.end_x - sign * dx, self.end_y,
            self.end_x, self.end_y
        )

        painter.drawPath(path)


class NodeScene(QGraphicsScene):
    """节点场景"""

    node_selected = pyqtSignal(Node)
    node_double_clicked = pyqtSignal(Node)

    def __init__(self, editor: 'NodeEditor'):
        super().__init__()
        self.editor = editor
        self.nodes: List[Node] = []
        self.connections: List[Connection] = []
        self.node_items = {}
        self.connection_items = []
        self.temp_line: Optional[TempConnectionLine] = None
        self.lastMousePos = QPointF()

        # 拖拽连接状态
        self.drag_output_port: Optional[Port] = None  # 正在拖拽的输出端口

        self.setSceneRect(-5000, -5000, 10000, 10000)
        self.setBackgroundBrush(QColor(45, 45, 48))
        self.dot_spacing = 25
        self.dot_radius = 1.5
        self.dot_color = QColor(80, 80, 85)
        self.show_grid = True

    def drawBackground(self, painter: QPainter, rect: QRectF):
        super().drawBackground(painter, rect)
        if not self.show_grid:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.dot_color))
        painter.setPen(Qt.PenStyle.NoPen)
        left = int(rect.left()) - (int(rect.left()) % self.dot_spacing)
        top = int(rect.top()) - (int(rect.top()) % self.dot_spacing)
        right = int(rect.right()) + self.dot_spacing
        bottom = int(rect.bottom()) + self.dot_spacing
        x = left
        while x < right:
            y = top
            while y < bottom:
                painter.drawEllipse(QPointF(x, y), self.dot_radius, self.dot_radius)
                y += self.dot_spacing
            x += self.dot_spacing
        painter.restore()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 释放到空白区域时取消连接"""
        if self.drag_output_port is not None and event.button() == Qt.MouseButton.LeftButton:
            self.cleanup_drag()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def cleanup_drag(self):
        """清理拖拽连接状态"""
        self.drag_output_port = None
        if self.temp_line is not None:
            self.removeItem(self.temp_line)
            self.temp_line = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasText():
            node_name = mime_data.text()
            pos = event.scenePos()
            node = NodeRegistry.create(node_name, x=pos.x(), y=pos.y())
            if node:
                self.add_node(node)
                event.acceptProposedAction()

    def add_node(self, node: Node) -> NodeGraphicsItem:
        """添加节点到场景"""
        # 更新节点的width为图形项的实际宽度
        self.nodes.append(node)
        item = NodeGraphicsItem(node, self.editor)
        node.width = item.width  # 同步宽度
        self.addItem(item)

        item.input_port_items = []
        for i, port in enumerate(node.inputs):
            port_item = PortGraphicsItem(port, item, False, i)
            item.input_port_items.append(port_item)
            self.addItem(port_item)
            port_item.setParentItem(item)
            port_item.update_position()

        item.output_port_items = []
        for i, port in enumerate(node.outputs):
            port_item = PortGraphicsItem(port, item, True, i)
            item.output_port_items.append(port_item)
            self.addItem(port_item)
            port_item.setParentItem(item)
            port_item.update_position()

        self.node_items[node.id] = item
        self.editor.auto_generate_code()
        return item

    def add_connection(self, connection: Connection) -> ConnectionGraphicsItem:
        self.connections.append(connection)
        item = ConnectionGraphicsItem(connection, self)
        connection.graphics_item = item  # 设置图形项引用
        self.addItem(item)
        self.connection_items.append(item)
        self.editor.auto_generate_code()
        return item

    def remove_node(self, node: Node, record_operation=True):
        """删除节点及其所有关联项"""
        if node not in self.nodes:
            return

        self.nodes.remove(node)

        if node.id in self.node_items:
            item = self.node_items[node.id]

            # 找出并删除相关的连接
            connections_to_remove = []
            for conn in list(self.connections):
                if conn.input_port.node.id == node.id or conn.output_port.node.id == node.id:
                    connections_to_remove.append(conn)

            for conn in connections_to_remove:
                # 清除连接两端端口的 graphics_item 引用
                if hasattr(conn.input_port, 'graphics_item'):
                    conn.input_port.graphics_item = None
                if hasattr(conn.output_port, 'graphics_item'):
                    conn.output_port.graphics_item = None

                # 找到对应的图形项并删除
                for conn_item in list(self.connection_items):
                    if conn_item.connection == conn:
                        self.connection_items.remove(conn_item)
                        self.removeItem(conn_item)
                        break
                if conn in self.connections:
                    self.connections.remove(conn)
                conn.delete()

            # 删除所有端口图形项
            if hasattr(item, 'input_port_items'):
                for port_item in item.input_port_items:
                    port_item.port.graphics_item = None
                    self.removeItem(port_item)
            if hasattr(item, 'output_port_items'):
                for port_item in item.output_port_items:
                    port_item.port.graphics_item = None
                    self.removeItem(port_item)

            del self.node_items[node.id]
            self.removeItem(item)

        self.update()
        if record_operation:
            self.editor.auto_generate_code()
            # 记录操作
            self.editor.record_operation()
    
    def remove_nodes(self, nodes: list[Node]):
        """批量删除节点，使用事务性操作"""
        if not nodes:
            return
        
        # 开始事务
        for node in nodes:
            self.remove_node(node, record_operation=False)
        
        # 事务结束，统一生成代码和记录操作
        self.editor.auto_generate_code()
        self.editor.record_operation()

    def remove_connection(self, connection: Connection):
        if connection in self.connections:
            self.connections.remove(connection)
        # 找到对应的图形项并删除
        for conn_item in list(self.connection_items):
            if conn_item.connection == connection:
                self.connection_items.remove(conn_item)
                self.removeItem(conn_item)
                break
        # 清除端口引用
        if connection.input_port and hasattr(connection.input_port, 'graphics_item'):
            connection.input_port.graphics_item = None
        if connection.output_port and hasattr(connection.output_port, 'graphics_item'):
            connection.output_port.graphics_item = None
        connection.delete()
        self.editor.auto_generate_code()
        # 记录操作
        self.editor.record_operation()

    def clear(self):
        # 清除端口引用
        for item in list(self.node_items.values()):
            if hasattr(item, 'input_port_items'):
                for port_item in item.input_port_items:
                    port_item.port.graphics_item = None
            if hasattr(item, 'output_port_items'):
                for port_item in item.output_port_items:
                    port_item.port.graphics_item = None

        # 使用场景原生的 clear 删除所有图形项
        super().clear()

        # 清空数据
        self.connections.clear()
        self.nodes.clear()
        self.node_items.clear()
        self.connection_items.clear()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.lastMousePos = event.scenePos()
        if self.temp_line:
            self.temp_line.set_end_point(event.scenePos().x(), event.scenePos().y())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            selected_nodes = []
            for item in list(self.selectedItems()):
                if isinstance(item, ConnectionGraphicsItem):
                    self.remove_connection(item.connection)
                elif isinstance(item, NodeGraphicsItem):
                    selected_nodes.append(item.node)
            # 批量删除节点，使用事务性操作
            if selected_nodes:
                self.remove_nodes(selected_nodes)
        else:
            super().keyPressEvent(event)


class NodeGraphicsView(QGraphicsView):
    """节点图形视图"""

    def __init__(self, scene: NodeScene):
        super().__init__(scene)
        self.scene = scene
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setAcceptDrops(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self._is_panning = False
        self._pan_start = QPointF()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.LeftButton:
            # Ctrl+左键拖拽：强制移动画布
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self._is_panning = True
                self._pan_start = event.pos()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
            else:
                # 恢复默认的橡胶框选模式
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        elif self.scene.drag_output_port is not None:
            # 拖拽连接模式
            scene_pos = self.mapToScene(event.pos())
            if self.scene.temp_line is not None:
                self.scene.temp_line.set_end_point(scene_pos.x(), scene_pos.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        elif self.scene.drag_output_port is not None and event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            items = self.scene.items(scene_pos)
            target_port_item = None
            for item in items:
                if isinstance(item, PortGraphicsItem) and not item.is_output:
                    target_port_item = item
                    break

            if target_port_item is not None:
                output_port_item = self.scene.drag_output_port.graphics_item
                if output_port_item is not None:
                    self.scene.editor.create_connection(output_port_item, target_port_item)

            self.scene.cleanup_drag()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / 1.15
        old_pos = self.mapToScene(event.position().toPoint())
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
        self.viewport().update()
        if hasattr(self.scene, 'editor'):
            self.scene.editor.update_zoom_label()
        event.accept()

    def keyPressEvent(self, event):
        # F键：聚焦到选中节点
        if event.key() == Qt.Key.Key_F:
            selected_items = self.scene.selectedItems()
            if selected_items:
                # 计算所有选中项的边界框
                rect = QRectF()
                for item in selected_items:
                    rect = rect.united(item.boundingRect().translated(item.pos()))
                # 调整视图以显示所有选中项
                self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
                event.accept()
        # Home键：居中显示所有节点
        elif event.key() == Qt.Key.Key_Home:
            if self.scene.nodes:
                # 计算所有节点的边界框
                rect = QRectF()
                for node in self.scene.nodes:
                    item = self.scene.node_items.get(node.id)
                    if item:
                        rect = rect.united(item.boundingRect().translated(item.pos()))
                # 调整视图以显示所有节点
                self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
                event.accept()
        # Ctrl+D：取消所有选中状态
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_D:
            for item in self.scene.selectedItems():
                item.setSelected(False)
            event.accept()
        else:
            super().keyPressEvent(event)


class NodePalette(QWidget):
    """节点调色板"""

    node_selected = pyqtSignal(str)

    TAG_ICONS = {
        "状态定义": "📦",
        "输入事件": "🎮",
        "动画控制": "🎬",
        "条件检查": "🔍",
        "动作操作": "⚡",
        "轨道系统": "🛤️",
        "逻辑控制": "🧠",
        "动画模式": "🔄",
        "数学运算": "➕",
        "自定义代码": "💻",
    }

    def __init__(self, editor: 'NodeEditor'):
        super().__init__()
        self.editor = editor
        self.view_mode = 'tag'  # 'tag' or 'port'
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("🧩 节点")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 8px; background: #333; color: white;")
        layout.addWidget(title)

        # 视图切换按钮
        self.view_btn = QPushButton("🔄 按分类")
        self.view_btn.clicked.connect(self.toggle_view_mode)
        self.view_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px 10px;
                margin: 5px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #094771;
            }
        """)
        layout.addWidget(self.view_btn)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 搜索节点...")
        self.search_edit.textChanged.connect(self.filter_nodes)
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px 10px;
                margin: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #094771;
            }
        """)
        # 添加搜索补全功能
        from PyQt6.QtWidgets import QCompleter
        from PyQt6.QtCore import QStringListModel
        self.completer = QCompleter()
        self.search_edit.setCompleter(self.completer)
        layout.addWidget(self.search_edit)

        hint = QLabel("拖拽到工作区 | Delete删除 | 双击添加")
        hint.setStyleSheet("color: #888; font-size: 10px; padding: 3px 10px;")
        layout.addWidget(hint)

        self.tree = DraggableTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #2d2d30;
                color: #cccccc;
                border: none;
                font-size: 12px;
            }
            QTreeWidget::item {
                padding: 4px 5px;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
            }
            QTreeWidget::branch:selected {
                background-color: #094771;
            }
        """)
        layout.addWidget(self.tree)

        self.node_count_label = QLabel("")
        self.node_count_label.setStyleSheet("color: #666; font-size: 10px; padding: 3px 10px;")
        layout.addWidget(self.node_count_label)

    def load_nodes(self):
        self.tree.clear()
        tags = NodeRegistry.get_tags()
        node_tags = NodeRegistry.get_node_tags()
        total_count = 0
        
        all_node_names = []

        if self.view_mode == 'port':
            self._load_port_view(all_node_names)
        else:
            for tag in sorted(tags):
                icon = self.TAG_ICONS.get(tag, "📎")
                tag_item = QTreeWidgetItem([f"{icon}  {tag}"])
                tag_item.setExpanded(True)

                nodes_in_tag = [name for name, t in node_tags.items() if t == tag]
                for node_name in sorted(nodes_in_tag):
                    title = NodeRegistry.get_node_title(node_name)
                    description = NodeRegistry.get_node_description(node_name)
                    node_item = QTreeWidgetItem([f"  {title}"])
                    node_item.setData(0, Qt.ItemDataRole.UserRole, node_name)
                    node_item.setToolTip(0, description)
                    tag_item.addChild(node_item)
                    total_count += 1
                    all_node_names.append(title)

                self.tree.addTopLevelItem(tag_item)

            from PyQt6.QtCore import QStringListModel
            model = QStringListModel(all_node_names)
            self.completer.setModel(model)
            self.node_count_label.setText(f"共 {total_count} 个节点")

    def _load_port_view(self, all_node_names):
        """按端口类型分类加载节点"""
        from PyQt6.QtCore import QStringListModel
        PORT_ICONS = {
            'input': "📥",
            'output': "📤",
            'exec': "⚡",
            'data': "📊",
        }
        
        # 收集所有节点的端口信息
        port_groups = {}  # port_type -> [(node_name, title, ports_info)]
        node_tags = NodeRegistry.get_node_tags()
        total_count = 0
        
        all_nodes = NodeRegistry.get_all_nodes()
        for node_name in sorted(all_nodes.keys()):
            title = NodeRegistry.get_node_title(node_name)
            ports = NodeRegistry.get_node_ports(node_name)
            
            all_node_names.append(title)
            
            # 按输入端口分组
            for pname, ptype, pdata in ports['inputs']:
                group_key = f"输入: {pname}"
                if group_key not in port_groups:
                    port_groups[group_key] = []
                port_groups[group_key].append((node_name, title, ports))
                total_count += 1
            
            # 按输出端口分组
            for pname, ptype, pdata in ports['outputs']:
                group_key = f"输出: {pname}"
                if group_key not in port_groups:
                    port_groups[group_key] = []
                port_groups[group_key].append((node_name, title, ports))
                total_count += 1
        
        # 按端口名称排序显示
        for port_key in sorted(port_groups.keys()):
            is_input = port_key.startswith("输入:")
            icon = "📥" if is_input else "📤"
            port_item = QTreeWidgetItem([f"{icon}  {port_key}"])
            port_item.setExpanded(True)
            
            seen = set()
            for node_name, title, ports in port_groups[port_key]:
                if node_name in seen:
                    continue
                seen.add(node_name)
                
                # 显示端口信息
                port_desc = []
                for pname, ptype, pdata in ports['inputs']:
                    port_desc.append(f"◀{pname}")
                for pname, ptype, pdata in ports['outputs']:
                    port_desc.append(f"▶{pname}")
                display = f"  {title}  ({' | '.join(port_desc)})"
                node_item = QTreeWidgetItem([display])
                node_item.setData(0, Qt.ItemDataRole.UserRole, node_name)
                port_item.addChild(node_item)
                self.tree.addTopLevelItem(port_item)

        model = QStringListModel(all_node_names)
        self.completer.setModel(model)
        self.node_count_label.setText(f"共 {len(all_nodes)} 个节点类型")

    def toggle_view_mode(self):
        if self.view_mode == 'tag':
            self.view_mode = 'port'
            self.view_btn.setText("🔄 按标签")
        else:
            self.view_mode = 'tag'
            self.view_btn.setText("🔄 按分类")
        self.load_nodes()

    def filter_nodes(self, text: str):
        text = text.lower()
        for i in range(self.tree.topLevelItemCount()):
            tag_item = self.tree.topLevelItem(i)
            tag_match = False
            for j in range(tag_item.childCount()):
                node_item = tag_item.child(j)
                node_name = node_item.text(0).lower()
                if not text or text in node_name:
                    node_item.setHidden(False)
                    tag_match = True
                else:
                    node_item.setHidden(True)
            tag_item.setHidden(not tag_match)

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        node_name = item.data(0, Qt.ItemDataRole.UserRole)
        if node_name:
            view = self.editor.graphics_view
            center = view.viewport().rect().center()
            pos = view.mapToScene(center)
            node = NodeRegistry.create(node_name, x=pos.x(), y=pos.y())
            if node:
                self.editor.scene.add_node(node)
                self.node_selected.emit(node_name)


class KeyLabel(QLabel):
    """可编辑的快捷键标签（Minecraft风格）"""

    shortcut_changed = pyqtSignal(str, str)  # key_name, new_shortcut

    def __init__(self, key_name, text, parent=None):
        super().__init__(text, parent)
        self.key_name = key_name
        self.is_listening = False
        self.current_shortcut = text
        self.setMinimumWidth(100)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: #333333; color: #FFFFFF; padding: 5px 10px; border-radius: 3px;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("点击修改快捷键")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_listening()

    def start_listening(self):
        """开始监听按键"""
        self.is_listening = True
        self.setStyleSheet("background: #4a9eff; color: #FFFFFF; padding: 5px 10px; border-radius: 3px; border: 2px solid #6ab7ff;")
        self.setText("按下按键...")
        self.grabKeyboard()
        self.setFocus()

    def stop_listening(self, accept=True):
        """停止监听"""
        self.is_listening = False
        if accept and self.current_shortcut != "-":
            self.setStyleSheet("background: #4CAF50; color: #FFFFFF; padding: 5px 10px; border-radius: 3px;")
            self.shortcut_changed.emit(self.key_name, self.current_shortcut)
        elif self.current_shortcut == "-":
            self.setStyleSheet("background: #f44336; color: #FFFFFF; padding: 5px 10px; border-radius: 3px;")
            self.shortcut_changed.emit(self.key_name, self.current_shortcut)
        else:
            self.setStyleSheet("background: #333333; color: #FFFFFF; padding: 5px 10px; border-radius: 3px;")
        self.releaseKeyboard()

    def keyPressEvent(self, event):
        if not self.is_listening:
            super().keyPressEvent(event)
            return

        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key.Key_Escape:
            self.stop_listening(False)
            return

        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self.stop_listening(True)
            return

        if key == Qt.Key.Key_Backspace or key == Qt.Key.Key_Delete:
            self.current_shortcut = "-"
            self.setText("已清除 (按Enter确认)")
            self.setStyleSheet("background: #f44336; color: #FFFFFF; padding: 5px 10px; border-radius: 3px;")
            event.accept()
            return

        if key == Qt.Key.Key_Tab or key == Qt.Key.Key_CapsLock or key == Qt.Key.Key_ScrollLock:
            event.accept()
            return

        modifiers_str = ""
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            modifiers_str += "Ctrl+"
        if modifiers & Qt.KeyboardModifier.AltModifier:
            modifiers_str += "Alt+"
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            modifiers_str += "Shift+"

        key_map = {
            Qt.Key.Key_A: 'A', Qt.Key.Key_B: 'B', Qt.Key.Key_C: 'C', Qt.Key.Key_D: 'D',
            Qt.Key.Key_E: 'E', Qt.Key.Key_F: 'F', Qt.Key.Key_G: 'G', Qt.Key.Key_H: 'H',
            Qt.Key.Key_I: 'I', Qt.Key.Key_J: 'J', Qt.Key.Key_K: 'K', Qt.Key.Key_L: 'L',
            Qt.Key.Key_M: 'M', Qt.Key.Key_N: 'N', Qt.Key.Key_O: 'O', Qt.Key.Key_P: 'P',
            Qt.Key.Key_Q: 'Q', Qt.Key.Key_R: 'R', Qt.Key.Key_S: 'S', Qt.Key.Key_T: 'T',
            Qt.Key.Key_U: 'U', Qt.Key.Key_V: 'V', Qt.Key.Key_W: 'W', Qt.Key.Key_X: 'X',
            Qt.Key.Key_Y: 'Y', Qt.Key.Key_Z: 'Z',
            Qt.Key.Key_0: '0', Qt.Key.Key_1: '1', Qt.Key.Key_2: '2', Qt.Key.Key_3: '3',
            Qt.Key.Key_4: '4', Qt.Key.Key_5: '5', Qt.Key.Key_6: '6', Qt.Key.Key_7: '7',
            Qt.Key.Key_8: '8', Qt.Key.Key_9: '9',
            Qt.Key.Key_Space: 'Space', Qt.Key.Key_F1: 'F1', Qt.Key.Key_F2: 'F2',
            Qt.Key.Key_F3: 'F3', Qt.Key.Key_F4: 'F4', Qt.Key.Key_F5: 'F5', Qt.Key.Key_F6: 'F6',
            Qt.Key.Key_F7: 'F7', Qt.Key.Key_F8: 'F8', Qt.Key.Key_F9: 'F9', Qt.Key.Key_F10: 'F10',
            Qt.Key.Key_F11: 'F11', Qt.Key.Key_F12: 'F12',
            Qt.Key.Key_Up: 'Up', Qt.Key.Key_Down: 'Down', Qt.Key.Key_Left: 'Left', Qt.Key.Key_Right: 'Right',
            Qt.Key.Key_Insert: 'Insert', Qt.Key.Key_Home: 'Home', Qt.Key.Key_End: 'End',
            Qt.Key.Key_PageUp: 'PageUp', Qt.Key.Key_PageDown: 'PageDown',
        }

        key_str = key_map.get(key, '')
        if not key_str:
            seq = QKeySequence(key)
            key_str = seq.toString()

        if key_str:
            self.current_shortcut = modifiers_str + key_str
            self.setText(self.current_shortcut + " (按Enter确认)")
            self.setStyleSheet("background: #90EE90; color: #000000; padding: 5px 10px; border-radius: 3px;")
        event.accept()

    def update_shortcut(self, shortcut_str):
        """更新显示的快捷键"""
        self.current_shortcut = shortcut_str
        self.setText(shortcut_str)
        self.setStyleSheet("background: #333333; color: #FFFFFF; padding: 5px 10px; border-radius: 3px;")


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setWindowTitle("设置")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)

        # 创建选项卡部件
        tabs = QTabWidget()

        # 通用设置选项卡
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        # 网格设置
        grid_group = QGroupBox("网格设置")
        grid_layout = QVBoxLayout()
        self.show_grid_cb = QCheckBox("显示网格")
        self.show_grid_cb.stateChanged.connect(self.on_show_grid_changed)
        grid_layout.addWidget(self.show_grid_cb)

        grid_size_layout = QHBoxLayout()
        grid_size_layout.addWidget(QLabel("网格大小:"))
        self.grid_size_spin = QSpinBox()
        self.grid_size_spin.setRange(10, 100)
        self.grid_size_spin.valueChanged.connect(self.on_grid_size_changed)
        grid_size_layout.addWidget(self.grid_size_spin)
        grid_size_layout.addStretch()
        grid_layout.addLayout(grid_size_layout)
        grid_group.setLayout(grid_layout)
        general_layout.addWidget(grid_group)

        # 自动保存设置
        auto_save_group = QGroupBox("自动保存设置")
        auto_save_layout = QVBoxLayout()
        self.auto_save_cb = QCheckBox("启用自动保存")
        self.auto_save_cb.stateChanged.connect(self.on_auto_save_changed)
        auto_save_layout.addWidget(self.auto_save_cb)

        auto_save_interval_layout = QHBoxLayout()
        auto_save_interval_layout.addWidget(QLabel("自动保存间隔(秒):"))
        self.auto_save_interval_spin = QSpinBox()
        self.auto_save_interval_spin.setRange(10, 600)
        self.auto_save_interval_spin.valueChanged.connect(self.on_auto_save_interval_changed)
        auto_save_interval_layout.addWidget(self.auto_save_interval_spin)
        auto_save_interval_layout.addStretch()
        auto_save_layout.addLayout(auto_save_interval_layout)
        auto_save_group.setLayout(auto_save_layout)
        general_layout.addWidget(auto_save_group)

        general_layout.addStretch()
        tabs.addTab(general_tab, "通用设置")

        # 代码编辑器设置选项卡
        editor_tab = QWidget()
        editor_layout = QVBoxLayout(editor_tab)

        # 代码编辑器设置
        editor_group = QGroupBox("代码编辑器设置")
        editor_group_layout = QVBoxLayout()

        # 自动换行
        self.word_wrap_cb = QCheckBox("自动换行")
        self.word_wrap_cb.setToolTip("启用后，长行代码会自动换行显示")
        self.word_wrap_cb.stateChanged.connect(self.on_word_wrap_changed)
        editor_group_layout.addWidget(self.word_wrap_cb)

        # 字体大小
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("字体大小:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 32)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self.on_font_size_changed)
        font_size_layout.addWidget(self.font_size_spin)
        font_size_layout.addStretch()
        editor_group_layout.addLayout(font_size_layout)

        # Tab空格数
        tab_size_layout = QHBoxLayout()
        tab_size_layout.addWidget(QLabel("Tab空格数:"))
        self.tab_size_spin = QSpinBox()
        self.tab_size_spin.setRange(2, 8)
        self.tab_size_spin.setValue(4)
        self.tab_size_spin.valueChanged.connect(self.on_tab_size_changed)
        tab_size_layout.addWidget(self.tab_size_spin)
        tab_size_layout.addStretch()
        editor_group_layout.addLayout(tab_size_layout)

        editor_group.setLayout(editor_group_layout)
        editor_layout.addWidget(editor_group)
        editor_layout.addStretch()
        tabs.addTab(editor_tab, "编辑器设置")

        # 快捷键设置选项卡
        shortcuts_tab = QWidget()
        shortcuts_layout = QVBoxLayout(shortcuts_tab)

        shortcuts_scroll = QScrollArea()
        shortcuts_scroll.setWidgetResizable(True)
        shortcuts_content = QWidget()
        shortcuts_content_layout = QVBoxLayout(shortcuts_content)

        self.keybind_labels = {}

        keybinds = [
            ("新建项目", self.parent_window.new_action),
            ("保存项目", self.parent_window.save_action),
            ("打开项目", self.parent_window.open_action),
            ("生成代码", self.parent_window.generate_action),
            ("复制节点", self.parent_window.copy_action),
            ("粘贴节点", self.parent_window.paste_action),
            ("撤销操作", self.parent_window.undo_action),
            ("重做操作", self.parent_window.redo_action),
            ("聚焦节点", getattr(self.parent_window, 'focus_node_action', None)),
            ("居中显示", getattr(self.parent_window, 'home_view_action', None)),
            ("取消选中", getattr(self.parent_window, 'deselect_all_action', None)),
            ("删除节点", getattr(self.parent_window, 'delete_node_action', None)),
            ("设置", self.parent_window.settings_action),
            ("退出程序", self.parent_window.exit_action),
        ]

        for name, action in keybinds:
            row = QHBoxLayout()
            label = QLabel(name)
            label.setMinimumWidth(120)
            row.addWidget(label)

            if action and action.shortcut():
                shortcut_text = action.shortcut().toString()
            else:
                shortcut_text = "-"

            key_label = KeyLabel(name, shortcut_text)
            key_label.shortcut_changed.connect(self.update_action_shortcut)
            row.addWidget(key_label)

            self.keybind_labels[name] = key_label
            shortcuts_content_layout.addLayout(row)

        shortcuts_content_layout.addStretch()
        shortcuts_scroll.setWidget(shortcuts_content)
        shortcuts_layout.addWidget(QLabel("点击快捷键标签，按下新按键，按Enter确认，按Esc取消"))
        shortcuts_layout.addWidget(shortcuts_scroll)
        tabs.addTab(shortcuts_tab, "快捷键")

        # 帮助选项卡
        help_tab = QWidget()
        help_scroll = QScrollArea()
        help_scroll.setWidgetResizable(True)
        help_content = QWidget()
        help_layout = QVBoxLayout(help_content)

        help_title = QLabel("TACZ Lua Map 编辑器 v1.0.0")
        help_title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        help_layout.addWidget(help_title)

        help_author = QLabel("作者: 小欧6630")
        help_author.setStyleSheet("padding: 5px;")
        help_layout.addWidget(help_author)

        help_layout.addWidget(QLabel("这是一个用于创建 TACZ 枪械状态机的可视化节点编辑器。"))

        # 功能介绍
        features_header = QLabel("\n===== 功能介绍 =====")
        features_header.setStyleSheet("font-weight: bold; padding: 10px 5px 5px; color: #FFFFFF;")
        help_layout.addWidget(features_header)

        features = QLabel("""
【画布操作】
• 左键拖拽节点：移动选中的节点
• 左键拖拽空白区域：平移画布视图
• 左键框选：从空白区域开始框选多个节点
• Shift + 左键框选：向已有选区添加节点
• 滚轮缩放：以鼠标为中心缩放画布
• Ctrl + 左键拖拽：强制移动画布
• F键：聚焦到选中节点
• Home键：居中显示所有节点
• Ctrl + D：取消所有选中
• Delete/Backspace：删除选中节点

【节点操作】
• 双击节点：打开属性编辑面板
• Tab键：弹出节点搜索框
• Ctrl+C/V：复制粘贴节点
• Alt+拖拽：快速复制节点
• 拖拽连线到空白处：自动创建新节点

【连线操作】
• 贝塞尔曲线连线：光滑曲线连接
• 连线颜色区分：EXEC蓝色、BOOL绿色、NUMBER黄色、STRING粉色
• 悬停高亮：鼠标悬停时显示金色高亮
• 双击连线：删除该连线

【快捷功能】
• 撤销/重做：Ctrl+Z / Ctrl+Y
• Scratch预览：查看节点分类参考
• 导出代码：生成Lua状态机代码
        """)
        features.setStyleSheet("padding: 5px; background: #333333; color: #FFFFFF; border-radius: 5px; line-height: 1.5;")
        help_layout.addWidget(features)

        # 节点类型说明
        nodes_header = QLabel("\n===== 节点类型 =====")
        nodes_header.setStyleSheet("font-weight: bold; padding: 10px 5px 5px; color: #FFFFFF;")
        help_layout.addWidget(nodes_header)

        nodes_info = QLabel("""
【状态机基础结构】
根据官方文档，状态机包含以下基本要素：

1. 轨道(Track)
   - 动画的载体，动画是在轨道上播放的
   - 定义示例: BASE_TRACK, MAIN_TRACK, ADS_TRACK

2. 轨道行(Track Line)
   - 一些轨道的集合，对轨道进行方便管理
   - 示例: STATIC_TRACK_LINE, BLENDING_TRACK_LINE

3. 状态(State)
   - 检测枪械当前情况
   - 可包含子状态和状态参数
   - 示例: idle(静止), run(奔跑), walk(行走)

4. 状态机初始化
   - 决定状态机加载时的初始值
   - M:initialize() 函数在切枪时调用

【节点与状态机对应】
• 状态定义节点 → 对应 state 定义
• 输入事件节点 → 对应 INPUT_* 输入
• 动画控制节点 → 对应 context:runAnimation() 等
• 条件检查节点 → 对应状态转换逻辑
• 轨道系统节点 → 对应轨道和轨道行
        """)
        nodes_info.setStyleSheet("padding: 5px; background: #333333; color: #FFFFFF; border-radius: 5px; line-height: 1.5;")
        help_layout.addWidget(nodes_info)

        # 使用指南
        usage_header = QLabel("\n===== 使用指南 =====")
        usage_header.setStyleSheet("font-weight: bold; padding: 10px 5px 5px; color: #FFFFFF;")
        help_layout.addWidget(usage_header)

        usage_info = QLabel("""
【基本工作流程】
1. 从左侧面板拖拽节点到画布
2. 从输出端口拖拽到输入端口创建连线
3. 双击节点编辑属性参数
4. 在右侧代码面板查看生成的Lua代码
5. 点击"复制"或"下载"保存代码

【代码生成】
生成的代码遵循官方状态机格式：
- 自动创建轨道定义 (increment)
- 自动生成状态初始化
- 自动注册轨道、轨道行、状态和输入

【注意事项】
- EXEC端口只能连接到EXEC端口
- 输入端口只能有一个连接
- 删除节点会同时删除相关连线
- 批量删除使用事务性操作保证一致性

【快捷键】
• Ctrl+N 新建项目
• Ctrl+S 保存项目
• Ctrl+O 打开项目
• Ctrl+G 生成代码
• Ctrl+C/V 复制粘贴
• Ctrl+Z/Y 撤销重做
• F 聚焦节点
• Home 居中显示
        """)
        usage_info.setStyleSheet("padding: 5px; background: #333333; color: #FFFFFF; border-radius: 5px; line-height: 1.5;")
        help_layout.addWidget(usage_info)

        help_layout.addStretch()
        help_scroll.setWidget(help_content)
        help_tab_layout = QVBoxLayout(help_tab)
        help_tab_layout.setContentsMargins(0, 0, 0, 0)
        help_tab_layout.addWidget(help_scroll)
        tabs.addTab(help_tab, "帮助")

        # 高亮设置选项卡
        highlight_tab = QWidget()
        highlight_layout = QVBoxLayout(highlight_tab)

        highlight_header = QLabel("代码关键词高亮设置")
        highlight_header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 8px;")
        highlight_layout.addWidget(highlight_header)

        highlight_hint = QLabel("添加关键词和颜色，代码中匹配的关键词将高亮显示")
        highlight_hint.setStyleSheet("color: #888; font-size: 11px; padding: 2px 8px;")
        highlight_layout.addWidget(highlight_hint)

        # 添加行
        add_layout = QHBoxLayout()
        self.highlight_word_edit = QLineEdit()
        self.highlight_word_edit.setPlaceholderText("输入关键词...")
        add_layout.addWidget(self.highlight_word_edit)

        self.highlight_color_btn = QPushButton("🎨")
        self.highlight_color_btn.setFixedSize(40, 25)
        self.highlight_color_btn.setStyleSheet("background-color: #FFD700;")
        self.highlight_color = "#FFD700"
        self.highlight_color_btn.clicked.connect(self.pick_highlight_color)
        add_layout.addWidget(self.highlight_color_btn)

        self.highlight_add_btn = QPushButton("添加")
        self.highlight_add_btn.clicked.connect(self.add_highlight)
        add_layout.addWidget(self.highlight_add_btn)
        highlight_layout.addLayout(add_layout)

        # 高亮列表
        self.highlight_list = QListWidget()
        self.highlight_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d30;
                color: #cccccc;
                border: 1px solid #555;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 4px 8px;
            }
        """)
        highlight_layout.addWidget(self.highlight_list)

        # 删除按钮
        delete_layout = QHBoxLayout()
        delete_layout.addStretch()
        self.highlight_del_btn = QPushButton("删除选中")
        self.highlight_del_btn.clicked.connect(self.delete_highlight)
        delete_layout.addWidget(self.highlight_del_btn)
        highlight_layout.addLayout(delete_layout)

        highlight_layout.addStretch()
        tabs.addTab(highlight_tab, "高亮设置")

        # 关于选项卡（简化版）
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.addWidget(QLabel("版本: v1.0.0"))
        about_layout.addWidget(QLabel("作者: 小欧6630"))
        about_layout.addStretch()
        tabs.addTab(about_tab, "关于")

        layout.addWidget(tabs)

        # 按钮
        buttons = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        buttons.addStretch()
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)

    def load_settings(self):
        config = getattr(self.parent_window, 'config', {})
        # 网格设置
        if hasattr(self.parent_window, 'scene') and self.parent_window.scene:
            show_grid = config.get('show_grid', True)
            self.show_grid_cb.setChecked(show_grid)
            self.parent_window.scene.show_grid = show_grid
            if 'grid_size' in config:
                self.grid_size_spin.setValue(config['grid_size'])
                self.parent_window.scene.dot_spacing = config['grid_size']
        
        # 编辑器设置
        word_wrap = config.get('editor_word_wrap', False)
        self.word_wrap_cb.setChecked(word_wrap)
        if hasattr(self.parent_window, 'code_preview') and self.parent_window.code_preview:
            if word_wrap:
                self.parent_window.code_preview.code_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            else:
                self.parent_window.code_preview.code_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        font_size = config.get('editor_font_size', 12)
        self.font_size_spin.setValue(font_size)
        if hasattr(self.parent_window, 'code_preview') and self.parent_window.code_preview:
            font = self.parent_window.code_preview.code_edit.font()
            font.setPointSize(font_size)
            self.parent_window.code_preview.code_edit.setFont(font)
        
        tab_size = config.get('editor_tab_size', 4)
        self.tab_size_spin.setValue(tab_size)
        if hasattr(self.parent_window, 'code_preview') and self.parent_window.code_preview:
            self.parent_window.code_preview.code_edit.setTabStopDistance(
                tab_size * self.parent_window.code_preview.code_edit.fontMetrics().horizontalAdvance(' ')
            )

    def on_theme_changed(self, state):
        pass

    def on_show_grid_changed(self, state):
        if hasattr(self.parent_window, 'scene') and self.parent_window.scene:
            self.parent_window.scene.show_grid = (state == Qt.CheckState.Checked.value)
            self.parent_window.scene.update()

    def on_grid_size_changed(self, value):
        if hasattr(self.parent_window, 'scene') and self.parent_window.scene:
            self.parent_window.scene.dot_spacing = value
            self.parent_window.scene.update()

    def on_auto_save_changed(self, state):
        pass

    def on_auto_save_interval_changed(self, value):
        pass

    def on_word_wrap_changed(self, state):
        # 实时预览
        if hasattr(self.parent_window, 'code_preview') and self.parent_window.code_preview:
            wrap = (state == Qt.CheckState.Checked.value)
            if wrap:
                self.parent_window.code_preview.code_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            else:
                self.parent_window.code_preview.code_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    def on_font_size_changed(self, value):
        # 实时预览
        if hasattr(self.parent_window, 'code_preview') and self.parent_window.code_preview:
            font = self.parent_window.code_preview.code_edit.font()
            font.setPointSize(value)
            self.parent_window.code_preview.code_edit.setFont(font)

    def on_tab_size_changed(self, value):
        # 实时预览
        if hasattr(self.parent_window, 'code_preview') and self.parent_window.code_preview:
            self.parent_window.code_preview.code_edit.setTabStopDistance(
                value * self.parent_window.code_preview.code_edit.fontMetrics().horizontalAdvance(' ')
            )

    def pick_highlight_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self.highlight_color = color.name()
            self.highlight_color_btn.setStyleSheet(f"background-color: {self.highlight_color};")

    def add_highlight(self):
        word = self.highlight_word_edit.text().strip()
        if not word:
            return
        # 检查是否已存在
        for i in range(self.highlight_list.count()):
            item = self.highlight_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == word:
                return
        # 添加到列表
        item_text = f"  {word}  "
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, word)
        item.setData(Qt.ItemDataRole.UserRole + 1, self.highlight_color)
        item.setForeground(QColor(self.highlight_color))
        self.highlight_list.addItem(item)
        self.highlight_word_edit.clear()
        self.apply_highlight_highlights()

    def delete_highlight(self):
        selected = self.highlight_list.selectedItems()
        for item in selected:
            self.highlight_list.takeItem(self.highlight_list.row(item))
        self.apply_highlight_highlights()

    def apply_highlight_highlights(self):
        """应用高亮规则到代码编辑器"""
        if hasattr(self.parent_window, 'code_preview') and self.parent_window.code_preview:
            code_edit = self.parent_window.code_preview.code_edit
            code_edit.clear_extra_selections()
            for i in range(self.highlight_list.count()):
                item = self.highlight_list.item(i)
                word = item.data(Qt.ItemDataRole.UserRole)
                color = item.data(Qt.ItemDataRole.UserRole + 1)
                if word and color:
                    code_edit.add_highlight_rule(word, color)

    def get_highlight_rules(self):
        """获取高亮规则列表"""
        rules = []
        for i in range(self.highlight_list.count()):
            item = self.highlight_list.item(i)
            word = item.data(Qt.ItemDataRole.UserRole)
            color = item.data(Qt.ItemDataRole.UserRole + 1)
            if word and color:
                rules.append({'word': word, 'color': color})
        return rules

    def set_highlight_rules(self, rules):
        """从规则列表恢复高亮设置"""
        self.highlight_list.clear()
        for rule in rules:
            word = rule.get('word', '')
            color = rule.get('color', '#FFD700')
            item_text = f"  {word}  "
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, word)
            item.setData(Qt.ItemDataRole.UserRole + 1, color)
            item.setForeground(QColor(color))
            self.highlight_list.addItem(item)
        self.apply_highlight_highlights()

    def update_action_shortcut(self, key_name, shortcut_str):
        action_map = {
            "新建项目": self.parent_window.new_action,
            "保存项目": self.parent_window.save_action,
            "打开项目": self.parent_window.open_action,
            "生成代码": self.parent_window.generate_action,
            "复制节点": self.parent_window.copy_action,
            "粘贴节点": self.parent_window.paste_action,
            "撤销操作": self.parent_window.undo_action,
            "重做操作": self.parent_window.redo_action,
            "聚焦节点": getattr(self.parent_window, 'focus_node_action', None),
            "居中显示": getattr(self.parent_window, 'home_view_action', None),
            "取消选中": getattr(self.parent_window, 'deselect_all_action', None),
            "删除节点": getattr(self.parent_window, 'delete_node_action', None),
            "设置": self.parent_window.settings_action,
            "退出程序": self.parent_window.exit_action,
        }
        # 检查快捷键是否重复
        if shortcut_str != "-":
            for other_name, other_action in action_map.items():
                if other_name != key_name and other_action and other_action.shortcut():
                    other_shortcut = other_action.shortcut().toString()
                    if other_shortcut == shortcut_str:
                        QMessageBox.warning(self, "快捷键冲突",
                                          f"快捷键 '{shortcut_str}' 已被 '{other_name}' 使用！\n\n请更换其他快捷键组合。")
                        # 恢复原来的快捷键显示
                        if key_name in self.keybind_labels:
                            orig_action = action_map.get(key_name)
                            if orig_action and orig_action.shortcut():
                                self.keybind_labels[key_name].update_shortcut(orig_action.shortcut().toString())
                            else:
                                self.keybind_labels[key_name].update_shortcut("-")
                        return

        if key_name in action_map and action_map[key_name]:
            try:
                action = action_map[key_name]
                keys = QKeySequence(shortcut_str, QKeySequence.SequenceFormat.NativeText)
                if not keys.isEmpty():
                    action.setShortcut(keys)
                    # 保存到配置文件
                    if hasattr(self.parent_window, 'config'):
                        self.parent_window.config['shortcuts'][key_name] = shortcut_str
                        ConfigManager.save_config(self.parent_window.config)
                    print(f"快捷键已更新: {key_name} = {shortcut_str}")
                else:
                    print(f"快捷键解析失败: {shortcut_str}")
            except Exception as e:
                print(f"更新快捷键失败: {key_name} = {shortcut_str}, 错误: {e}")

    def closeEvent(self, event):
        """关闭设置对话框时保存所有设置"""
        if hasattr(self.parent_window, 'config'):
            config = self.parent_window.config
            config['show_grid'] = self.show_grid_cb.isChecked()
            config['grid_size'] = self.grid_size_spin.value()
            config['auto_save'] = self.auto_save_cb.isChecked()
            config['auto_save_interval'] = self.auto_save_interval_spin.value()
            config['editor_word_wrap'] = self.word_wrap_cb.isChecked()
            config['editor_font_size'] = self.font_size_spin.value()
            config['editor_tab_size'] = self.tab_size_spin.value()
            ConfigManager.save_config(config)
        self.accept()


class MultiLineEditorDialog(QDialog):
    """多行文本编辑器对话框"""

    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        self.editor = LuaCodeEditor()
        self.editor.setPlainText(content)
        layout.addWidget(self.editor)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def get_content(self):
        return self.editor.toPlainText()


class PropertiesDialog(QDialog):
    """属性编辑对话框"""

    # 始终使用多行编辑器的字段名
    MULTI_LINE_KEYS = {'code'}

    def __init__(self, node: Node, parent=None):
        super().__init__(parent)
        self.node = node
        self.multi_line_values = {}
        self.original_multi_line_values = {}
        self.init_ui()

    def is_multi_line_key(self, key):
        if key in self.MULTI_LINE_KEYS:
            return True
        config = self.node._get_config()
        value = config.get(key)
        return isinstance(value, str) and ('\n' in value or len(value) > 50)

    def init_ui(self):
        self.setWindowTitle("编辑属性")
        self.setMinimumWidth(300)

        layout = QFormLayout(self)

        self.edits = {}
        config = self.node._get_config()

        for key, value in config.items():
            if self.is_multi_line_key(key):
                display_text = str(value[:50]) + '...' if len(str(value)) > 50 else str(value)
                edit = QLineEdit(display_text)
                edit.setReadOnly(True)
                button = QPushButton("编辑")
                button.clicked.connect(lambda checked, k=key, v=value: self.open_multi_line_editor(k, v))
                row_layout = QHBoxLayout()
                row_layout.addWidget(edit, 1)
                row_layout.addWidget(button)
                layout.addRow(key, row_layout)
                self.edits[key] = edit
                self.original_multi_line_values[key] = value
            else:
                edit = QLineEdit(str(value))
                layout.addRow(key, edit)
                self.edits[key] = edit

        buttons = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)

    def open_multi_line_editor(self, key, value):
        dialog = MultiLineEditorDialog(f"编辑 {key}", str(value), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_value = dialog.get_content()
            self.multi_line_values[key] = new_value
            self.original_multi_line_values[key] = new_value
            if key in self.edits:
                self.edits[key].setText(new_value[:50] + '...' if len(new_value) > 50 else new_value)

    def get_values(self):
        values = {}
        config = self.node._get_config()
        for key, edit in self.edits.items():
            if key in self.multi_line_values:
                values[key] = self.multi_line_values[key]
            elif key in self.original_multi_line_values:
                values[key] = self.original_multi_line_values[key]
            else:
                raw = edit.text()
                original = config.get(key)
                if isinstance(original, bool):
                    values[key] = raw.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(original, int):
                    try:
                        values[key] = int(raw)
                    except ValueError:
                        values[key] = original
                elif isinstance(original, float):
                    try:
                        values[key] = float(raw)
                    except ValueError:
                        values[key] = original
                else:
                    values[key] = raw
        return values


class LineNumberArea(QWidget):
    """行号显示区域"""

    def __init__(self, editor: 'LuaCodeEditor'):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.line_number_area_width(), 0)

    def line_number_area_width(self):
        digits = max(1, len(str(self.code_editor.blockCount())))
        space = 5 + self.code_editor.fontMetrics().horizontalAdvance('9') * digits
        return space

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(30, 30, 30))

        block = self.code_editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.code_editor.blockBoundingGeometry(block).translated(
            self.code_editor.contentOffset()).top())
        bottom = top + round(self.code_editor.blockBoundingRect(block).height())
        line_height = self.code_editor.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(100, 100, 100))
                painter.drawText(0, top, self.width() - 5,
                               line_height,
                               Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.code_editor.blockBoundingRect(block).height())
            block_number += 1


class LuaCodeEditor(QPlainTextEdit):
    """带行号、Tab补全的Lua代码编辑器"""

    KEYWORDS = [
        'context', 'M', 'self', 'local', 'function', 'return', 'if', 'then',
        'else', 'end', 'true', 'false', 'nil', 'and', 'or', 'not'
    ]

    CONTEXT_METHODS = [
        'runAnimation', 'stopAnimation', 'popShellFrom', 'setShouldHideCrossHair',
        'anchorWalkDist', 'trigger', 'getTrack', 'ensureTrackLineSize',
        'ensureTracksAmount'
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))
        self.setStyleSheet("""
            QPlainTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 0 5px 0 20px;
            }
        """)
        self._completions = []
        self._current_completion = -1
        self._highlight_rules = []

        # 行号区域
        self.line_number_area = LineNumberArea(self)
        self.line_number_width = 40
        self.setViewportMargins(self.line_number_width, 0, 0, 0)

        self.blockCountChanged.connect(self._update_line_number_width)
        self.verticalScrollBar().valueChanged.connect(self._update_line_number_area)
        self.textChanged.connect(self._apply_highlight_selections)

    def add_highlight_rule(self, word, color):
        """添加高亮规则"""
        self._highlight_rules.append({'word': word, 'color': color})
        self._apply_highlight_selections()

    def clear_extra_selections(self):
        """清除高亮规则"""
        self._highlight_rules.clear()
        self.setExtraSelections([])

    def _apply_highlight_selections(self):
        """应用高亮选区"""
        try:
            if not self._highlight_rules:
                self.setExtraSelections([])
                return

            if self.document() is None:
                return

            selections = []
            full_text = self.toPlainText()
            font = self.font()

            for rule in self._highlight_rules:
                word = rule['word']
                color_str = rule['color']
                start = 0
                while True:
                    idx = full_text.find(word, start)
                    if idx == -1:
                        break
                    sel = QTextEdit.ExtraSelection()
                    sel.format.setBackground(QColor(color_str))
                    sel.format.setForeground(QColor('#000000'))
                    sel.format.setFontWeight(font.weight())
                    cursor = QTextCursor(self.document())
                    cursor.setPosition(idx)
                    cursor.setPosition(idx + len(word), QTextCursor.MoveMode.KeepAnchor)
                    sel.cursor = cursor
                    selections.append(sel)
                    start = idx + len(word)

            self.setExtraSelections(selections)
        except Exception:
            pass

    def _update_line_number_width(self):
        self.line_number_width = self.line_number_area.line_number_area_width()
        self.setViewportMargins(self.line_number_width, 0, 0, 0)
        self.line_number_area.update()

    def _update_line_number_area(self):
        self.line_number_area.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.line_number_area.setGeometry(0, 0, self.line_number_width, self.height())

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self.line_number_area.update()


class CodePreview(QWidget):
    """代码预览面板"""

    def __init__(self, editor: 'NodeEditor'):
        super().__init__()
        self.editor = editor
        self.init_ui()

    def init_ui(self):
        from PyQt6.QtWidgets import QScrollBar
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QHBoxLayout()
        title = QLabel("📝 Lua 代码")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 8px; background: #333; color: white;")
        header.addWidget(title)

        copy_btn = QPushButton("复制")
        copy_btn.setStyleSheet("QPushButton { background: #094771; color: white; border: none; padding: 5px 10px; }")
        copy_btn.clicked.connect(self.copy_code)
        header.addWidget(copy_btn)

        download_btn = QPushButton("下载")
        download_btn.setStyleSheet("QPushButton { background: #094771; color: white; border: none; padding: 5px 10px; }")
        download_btn.clicked.connect(self.download_code)
        header.addWidget(download_btn)

        layout.addLayout(header)

        self.code_edit = LuaCodeEditor()
        layout.addWidget(self.code_edit)

    def update_code(self, code: str):
        self.code_edit.setPlainText(code)
        self.code_edit._apply_highlight_selections()

    def copy_code(self):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_edit.toPlainText())
        QMessageBox.information(self, "提示", "代码已复制！")

    def download_code(self):
        filename, _ = QFileDialog.getSaveFileName(self, "保存", "", "Lua Files (*.lua)")
        if filename:
            if not filename.endswith('.lua'):
                filename += '.lua'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.code_edit.toPlainText())
            QMessageBox.information(self, "提示", f"已保存到 {filename}")


class NodeEditor(QMainWindow):
    """节点编辑器主窗口"""

    def __init__(self):
        super().__init__()
        
        # 获取日志记录器
        from pyqt6_editor.logger import Logger
        self.logger = Logger.get_logger()
        self.logger.info("NodeEditor 初始化开始")
        
        self.scene = NodeScene(self)
        self.init_ui()
        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        
        # 撤销/重做栈
        self.undo_stack = []
        self.redo_stack = []
        self.max_stack_size = 50

        # 加载配置
        self.logger.info("加载配置文件...")
        self.config = ConfigManager.load_config()
        self.logger.info(f"配置加载成功: {ConfigManager.get_config_path()}")
        
        # 保存初始状态（空场景）
        self.record_operation()
        self.logger.info("NodeEditor 初始化完成")

    def init_ui(self):
        self.setWindowTitle("TACZ Lua Map 编辑器")
        self.setGeometry(100, 100, 1400, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.palette = NodePalette(self)
        self.palette.setMaximumWidth(220)
        self.palette.setMinimumWidth(180)
        self.palette.load_nodes()

        self.graphics_view = NodeGraphicsView(self.scene)

        self.code_preview = CodePreview(self)
        self.code_preview.setMinimumWidth(350)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.palette)
        splitter.addWidget(self.graphics_view)
        splitter.addWidget(self.code_preview)
        splitter.setSizes([220, 800, 380])

        main_layout.addWidget(splitter)

        self.statusBar()
        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet("padding: 0px 10px; color: gray;")
        self.statusBar().addPermanentWidget(self.zoom_label)

    def create_actions(self):
        self.new_action = QAction("新建", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.triggered.connect(self.new_project)

        self.save_action = QAction("保存", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_project)

        self.open_action = QAction("打开", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.open_project)

        self.generate_action = QAction("生成代码", self)
        self.generate_action.setShortcut(QKeySequence("Ctrl+G"))
        self.generate_action.triggered.connect(self.generate_code)

        self.copy_action = QAction("复制", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.triggered.connect(self.copy_nodes)

        self.paste_action = QAction("粘贴", self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.triggered.connect(self.paste_nodes)

        self.theme_action = QAction("切换主题", self)
        self.theme_action.setShortcut(QKeySequence("Ctrl+T"))
        self.theme_action.triggered.connect(self.toggle_theme)

        self.scratch_preview_action = QAction("Scratch 预览", self)
        self.scratch_preview_action.triggered.connect(self.show_scratch_preview)

        self.undo_action = QAction("撤销", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.undo)

        self.redo_action = QAction("重做", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.redo)

        self.settings_action = QAction("设置", self)
        self.settings_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.settings_action.triggered.connect(self.show_settings)

        self.exit_action = QAction("退出", self)
        self.exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.exit_action.triggered.connect(self.close)

        self.focus_node_action = QAction("聚焦节点", self)
        self.focus_node_action.setShortcut(QKeySequence("F"))
        self.focus_node_action.triggered.connect(self.focus_selected_node)

        self.home_view_action = QAction("居中显示", self)
        self.home_view_action.setShortcut(QKeySequence("Home"))
        self.home_view_action.triggered.connect(self.home_all_nodes)

        self.deselect_all_action = QAction("取消选中", self)
        self.deselect_all_action.setShortcut(QKeySequence("Ctrl+D"))
        self.deselect_all_action.triggered.connect(self.deselect_all)

        self.delete_node_action = QAction("删除节点", self)
        self.delete_node_action.setShortcut(QKeySequence("Delete"))
        self.delete_node_action.triggered.connect(self.delete_selected_nodes)

        self.alt_copy_hint_action = QAction("Alt+拖拽快速复制", self)
        self.pan_hint_action = QAction("Ctrl+左键拖拽移动画布", self)

        # 加载保存的快捷键配置
        self.load_shortcuts_from_config()

    def load_shortcuts_from_config(self):
        """从配置文件加载快捷键"""
        if not hasattr(self, 'config') or 'shortcuts' not in self.config:
            return
            
        action_map = {
            "新建项目": self.new_action,
            "保存项目": self.save_action,
            "打开项目": self.open_action,
            "生成代码": self.generate_action,
            "复制节点": self.copy_action,
            "粘贴节点": self.paste_action,
            "撤销操作": self.undo_action,
            "重做操作": self.redo_action,
            "切换主题": self.theme_action,
            "退出程序": self.exit_action,
        }
        
        shortcuts = self.config['shortcuts']
        for key_name, shortcut_str in shortcuts.items():
            if key_name in action_map and action_map[key_name]:
                try:
                    keys = QKeySequence.parseShortcut(shortcut_str)
                    action_map[key_name].setShortcut(keys)
                except Exception as e:
                    print(f"加载快捷键失败: {key_name} - {e}")

    def toggle_theme(self):
        """切换主题"""
        app = QApplication.instance()
        if not hasattr(self, 'is_dark_theme'):
            self.is_dark_theme = True
        
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            # 深色主题
            app.setStyleSheet("""
                QWidget {
                    background-color: rgb(30, 30, 30);
                    color: rgb(220, 220, 220);
                }
                QMenuBar {
                    background-color: rgb(45, 45, 48);
                    color: rgb(220, 220, 220);
                }
                QMenuBar::item:selected {
                    background-color: rgb(70, 70, 75);
                }
                QMenu {
                    background-color: rgb(45, 45, 48);
                    color: rgb(220, 220, 220);
                    border: 1px solid rgb(60, 60, 65);
                }
                QMenu::item:selected {
                    background-color: rgb(70, 70, 75);
                }
                QToolBar {
                    background-color: rgb(45, 45, 48);
                    border: none;
                }
                QToolButton {
                    background-color: rgb(45, 45, 48);
                    color: rgb(220, 220, 220);
                    padding: 5px;
                }
                QToolButton:hover {
                    background-color: rgb(70, 70, 75);
                }
                QStatusBar {
                    background-color: rgb(30, 30, 30);
                    color: rgb(180, 180, 180);
                }
                QTreeWidget {
                    background-color: rgb(35, 35, 38);
                    color: rgb(220, 220, 220);
                    border: none;
                }
                QTreeWidget::item:selected {
                    background-color: rgb(60, 60, 140);
                }
                QTreeWidget::item:hover {
                    background-color: rgb(55, 55, 60);
                }
                QTextEdit, QPlainTextEdit {
                    background-color: rgb(35, 35, 38);
                    color: rgb(220, 220, 220);
                    border: 1px solid rgb(60, 60, 65);
                }
                QScrollBar:vertical {
                    background: rgb(40, 40, 45);
                    width: 12px;
                }
                QScrollBar::handle:vertical {
                    background: rgb(80, 80, 85);
                    min-height: 20px;
                }
                QScrollBar:horizontal {
                    background: rgb(40, 40, 45);
                    height: 12px;
                }
                QScrollBar::handle:horizontal {
                    background: rgb(80, 80, 85);
                    min-width: 20px;
                }
                QSplitter::handle {
                    background-color: rgb(60, 60, 65);
                }
                QLabel {
                    background-color: transparent;
                    color: rgb(220, 220, 220);
                }
                QPushButton {
                    background-color: rgb(55, 55, 60);
                    color: rgb(220, 220, 220);
                    border: 1px solid rgb(70, 70, 75);
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: rgb(70, 70, 75);
                }
                QPushButton:pressed {
                    background-color: rgb(45, 45, 50);
                }
                QInputDialog, QFileDialog {
                    background-color: rgb(45, 45, 48);
                }
                QMessageBox {
                    background-color: rgb(45, 45, 48);
                }
                QTabWidget::pane {
                    border: 1px solid rgb(60, 60, 65);
                    background-color: rgb(35, 35, 38);
                }
                QTabBar::tab {
                    background-color: rgb(40, 40, 45);
                    color: rgb(180, 180, 180);
                    padding: 5px 15px;
                }
                QTabBar::tab:selected {
                    background-color: rgb(35, 35, 38);
                    color: rgb(220, 220, 220);
                }
            """)
        else:
            # 亮色主题
            app.setStyleSheet("""
                QWidget {
                    background-color: rgb(240, 240, 240);
                    color: rgb(30, 30, 30);
                }
                QMenuBar {
                    background-color: rgb(220, 220, 220);
                    color: rgb(30, 30, 30);
                }
                QMenuBar::item:selected {
                    background-color: rgb(180, 180, 180);
                }
                QMenu {
                    background-color: rgb(220, 220, 220);
                    color: rgb(30, 30, 30);
                    border: 1px solid rgb(180, 180, 180);
                }
                QMenu::item:selected {
                    background-color: rgb(180, 180, 180);
                }
                QToolBar {
                    background-color: rgb(220, 220, 220);
                    border: none;
                }
                QToolButton {
                    background-color: rgb(220, 220, 220);
                    color: rgb(30, 30, 30);
                    padding: 5px;
                }
                QToolButton:hover {
                    background-color: rgb(180, 180, 180);
                }
                QStatusBar {
                    background-color: rgb(240, 240, 240);
                    color: rgb(60, 60, 60);
                }
                QTreeWidget {
                    background-color: rgb(255, 255, 255);
                    color: rgb(30, 30, 30);
                    border: 1px solid rgb(180, 180, 180);
                }
                QTreeWidget::item:selected {
                    background-color: rgb(100, 100, 200);
                    color: white;
                }
                QTreeWidget::item:hover {
                    background-color: rgb(200, 200, 200);
                }
                QTextEdit, QPlainTextEdit {
                    background-color: rgb(255, 255, 255);
                    color: rgb(30, 30, 30);
                    border: 1px solid rgb(180, 180, 180);
                }
                QScrollBar:vertical {
                    background: rgb(220, 220, 220);
                    width: 12px;
                }
                QScrollBar::handle:vertical {
                    background: rgb(180, 180, 180);
                    min-height: 20px;
                }
                QScrollBar:horizontal {
                    background: rgb(220, 220, 220);
                    height: 12px;
                }
                QScrollBar::handle:horizontal {
                    background: rgb(180, 180, 180);
                    min-width: 20px;
                }
                QSplitter::handle {
                    background-color: rgb(180, 180, 180);
                }
                QLabel {
                    background-color: transparent;
                    color: rgb(30, 30, 30);
                }
                QPushButton {
                    background-color: rgb(220, 220, 220);
                    color: rgb(30, 30, 30);
                    border: 1px solid rgb(180, 180, 180);
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: rgb(180, 180, 180);
                }
                QPushButton:pressed {
                    background-color: rgb(200, 200, 200);
                }
                QInputDialog, QFileDialog {
                    background-color: rgb(220, 220, 220);
                }
                QMessageBox {
                    background-color: rgb(220, 220, 220);
                }
                QTabWidget::pane {
                    border: 1px solid rgb(180, 180, 180);
                    background-color: rgb(255, 255, 255);
                }
                QTabBar::tab {
                    background-color: rgb(220, 220, 220);
                    color: rgb(60, 60, 60);
                    padding: 5px 15px;
                }
                QTabBar::tab:selected {
                    background-color: rgb(255, 255, 255);
                    color: rgb(30, 30, 30);
                }
            """)
        # 更新场景背景
        if self.is_dark_theme:
            self.scene.setBackgroundBrush(QColor(45, 45, 48))
            self.scene.dot_color = QColor(80, 80, 85)
        else:
            self.scene.setBackgroundBrush(QColor(240, 240, 240))
            self.scene.dot_color = QColor(180, 180, 180)
        self.scene.update()

    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def create_menus(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("background: #2d2d30; color: white;")

        file_menu = menubar.addMenu("文件")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menubar.addMenu("编辑")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.generate_action)

        view_menu = menubar.addMenu("视图")
        view_menu.addAction(self.scratch_preview_action)

        tools_menu = menubar.addMenu("工具")
        tools_menu.addAction(self.settings_action)

        help_menu = menubar.addMenu("帮助")
        
        # 查看日志文件
        open_log_action = QAction("查看日志文件", self)
        open_log_action.triggered.connect(self.open_log_file)
        help_menu.addAction(open_log_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setStyleSheet("background: #333; color: white;")
        self.addToolBar(toolbar)
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.generate_action)

    def new_project(self):
        reply = QMessageBox.question(self, "确认", "确定新建？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.scene.clear()
            self.code_preview.update_code("")

    def open_project(self):
        filename, _ = QFileDialog.getOpenFileName(self, "打开", "", "TLM 项目 (*.tlm)")
        if filename:
            self.load_project(filename)

    def save_project(self):
        filename, _ = QFileDialog.getSaveFileName(self, "保存", "", "TLM 项目 (*.tlm)")
        if filename:
            if not filename.endswith('.tlm'):
                filename += '.tlm'
            data = {
                'nodes': [n.to_dict() for n in self.scene.nodes],
                'connections': [c.to_dict() for c in self.scene.connections]
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            QMessageBox.information(self, "提示", f"已保存到 {filename}")

    def load_project(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.scene.clear()
        node_map = {}
        for node_data in data.get('nodes', []):
            node = NodeRegistry.create(node_data['class'], x=node_data['x'], y=node_data['y'])
            if node:
                node.id = node_data['id']
                # 恢复端口 ID
                for i, input_data in enumerate(node_data.get('inputs', [])):
                    if i < len(node.inputs):
                        node.inputs[i].id = input_data.get('id', node.inputs[i].id)
                for i, output_data in enumerate(node_data.get('outputs', [])):
                    if i < len(node.outputs):
                        node.outputs[i].id = output_data.get('id', node.outputs[i].id)
                item = self.scene.add_node(node)
                node_map[node.id] = item

        # 加载连接
        for conn_data in data.get('connections', []):
            input_node_id = conn_data.get('input_node_id')
            output_node_id = conn_data.get('output_node_id')
            input_port_id = conn_data.get('input_port_id')
            output_port_id = conn_data.get('output_port_id')

            if input_node_id in node_map and output_node_id in node_map:
                input_item = node_map[input_node_id]
                output_item = node_map[output_node_id]

                # 找到对应的端口
                input_port_item = None
                output_port_item = None
                for port_item in input_item.input_port_items:
                    if port_item.port.id == input_port_id:
                        input_port_item = port_item
                        break
                for port_item in output_item.output_port_items:
                    if port_item.port.id == output_port_id:
                        output_port_item = port_item
                        break

                if input_port_item and output_port_item:
                    self.create_connection(output_port_item, input_port_item)

    def generate_code(self):
        generator = LuaCodeGenerator()
        code = generator.generate(self.scene.nodes, self.scene.connections)
        self.code_preview.update_code(code)

    def auto_generate_code(self):
        """自动生成代码"""
        generator = LuaCodeGenerator()
        code = generator.generate(self.scene.nodes, self.scene.connections)
        self.code_preview.update_code(code)

    def start_connection_drag(self, port_item: 'PortGraphicsItem'):
        """开始拖拽连接"""
        if self.scene.drag_output_port is not None:
            return
        self.scene.drag_output_port = port_item.port
        pos = port_item.get_port_position()
        self.scene.temp_line = TempConnectionLine(pos[0], pos[1])
        self.scene.addItem(self.scene.temp_line)

    def end_connection_drag(self, input_port_item: 'PortGraphicsItem'):
        """结束拖拽连接"""
        if self.scene.drag_output_port is None:
            return

        # 不允许同节点连接
        if self.scene.drag_output_port.node.id == input_port_item.port.node.id:
            self.scene.cleanup_drag()
            return

        output_port_item = self.scene.drag_output_port.graphics_item
        if output_port_item is not None:
            self.create_connection(output_port_item, input_port_item)

        self.scene.cleanup_drag()

    def create_connection(self, output_port: 'PortGraphicsItem', input_port: 'PortGraphicsItem'):
        from .node import PortDirection

        if output_port.port.direction != PortDirection.OUTPUT:
            return

        if input_port.port.direction != PortDirection.INPUT:
            return

        if output_port.port.port_type != input_port.port.port_type:
            return

        # 将 PortGraphicsItem 引用附加到 Port 对象上
        output_port.port.graphics_item = output_port
        input_port.port.graphics_item = input_port

        connection = Connection(output_port.port, input_port.port)
        self.scene.add_connection(connection)
        self.scene.update()
        # 记录操作
        self.record_operation()

    def edit_node_properties(self, node: Node):
        """编辑节点属性"""
        dialog = PropertiesDialog(node, self)
        if dialog.exec():
            values = dialog.get_values()
            # 存储到节点的 _stored_config，这样 _get_config() 会返回更新后的值
            if node._stored_config is None:
                node._stored_config = {}
            for key, value in values.items():
                node._stored_config[key] = value
            # 保存版本
            node.save_version("编辑属性")
            # 重新创建节点图形项以更新大小
            if node.id in self.scene.node_items:
                old_item = self.scene.node_items[node.id]
                old_pos = old_item.pos()
                # 从场景移除旧图形项
                self.scene.removeItem(old_item)
                # 移除旧的端口图形项
                if hasattr(old_item, 'input_port_items'):
                    for port_item in old_item.input_port_items:
                        self.scene.removeItem(port_item)
                if hasattr(old_item, 'output_port_items'):
                    for port_item in old_item.output_port_items:
                        self.scene.removeItem(port_item)
                # 删除旧图形项
                del self.scene.node_items[node.id]
                # 使用add_node重新创建，确保端口项正确创建
                # 保存节点当前位置
                old_x, old_y = node.x, node.y
                node.x = old_pos.x()
                node.y = old_pos.y()
                self.scene.add_node(node)
                # 重新设置位置
                new_item = self.scene.node_items.get(node.id)
                if new_item:
                    new_item.setPos(old_pos)
                # 重新创建连接
                for conn in self.scene.connections:
                    if conn.input_port.node.id == node.id or conn.output_port.node.id == node.id:
                        # 检查是否已经有这个连接的图形项
                        has_item = False
                        for ci in self.scene.connection_items:
                            if ci.connection.id == conn.id:
                                has_item = True
                                break
                        if not has_item:
                            input_item = self.scene.node_items.get(conn.input_port.node.id)
                            output_item = self.scene.node_items.get(conn.output_port.node.id)
                            if input_item and output_item:
                                conn_item = ConnectionGraphicsItem(conn, self.scene)
                                self.scene.connection_items.append(conn_item)
                                self.scene.addItem(conn_item)
            self.scene.update()
            # 自动生成代码
            self.auto_generate_code()
            # 记录操作
            self.record_operation()

    def update_connections(self):
        self.scene.update()

    def focus_selected_node(self):
        """聚焦到选中的节点"""
        selected_items = self.scene.selectedItems()
        node_items = [item for item in selected_items if isinstance(item, NodeGraphicsItem)]
        if node_items:
            item = node_items[0]
            rect = item.boundingRect()
            center = rect.center() + item.pos()
            self.graphics_view.centerOn(center)

    def home_all_nodes(self):
        """居中显示所有节点"""
        if self.scene.node_items:
            rect = self.scene.itemsBoundingRect()
            self.graphics_view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            self.graphics_view.scale(0.8, 0.8)

    def deselect_all(self):
        """取消所有选中"""
        for item in self.scene.selectedItems():
            item.setSelected(False)

    def delete_selected_nodes(self):
        """删除选中节点"""
        selected_items = self.scene.selectedItems()
        node_items = [item for item in selected_items if isinstance(item, NodeGraphicsItem)]
        if node_items:
            nodes = [item.node for item in node_items]
            self.scene.remove_nodes(nodes)

    def copy_nodes(self):
        """复制选中节点"""
        selected_items = self.scene.selectedItems()
        node_items = [item for item in selected_items if isinstance(item, NodeGraphicsItem)]
        if node_items:
            self.copied_nodes = []
            for item in node_items:
                # 保存节点数据
                node_data = item.node.to_dict()
                self.copied_nodes.append(node_data)

    def paste_nodes(self):
        """粘贴节点"""
        if hasattr(self, 'copied_nodes') and self.copied_nodes:
            # 计算偏移量
            offset = 20
            for node_data in self.copied_nodes:
                # 创建新节点
                node = NodeRegistry.create(node_data['class'], x=node_data['x'] + offset, y=node_data['y'] + offset)
                if node:
                    # 恢复节点属性
                    node.id = node_data['id']
                    for i, input_data in enumerate(node_data.get('inputs', [])):
                        if i < len(node.inputs):
                            node.inputs[i].id = input_data.get('id', node.inputs[i].id)
                    for i, output_data in enumerate(node_data.get('outputs', [])):
                        if i < len(node.outputs):
                            node.outputs[i].id = output_data.get('id', node.outputs[i].id)
                    # 添加到场景
                    self.scene.add_node(node)
            # 自动生成代码
            self.auto_generate_code()
            # 记录操作
            self.record_operation()

    def keyPressEvent(self, event):
        """处理键盘事件"""
        # Tab键：在鼠标位置弹出搜索框，支持直接创建节点
        if event.key() == Qt.Key.Key_Tab:
            # 获取鼠标位置
            pos = self.graphics_view.mapFromGlobal(QCursor.pos())
            scene_pos = self.graphics_view.mapToScene(pos)
            # 弹出搜索对话框
            node_name, ok = QInputDialog.getText(self, "创建节点", "请输入节点名称：")
            if ok and node_name:
                # 查找匹配的节点
                nodes = NodeRegistry.get_all_nodes()
                matching_nodes = [name for name in nodes if node_name.lower() in name.lower()]
                if matching_nodes:
                    # 如果只有一个匹配，直接创建
                    if len(matching_nodes) == 1:
                        node = NodeRegistry.create(matching_nodes[0], x=scene_pos.x(), y=scene_pos.y())
                        if node:
                            self.scene.add_node(node)
                    else:
                        # 多个匹配，让用户选择
                        node_choice, ok = QInputDialog.getItem(self, "选择节点", "请选择要创建的节点：", matching_nodes, 0, False)
                        if ok:
                            node = NodeRegistry.create(node_choice, x=scene_pos.x(), y=scene_pos.y())
                            if node:
                                self.scene.add_node(node)
        else:
            super().keyPressEvent(event)

    def show_scratch_preview(self):
        """显示 Scratch 预览界面"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Scratch 预览 - 节点分类参考")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # 标题
        title = QLabel("🧩 节点分类参考")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; background: #333; color: white;")
        layout.addWidget(title)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 节点分类
        tags = NodeRegistry.get_tags()
        node_tags = NodeRegistry.get_node_tags()
        
        for tag in sorted(tags):
            # 分类标题
            tag_label = QLabel(f"<b>{tag}</b>")
            tag_label.setStyleSheet("font-size: 14px; padding: 8px; background: #444; color: white;")
            scroll_layout.addWidget(tag_label)
            
            # 节点列表
            nodes_in_tag = [name for name, t in node_tags.items() if t == tag]
            if nodes_in_tag:
                node_container = QWidget()
                node_layout = QHBoxLayout(node_container)
                node_layout.setContentsMargins(10, 5, 10, 5)
                
                for node_name in sorted(nodes_in_tag):
                    title = NodeRegistry.get_node_title(node_name)
                    description = NodeRegistry.get_node_description(node_name)
                    
                    node_widget = QWidget()
                    node_widget.setStyleSheet("""
                        QWidget {
                            background-color: #555;
                            border-radius: 8px;
                            padding: 10px;
                            margin: 5px;
                        }
                        QWidget:hover {
                            background-color: #666;
                        }
                    """)
                    node_widget.setToolTip(description)
                    
                    node_vlayout = QVBoxLayout(node_widget)
                    node_title = QLabel(title)
                    node_title.setStyleSheet("font-weight: bold; color: white;")
                    node_vlayout.addWidget(node_title)
                    
                    # 简短描述
                    if description:
                        short_desc = description.split('\n')[0] if '\n' in description else description
                        if len(short_desc) > 50:
                            short_desc = short_desc[:50] + '...'
                        desc_label = QLabel(short_desc)
                        desc_label.setStyleSheet("font-size: 10px; color: #ccc;")
                        desc_label.setWordWrap(True)
                        node_vlayout.addWidget(desc_label)
                    
                    node_layout.addWidget(node_widget)
                
                scroll_layout.addWidget(node_container)
            else:
                empty_label = QLabel("  无节点")
                empty_label.setStyleSheet("color: #888; padding: 5px 10px;")
                scroll_layout.addWidget(empty_label)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        dialog.exec()

    def undo(self):
        """撤销操作"""
        if len(self.undo_stack) > 1:
            # 当前状态移入重做栈
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            # 恢复上一个状态
            prev_state = self.undo_stack[-1]
            self.restore_state(prev_state)
            print(f"撤销成功，当前栈大小: {len(self.undo_stack)}")
        else:
            print(f"无法撤销，栈大小: {len(self.undo_stack)}")

    def redo(self):
        """重做操作"""
        if self.redo_stack:
            # 重做状态移回撤销栈
            next_state = self.redo_stack.pop()
            self.undo_stack.append(next_state)
            self.restore_state(next_state)
            print(f"重做成功，当前栈大小: {len(self.undo_stack)}")
        else:
            print("无法重做，重做栈为空")

    def save_state(self):
        """保存当前状态"""
        return {
            'nodes': [n.to_dict() for n in self.scene.nodes],
            'connections': [c.to_dict() for c in self.scene.connections]
        }

    def restore_state(self, state):
        """恢复状态"""
        # 清空当前场景
        self.scene.clear()
        
        # 恢复节点
        node_map = {}
        for node_data in state.get('nodes', []):
            node = NodeRegistry.create(node_data['class'], x=node_data['x'], y=node_data['y'])
            if node:
                node.id = node_data['id']
                # 恢复节点配置
                if 'config' in node_data and node_data['config']:
                    node_config = node._get_config()
                    for key, value in node_data['config'].items():
                        if key in node_config:
                            node_config[key] = value
                # 恢复端口 ID
                for i, input_data in enumerate(node_data.get('inputs', [])):
                    if i < len(node.inputs):
                        node.inputs[i].id = input_data.get('id', node.inputs[i].id)
                for i, output_data in enumerate(node_data.get('outputs', [])):
                    if i < len(node.outputs):
                        node.outputs[i].id = output_data.get('id', node.outputs[i].id)
                item = self.scene.add_node(node)
                node_map[node.id] = item
        
        # 恢复连接
        for conn_data in state.get('connections', []):
            input_node_id = conn_data.get('input_node_id')
            output_node_id = conn_data.get('output_node_id')
            input_port_id = conn_data.get('input_port_id')
            output_port_id = conn_data.get('output_port_id')
            
            if input_node_id in node_map and output_node_id in node_map:
                input_item = node_map[input_node_id]
                output_item = node_map[output_node_id]
                
                # 找到对应的端口
                input_port_item = None
                output_port_item = None
                for port_item in input_item.input_port_items:
                    if port_item.port.id == input_port_id:
                        input_port_item = port_item
                        break
                for port_item in output_item.output_port_items:
                    if port_item.port.id == output_port_id:
                        output_port_item = port_item
                        break
                
                if input_port_item and output_port_item:
                    self.create_connection(output_port_item, input_port_item)
        
        # 自动生成代码
        self.auto_generate_code()

    def record_operation(self):
        """记录操作到撤销栈"""
        state = self.save_state()
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_stack_size:
            self.undo_stack.pop(0)
        # 清空重做栈
        self.redo_stack.clear()

    def show_about(self):
        about_text = """
        <h2>TLM TACZ Lua Map 编辑器</h2>
        <p><b>版本：</b>v1.0.0</p>
        <p><b>作者：</b>xiaoou6630</p>
        <p><b>版权所有：</b>&copy; 2026 xiaoou6630. 保留所有权利。</p>
        <hr>
        <p>基于 PyQt6 的 TACZ 状态机可视化节点编辑器</p>
        <p><b>使用教程：</b>请查看 设置 → 帮助</p>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("关于")
        msg.setText(about_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.exec()

    def open_log_file(self):
        """打开日志文件所在目录"""
        from pyqt6_editor.logger import Logger
        log_dir = Logger.get_log_directory()
        log_file = Logger.get_log_file_path()
        
        if log_dir:
            import subprocess
            try:
                # 打开日志文件所在目录
                subprocess.Popen(['explorer', '/select,', log_file.replace('/', '\\')])
                self.logger.info(f"用户打开日志文件目录: {log_dir}")
            except Exception as e:
                self.logger.error(f"打开日志目录失败: {e}")
                QMessageBox.warning(self, "错误", f"无法打开日志目录:\n{log_dir}\n\n错误: {e}")
        else:
            QMessageBox.information(self, "提示", "日志文件尚未创建")

    def update_zoom_label(self):
        zoom = int(self.graphics_view.transform().m11() * 100)
        self.zoom_label.setText(f"缩放: {zoom}%")

    def resizeEvent(self, event):
        super().resizeEvent(event)
