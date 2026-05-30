"""
示例模组 - TLM 节点扩展包
你可以复制这个文件，创建自己的节点模组

每个节点使用 @register_node 装饰器定义
"""

from pyqt6_editor.node import Node, PortType
from pyqt6_editor.registry import NodeRegistry


def register_node(tag: str, color: str, title: str = None, description: str = None):
    """节点注册装饰器"""
    def decorator(cls):
        cls.tag = tag
        cls.color = color
        cls.title = title or cls.__name__
        cls.description = description or cls.__doc__ or ""
        return NodeRegistry.register(cls)
    return decorator


# ==================== 示例节点 ====================

@register_node("示例模组", "#FF5722", "我的节点", "这是一个自定义节点示例")
class MyCustomNode(Node):
    """自定义节点示例"""

    def _init_ports(self):
        self.add_input("输入", PortType.EXEC, "exec")
        self.add_output("输出", PortType.EXEC, "exec")

    def _get_config(self):
        return {"my_param": "hello"}
