"""
节点注册系统
"""

from typing import Type, Dict, List
from .node import Node


class NodeRegistry:
    """节点注册表"""
    
    _nodes: Dict[str, Type[Node]] = {}
    _tags: Dict[str, List[str]] = {}  # tag -> [node_class_names]
    
    @classmethod
    def register(cls, node_class: Type[Node]):
        """注册节点类"""
        name = node_class.__name__
        cls._nodes[name] = node_class
        
        # 按tag分类
        tag = getattr(node_class, 'tag', 'Base')
        if tag not in cls._tags:
            cls._tags[tag] = []
        if name not in cls._tags[tag]:
            cls._tags[tag].append(name)
        
        return node_class
    
    @classmethod
    def get(cls, name: str) -> Type[Node]:
        """获取节点类"""
        return cls._nodes.get(name)
    
    @classmethod
    def create(cls, name: str, x: float = 0, y: float = 0) -> Node:
        """创建节点实例"""
        node_class = cls.get(name)
        if node_class:
            return node_class(x=x, y=y)
        return None
    
    @classmethod
    def get_all_nodes(cls) -> Dict[str, Type[Node]]:
        """获取所有节点类"""
        return cls._nodes.copy()
    
    @classmethod
    def get_tags(cls) -> List[str]:
        """获取所有标签"""
        return list(cls._tags.keys())
    
    @classmethod
    def get_nodes_by_tag(cls, tag: str) -> List[str]:
        """根据标签获取节点名称"""
        return cls._tags.get(tag, [])
    
    @classmethod
    def get_node_tags(cls) -> Dict[str, str]:
        """获取所有节点的标签映射"""
        return {name: getattr(cls._nodes[name], 'tag', 'Base') for name in cls._nodes}
    
    @classmethod
    def get_node_title(cls, name: str) -> str:
        """获取节点的中文标题"""
        node_class = cls._nodes.get(name)
        return getattr(node_class, 'title', name) if node_class else name
    
    @classmethod
    def get_node_description(cls, name: str) -> str:
        """获取节点的描述"""
        node_class = cls._nodes.get(name)
        return getattr(node_class, 'description', '') if node_class else ''

    @classmethod
    def get_node_ports(cls, name: str) -> dict:
        """获取节点的输入/输出端口信息"""
        node_class = cls._nodes.get(name)
        if not node_class:
            return {'inputs': [], 'outputs': []}
        # 创建一个临时实例来获取端口（不添加到场景）
        try:
            temp = node_class(x=0, y=0)
            return {
                'inputs': [(p.name, p.port_type.value, p.data_type) for p in temp.inputs],
                'outputs': [(p.name, p.port_type.value, p.data_type) for p in temp.outputs],
            }
        except:
            return {'inputs': [], 'outputs': []}
