"""
节点基类和端口系统
"""

from typing import Any, Optional, List, Dict, TYPE_CHECKING
from enum import Enum
import uuid

if TYPE_CHECKING:
    from .connection import Connection


class PortType(Enum):
    """端口类型"""
    DATA = "data"
    EXEC = "exec"


class PortDirection(Enum):
    """端口方向"""
    INPUT = "input"
    OUTPUT = "output"


class Port:
    """端口类"""

    def __init__(self, name: str, port_type: PortType, direction: PortDirection, data_type: str = "any"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.port_type = port_type
        self.direction = direction
        self.data_type = data_type
        self.node: Optional['Node'] = None
        self.connections: List['Connection'] = []
        self.data: Any = None

    def connect(self, connection: 'Connection'):
        """连接到另一个端口"""
        self.connections.append(connection)

    def disconnect(self, connection: 'Connection'):
        """断开连接"""
        if connection in self.connections:
            self.connections.remove(connection)

    def get_connected_ports(self) -> List['Port']:
        """获取已连接的端口"""
        connected = []
        for conn in self.connections:
            if conn.input_port == self:
                connected.append(conn.output_port)
            elif conn.output_port == self:
                connected.append(conn.input_port)
        return connected

    def set_data(self, data: Any):
        """设置数据"""
        self.data = data

    def get_data(self) -> Any:
        """获取数据"""
        return self.data


class Node:
    """节点基类"""

    tag = "Base"
    color = "#808080"

    def __init__(self, x: float = 0, y: float = 0):
        self.id = str(uuid.uuid4())
        self.name = self.__class__.__name__
        self.tag = getattr(self.__class__, 'tag', 'Base')
        self.color = getattr(self.__class__, 'color', '#808080')

        self.x = x
        self.y = y
        self.width = 180
        self.height = 80

        self.inputs: List[Port] = []
        self.outputs: List[Port] = []

        self.version_history = []
        self.current_version = -1

        self._stored_config: Optional[Dict] = None

        self._init_ports()
        self.save_version()

    def _init_ports(self):
        """初始化端口 - 子类重写"""
        pass

    def add_input(self, name: str, port_type: PortType = PortType.DATA, data_type: str = "any") -> Port:
        """添加输入端口"""
        port = Port(name, port_type, PortDirection.INPUT, data_type)
        port.node = self
        self.inputs.append(port)
        return port

    def add_output(self, name: str, port_type: PortType = PortType.DATA, data_type: str = "any") -> Port:
        """添加输出端口"""
        port = Port(name, port_type, PortDirection.OUTPUT, data_type)
        port.node = self
        self.outputs.append(port)
        return port

    def get_port_by_name(self, name: str) -> Optional[Port]:
        """根据名称获取端口"""
        for port in self.inputs + self.outputs:
            if port.name == name:
                return port
        return None

    def get_input_by_name(self, name: str) -> Optional[Port]:
        """根据名称获取输入端口"""
        for port in self.inputs:
            if port.name == name:
                return port
        return None

    def get_output_by_name(self, name: str) -> Optional[Port]:
        """根据名称获取输出端口"""
        for port in self.outputs:
            if port.name == name:
                return port
        return None

    def execute(self):
        """执行节点 - 子类重写"""
        pass

    def to_dict(self) -> Dict:
        """序列化为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'tag': self.tag,
            'color': self.color,
            'x': self.x,
            'y': self.y,
            'inputs': [{'id': p.id, 'name': p.name, 'port_type': p.port_type.value, 'data_type': p.data_type} for p in self.inputs],
            'outputs': [{'id': p.id, 'name': p.name, 'port_type': p.port_type.value, 'data_type': p.data_type} for p in self.outputs],
            'config': self._get_config(),
            'class': self.__class__.__name__
        }

    def _get_config(self) -> Dict:
        """获取配置 - 子类重写返回默认配置，运行时修改的值存在 _stored_config"""
        default = {}
        for cls in type(self).__mro__:
            if cls is Node:
                break
            if '_get_default_config' in cls.__dict__:
                default = cls._get_default_config(self)
                break
        if self._stored_config is None:
            return default
        merged = dict(default)
        merged.update(self._stored_config)
        return merged

    @classmethod
    def from_dict(cls, data: Dict) -> 'Node':
        """从字典反序列化"""
        node = cls(x=data['x'], y=data['y'])
        node.id = data['id']

        for i, input_data in enumerate(data.get('inputs', [])):
            if i < len(node.inputs):
                node.inputs[i].id = input_data['id']
        for i, output_data in enumerate(data.get('outputs', [])):
            if i < len(node.outputs):
                node.outputs[i].id = output_data['id']

        return node

    def save_version(self, comment: str = ""):
        """保存当前版本"""
        version_data = {
            'config': self._get_config(),
            'position': (self.x, self.y),
            'comment': comment
        }
        if self.current_version < len(self.version_history) - 1:
            self.version_history = self.version_history[:self.current_version + 1]
        self.version_history.append(version_data)
        self.current_version = len(self.version_history) - 1

    def restore_version(self, version_index: int):
        """恢复到指定版本"""
        if 0 <= version_index < len(self.version_history):
            version_data = self.version_history[version_index]
            config = self._get_config()
            for key, value in version_data['config'].items():
                if key in config:
                    config[key] = value
            self.x, self.y = version_data['position']
            self.current_version = version_index
            return True
        return False

    def get_version_history(self):
        """获取版本历史"""
        return self.version_history

    def __repr__(self):
        return f"<Node '{self.name}' at ({self.x}, {self.y})>"
