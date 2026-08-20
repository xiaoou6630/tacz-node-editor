"""
TACZ Lua 状态机节点库
使用装饰器注册节点，并按 tag 分类
支持中文名称和 tooltip

【节点系统说明】
节点是状态机的基本构建单元，每个节点代表一个操作或条件。
节点通过输入/输出端口连接，形成完整的状态机逻辑。

【端口类型】
- EXEC（执行端口）：用于控制流程的执行顺序，粉色圆点表示
- DATA（数据端口）：用于传递数据值，灰色圆点表示

【节点分类】
- 状态定义：定义状态机的基本结构和状态转换
- 输入事件：响应玩家的各种输入操作
- 动画控制：控制武器模型的动画播放
- 条件检查：根据条件产生分支流程
- 动作操作：执行特定的游戏内动作
- 轨道系统：定义和管理动画轨道
- 逻辑控制：基本的逻辑运算节点
- 动画模式：定义动画的播放模式常量
- 数学运算：基本的数学计算
"""

from pyqt6_editor.node import Node, Port, PortType
from pyqt6_editor.registry import NodeRegistry


def register_node(tag: str, color: str, title: str = None, description: str = None):
    """
    节点注册装饰器

    参数:
        tag: 分类标签（中文），用于在左侧面板中对节点进行分组
        color: 节点背景颜色，使用十六进制颜色码（如 #FF69B4）
        title: 中文显示名称，节点左上角显示的文字
        description: 节点提示信息，鼠标悬停时显示的详细说明
    """
    def decorator(cls):
        cls.tag = tag
        cls.color = color
        cls.title = title or cls.__name__
        cls.description = description or cls.__doc__ or ""
        return NodeRegistry.register(cls)
    return decorator


# ==================== 状态定义节点 ====================
# 状态定义节点用于构建状态机的骨架，包括：
# - 定义状态节点（状态表）
# - 进入状态节点（entry）- 状态开始时执行一次
# - 更新状态节点（update）- 每帧执行
# - 退出状态节点（exit）- 状态结束时执行一次
# - 状态转换节点（transition）- 定义状态间的转换逻辑

@register_node("状态定义", "#FF69B4", "状态定义", "定义一个状态节点，用于组织状态机逻辑\n\n【用途】\n作为状态机中每个状态的容器节点，用于分组该状态下的所有行为\n\n【配置参数】\n- state_names: 状态名称列表\n\n【示例】\n创建名为 'idle' 的状态节点")
class StateDefineNode(Node):
    """定义状态节点 - 作为状态机中每个状态的容器"""

    def _init_ports(self):
        self.add_output("states", PortType.DATA, "list")

    def _get_default_config(self):
        return {'state_names': []}


@register_node("状态定义", "#FF69B4", "进入状态", "状态进入时执行，用于初始化\n\n【用途】\n当状态机进入某个状态时，entry 方法会被调用一次\n常用于初始化变量、播放起始动画等一次性操作\n\n【配置参数】\n- state_name: 所属状态名称（如 'idle', 'reload'）\n\n【示例】\n进入 idle 状态时播放 idle 动画")
class EntryNode(Node):
    """进入状态节点 - 状态开始时执行一次的初始化操作"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'state_name': 'idle'}


@register_node("状态定义", "#FF69B4", "更新状态", "每帧更新时执行，用于检查条件\n\n【用途】\n状态机的 update 方法每帧都会被调用\n常用于检测游戏条件、更新动画状态等持续性操作\n\n【配置参数】\n- state_name: 所属状态名称\n- condition: 附加条件表达式（可选）\n\n【示例】\n在 idle 状态的 update 中检测是否需要换弹")
class UpdateNode(Node):
    """更新状态节点 - 每帧执行的持续性检查和更新"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'state_name': 'idle', 'condition': ''}


@register_node("状态定义", "#FF69B4", "退出状态", "状态退出时执行，用于清理\n\n【用途】\n当状态机离开某个状态时，exit 方法会被调用\n常用于停止动画、清理临时数据等收尾工作\n\n【配置参数】\n- state_name: 所属状态名称\n\n【示例】\n退出 inspect 状态时恢复准星显示")
class ExitNode(Node):
    """退出状态节点 - 状态结束时执行一次的清理操作"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'state_name': 'idle'}


@register_node("状态定义", "#FF69B4", "状态转换", "定义状态转换条件和目标状态\n\n【用途】\ntransition 方法根据接收到的输入信号和条件判断是否转换到其他状态\n这是状态机核心逻辑所在\n\n【配置参数】\n- from_state: 源状态名称\n- to_state: 目标状态名称\n- condition: 转换条件表达式\n\n【示例】\n当 input == INPUT_RELOAD 时，从 idle 转换到 reload 状态")
class TransitionNode(Node):
    """状态转换节点 - 定义状态间的转换逻辑"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_input("条件", PortType.DATA, "bool")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'from_state': 'idle', 'to_state': 'idle', 'condition': ''}


# ==================== 输入事件节点 ====================
# 输入事件节点代表玩家在游戏中产生的各种操作输入
# 这些节点只有输出端口，连接到对应的状态转换逻辑

@register_node("输入事件", "#87CEEB", "掏枪", "INPUT_DRAW - 玩家掏出武器时触发\n\n【用途】\n当玩家从物品栏切换到武器时触发\n通常连接到状态机的起始状态转换")
class DrawNode(Node):
    """掏枪输入节点 - 玩家切换到武器时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "射击", "INPUT_SHOOT - 玩家按下开火键时触发\n\n【用途】\n当玩家按住或按下开火键时触发\n可进一步区分解除开枪和按住开枪")
class ShootNode(Node):
    """射击输入节点 - 玩家开火时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "换弹", "INPUT_RELOAD - 玩家按下换弹键时触发\n\n【用途】\n当玩家按下 R 键（默认）换弹时触发\n可结合弹药检查节点判断换弹类型")
class ReloadNode(Node):
    """换弹输入节点 - 玩家请求换弹时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "检视", "INPUT_INSPECT - 玩家按下检视键时触发\n\n【用途】\n当玩家按下检视键时触发\n通常需要隐藏准星、播放检视动画")
class InspectNode(Node):
    """检视输入节点 - 玩家请求检视武器时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "拉栓", "INPUT_BOLT - 玩家拉动枪栓时触发\n\n【用途】\n主要用于栓动步枪，拉栓动作完成后触发")
class BoltNode(Node):
    """拉栓输入节点 - 玩家拉动枪栓时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "瞄准", "INPUT_AIM - 玩家按下瞄准键时触发\n\n【用途】\n当玩家按住右键（默认）进入瞄准状态时触发\n可用于切换到瞄准动画")
class AimNode(Node):
    """瞄准输入节点 - 玩家进入瞄准状态时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "奔跑", "INPUT_RUN - 玩家按住奔跑键时触发\n\n【用途】\n当玩家按住 Shift 键（默认）奔跑时触发")
class RunNode(Node):
    """奔跑输入节点 - 玩家开始奔跑时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "行走", "INPUT_WALK - 玩家移动时触发\n\n【用途】\n检测玩家的移动方向和状态")
class WalkNode(Node):
    """行走输入节点 - 玩家移动时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


# ==================== 动画控制节点 ====================
# 动画控制节点用于控制武器模型的动画播放
# TACZ 使用轨道系统管理多个动画的同时播放

@register_node("动画控制", "#32CD32", "播放动画", "播放指定的动画片段\n\n【用途】\n在指定轨道上播放一个动画片段\n支持多种播放模式和混合过渡\n\n【配置参数】\n- animation_name: 动画名称（如 'reload_empty'）\n- track: 轨道名称（MAIN_TRACK, MOVEMENT_TRACK 等）\n- blend: 是否混合过渡\n- mode: 播放模式（PLAY_ONCE_STOP, PLAY_ONCE_HOLD, LOOP）\n- blend_time: 过渡时间（秒）\n\n【示例】\n在主轨道播放换弹动画，过渡时间 0.2 秒")
class RunAnimationNode(Node):
    """播放动画节点 - 在指定轨道上播放动画"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'animation_name': 'idle', 'track': 'MAIN_TRACK', 'blend': False, 'mode': 'PLAY_ONCE_STOP', 'blend_time': 0.2}


@register_node("动画控制", "#32CD32", "停止动画", "停止指定轨道上的动画\n\n【用途】\n立即停止指定轨道上正在播放的动画\n常用于打断正在播放的动画以切换到其他动画\n\n【配置参数】\n- track: 轨道名称\n\n【示例】\n停止主轨道动画以便播放下一个动作")
class StopAnimationNode(Node):
    """停止动画节点 - 停止指定轨道上的动画"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'track': 'MAIN_TRACK'}


@register_node("动画控制", "#32CD32", "循环动画", "循环播放动画直到被停止\n\n【用途】\n在指定轨道上循环播放动画\n常用于 idle、奔跑等持续性动画\n\n【配置参数】\n- animation_name: 动画名称\n- track: 轨道名称\n\n【示例】\n在混合轨道循环播放 idle 动画")
class LoopAnimationNode(Node):
    """循环动画节点 - 循环播放动画"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'animation_name': 'idle', 'track': 'MOVEMENT_TRACK'}


@register_node("动画控制", "#32CD32", "设置进度", "设置动画播放进度\n\n【用途】\n直接设置指定轨道的动画播放进度（0.0 到 1.0）\n常用于同步动画进度或快进到特定帧\n\n【配置参数】\n- track: 轨道名称\n- progress: 进度值（0.0-1.0）\n- is_hold: 是否保持在当前进度\n\n【示例】\n设置动画进度为最后一帧 (1.0)")
class SetProgressNode(Node):
    """设置进度节点 - 设置动画播放进度"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'track': 'MAIN_TRACK', 'progress': 1.0, 'is_hold': True}


# ==================== 条件检查节点 ====================
# 条件检查节点用于根据游戏状态产生分支流程
# 每个条件节点有"是"和"否"两个输出端口

@register_node("条件检查", "#BA55D3", "有弹药", "检查弹匣中是否有弹药\n\n【用途】\n同时检查枪管和弹匣是否有弹药\n返回是表示有弹药可用，返回否表示需要换弹\n\n【输出端口】\n- 是: 有弹药时执行\n- 否: 无弹药时执行\n\n【示例】\n连接有弹药分支到射击，连接无弹药分支到换弹")
class CheckAmmoNode(Node):
    """检查弹药节点 - 判断是否有可用弹药"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("是", PortType.EXEC, "exec")
        self.add_output("否", PortType.EXEC, "exec")


@register_node("条件检查", "#BA55D3", "弹药数量", "比较弹匣中的弹药数量\n\n【用途】\n比较当前弹药数量与设定值\n支持多种比较运算符\n\n【配置参数】\n- operator: 比较运算符（<, <=, >, >=, ==, ~=）\n- value: 比较值\n\n【输出端口】\n- 是: 条件满足时执行\n- 否: 条件不满足时执行")
class CheckAmmoCountNode(Node):
    """弹药数量检查节点 - 比较弹药数量"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("是", PortType.EXEC, "exec")
        self.add_output("否", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'operator': '<=', 'value': 0}


@register_node("条件检查", "#BA55D3", "过热检查", "检查武器是否过热\n\n【用途】\n对于可过热武器，检查当前热度状态\n返回是表示过热中，返回否表示正常\n\n【输出端口】\n- 是: 过热时执行\n- 否: 正常时执行")
class CheckHeatNode(Node):
    """过热检查节点 - 检查武器热度状态"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("是", PortType.EXEC, "exec")
        self.add_output("否", PortType.EXEC, "exec")


@register_node("条件检查", "#BA55D3", "瞄准进度", "检查瞄准进度是否达到阈值\n\n【用途】\n检测玩家的瞄准进度（0.0 到 1.0）\n用于判断瞄准是否完成\n\n【配置参数】\n- progress: 进度阈值（0.0-1.0）\n\n【输出端口】\n- 是: 进度达到阈值时执行\n- 否: 进度未达阈值时执行")
class CheckAimingNode(Node):
    """瞄准进度检查节点 - 检查瞄准是否完成"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("是", PortType.EXEC, "exec")
        self.add_output("否", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'progress': 0.5}


@register_node("条件检查", "#BA55D3", "在地面上", "检查玩家是否站在地面上\n\n【用途】\n判断玩家是否与地面接触\n用于区分跳跃和行走状态\n\n【输出端口】\n- 是: 在地面上时执行\n- 否: 在空中时执行")
class CheckGroundNode(Node):
    """地面检查节点 - 检查玩家是否在地面上"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("是", PortType.EXEC, "exec")
        self.add_output("否", PortType.EXEC, "exec")


@register_node("条件检查", "#BA55D3", "动画停止", "检查指定轨道的动画是否已停止\n\n【用途】\n用于等待动画播放完成后再进行下一步操作\n\n【配置参数】\n- track: 轨道名称\n\n【输出端口】\n- 是: 动画已停止时执行\n- 否: 动画仍在播放时执行")
class CheckStoppedNode(Node):
    """动画停止检查节点 - 检查动画是否播放完成"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("是", PortType.EXEC, "exec")
        self.add_output("否", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'track': 'MAIN_TRACK'}


@register_node("条件检查", "#BA55D3", "射击冷却", "检查射击冷却时间\n\n【用途】\n检测距离上次射击已经过去的时间\n用于控制射击频率\n\n【配置参数】\n- operator: 比较运算符\n- value: 冷却时间阈值（秒）\n\n【输出端口】\n- 是: 冷却完成时执行\n- 否: 冷却中时执行")
class CheckShootCooldownNode(Node):
    """射击冷却检查节点 - 检查射击间隔"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("是", PortType.EXEC, "exec")
        self.add_output("否", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'operator': '>', 'value': 0}


# ==================== 动作操作节点 ====================
# 动作操作节点用于执行特定的游戏内动作

@register_node("动作操作", "#FF8C00", "抛壳", "从指定位置抛出弹壳\n\n【用途】\n在射击时从指定位置抛出弹壳动画\n增强射击的真实感\n\n【配置参数】\n- index: 弹壳位置索引\n\n【示例】\n从 0 号位置抛壳")
class PopShellNode(Node):
    """抛壳动作节点 - 播放抛壳动画"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'index': 0}


@register_node("动作操作", "#FF8C00", "触发事件", "触发一个状态机内部事件\n\n【用途】\n用于在状态内部触发特定事件\n通常与其他条件检查配合使用\n\n【配置参数】\n- event_name: 事件名称\n\n【示例】\n触发 INPUT_RELOAD 事件")
class TriggerNode(Node):
    """触发事件节点 - 触发内部事件"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'event_name': 'INPUT_RELOAD'}


@register_node("动作操作", "#9C27B0", "自定义代码", "执行自定义 Lua 代码\n\n【用途】\n当内置节点无法满足需求时，可编写任意 Lua 代码\n\n【示例】\nlocal entity = this:getEntity()\nif entity ~= nil then\n    entity:heal(5.0)\nend")
class CustomLuaNode(Node):
    """自定义代码节点 - 执行任意 Lua 代码"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'code': '-- 在此编写自定义 Lua 代码\n-- 例如：this:getEntity():heal(5.0)'}


@register_node("动作操作", "#FF8C00", "隐藏准星", "显示或隐藏屏幕中央准星\n\n【用途】\n在检视等需要专注观察的动作中隐藏准星\n\n【配置参数】\n- hide: 是否隐藏（true/false）\n\n【示例】\n检视时隐藏准星，检视结束后恢复")
class HideCrosshairNode(Node):
    """隐藏准星节点 - 控制准星显示"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'hide': True}


@register_node("动作操作", "#FF8C00", "锁定行走", "锁定武器的行走距离锚点\n\n【用途】\n确保行走动画的起点一致\n避免每次行走开始时动画跳变")
class AnchorWalkDistNode(Node):
    """锁定行走距离节点 - 锁定行走动画起点"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")


# ==================== 轨道系统节点 ====================
# 轨道系统节点用于定义动画轨道常量
# 轨道用于在同时播放多个动画时进行区分

@register_node("轨道系统", "#4A90E2", "轨道行", "定义轨道行常量\n\n【用途】\n轨道行是一组相关轨道的容器\n- STATIC: 主轨道行，用于基础动作\n- GUN_KICK: 射击轨道行，用于枪械后坐力动画\n- BLENDING: 混合轨道行，用于可叠加的动作\n\n【输出端口】\n- STATIC: 静态轨道行\n- GUN_KICK: 枪械后坐力轨道行\n- BLENDING: 混合轨道行")
class TrackLineNode(Node):
    """轨道行定义节点 - 定义轨道行常量"""

    def _init_ports(self):
        self.add_output("STATIC", PortType.DATA, "object")
        self.add_output("GUN_KICK", PortType.DATA, "object")
        self.add_output("BLENDING", PortType.DATA, "object")


@register_node("轨道系统", "#4A90E2", "轨道", "定义单个轨道常量\n\n【用途】\n轨道是实际承载动画播放的通道\n同一轨道行可以有多个轨道同时播放不同动画\n\n【轨道说明】\n- BASE: 基础轨道，播放武器静止动画\n- BOLT_CAUGHT: 空挂轨道\n- ADS: 瞄准轨道\n- MAIN: 主轨道，用于主要动作\n- SPRINT: 冲刺轨道\n- MOVEMENT: 移动轨道，用于行走奔跑")
class TrackNode(Node):
    """轨道定义节点 - 定义轨道常量"""

    def _init_ports(self):
        self.add_output("BASE", PortType.DATA, "object")
        self.add_output("BOLT_CAUGHT", PortType.DATA, "object")
        self.add_output("ADS", PortType.DATA, "object")
        self.add_output("MAIN", PortType.DATA, "object")
        self.add_output("SPRINT", PortType.DATA, "object")
        self.add_output("MOVEMENT", PortType.DATA, "object")


@register_node("轨道系统", "#4A90E2", "获取轨道", "获取指定轨道对象\n\n【用途】\n通过轨道行和轨道名称获取完整的轨道对象\n这是实际调用时获取轨道的方式\n\n【配置参数】\n- track_line: 轨道行名称\n- track: 轨道名称\n\n【示例】\n获取主轨道行上的主轨道")
class GetTrackNode(Node):
    """获取轨道节点 - 获取完整的轨道对象"""

    def _init_ports(self):
        self.add_input("", PortType.DATA, "object")
        self.add_output("轨道", PortType.DATA, "object")

    def _get_default_config(self):
        return {'track_line': 'STATIC_TRACK_LINE', 'track': 'MAIN_TRACK'}


# ==================== 逻辑控制节点 ====================
# 逻辑控制节点用于实现基本的程序逻辑

@register_node("逻辑控制", "#FFB347", "条件分支", "根据布尔条件产生分支\n\n【用途】\n根据输入的布尔值选择执行路径\n类似于编程语言中的 if-else\n\n【输入端口】\n- 条件: 布尔值条件\n\n【输出端口】\n- 成立: 条件为 true 时执行\n- 不成立: 条件为 false 时执行")
class IfNode(Node):
    """条件分支节点 - 实现 if-else 逻辑"""

    def _init_ports(self):
        self.add_input("条件", PortType.DATA, "bool")
        self.add_output("成立", PortType.EXEC, "exec")
        self.add_output("不成立", PortType.EXEC, "exec")


@register_node("逻辑控制", "#FFB347", "返回状态", "返回指定的状态\n\n【用途】\n在 transition 方法中返回目标状态\n表示状态机应该转换到该状态\n\n【配置参数】\n- state_name: 目标状态名称")
class ReturnNode(Node):
    """返回状态节点 - 指定转换目标状态"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'state_name': 'idle'}


@register_node("逻辑控制", "#FFB347", "与运算", "逻辑与运算 (A and B)\n\n【用途】\n当两个输入都为 true 时输出 true\n常用于组合多个条件\n\n【输入端口】\n- A: 第一个布尔值\n- B: 第二个布尔值\n\n【输出端口】\n- 结果: A and B")
class AndNode(Node):
    """逻辑与节点 - AND 运算"""

    def _init_ports(self):
        self.add_input("A", PortType.DATA, "bool")
        self.add_input("B", PortType.DATA, "bool")
        self.add_output("结果", PortType.DATA, "bool")


@register_node("逻辑控制", "#FFB347", "或运算", "逻辑或运算 (A or B)\n\n【用途】\n当任意一个输入为 true 时输出 true\n常用于组合可选条件\n\n【输入端口】\n- A: 第一个布尔值\n- B: 第二个布尔值\n\n【输出端口】\n- 结果: A or B")
class OrNode(Node):
    """逻辑或节点 - OR 运算"""

    def _init_ports(self):
        self.add_input("A", PortType.DATA, "bool")
        self.add_input("B", PortType.DATA, "bool")
        self.add_output("结果", PortType.DATA, "bool")


@register_node("逻辑控制", "#FFB347", "非运算", "逻辑非运算 (not A)\n\n【用途】\n反转布尔值的逻辑状态\n\n【输入端口】\n- 输入: 原始布尔值\n\n【输出端口】\n- 结果: not 输入")
class NotNode(Node):
    """逻辑非节点 - NOT 运算"""

    def _init_ports(self):
        self.add_input("输入", PortType.DATA, "bool")
        self.add_output("结果", PortType.DATA, "bool")


@register_node("逻辑控制", "#FFB347", "比较", "比较两个值的大小\n\n【用途】\n对两个输入值进行比较运算\n常用于数值条件判断\n\n【配置参数】\n- operator: 比较运算符（==, ~=, <, >, <=, >=）\n\n【输入端口】\n- A: 第一个值\n- B: 第二个值\n\n【输出端口】\n- 结果: 比较结果的布尔值")
class CompareNode(Node):
    """比较运算节点 - 比较两个值"""

    def _init_ports(self):
        self.add_input("A", PortType.DATA, "any")
        self.add_input("B", PortType.DATA, "any")
        self.add_output("结果", PortType.DATA, "bool")

    def _get_default_config(self):
        return {'operator': '=='}


# ==================== 动画模式节点 ====================
# 动画模式节点用于定义动画播放模式的常量
# 这些常量传递给 runAnimation 的 playType 参数

@register_node("动画模式", "#98FB98", "循环模式", "LOOP - 无限循环播放动画\n\n【用途】\n动画会无限循环播放直到被停止\n适用于 idle、跑步等持续性动画\n\n【示例】\ncontext:runAnimation('idle', track, true, LOOP, 0)")
class LoopModeNode(Node):
    """循环模式常量节点 - LOOP 播放模式"""

    def _init_ports(self):
        self.add_output("模式", PortType.DATA, "string")

    def execute(self):
        self.get_output_by_name("模式").set_data("LOOP")


@register_node("动画模式", "#98FB98", "播放一次停止", "PLAY_ONCE_STOP - 播放一次后停止\n\n【用途】\n动画播放一次后自动停止\n适用于射击、拉栓等一次性动作\n\n【示例】\ncontext:runAnimation('shoot', track, true, PLAY_ONCE_STOP, 0)")
class PlayOnceStopNode(Node):
    """播放一次停止常量节点 - PLAY_ONCE_STOP 模式"""

    def _init_ports(self):
        self.add_output("模式", PortType.DATA, "string")

    def execute(self):
        self.get_output_by_name("模式").set_data("PLAY_ONCE_STOP")


@register_node("动画模式", "#98FB98", "播放一次保持", "PLAY_ONCE_HOLD - 播放一次后保持最后一帧\n\n【用途】\n动画播放一次后停在最后一帧\n常用于需要保持姿态的动作\n\n【示例】\ncontext:runAnimation('aim', track, false, PLAY_ONCE_HOLD, 0.2)")
class PlayOnceHoldNode(Node):
    """播放一次保持常量节点 - PLAY_ONCE_HOLD 模式"""

    def _init_ports(self):
        self.add_output("模式", PortType.DATA, "string")

    def execute(self):
        self.get_output_by_name("模式").set_data("PLAY_ONCE_HOLD")


# ==================== 数学运算节点 ====================
# 数学运算节点用于执行基本的数值计算

@register_node("数学运算", "#DDA0DD", "加法", "加法运算 (A + B)\n\n【用途】\n计算两个数值的和\n\n【输入端口】\n- A: 第一个数值\n- B: 第二个数值\n\n【输出端口】\n- 结果: A + B")
class AddNode(Node):
    """加法运算节点 - 计算 A + B"""

    def _init_ports(self):
        self.add_input("A", PortType.DATA, "number")
        self.add_input("B", PortType.DATA, "number")
        self.add_output("结果", PortType.DATA, "number")

    def execute(self):
        a = self.get_input_by_name("A").get_data() or 0
        b = self.get_input_by_name("B").get_data() or 0
        self.get_output_by_name("结果").set_data(a + b)


@register_node("数学运算", "#DDA0DD", "减法", "减法运算 (A - B)\n\n【用途】\n计算两个数值的差\n\n【输入端口】\n- A: 被减数\n- B: 减数\n\n【输出端口】\n- 结果: A - B")
class SubtractNode(Node):
    """减法运算节点 - 计算 A - B"""

    def _init_ports(self):
        self.add_input("A", PortType.DATA, "number")
        self.add_input("B", PortType.DATA, "number")
        self.add_output("结果", PortType.DATA, "number")

    def execute(self):
        a = self.get_input_by_name("A").get_data() or 0
        b = self.get_input_by_name("B").get_data() or 0
        self.get_output_by_name("结果").set_data(a - b)


@register_node("数学运算", "#DDA0DD", "乘法", "乘法运算 (A * B)\n\n【用途】\n计算两个数值的乘积\n\n【输入端口】\n- A: 第一个数值\n- B: 第二个数值\n\n【输出端口】\n- 结果: A * B")
class MultiplyNode(Node):
    """乘法运算节点 - 计算 A * B"""

    def _init_ports(self):
        self.add_input("A", PortType.DATA, "number")
        self.add_input("B", PortType.DATA, "number")
        self.add_output("结果", PortType.DATA, "number")

    def execute(self):
        a = self.get_input_by_name("A").get_data() or 0
        b = self.get_input_by_name("B").get_data() or 0
        self.get_output_by_name("结果").set_data(a * b)


@register_node("数学运算", "#DDA0DD", "除法", "除法运算 (A / B)\n\n【用途】\n计算两个数值的商\n注意：除数不能为零\n\n【输入端口】\n- A: 被除数\n- B: 除数\n\n【输出端口】\n- 结果: A / B（除数为零时返回零）")
class DivideNode(Node):
    """除法运算节点 - 计算 A / B"""

    def _init_ports(self):
        self.add_input("A", PortType.DATA, "number")
        self.add_input("B", PortType.DATA, "number")
        self.add_output("结果", PortType.DATA, "number")

    def execute(self):
        a = self.get_input_by_name("A").get_data() or 0
        b = self.get_input_by_name("B").get_data() or 1
        self.get_output_by_name("结果").set_data(a / b if b != 0 else 0)


# ==================== 更多输入事件节点 ====================
# 根据官方教程补充的输入事件

@register_node("输入事件", "#87CEEB", "近战配件", "INPUT_BAYONET_MUZZLE - 使用枪口近战配件时触发\n\n【用途】\n当玩家使用刺刀等近战配件攻击时触发\n通常支持多个近战动画循环播放")
class BayonetMuzzleNode(Node):
    """枪口近战输入节点 - 使用近战配件攻击时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "肘击", "INPUT_BAYONET_STOCK - 使用枪托肘击时触发\n\n【用途】\n当玩家使用枪托进行肘击攻击时触发\n播放枪托肘击动画后返回闲置状态\n\n【对应动画】\n- melee_stock: 枪托肘击动画")
class BayonetStockNode(Node):
    """枪托肘击输入节点 - 使用枪托肘击时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "推击", "INPUT_BAYONET_PUSH - 使用推击时触发\n\n【用途】\n当玩家使用推击攻击时触发\n播放推击动画后返回闲置状态\n\n【对应动画】\n- melee_push: 推击动画")
class BayonetPushNode(Node):
    """推击输入节点 - 使用推击攻击时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "丢枪", "INPUT_PUT_AWAY - 玩家收起武器时触发\n\n【用途】\n当玩家切换到其他物品时触发\n播放收起动画后转到最终状态\n\n【对应动画】\n- put_away: 收起武器动画")
class PutAwayNode(Node):
    """丢枪输入节点 - 玩家收起武器时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "闲置", "INPUT_IDLE - 玩家停止移动时触发\n\n【用途】\n当玩家停止所有移动输入时触发\n用于从奔跑/行走状态回到静止状态")
class IdleInputNode(Node):
    """闲置输入节点 - 玩家停止移动时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "快慢机", "INPUT_FIRE_SELECT - 切换快慢机时触发\n\n【用途】\n当玩家切换射击模式（单发/连发/全自动）时触发\n播放快慢机切换动画\n\n【对应动画】\n- fanning_1: 快慢机切换动画")
class FireSelectNode(Node):
    """快慢机输入节点 - 切换射击模式时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "冲刺", "INPUT_SPRINT - 玩家战术冲刺时触发\n\n【用途】\n当玩家进行战术冲刺时触发\n用于切换到冲刺动画状态")
class SprintNode(Node):
    """冲刺输入节点 - 玩家战术冲刺时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "下蹲", "INPUT_SLIDE - 玩家下蹲/滑铲时触发\n\n【用途】\n当玩家下蹲或滑铲时触发\n用于切换到下蹲动画状态")
class SlideNode(Node):
    """下蹲输入节点 - 玩家下蹲/滑铲时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "空挂触发", "INPUT_BOLT_CAUGHT - 进入空仓挂机时触发\n\n【用途】\n当武器子弹打空时触发\n用于切换到空仓挂机状态\n\n【状态转换】\nnormal -> bolt_caught")
class BoltCaughtNode(Node):
    """空挂触发输入节点 - 进入空仓挂机时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "解除空挂", "INPUT_BOLT_NORMAL - 解除空仓挂机时触发\n\n【用途】\n当换弹完成、子弹重新装填时触发\n用于从空挂状态回到正常状态\n\n【状态转换】\nbolt_caught -> normal")
class BoltNormalNode(Node):
    """解除空挂输入节点 - 解除空仓挂机时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "过热", "INPUT_OVER_HEAT - 武器过热时触发\n\n【用途】\n当连续射击导致武器过热时触发\n用于切换到过热状态\n\n【适用武器】\n- 转管机枪等可过热武器")
class OverHeatNode(Node):
    """过热输入节点 - 武器过热时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "冷却", "INPUT_COOLING_HEAT - 武器冷却时触发\n\n【用途】\n当武器温度下降到安全水平时触发\n用于从过热状态回到正常状态")
class CoolingHeatNode(Node):
    """冷却输入节点 - 武器冷却时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "检视退出", "INPUT_INSPECT_RETREAT - 退出检视时触发\n\n【用途】\n当检视动画播放完成或被中断时触发\n用于从检视状态回到闲置状态")
class InspectRetreatNode(Node):
    """检视退出输入节点 - 退出检视时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "瞄准退出", "INPUT_AIM_RETREAT - 退出瞄准时触发\n\n【用途】\n当玩家松开瞄准键时触发\n用于从瞄准状态回到正常状态")
class AimRetreatNode(Node):
    """瞄准退出输入节点 - 退出瞄准时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


@register_node("输入事件", "#87CEEB", "转管", "INPUT_SPIN - 转管武器转轮时触发\n\n【用途】\n当转管武器的转轮启动时触发\n用于播放转轮动画\n\n【适用武器】\n- 转管机枪（如 Minigun）")
class SpinNode(Node):
    """转管输入节点 - 转管武器转轮时触发"""

    def _init_ports(self):
        self.add_output("触发", PortType.EXEC, "exec")


# ==================== 更多动画控制节点 ====================

@register_node("动画控制", "#32CD32", "调整进度", "调整动画播放进度\n\n【用途】\n相对调整当前动画的播放进度（向前或向后）\n常用于修正动画播放位置\n\n【配置参数】\n- track: 轨道名称\n- delta: 调整的偏移量（秒，可为负）\n- is_hold: 是否保持在调整后的进度\n\n【示例】\n将动画进度向前拨动 put_away_time 秒")
class AdjustProgressNode(Node):
    """调整进度节点 - 相对调整动画播放进度"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'track': 'MAIN_TRACK', 'delta': 0.2, 'is_hold': False}


@register_node("动画控制", "#32CD32", "混合动画", "在空闲轨道上播放叠加动画\n\n【用途】\n使用 findIdleTrack 找到空闲轨道播放动画\n适用于射击动画等需要快速连续播放的情况\n\n【配置参数】\n- animation_name: 动画名称\n- track_line: 轨道行名称\n- blend: 是否混合（射击动画通常为 true）\n- mode: 播放模式\n\n【示例】\n在射击轨道行找空闲轨道播放 shoot 动画")
class PlayBlendedAnimationNode(Node):
    """混合动画节点 - 在空闲轨道上播放叠加动画"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'animation_name': 'shoot', 'track_line': 'GUN_KICK_TRACK_LINE', 'blend': True, 'mode': 'PLAY_ONCE_STOP'}


# ==================== 更多动作操作节点 ====================

@register_node("动作操作", "#FF8C00", "播放丢枪动画", "播放收起武器动画\n\n【用途】\n玩家收起武器时播放丢枪/收起动画\n动画会设置到最后一帧然后回退\n\n【配置参数】\n- put_away_time: 收起动画时长\n\n【注意】\n此动画会设置动画进度为最后一帧，然后向前回退指定时间")
class PlayPutAwayNode(Node):
    """播放丢枪动画节点 - 收起武器时播放动画"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'put_away_time': 0.5}


@register_node("动作操作", "#FF8C00", "播放换弹动画", "播放换弹动画（战术换弹/空仓换弹）\n\n【用途】\n根据当前弹药状态播放对应的换弹动画\n通常结合弹药检查节点使用\n\n【配置参数】\n- reload_type: 换弹类型（tactical / empty）")
class PlayReloadNode(Node):
    """播放换弹动画节点 - 根据弹药状态播放对应换弹动画"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'reload_type': 'tactical'}


@register_node("动作操作", "#FF8C00", "播放检视动画", "播放检视动画\n\n【用途】\n播放武器检视动画，展示武器细节\n检视过程中需要隐藏准星\n\n【注意】\n检视完成后需要转到检视态，因为检视时需要隐藏准星")
class PlayInspectNode(Node):
    """播放检视动画节点 - 播放武器检视动画"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")


@register_node("动作操作", "#FF8C00", "循环近战动画", "循环播放多个近战动画\n\n【用途】\n用于枪口近战配件的多连击动画\n通过计数器决定播放第几个动画\n\n【配置参数】\n- animation_prefix: 动画前缀（如 'melee_bayonet_'）\n- counter_name: 计数器名称\n- max_count: 最大动画数量\n\n【示例】\n依次播放 melee_bayonet_1, melee_bayonet_2, melee_bayonet_3")
class CycleMeleeNode(Node):
    """循环近战动画节点 - 多连击近战动画"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'animation_prefix': 'melee_bayonet_', 'counter_name': 'bayonet_counter', 'max_count': 3}


@register_node("动作操作", "#FF8C00", "轨道占位", "在轨道上占位以防止动画叠加\n\n【用途】\n在特定轨道上播放空动画以占位\n防止后续动画被错误叠加")
class TrackHoldNode(Node):
    """轨道占位节点 - 在轨道上占位防止动画叠加"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'track': 'MAIN_TRACK'}


# ==================== 更多轨道系统节点 ====================

@register_node("轨道系统", "#4A90E2", "过热轨道", "定义过热相关轨道\n\n【用途】\n用于可过热武器的过热动画播放\n通常属于混合轨道行\n\n【输出端口】\n- OVER_HEAT: 过热轨道\n- OVER_HEATING: 过热中轨道\n- LOOP: 循环轨道（预留）")
class OverHeatTrackNode(Node):
    """过热轨道定义节点 - 定义过热相关轨道"""

    def _init_ports(self):
        self.add_output("OVER_HEAT", PortType.DATA, "object")
        self.add_output("OVER_HEATING", PortType.DATA, "object")
        self.add_output("LOOP", PortType.DATA, "object")


@register_node("轨道系统", "#4A90E2", "下蹲轨道", "定义下蹲/滑铲轨道\n\n【用途】\n用于下蹲和滑铲动画播放\n属于混合轨道行\n\n【输出端口】\n- SLIDE: 下蹲/滑铲轨道")
class SlideTrackNode(Node):
    """下蹲轨道定义节点 - 定义下蹲/滑铲轨道"""

    def _init_ports(self):
        self.add_output("SLIDE", PortType.DATA, "object")


@register_node("轨道系统", "#4A90E2", "寻找空闲轨道", "在轨道行中寻找空闲的轨道\n\n【用途】\n用于射击动画等需要快速连续播放的场景\n如果没有空闲轨道会自动分配新的\n\n【配置参数】\n- track_line: 轨道行名称\n- is_blending: 是否用于混合动画\n\n【示例】\n在射击轨道行找空闲轨道播放射击动画")
class FindIdleTrackNode(Node):
    """寻找空闲轨道节点 - 在轨道行中找空闲轨道"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("轨道", PortType.DATA, "object")

    def _get_default_config(self):
        return {'track_line': 'GUN_KICK_TRACK_LINE', 'is_blending': False}


# ==================== 更多条件检查节点 ====================

@register_node("条件检查", "#BA55D3", "轨道空闲", "检查指定轨道是否空闲（停止播放）\n\n【用途】\n用于判断轨道是否可以播放新动画\n\n【配置参数】\n- track: 轨道名称\n\n【输出端口】\n- 是: 轨道空闲时执行\n- 否: 轨道正在播放时执行")
class CheckTrackIdleNode(Node):
    """轨道空闲检查节点 - 检查轨道是否停止"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("是", PortType.EXEC, "exec")
        self.add_output("否", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'track': 'MAIN_TRACK'}


@register_node("条件检查", "#BA55D3", "轨道挂起", "检查指定轨道是否处于挂起状态\n\n【用途】\n用于判断动画是否播放完成并挂起\n\n【配置参数】\n- track: 轨道名称\n\n【输出端口】\n- 是: 轨道挂起时执行\n- 否: 轨道未挂起时执行")
class CheckTrackHoldingNode(Node):
    """轨道挂起检查节点 - 检查轨道是否挂起"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("是", PortType.EXEC, "exec")
        self.add_output("否", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'track': 'MOVEMENT_TRACK'}


@register_node("条件检查", "#BA55D3", "行走方向", "检查玩家的行走方向\n\n【用途】\n检测玩家移动方向（前进、后退、侧移）\n用于播放对应的行走动画\n\n【配置参数】\n- direction: 目标方向（forward, backward, strafe）\n\n【输出端口】\n- 是: 方向匹配时执行\n- 否: 方向不匹配时执行")
class CheckWalkDirectionNode(Node):
    """行走方向检查节点 - 检查玩家移动方向"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("是", PortType.EXEC, "exec")
        self.add_output("否", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'direction': 'forward'}


@register_node("条件检查", "#BA55D3", "是否奔跑", "检查玩家是否在奔跑\n\n【用途】\n检测玩家当前是否在奔跑状态\n用于区分行走和奔跑动画\n\n【输出端口】\n- 是: 在奔跑时执行\n- 否: 未奔跑时执行")
class CheckRunningNode(Node):
    """奔跑检查节点 - 检查玩家是否奔跑"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("是", PortType.EXEC, "exec")
        self.add_output("否", PortType.EXEC, "exec")

