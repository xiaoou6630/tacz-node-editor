"""
Lua 代码生成器 - TACZ 枪械状态机专用
根据节点图生成符合 TACZ 格式的 Lua 状态机脚本
"""

from typing import List, Dict, Set
from .node import Node, PortType
from .connection import Connection


class LuaCodeGenerator:
    """Lua 代码生成器 - 生成 TACZ 兼容的状态机代码"""

    def __init__(self):
        self.code_lines = []
        self.indent_level = 0
        self.states: Set[str] = set()
        self.node_map: Dict[str, Node] = {}
        self.connections: List[Connection] = []
        self.used_tracks: Set[str] = set()

    def generate(self, nodes: List[Node], connections: List[Connection]) -> str:
        """生成完整的 Lua 代码"""
        self.code_lines = []
        self.indent_level = 0
        self.states = set()
        self.node_map = {n.id: n for n in nodes}
        self.connections = connections
        self.used_tracks = set()
        self.generated_node_ids = set()

        if not nodes:
            return self._generate_empty()

        # 找出所有 EntryNode
        entry_nodes = [n for n in nodes if n.__class__.__name__ == 'EntryNode']

        # 为每个 EntryNode 收集状态信息
        state_flows = {}  # state_name -> list of nodes in flow
        for entry_node in entry_nodes:
            config = entry_node._get_config()
            state_name = config.get('state_name', 'idle')
            self.states.add(state_name)

            visited = set()
            ordered_ids = []
            self._collect_flow_nodes(entry_node, visited, ordered_ids)
            state_flows[state_name] = [self.node_map[nid] for nid in ordered_ids if nid in self.node_map]

        # 收集孤立节点
        connected_ids = set()
        for flow in state_flows.values():
            for node in flow:
                connected_ids.add(node.id)

        # 按视觉 Y 坐标排序孤立节点（从上到下）
        isolated_nodes = [n for n in nodes
                         if n.id not in connected_ids
                         and n.__class__.__name__ not in ('EntryNode',)]
        isolated_nodes.sort(key=lambda n: n.y)

        # 追踪使用的轨道
        for flow in state_flows.values():
            for node in flow:
                self._track_used_tracks(node)

        if isolated_nodes:
            self.states.add('default')
            state_flows['default'] = isolated_nodes
            for node in isolated_nodes:
                self._track_used_tracks(node)

        # 生成代码
        self._generate_track_definitions()
        self._generate_state_table(state_flows)
        self._generate_state_methods(state_flows)
        self._generate_helper_functions()

        return "\n".join(self.code_lines)

    def _track_used_tracks(self, node: Node):
        """追踪节点使用的轨道"""
        config = node._get_config()
        if 'track' in config:
            self.used_tracks.add(config.get('track', 'MAIN_TRACK'))

    def _collect_flow_nodes(self, start_node: Node, visited: Set[str], ordered_ids: List[str]):
        """收集从 start_node 出发可到达的所有节点，按连接创建顺序"""
        if start_node.id in visited:
            return
        visited.add(start_node.id)
        ordered_ids.append(start_node.id)

        for out_port in start_node.outputs:
            if out_port.port_type == PortType.EXEC:
                conns = [c for c in out_port.connections if c.output_port == out_port]
                conns.sort(key=lambda c: getattr(c, 'order', 0))
                for conn in conns:
                    next_node = conn.input_port.node
                    if next_node:
                        self._collect_flow_nodes(next_node, visited, ordered_ids)

    def _add_line(self, line: str = ""):
        """添加代码行"""
        self.code_lines.append("    " * self.indent_level + line)

    def _generate_empty(self) -> str:
        """生成空状态机"""
        return '''local M = {
    STATIC_TRACK_LINE = 0,
    MAIN_TRACK = 0,
}

function M:initialize(context)
end

function M:exit(context)
end

function M:states()
    return {}
end

return M'''

    def _generate_track_definitions(self):
        """生成轨道定义（只包含使用的）"""
        self._add_line("-- 轨道定义")
        self._add_line("local track_line_top = {value = 0}")
        self._add_line("local static_track_top = {value = 0}")
        self._add_line("local blending_track_top = {value = 0}")
        self._add_line()
        self._add_line("local function increment(obj)")
        self._indent()
        self._add_line("obj.value = obj.value + 1")
        self._add_line("return obj.value - 1")
        self._dedent()
        self._add_line("end")
        self._add_line()
        self._add_line("local STATIC_TRACK_LINE = increment(track_line_top)")
        self._add_line("local BASE_TRACK = increment(static_track_top)")

        # 只生成使用的轨道
        if 'MAIN_TRACK' in self.used_tracks or not self.used_tracks:
            self._add_line("local MAIN_TRACK = increment(static_track_top)")
        if 'MOVEMENT_TRACK' in self.used_tracks:
            self._add_line("local MOVEMENT_TRACK = increment(blending_track_top)")
        if 'ADS_TRACK' in self.used_tracks:
            self._add_line("local ADS_TRACK = increment(static_track_top)")
        if 'SPRINT_TRACK' in self.used_tracks:
            self._add_line("local SPRINT_TRACK = increment(static_track_top)")
        self._add_line()

    def _generate_state_table(self, state_flows: Dict):
        """生成状态表"""
        self._add_line("-- 状态机")
        self._add_line("local M = {")
        self._indent()

        # 轨道常量
        self._add_line("STATIC_TRACK_LINE = STATIC_TRACK_LINE,")
        self._add_line("MAIN_TRACK = MAIN_TRACK,")
        self._add_line()

        # 状态定义
        for state_name in sorted(self.states):
            self._add_line(f"{state_name} = {{}},")

        self._dedent()
        self._add_line("}")
        self._add_line()

    def _generate_state_methods(self, state_flows: Dict):
        """生成所有状态方法"""
        for state_name, flow_nodes in sorted(state_flows.items()):
            if not flow_nodes:
                continue

            entry_actions = []
            update_checks = []
            exit_actions = []
            transitions = []
            seen_ids = set()

            for node in flow_nodes:
                class_name = node.__class__.__name__
                if class_name == 'EntryNode':
                    continue
                elif class_name == 'UpdateNode':
                    update_checks.append(node)
                elif class_name == 'ExitNode':
                    exit_actions.append(node)
                elif class_name == 'TransitionNode':
                    transitions.append(node)
                else:
                    if node.id not in seen_ids:
                        entry_actions.append(node)
                        seen_ids.add(node.id)

            if entry_actions:
                self._add_line(f"function M.{state_name}.entry(this, context)")
                self._indent()
                self._generate_nodes_with_conditions(entry_actions)
                self._dedent()
                self._add_line("end")
                self._add_line()

            if update_checks:
                self._add_line(f"function M.{state_name}.update(this, context)")
                self._indent()
                self._generate_nodes_with_conditions(update_checks)
                self._dedent()
                self._add_line("end")
                self._add_line()

            if exit_actions:
                self._add_line(f"function M.{state_name}.exit(this, context)")
                self._indent()
                self._generate_nodes_with_conditions(exit_actions)
                self._dedent()
                self._add_line("end")
                self._add_line()

            if transitions:
                self._add_line(f"function M.{state_name}.transition(this, context, input)")
                self._indent()
                for node in transitions:
                    self._generate_transition_code(node)
                self._dedent()
                self._add_line("end")
                self._add_line()

    def _generate_helper_functions(self):
        """生成辅助函数"""
        self._add_line("function M:initialize(context)")
        self._indent()
        self._add_line("context:ensureTrackLineSize(track_line_top.value)")
        self._add_line("context:ensureTracksAmount(STATIC_TRACK_LINE, static_track_top.value)")
        self._dedent()
        self._add_line("end")
        self._add_line()

        self._add_line("function M:exit(context)")
        self._add_line("end")
        self._add_line()

        self._add_line("function M:states()")
        self._indent()
        self._add_line("return {")
        self._indent()
        for state_name in sorted(self.states):
            self._add_line(f"self.{state_name},")
        self._dedent()
        self._add_line("}")
        self._dedent()
        self._add_line("end")
        self._add_line()
        self._add_line("return M")

    def _is_condition_node(self, class_name: str) -> bool:
        """判断是否为条件节点"""
        return class_name in (
            'CheckAmmoNode', 'CheckAmmoCountNode', 'CheckHeatNode',
            'CheckAimingNode', 'CheckGroundNode', 'CheckStoppedNode',
            'CheckShootCooldownNode', 'CheckTrackIdleNode', 'CheckTrackHoldingNode',
            'CheckWalkDirectionNode', 'CheckRunningNode'
        )

    def _generate_nodes_with_conditions(self, nodes: List[Node]):
        """生成节点列表，自动处理 if/then/else/end 缩进"""
        i = 0
        while i < len(nodes):
            node = nodes[i]
            class_name = node.__class__.__name__

            if self._is_condition_node(class_name):
                self._generate_node_code(node)
                # 如果后面还有节点，缩进直到下一个条件节点
                i += 1
                if i < len(nodes):
                    self._indent()
                    while i < len(nodes) and not self._is_condition_node(nodes[i].__class__.__name__):
                        self._generate_node_code(nodes[i])
                        i += 1
                    self._dedent()
                    self._add_line("end")
                else:
                    # 后面没有节点了，直接 end
                    self._add_line("end")
            else:
                self._generate_node_code(node)
                i += 1

    def _generate_node_code(self, node: Node):
        """为单个节点生成 Lua 代码"""
        if node.id in self.generated_node_ids:
            return
        self.generated_node_ids.add(node.id)

        class_name = node.__class__.__name__
        config = node._get_config()

        if class_name == 'BoltNode':
            self._add_line("context:trigger(INPUT_BOLT)")
        elif class_name == 'AimNode':
            self._add_line("context:trigger(INPUT_AIM)")
        elif class_name == 'DrawNode':
            self._add_line("context:trigger(INPUT_DRAW)")
        elif class_name == 'ShootNode':
            self._add_line("context:trigger(INPUT_SHOOT)")
        elif class_name == 'ReloadNode':
            self._add_line("context:trigger(INPUT_RELOAD)")
        elif class_name == 'InspectNode':
            self._add_line("context:trigger(INPUT_INSPECT)")
        elif class_name == 'RunNode':
            self._add_line("context:trigger(INPUT_RUN)")
        elif class_name == 'WalkNode':
            self._add_line("context:trigger(INPUT_WALK)")
        elif class_name == 'BayonetMuzzleNode':
            self._add_line("context:trigger(INPUT_BAYONET_MUZZLE)")
        elif class_name == 'BayonetStockNode':
            self._add_line("context:trigger(INPUT_BAYONET_STOCK)")
        elif class_name == 'BayonetPushNode':
            self._add_line("context:trigger(INPUT_BAYONET_PUSH)")
        elif class_name == 'PutAwayNode':
            self._add_line("context:trigger(INPUT_PUT_AWAY)")
        elif class_name == 'IdleInputNode':
            self._add_line("context:trigger(INPUT_IDLE)")
        elif class_name == 'FireSelectNode':
            self._add_line("context:trigger(INPUT_FIRE_SELECT)")
        elif class_name == 'SprintNode':
            self._add_line("context:trigger(INPUT_SPRINT)")
        elif class_name == 'SlideNode':
            self._add_line("context:trigger(INPUT_SLIDE)")
        elif class_name == 'BoltCaughtNode':
            self._add_line("context:trigger(INPUT_BOLT_CAUGHT)")
        elif class_name == 'BoltNormalNode':
            self._add_line("context:trigger(INPUT_BOLT_NORMAL)")
        elif class_name == 'OverHeatNode':
            self._add_line("context:trigger(INPUT_OVER_HEAT)")
        elif class_name == 'CoolingHeatNode':
            self._add_line("context:trigger(INPUT_COOLING_HEAT)")
        elif class_name == 'InspectRetreatNode':
            self._add_line("context:trigger(INPUT_INSPECT_RETREAT)")
        elif class_name == 'AimRetreatNode':
            self._add_line("context:trigger(INPUT_AIM_RETREAT)")
        elif class_name == 'SpinNode':
            self._add_line("context:trigger(INPUT_SPIN)")
        elif class_name == 'PopShellNode':
            index = config.get('index', 0)
            self._add_line(f"context:popShellFrom({index})")
        elif class_name == 'RunAnimationNode':
            anim_name = config.get('animation_name', 'idle')
            track = config.get('track', 'MAIN_TRACK')
            blend = config.get('blend', False)
            mode = config.get('mode', 'PLAY_ONCE_STOP')
            blend_time = config.get('blend_time', 0.2)
            blend_str = "true" if blend else "false"
            self._add_line(f'context:runAnimation("{anim_name}", context:getTrack(STATIC_TRACK_LINE, {track}), {blend_str}, {mode}, {blend_time})')
        elif class_name == 'StopAnimationNode':
            track = config.get('track', 'MAIN_TRACK')
            self._add_line(f"context:stopAnimation(context:getTrack(STATIC_TRACK_LINE, {track}))")
        elif class_name == 'LoopAnimationNode':
            anim_name = config.get('animation_name', 'idle')
            track = config.get('track', 'MOVEMENT_TRACK')
            self._add_line(f'context:runAnimation("{anim_name}", context:getTrack(STATIC_TRACK_LINE, {track}), true, LOOP, 0)')
        elif class_name == 'SetProgressNode':
            track = config.get('track', 'MAIN_TRACK')
            progress = config.get('progress', 1.0)
            hold = config.get('is_hold', True)
            hold_str = "true" if hold else "false"
            self._add_line(f"context:adjustAnimationProgress(context:getTrack(STATIC_TRACK_LINE, {track}), {progress}, {hold_str})")
        elif class_name == 'AdjustProgressNode':
            track = config.get('track', 'MAIN_TRACK')
            delta = config.get('delta', 0.2)
            hold = config.get('is_hold', False)
            hold_str = "true" if hold else "false"
            self._add_line(f"context:adjustAnimationDelta(context:getTrack(STATIC_TRACK_LINE, {track}), {delta}, {hold_str})")
        elif class_name == 'HideCrosshairNode':
            hide = config.get('hide', True)
            hide_str_val = "true" if hide else "false"
            self._add_line(f"context:setShouldHideCrossHair({hide_str_val})")
        elif class_name == 'AnchorWalkDistNode':
            self._add_line("context:anchorWalkDist()")
        elif class_name == 'TriggerNode':
            event_name = config.get('event_name', 'INPUT_RELOAD')
            self._add_line(f"context:trigger({event_name})")
        elif class_name == 'PlayPutAwayNode':
            put_away_time = config.get('put_away_time', 0.5)
            self._add_line(f"context:runAnimation('put_away', context:getTrack(STATIC_TRACK_LINE, MAIN_TRACK), false, PLAY_ONCE_HOLD, 0)")
            self._add_line(f"context:adjustAnimationDelta(context:getTrack(STATIC_TRACK_LINE, MAIN_TRACK), -{put_away_time}, false)")
        elif class_name == 'PlayReloadNode':
            reload_type = config.get('reload_type', 'tactical')
            self._add_line(f'context:runAnimation("{reload_type}", context:getTrack(STATIC_TRACK_LINE, MAIN_TRACK), false, PLAY_ONCE_STOP, 0)')
        elif class_name == 'PlayInspectNode':
            self._add_line("context:runAnimation('inspect', context:getTrack(STATIC_TRACK_LINE, MAIN_TRACK), false, PLAY_ONCE_HOLD, 0)")
        elif class_name == 'PlayBlendedAnimationNode':
            anim_name = config.get('animation_name', 'shoot')
            track_line = config.get('track_line', 'GUN_KICK_TRACK_LINE')
            blend = config.get('blend', True)
            mode = config.get('mode', 'PLAY_ONCE_STOP')
            blend_str = "true" if blend else "false"
            self._add_line(f'local _track = context:findIdleTrack({track_line}, {blend_str})')
            self._add_line(f'context:runAnimation("{anim_name}", _track, {blend_str}, {mode}, 0)')
        elif class_name == 'CycleMeleeNode':
            anim_prefix = config.get('animation_prefix', 'melee_bayonet_')
            counter_name = config.get('counter_name', 'bayonet_counter')
            max_count = config.get('max_count', 3)
            self._add_line(f"if not {counter_name} then {counter_name} = 0 end")
            self._add_line(f"{counter_name} = {counter_name} + 1")
            self._add_line(f"if {counter_name} > {max_count} then {counter_name} = 1 end")
            self._add_line(f'context:runAnimation("{anim_prefix}" .. {counter_name}, context:getTrack(STATIC_TRACK_LINE, MAIN_TRACK), false, PLAY_ONCE_STOP, 0)')
        elif class_name == 'TrackHoldNode':
            track = config.get('track', 'MAIN_TRACK')
            self._add_line(f"context:runAnimation('', context:getTrack(STATIC_TRACK_LINE, {track}), false, PLAY_ONCE_HOLD, 0)")
        elif class_name == 'FindIdleTrackNode':
            track_line = config.get('track_line', 'GUN_KICK_TRACK_LINE')
            is_blending = config.get('is_blending', False)
            blend_str = "true" if is_blending else "false"
            self._add_line(f"context:findIdleTrack({track_line}, {blend_str})")
        elif class_name == 'CheckAmmoNode':
            self._add_line("if context:hasAmmo() then")
        elif class_name == 'CheckAmmoCountNode':
            operator = config.get('operator', '<=')
            value = config.get('value', 0)
            self._add_line(f"if context:getAmmoCount() {operator} {value} then")
        elif class_name == 'CheckHeatNode':
            self._add_line("if context:isOverheated() then")
        elif class_name == 'CheckAimingNode':
            progress = config.get('progress', 0.5)
            self._add_line(f"if context:getAimProgress() >= {progress} then")
        elif class_name == 'CheckGroundNode':
            self._add_line("if context:isOnGround() then")
        elif class_name == 'CheckStoppedNode':
            track = config.get('track', 'MAIN_TRACK')
            self._add_line(f"if context:isAnimationStopped(context:getTrack(STATIC_TRACK_LINE, {track})) then")
        elif class_name == 'CheckShootCooldownNode':
            operator = config.get('operator', '>')
            value = config.get('value', 0)
            self._add_line(f"if context:getTimeSinceShoot() {operator} {value} then")
        elif class_name == 'CheckTrackIdleNode':
            track = config.get('track', 'MAIN_TRACK')
            self._add_line(f"if context:isTrackIdle(context:getTrack(STATIC_TRACK_LINE, {track})) then")
        elif class_name == 'CheckTrackHoldingNode':
            track = config.get('track', 'MOVEMENT_TRACK')
            self._add_line(f"if context:isTrackHolding(context:getTrack(STATIC_TRACK_LINE, {track})) then")
        elif class_name == 'CheckWalkDirectionNode':
            direction = config.get('direction', 'forward')
            self._add_line(f"if context:getWalkDirection() == '{direction}' then")
        elif class_name == 'CheckRunningNode':
            self._add_line("if context:isRunning() then")
        elif class_name == 'LoopModeNode':
            pass
        elif class_name == 'PlayOnceStopNode':
            pass
        elif class_name == 'PlayOnceHoldNode':
            pass
        elif class_name == 'TrackLineNode':
            pass
        elif class_name == 'TrackNode':
            pass
        elif class_name == 'GetTrackNode':
            pass
        elif class_name == 'IfNode':
            pass
        elif class_name == 'ReturnNode':
            pass
        elif class_name == 'AndNode':
            pass
        elif class_name == 'OrNode':
            pass
        elif class_name == 'NotNode':
            pass
        elif class_name == 'CompareNode':
            pass
        elif class_name == 'AddNode':
            pass
        elif class_name == 'SubtractNode':
            pass
        elif class_name == 'MultiplyNode':
            pass
        elif class_name == 'DivideNode':
            pass
        elif class_name == 'OverHeatTrackNode':
            pass
        elif class_name == 'SlideTrackNode':
            pass
        elif class_name == 'StateDefineNode':
            pass
        elif class_name == 'CustomLuaNode':
            code = config.get('code', '').strip()
            if code:
                for line in code.split('\n'):
                    stripped = line.strip()
                    if stripped:
                        self._add_line(stripped)
        else:
            self._add_line(f"-- {class_name}")

    def _generate_transition_code(self, node: Node):
        """为转换节点生成代码"""
        config = node._get_config()
        to_state = config.get('to_state', 'idle')
        condition = config.get('condition', '')

        if condition:
            self._add_line(f"if ({condition}) then")
            self._indent()
            self._add_line(f"return M.{to_state}")
            self._dedent()
            self._add_line("end")
        else:
            self._add_line(f"return M.{to_state}")

    def _indent(self):
        """增加缩进"""
        self.indent_level += 1

    def _dedent(self):
        """减少缩进"""
        self.indent_level -= 1
