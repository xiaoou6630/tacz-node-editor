# TACZ Lua Map 编辑器 API 文档

## 1. 核心类

### 1.1 Node 类

**描述**：节点基类，所有节点类型的父类。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `__init__(x, y)` | x: float 节点横坐标<br>y: float 节点纵坐标 | 无 | 初始化节点 |
| `_init_ports()` | 无 | 无 | 初始化端口，子类重写 |
| `add_input(name, port_type, data_type)` | name: str 端口名称<br>port_type: PortType 端口类型<br>data_type: str 数据类型 | Port | 添加输入端口 |
| `add_output(name, port_type, data_type)` | name: str 端口名称<br>port_type: PortType 端口类型<br>data_type: str 数据类型 | Port | 添加输出端口 |
| `get_port_by_name(name)` | name: str 端口名称 | Port | 根据名称获取端口 |
| `get_input_by_name(name)` | name: str 端口名称 | Port | 根据名称获取输入端口 |
| `get_output_by_name(name)` | name: str 端口名称 | Port | 根据名称获取输出端口 |
| `execute()` | 无 | 无 | 执行节点，子类重写 |
| `to_dict()` | 无 | dict | 序列化为字典 |
| `_get_config()` | 无 | dict | 获取配置，子类重写 |
| `from_dict(data)` | data: dict 节点数据 | Node | 从字典反序列化 |
| `save_version(comment)` | comment: str 版本注释 | 无 | 保存当前版本 |
| `restore_version(version_index)` | version_index: int 版本索引 | bool | 恢复到指定版本 |
| `get_version_history()` | 无 | list | 获取版本历史 |

**示例**：
```python
class MyNode(Node):
    tag = "自定义节点"
    color = "#FF5733"
    title = "我的节点"
    description = "这是一个自定义节点"
    
    def _init_ports(self):
        self.add_input("输入1", PortType.DATA, "number")
        self.add_output("输出1", PortType.DATA, "number")
    
    def _get_config(self):
        return {"value": 100}
    
    def execute(self):
        input_port = self.get_input_by_name("输入1")
        value = input_port.get_data() or 0
        output_port = self.get_output_by_name("输出1")
        output_port.set_data(value * 2)
```

### 1.2 Port 类

**描述**：端口类，用于节点之间的数据传递。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `__init__(name, port_type, direction, data_type)` | name: str 端口名称<br>port_type: PortType 端口类型<br>direction: PortDirection 端口方向<br>data_type: str 数据类型 | 无 | 初始化端口 |
| `connect(connection)` | connection: Connection 连接对象 | 无 | 连接到另一个端口 |
| `disconnect(connection)` | connection: Connection 连接对象 | 无 | 断开连接 |
| `get_connected_ports()` | 无 | list[Port] | 获取已连接的端口 |
| `set_data(data)` | data: Any 数据值 | 无 | 设置数据 |
| `get_data()` | 无 | Any | 获取数据 |

### 1.3 Connection 类

**描述**：连接线类，用于连接两个端口。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `__init__(output_port, input_port)` | output_port: Port 输出端口<br>input_port: Port 输入端口 | 无 | 初始化连接 |
| `get_start_point()` | 无 | tuple(float, float) | 获取起点坐标 |
| `get_end_point()` | 无 | tuple(float, float) | 获取终点坐标 |
| `delete()` | 无 | 无 | 删除连接 |
| `to_dict()` | 无 | dict | 序列化为字典 |

### 1.4 NodeRegistry 类

**描述**：节点注册表，用于管理所有节点类型。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `register(node_class)` | node_class: Type[Node] 节点类 | Type[Node] | 注册节点类 |
| `get(name)` | name: str 节点名称 | Type[Node] | 获取节点类 |
| `create(name, x, y)` | name: str 节点名称<br>x: float 横坐标<br>y: float 纵坐标 | Node | 创建节点实例 |
| `get_all_nodes()` | 无 | dict[str, Type[Node]] | 获取所有节点类 |
| `get_tags()` | 无 | list[str] | 获取所有标签 |
| `get_nodes_by_tag(tag)` | tag: str 标签名称 | list[str] | 根据标签获取节点名称 |
| `get_node_tags()` | 无 | dict[str, str] | 获取所有节点的标签映射 |
| `get_node_title(name)` | name: str 节点名称 | str | 获取节点的中文标题 |
| `get_node_description(name)` | name: str 节点名称 | str | 获取节点的描述 |
| `load_from_script(script_path)` | script_path: str 脚本路径 | bool | 从 Python 脚本加载自定义节点类型 |

**示例**：
```python
# 注册节点
@register_node("自定义节点", "#FF5733", "我的节点", "这是一个自定义节点")
class MyNode(Node):
    def _init_ports(self):
        self.add_input("输入", PortType.DATA, "number")
        self.add_output("输出", PortType.DATA, "number")

# 创建节点实例
node = NodeRegistry.create("MyNode", x=100, y=100)
```

### 1.5 NodeEditor 类

**描述**：节点编辑器主窗口。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `__init__(mod_loader)` | mod_loader: ModLoader 模组加载器 | 无 | 初始化编辑器 |
| `init_ui()` | 无 | 无 | 初始化用户界面 |
| `create_actions()` | 无 | 无 | 创建动作 |
| `create_menus()` | 无 | 无 | 创建菜单 |
| `create_toolbar()` | 无 | 无 | 创建工具栏 |
| `new_project()` | 无 | 无 | 新建项目 |
| `open_project()` | 无 | 无 | 打开项目 |
| `save_project()` | 无 | 无 | 保存项目 |
| `load_project(filename)` | filename: str 项目文件路径 | 无 | 加载项目 |
| `generate_code()` | 无 | 无 | 生成代码 |
| `auto_generate_code()` | 无 | 无 | 自动生成代码 |
| `handle_port_click(port_item)` | port_item: PortGraphicsItem 端口图形项 | 无 | 处理端口点击 |
| `create_connection(output_port, input_port)` | output_port: PortGraphicsItem 输出端口<br>input_port: PortGraphicsItem 输入端口 | 无 | 创建连接 |
| `edit_node_properties(node)` | node: Node 节点对象 | 无 | 编辑节点属性 |
| `copy_nodes()` | 无 | 无 | 复制选中节点 |
| `paste_nodes()` | 无 | 无 | 粘贴节点 |
| `toggle_theme()` | 无 | 无 | 切换主题 |
| `show_scratch_preview()` | 无 | 无 | 显示 Scratch 预览 |
| `load_python_script()` | 无 | 无 | 加载 Python 脚本 |
| `undo()` | 无 | 无 | 撤销操作 |
| `redo()` | 无 | 无 | 重做操作 |
| `save_state()` | 无 | dict | 保存当前状态 |
| `restore_state(state)` | state: dict 状态数据 | 无 | 恢复状态 |
| `record_operation()` | 无 | 无 | 记录操作到撤销栈 |

## 2. 枚举类型

### 2.1 PortType

**描述**：端口类型枚举。

**值**：
- `DATA` - 数据端口
- `EXEC` - 执行端口

### 2.2 PortDirection

**描述**：端口方向枚举。

**值**：
- `INPUT` - 输入端口
- `OUTPUT` - 输出端口

## 3. 装饰器

### 3.1 register_node

**描述**：节点注册装饰器，用于注册节点类。

**参数**：
- `tag` - 分类标签（中文），用于在左侧面板中对节点进行分组
- `color` - 节点背景颜色，使用十六进制颜色码（如 #FF69B4）
- `title` - 中文显示名称，节点左上角显示的文字
- `description` - 节点提示信息，鼠标悬停时显示的详细说明

**示例**：
```python
@register_node("状态定义", "#FF69B4", "状态定义", "定义一个状态节点，用于组织状态机逻辑")
class StateDefineNode(Node):
    def _init_ports(self):
        self.add_output("states", PortType.DATA, "list")
    
    def _get_config(self):
        return {'state_names': []}
```

## 4. 模组系统

### 4.1 ModLoader 类

**描述**：模组加载器，用于加载外部模组。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `__init__(mods_dir)` | mods_dir: str 模组目录路径 | 无 | 初始化模组加载器 |
| `load_all_mods()` | 无 | 无 | 加载所有模组 |
| `get_loaded_mods_info()` | 无 | str | 获取已加载模组信息 |

## 5. 代码生成

### 5.1 LuaCodeGenerator 类

**描述**：Lua 代码生成器，用于将节点图转换为 Lua 代码。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `generate(nodes, connections)` | nodes: list[Node] 节点列表<br>connections: list[Connection] 连接列表 | str | 生成 Lua 代码 |

## 6. 反向解析

### 6.1 ReverseParser 类

**描述**：反向解析器，用于将 Lua 代码转换为节点图。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `parse(code)` | code: str Lua 代码 | tuple(list[Node], list[tuple]) | 解析代码并生成节点和连接 |

## 7. 图形界面组件

### 7.1 NodeGraphicsItem

**描述**：节点图形项，用于在场景中显示节点。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `__init__(node, editor)` | node: Node 节点对象<br>editor: NodeEditor 编辑器对象 | 无 | 初始化节点图形项 |
| `boundingRect()` | 无 | QRectF | 获取边界矩形 |
| `paint(painter, option, widget)` | painter: QPainter 画家<br>option: QStyleOptionGraphicsItem 样式选项<br>widget: QWidget 部件 | 无 | 绘制节点 |
| `_draw_ports(painter)` | painter: QPainter 画家 | 无 | 绘制端口 |
| `mousePressEvent(event)` | event: QGraphicsSceneMouseEvent 鼠标事件 | 无 | 处理鼠标按下事件 |
| `mouseMoveEvent(event)` | event: QGraphicsSceneMouseEvent 鼠标事件 | 无 | 处理鼠标移动事件 |
| `mouseDoubleClickEvent(event)` | event: QGraphicsSceneMouseEvent 鼠标事件 | 无 | 处理鼠标双击事件 |
| `hoverEnterEvent(event)` | event: QGraphicsSceneHoverEvent 悬停事件 | 无 | 处理鼠标进入事件 |
| `hoverLeaveEvent(event)` | event: QGraphicsSceneHoverEvent 悬停事件 | 无 | 处理鼠标离开事件 |

### 7.2 ConnectionGraphicsItem

**描述**：连接线图形项，用于在场景中显示连接线。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `__init__(connection, node_scene)` | connection: Connection 连接对象<br>node_scene: NodeScene 节点场景 | 无 | 初始化连接线图形项 |
| `boundingRect()` | 无 | QRectF | 获取边界矩形 |
| `paint(painter, option, widget)` | painter: QPainter 画家<br>option: QStyleOptionGraphicsItem 样式选项<br>widget: QWidget 部件 | 无 | 绘制连接线 |
| `hoverEnterEvent(event)` | event: QGraphicsSceneHoverEvent 悬停事件 | 无 | 处理鼠标进入事件 |
| `hoverLeaveEvent(event)` | event: QGraphicsSceneHoverEvent 悬停事件 | 无 | 处理鼠标离开事件 |
| `mouseDoubleClickEvent(event)` | event: QGraphicsSceneMouseEvent 鼠标事件 | 无 | 处理鼠标双击事件 |
| `contextMenuEvent(event)` | event: QGraphicsSceneContextMenuEvent 上下文菜单事件 | 无 | 处理上下文菜单事件 |

### 7.3 NodeGraphicsView

**描述**：节点图形视图，用于显示节点场景。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `__init__(scene)` | scene: NodeScene 节点场景 | 无 | 初始化节点图形视图 |
| `mousePressEvent(event)` | event: QMouseEvent 鼠标事件 | 无 | 处理鼠标按下事件 |
| `mouseMoveEvent(event)` | event: QMouseEvent 鼠标事件 | 无 | 处理鼠标移动事件 |
| `mouseReleaseEvent(event)` | event: QMouseEvent 鼠标事件 | 无 | 处理鼠标释放事件 |
| `wheelEvent(event)` | event: QWheelEvent 滚轮事件 | 无 | 处理滚轮事件 |
| `keyPressEvent(event)` | event: QKeyEvent 键盘事件 | 无 | 处理键盘事件 |

### 7.4 NodeScene

**描述**：节点场景，用于管理节点和连接。

**主要方法**：

| 方法名 | 参数 | 返回值 | 描述 |
|-------|------|-------|------|
| `__init__(editor)` | editor: NodeEditor 编辑器对象 | 无 | 初始化节点场景 |
| `drawBackground(painter, rect)` | painter: QPainter 画家<br>rect: QRectF 矩形 | 无 | 绘制背景 |
| `dragEnterEvent(event)` | event: QGraphicsSceneDragDropEvent 拖拽事件 | 无 | 处理拖拽进入事件 |
| `dragMoveEvent(event)` | event: QGraphicsSceneDragDropEvent 拖拽事件 | 无 | 处理拖拽移动事件 |
| `dragLeaveEvent(event)` | event: QGraphicsSceneDragDropEvent 拖拽事件 | 无 | 处理拖拽离开事件 |
| `dropEvent(event)` | event: QGraphicsSceneDragDropEvent 拖拽事件 | 无 | 处理拖拽放下事件 |
| `add_node(node)` | node: Node 节点对象 | NodeGraphicsItem | 添加节点到场景 |
| `add_connection(connection)` | connection: Connection 连接对象 | ConnectionGraphicsItem | 添加连接到场景 |
| `remove_node(node)` | node: Node 节点对象 | 无 | 删除节点及其所有关联项 |
| `remove_connection(connection)` | connection: Connection 连接对象 | 无 | 删除连接 |
| `clear()` | 无 | 无 | 清空场景 |
| `mouseMoveEvent(event)` | event: QGraphicsSceneMouseEvent 鼠标事件 | 无 | 处理鼠标移动事件 |
| `keyPressEvent(event)` | event: QKeyEvent 键盘事件 | 无 | 处理键盘事件 |

## 8. 工具函数

### 8.1 get_exe_dir

**描述**：获取可执行文件所在目录（兼容开发和打包）。

**返回值**：str - 可执行文件所在目录路径。

**示例**：
```python
from pyqt6_editor.main import get_exe_dir

exec_dir = get_exe_dir()
print(f"可执行文件目录: {exec_dir}")
```

## 9. 示例代码

### 9.1 创建自定义节点

```python
from pyqt6_editor.node import Node, PortType
from pyqt6_editor.registry import register_node

@register_node("自定义节点", "#FF5733", "我的计算节点", "这是一个简单的计算节点")
class MyMathNode(Node):
    def _init_ports(self):
        self.add_input("操作数1", PortType.DATA, "number")
        self.add_input("操作数2", PortType.DATA, "number")
        self.add_output("结果", PortType.DATA, "number")
    
    def _get_config(self):
        return {"operation": "add"}  # add, subtract, multiply, divide
    
    def execute(self):
        op1 = self.get_input_by_name("操作数1").get_data() or 0
        op2 = self.get_input_by_name("操作数2").get_data() or 0
        operation = self._get_config().get("operation", "add")
        
        if operation == "add":
            result = op1 + op2
        elif operation == "subtract":
            result = op1 - op2
        elif operation == "multiply":
            result = op1 * op2
        elif operation == "divide":
            result = op1 / op2 if op2 != 0 else 0
        else:
            result = 0
        
        self.get_output_by_name("结果").set_data(result)
```

### 9.2 加载自定义节点脚本

```python
# custom_nodes.py
from pyqt6_editor.node import Node, PortType
from pyqt6_editor.registry import register_node

@register_node("自定义节点", "#4CAF50", "计数器节点", "一个简单的计数器节点")
class CounterNode(Node):
    def _init_ports(self):
        self.add_input("重置", PortType.EXEC, "exec")
        self.add_input("增加", PortType.EXEC, "exec")
        self.add_output("值", PortType.DATA, "number")
    
    def _get_config(self):
        return {"count": 0}
    
    def execute(self):
        config = self._get_config()
        # 这里可以根据输入端口的触发情况来执行不同的逻辑
        # 简化示例，直接返回当前值
        self.get_output_by_name("值").set_data(config.get("count", 0))
```

然后在编辑器中通过 "工具" -> "加载 Python 脚本" 菜单加载此脚本。

## 10. 常见问题与解决方案

### 10.1 节点不显示在面板中

**原因**：
- 节点类没有使用 `@register_node` 装饰器
- 装饰器参数不正确
- 脚本没有被正确加载

**解决方案**：
- 确保使用 `@register_node` 装饰器
- 检查装饰器参数是否正确
- 检查脚本是否有语法错误

### 10.2 连接无法创建

**原因**：
- 端口类型不匹配（EXEC 端口只能连接到 EXEC 端口）
- 输入端口已经有连接（每个输入端口只能有一个连接）

**解决方案**：
- 确保端口类型匹配
- 先删除现有连接再创建新连接

### 10.3 代码生成失败

**原因**：
- 节点之间的连接不完整
- 节点配置不正确
- 代码生成器无法处理某些节点组合

**解决方案**：
- 确保所有必要的连接都已创建
- 检查节点配置是否正确
- 简化节点图结构

### 10.4 模组加载失败

**原因**：
- 模组文件格式不正确
- 模组依赖缺失
- 模组代码有语法错误

**解决方案**：
- 检查模组文件格式
- 确保所有依赖都已安装
- 检查模组代码是否有语法错误

## 11. 性能优化建议

1. **减少节点数量**：节点数量过多会影响性能，尽量使用组合节点减少节点总数。

2. **合理使用连接**：过多的连接会增加渲染和计算负担，尽量减少不必要的连接。

3. **使用批处理**：对于重复的操作，使用批处理节点代替多个单独节点。

4. **优化自定义节点**：在自定义节点的 `execute` 方法中避免复杂计算，尽量使用简单的逻辑。

5. **使用缓存**：对于计算密集型操作，考虑使用缓存机制避免重复计算。

6. **减少重绘**：避免频繁的场景重绘，只在必要时调用 `update()` 方法。

7. **使用适当的节点类型**：根据实际需求选择合适的节点类型，避免使用过于复杂的节点。

8. **定期保存**：定期保存项目，避免意外丢失数据。

## 12. 版本历史

| 版本 | 日期 | 描述 |
|------|------|------|
| 0.1.0 | 2026-04-18 | 初始版本，包含基本功能 |
| 0.1.1 | 2026-04-20 | 添加撤销/重做功能 |
| 0.1.2 | 2026-04-22 | 添加节点版本控制 |
| 0.1.3 | 2026-04-24 | 添加 Python 脚本接口 |
| 0.1.4 | 2026-04-26 | 优化性能和用户体验 |

## 13. 联系方式

如果您有任何问题或建议，请通过以下方式联系我们：

- 邮箱：xiaoou6630@example.com
- GitHub：https://github.com/xiaoou6630/tacz-node-editor
- 论坛：https://forum.example.com/tacz-node-editor

---

**© 2026 TACZ Lua Map 编辑器团队. 保留所有权利。**