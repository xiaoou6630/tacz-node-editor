"""
连接线系统
"""

from typing import Optional, Tuple
from .node import Port


_connection_order = 0

class Connection:
    """连接类"""
    
    def __init__(self, output_port: Port, input_port: Port):
        global _connection_order
        _connection_order += 1
        self.order = _connection_order
        self.id = f"{output_port.id}_{input_port.id}"
        self.output_port = output_port
        self.input_port = input_port
        
        input_port.connect(self)
        output_port.connect(self)
    
    def delete(self):
        """删除连接"""
        self.input_port.disconnect(self)
        self.output_port.disconnect(self)
    
    def get_start_point(self) -> Tuple[float, float]:
        """获取起点坐标（输出端口）"""
        # 优先使用端口图形项的实际位置
        if hasattr(self.output_port, 'graphics_item') and self.output_port.graphics_item:
            pos = self.output_port.graphics_item.get_port_position()
            return pos
        
        # 回退到使用 node 属性计算
        return (
            self.output_port.node.x + self.output_port.node.width,
            self.output_port.node.y + self._get_port_y(self.output_port)
        )
    
    def get_end_point(self) -> Tuple[float, float]:
        """获取终点坐标（输入端口）"""
        # 优先使用端口图形项的实际位置
        if hasattr(self.input_port, 'graphics_item') and self.input_port.graphics_item:
            pos = self.input_port.graphics_item.get_port_position()
            return pos
        
        # 回退到使用 node 属性计算
        return (
            self.input_port.node.x,
            self.input_port.node.y + self._get_port_y(self.input_port)
        )
    
    def _get_port_y(self, port: Port) -> float:
        """获取端口的Y坐标偏移（与 NodeGraphicsItem._draw_ports 保持一致）"""
        if port.direction.value == "input":
            ports = port.node.inputs
            index = ports.index(port)
            return 40 + index * 20
        else:
            ports = port.node.outputs
            index = ports.index(port)
            return 40 + index * 20
    
    def to_dict(self):
        """序列化为字典"""
        return {
            'id': self.id,
            'input_port_id': self.input_port.id,
            'output_port_id': self.output_port.id,
            'input_node_id': self.input_port.node.id,
            'output_node_id': self.output_port.node.id
        }
