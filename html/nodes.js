/**
 * TACZ 节点定义库 - 基于 Web 的节点编辑器
 *
 * 提供所有 TACZ 状态机节点类型定义，按功能分类注册。
 * 每个节点包含标题、颜色、端口描述和默认配置。
 *
 * 模块导出:
 *   - NodeRegistry: 节点注册表，提供查询和实例化方法
 *   - createDefaultNode(type, x, y): 创建完整渲染就绪的节点对象
 */

// ─── 节点定义 ────────────────────────────────────────

const _definitions = [
  // ==================== 状态定义 (#FF69B4) ====================
  {
    id: 'StateDefineNode',
    title: '状态定义',
    color: '#FF69B4',
    category: '状态定义',
    description: '定义一个状态节点，用于组织状态机逻辑。作为状态机中每个状态的容器节点，用于分组该状态下的所有行为。',
    inputs: [],
    outputs: [
      { name: 'states', type: 'data', dataType: 'list' }
    ],
    defaultConfig: {}
  },
  {
    id: 'EntryNode',
    title: '进入状态',
    color: '#FF69B4',
    category: '状态定义',
    description: '状态进入时执行，用于初始化。当状态机进入某个状态时调用一次。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { state_name: 'idle' }
  },
  {
    id: 'UpdateNode',
    title: '更新状态',
    color: '#FF69B4',
    category: '状态定义',
    description: '每帧更新时执行，用于检查条件。状态机的 update 方法每帧都会被调用。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { state_name: 'idle', condition: '' }
  },
  {
    id: 'ExitNode',
    title: '退出状态',
    color: '#FF69B4',
    category: '状态定义',
    description: '状态退出时执行，用于清理。当状态机离开某个状态时调用一次。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { state_name: 'idle' }
  },
  {
    id: 'TransitionNode',
    title: '状态转换',
    color: '#FF69B4',
    category: '状态定义',
    description: '定义状态转换条件和目标状态。根据接收到的输入信号和条件判断是否转换到其他状态。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' },
      { name: '条件', type: 'data', dataType: 'bool' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { from_state: 'idle', to_state: 'idle', condition: '' }
  },

  // ==================== 输入事件 (#87CEEB) ====================
  {
    id: 'DrawNode',
    title: '掏枪',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_DRAW - 玩家掏出武器时触发。通常连接到状态机的起始状态转换。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'ShootNode',
    title: '射击',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_SHOOT - 玩家按下开火键时触发。可进一步区分解除开枪和按住开枪。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'ReloadNode',
    title: '换弹',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_RELOAD - 玩家按下换弹键时触发。可结合弹药检查节点判断换弹类型。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'InspectNode',
    title: '检视',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_INSPECT - 玩家按下检视键时触发。通常需要隐藏准星、播放检视动画。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'BoltNode',
    title: '拉栓',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_BOLT - 玩家拉动枪栓时触发。主要用于栓动步枪，拉栓动作完成后触发。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'AimNode',
    title: '瞄准',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_AIM - 玩家按下瞄准键时触发。可用于切换到瞄准动画。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'RunNode',
    title: '奔跑',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_RUN - 玩家按住奔跑键时触发。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'WalkNode',
    title: '行走',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_WALK - 玩家移动时触发。检测玩家的移动方向和状态。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'BayonetMuzzleNode',
    title: '近战配件',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_BAYONET_MUZZLE - 使用枪口近战配件时触发。通常支持多个近战动画循环播放。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'BayonetStockNode',
    title: '肘击',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_BAYONET_STOCK - 使用枪托肘击时触发。播放枪托肘击动画后返回闲置状态。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'BayonetPushNode',
    title: '推击',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_BAYONET_PUSH - 使用推击时触发。播放推击动画后返回闲置状态。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'PutAwayNode',
    title: '丢枪',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_PUT_AWAY - 玩家收起武器时触发。播放收起动画后转到最终状态。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'IdleInputNode',
    title: '闲置',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_IDLE - 玩家停止移动时触发。用于从奔跑/行走状态回到静止状态。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'FireSelectNode',
    title: '快慢机',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_FIRE_SELECT - 切换快慢机时触发。播放快慢机切换动画。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'SprintNode',
    title: '冲刺',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_SPRINT - 玩家战术冲刺时触发。用于切换到冲刺动画状态。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'SlideNode',
    title: '下蹲',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_SLIDE - 玩家下蹲/滑铲时触发。用于切换到下蹲动画状态。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'BoltCaughtNode',
    title: '空挂触发',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_BOLT_CAUGHT - 进入空仓挂机时触发。当武器子弹打空时触发。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'BoltNormalNode',
    title: '解除空挂',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_BOLT_NORMAL - 解除空仓挂机时触发。当换弹完成时触发。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'OverHeatNode',
    title: '过热',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_OVER_HEAT - 武器过热时触发。用于切换到过热状态。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'CoolingHeatNode',
    title: '冷却',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_COOLING_HEAT - 武器冷却时触发。用于从过热状态回到正常状态。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'InspectRetreatNode',
    title: '检视退出',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_INSPECT_RETREAT - 退出检视时触发。用于从检视状态回到闲置状态。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'AimRetreatNode',
    title: '瞄准退出',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_AIM_RETREAT - 退出瞄准时触发。用于从瞄准状态回到正常状态。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'SpinNode',
    title: '转管',
    color: '#87CEEB',
    category: '输入事件',
    description: 'INPUT_SPIN - 转管武器转轮时触发。用于播放转轮动画。',
    inputs: [],
    outputs: [
      { name: '触发', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },

  // ==================== 动画控制 (#32CD32) ====================
  {
    id: 'RunAnimationNode',
    title: '播放动画',
    color: '#32CD32',
    category: '动画控制',
    description: '在指定轨道上播放一个动画片段，支持多种播放模式和混合过渡。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {
      animation_name: 'idle',
      track: 'MAIN_TRACK',
      blend: false,
      mode: 'PLAY_ONCE_STOP',
      blend_time: 0.2
    }
  },
  {
    id: 'StopAnimationNode',
    title: '停止动画',
    color: '#32CD32',
    category: '动画控制',
    description: '立即停止指定轨道上正在播放的动画。常用于打断正在播放的动画以切换到其他动画。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { track: 'MAIN_TRACK' }
  },
  {
    id: 'LoopAnimationNode',
    title: '循环动画',
    color: '#32CD32',
    category: '动画控制',
    description: '在指定轨道上循环播放动画，常用于 idle、奔跑等持续性动画。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { animation_name: 'idle', track: 'MOVEMENT_TRACK' }
  },
  {
    id: 'SetProgressNode',
    title: '设置进度',
    color: '#32CD32',
    category: '动画控制',
    description: '直接设置指定轨道的动画播放进度（0.0 到 1.0）。常用于同步动画进度或快进到特定帧。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { track: 'MAIN_TRACK', progress: 1.0, is_hold: true }
  },
  {
    id: 'AdjustProgressNode',
    title: '调整进度',
    color: '#32CD32',
    category: '动画控制',
    description: '相对调整当前动画的播放进度（向前或向后），常用于修正动画播放位置。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { track: 'MAIN_TRACK', delta: 0.2, is_hold: false }
  },
  {
    id: 'PlayBlendedAnimationNode',
    title: '混合动画',
    color: '#32CD32',
    category: '动画控制',
    description: '使用 findIdleTrack 找到空闲轨道播放动画。适用于射击动画等需要快速连续播放的情况。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {
      animation_name: 'shoot',
      track_line: 'GUN_KICK_TRACK_LINE',
      blend: true,
      mode: 'PLAY_ONCE_STOP'
    }
  },

  // ==================== 条件检查 (#BA55D3) ====================
  {
    id: 'CheckAmmoNode',
    title: '有弹药',
    color: '#BA55D3',
    category: '条件检查',
    description: '检查弹匣中是否有弹药。同时检查枪管和弹匣是否有弹药。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '是', type: 'exec', dataType: 'exec' },
      { name: '否', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'CheckAmmoCountNode',
    title: '弹药数量',
    color: '#BA55D3',
    category: '条件检查',
    description: '比较当前弹药数量与设定值，支持多种比较运算符。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '是', type: 'exec', dataType: 'exec' },
      { name: '否', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { operator: '<=', value: 0 }
  },
  {
    id: 'CheckHeatNode',
    title: '过热检查',
    color: '#BA55D3',
    category: '条件检查',
    description: '检查武器是否过热。对于可过热武器，检查当前热度状态。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '是', type: 'exec', dataType: 'exec' },
      { name: '否', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'CheckAimingNode',
    title: '瞄准进度',
    color: '#BA55D3',
    category: '条件检查',
    description: '检查瞄准进度是否达到阈值（0.0 到 1.0）。用于判断瞄准是否完成。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '是', type: 'exec', dataType: 'exec' },
      { name: '否', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { progress: 0.5 }
  },
  {
    id: 'CheckGroundNode',
    title: '在地面上',
    color: '#BA55D3',
    category: '条件检查',
    description: '检查玩家是否站在地面上。用于区分跳跃和行走状态。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '是', type: 'exec', dataType: 'exec' },
      { name: '否', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'CheckStoppedNode',
    title: '动画停止',
    color: '#BA55D3',
    category: '条件检查',
    description: '检查指定轨道的动画是否已停止。用于等待动画播放完成后再进行下一步操作。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '是', type: 'exec', dataType: 'exec' },
      { name: '否', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { track: 'MAIN_TRACK' }
  },
  {
    id: 'CheckShootCooldownNode',
    title: '射击冷却',
    color: '#BA55D3',
    category: '条件检查',
    description: '检查射击冷却时间，用于控制射击频率。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '是', type: 'exec', dataType: 'exec' },
      { name: '否', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { operator: '>', value: 0 }
  },
  {
    id: 'CheckTrackIdleNode',
    title: '轨道空闲',
    color: '#BA55D3',
    category: '条件检查',
    description: '检查指定轨道是否空闲（停止播放）。用于判断轨道是否可以播放新动画。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '是', type: 'exec', dataType: 'exec' },
      { name: '否', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { track: 'MAIN_TRACK' }
  },
  {
    id: 'CheckTrackHoldingNode',
    title: '轨道挂起',
    color: '#BA55D3',
    category: '条件检查',
    description: '检查指定轨道是否处于挂起状态。用于判断动画是否播放完成并挂起。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '是', type: 'exec', dataType: 'exec' },
      { name: '否', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { track: 'MOVEMENT_TRACK' }
  },
  {
    id: 'CheckWalkDirectionNode',
    title: '行走方向',
    color: '#BA55D3',
    category: '条件检查',
    description: '检测玩家移动方向（前进、后退、侧移），用于播放对应的行走动画。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '是', type: 'exec', dataType: 'exec' },
      { name: '否', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { direction: 'forward' }
  },
  {
    id: 'CheckRunningNode',
    title: '是否奔跑',
    color: '#BA55D3',
    category: '条件检查',
    description: '检测玩家当前是否在奔跑状态。用于区分行走和奔跑动画。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '是', type: 'exec', dataType: 'exec' },
      { name: '否', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },

  // ==================== 动作操作 (#FF8C00) ====================
  {
    id: 'PopShellNode',
    title: '抛壳',
    color: '#FF8C00',
    category: '动作操作',
    description: '从指定位置抛出弹壳。在射击时从指定位置抛出弹壳动画，增强射击的真实感。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { index: 0 }
  },
  {
    id: 'TriggerNode',
    title: '触发事件',
    color: '#FF8C00',
    category: '动作操作',
    description: '触发一个状态机内部事件。通常与其他条件检查配合使用。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { event_name: 'INPUT_RELOAD' }
  },
  {
    id: 'CustomLuaNode',
    title: '自定义代码',
    color: '#FF8C00',
    category: '动作操作',
    description: '执行自定义 Lua 代码。当内置节点无法满足需求时，可编写任意 Lua 代码。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { code: '-- custom code' }
  },
  {
    id: 'HideCrosshairNode',
    title: '隐藏准星',
    color: '#FF8C00',
    category: '动作操作',
    description: '显示或隐藏屏幕中央准星。在检视等需要专注观察的动作中隐藏准星。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { hide: true }
  },
  {
    id: 'AnchorWalkDistNode',
    title: '锁定行走',
    color: '#FF8C00',
    category: '动作操作',
    description: '锁定武器的行走距离锚点。确保行走动画的起点一致，避免每次行走开始时动画跳变。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'PlayPutAwayNode',
    title: '播放丢枪动画',
    color: '#FF8C00',
    category: '动作操作',
    description: '播放收起武器动画。动画会设置到最后一帧然后回退。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { put_away_time: 0.5 }
  },
  {
    id: 'PlayReloadNode',
    title: '播放换弹动画',
    color: '#FF8C00',
    category: '动作操作',
    description: '根据当前弹药状态播放对应的换弹动画（战术换弹/空仓换弹）。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { reload_type: 'tactical' }
  },
  {
    id: 'PlayInspectNode',
    title: '播放检视动画',
    color: '#FF8C00',
    category: '动作操作',
    description: '播放武器检视动画，展示武器细节。检视过程中需要隐藏准星。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'CycleMeleeNode',
    title: '循环近战动画',
    color: '#FF8C00',
    category: '动作操作',
    description: '循环播放多个近战动画，通过计数器决定播放第几个动画。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {
      animation_prefix: 'melee_bayonet_',
      counter_name: 'bayonet_counter',
      max_count: 3
    }
  },
  {
    id: 'TrackHoldNode',
    title: '轨道占位',
    color: '#FF8C00',
    category: '动作操作',
    description: '在特定轨道上播放空动画以占位，防止后续动画被错误叠加。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: { track: 'MAIN_TRACK' }
  },

  // ==================== 轨道系统 (#4A90E2) ====================
  {
    id: 'TrackLineNode',
    title: '轨道行',
    color: '#4A90E2',
    category: '轨道系统',
    description: '定义轨道行常量。轨道行是一组相关轨道的容器。',
    inputs: [],
    outputs: [
      { name: 'STATIC', type: 'data', dataType: 'object' },
      { name: 'GUN_KICK', type: 'data', dataType: 'object' },
      { name: 'BLENDING', type: 'data', dataType: 'object' }
    ],
    defaultConfig: {}
  },
  {
    id: 'TrackNode',
    title: '轨道',
    color: '#4A90E2',
    category: '轨道系统',
    description: '定义轨道常量。轨道是实际承载动画播放的通道，同一轨道行可以有多个轨道同时播放不同动画。',
    inputs: [],
    outputs: [
      { name: 'BASE', type: 'data', dataType: 'object' },
      { name: 'BOLT_CAUGHT', type: 'data', dataType: 'object' },
      { name: 'ADS', type: 'data', dataType: 'object' },
      { name: 'MAIN', type: 'data', dataType: 'object' },
      { name: 'SPRINT', type: 'data', dataType: 'object' },
      { name: 'MOVEMENT', type: 'data', dataType: 'object' }
    ],
    defaultConfig: {}
  },
  {
    id: 'GetTrackNode',
    title: '获取轨道',
    color: '#4A90E2',
    category: '轨道系统',
    description: '通过轨道行和轨道名称获取完整的轨道对象。这是实际调用时获取轨道的方式。',
    inputs: [
      { name: '', type: 'data', dataType: 'object' }
    ],
    outputs: [
      { name: '轨道', type: 'data', dataType: 'object' }
    ],
    defaultConfig: { track_line: 'STATIC_TRACK_LINE', track: 'MAIN_TRACK' }
  },
  {
    id: 'OverHeatTrackNode',
    title: '过热轨道',
    color: '#4A90E2',
    category: '轨道系统',
    description: '定义过热相关轨道，用于可过热武器的过热动画播放。',
    inputs: [],
    outputs: [
      { name: 'OVER_HEAT', type: 'data', dataType: 'object' },
      { name: 'OVER_HEATING', type: 'data', dataType: 'object' },
      { name: 'LOOP', type: 'data', dataType: 'object' }
    ],
    defaultConfig: {}
  },
  {
    id: 'SlideTrackNode',
    title: '下蹲轨道',
    color: '#4A90E2',
    category: '轨道系统',
    description: '定义下蹲/滑铲轨道，用于下蹲和滑铲动画播放。',
    inputs: [],
    outputs: [
      { name: 'SLIDE', type: 'data', dataType: 'object' }
    ],
    defaultConfig: {}
  },
  {
    id: 'FindIdleTrackNode',
    title: '寻找空闲轨道',
    color: '#4A90E2',
    category: '轨道系统',
    description: '在轨道行中寻找空闲的轨道。用于射击动画等需要快速连续播放的场景。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [
      { name: '轨道', type: 'data', dataType: 'object' }
    ],
    defaultConfig: { track_line: 'GUN_KICK_TRACK_LINE', is_blending: false }
  },

  // ==================== 逻辑控制 (#FFB347) ====================
  {
    id: 'IfNode',
    title: '条件分支',
    color: '#FFB347',
    category: '逻辑控制',
    description: '根据输入的布尔值选择执行路径，类似于编程语言中的 if-else。',
    inputs: [
      { name: '条件', type: 'data', dataType: 'bool' }
    ],
    outputs: [
      { name: '成立', type: 'exec', dataType: 'exec' },
      { name: '不成立', type: 'exec', dataType: 'exec' }
    ],
    defaultConfig: {}
  },
  {
    id: 'ReturnNode',
    title: '返回状态',
    color: '#FFB347',
    category: '逻辑控制',
    description: '在 transition 方法中返回目标状态，表示状态机应该转换到该状态。',
    inputs: [
      { name: '', type: 'exec', dataType: 'exec' }
    ],
    outputs: [],
    defaultConfig: { state_name: 'idle' }
  },
  {
    id: 'AndNode',
    title: '与运算',
    color: '#FFB347',
    category: '逻辑控制',
    description: '逻辑与运算 (A and B)。当两个输入都为 true 时输出 true。',
    inputs: [
      { name: 'A', type: 'data', dataType: 'bool' },
      { name: 'B', type: 'data', dataType: 'bool' }
    ],
    outputs: [
      { name: '结果', type: 'data', dataType: 'bool' }
    ],
    defaultConfig: {}
  },
  {
    id: 'OrNode',
    title: '或运算',
    color: '#FFB347',
    category: '逻辑控制',
    description: '逻辑或运算 (A or B)。当任意一个输入为 true 时输出 true。',
    inputs: [
      { name: 'A', type: 'data', dataType: 'bool' },
      { name: 'B', type: 'data', dataType: 'bool' }
    ],
    outputs: [
      { name: '结果', type: 'data', dataType: 'bool' }
    ],
    defaultConfig: {}
  },
  {
    id: 'NotNode',
    title: '非运算',
    color: '#FFB347',
    category: '逻辑控制',
    description: '逻辑非运算 (not A)。反转布尔值的逻辑状态。',
    inputs: [
      { name: '输入', type: 'data', dataType: 'bool' }
    ],
    outputs: [
      { name: '结果', type: 'data', dataType: 'bool' }
    ],
    defaultConfig: {}
  },
  {
    id: 'CompareNode',
    title: '比较',
    color: '#FFB347',
    category: '逻辑控制',
    description: '对两个输入值进行比较运算，常用于数值条件判断。',
    inputs: [
      { name: 'A', type: 'data', dataType: 'any' },
      { name: 'B', type: 'data', dataType: 'any' }
    ],
    outputs: [
      { name: '结果', type: 'data', dataType: 'bool' }
    ],
    defaultConfig: { operator: '==' }
  },

  // ==================== 动画模式 (#98FB98) ====================
  {
    id: 'LoopModeNode',
    title: '循环模式',
    color: '#98FB98',
    category: '动画模式',
    description: 'LOOP - 无限循环播放动画。适用于 idle、跑步等持续性动画。',
    inputs: [],
    outputs: [
      { name: '模式', type: 'data', dataType: 'string' }
    ],
    defaultConfig: {}
  },
  {
    id: 'PlayOnceStopNode',
    title: '播放一次停止',
    color: '#98FB98',
    category: '动画模式',
    description: 'PLAY_ONCE_STOP - 播放一次后自动停止。适用于射击、拉栓等一次性动作。',
    inputs: [],
    outputs: [
      { name: '模式', type: 'data', dataType: 'string' }
    ],
    defaultConfig: {}
  },
  {
    id: 'PlayOnceHoldNode',
    title: '播放一次保持',
    color: '#98FB98',
    category: '动画模式',
    description: 'PLAY_ONCE_HOLD - 播放一次后保持最后一帧。常用于需要保持姿态的动作。',
    inputs: [],
    outputs: [
      { name: '模式', type: 'data', dataType: 'string' }
    ],
    defaultConfig: {}
  },

  // ==================== 数学运算 (#DDA0DD) ====================
  {
    id: 'AddNode',
    title: '加法',
    color: '#DDA0DD',
    category: '数学运算',
    description: '加法运算 (A + B)，计算两个数值的和。',
    inputs: [
      { name: 'A', type: 'data', dataType: 'number' },
      { name: 'B', type: 'data', dataType: 'number' }
    ],
    outputs: [
      { name: '结果', type: 'data', dataType: 'number' }
    ],
    defaultConfig: {}
  },
  {
    id: 'SubtractNode',
    title: '减法',
    color: '#DDA0DD',
    category: '数学运算',
    description: '减法运算 (A - B)，计算两个数值的差。',
    inputs: [
      { name: 'A', type: 'data', dataType: 'number' },
      { name: 'B', type: 'data', dataType: 'number' }
    ],
    outputs: [
      { name: '结果', type: 'data', dataType: 'number' }
    ],
    defaultConfig: {}
  },
  {
    id: 'MultiplyNode',
    title: '乘法',
    color: '#DDA0DD',
    category: '数学运算',
    description: '乘法运算 (A * B)，计算两个数值的乘积。',
    inputs: [
      { name: 'A', type: 'data', dataType: 'number' },
      { name: 'B', type: 'data', dataType: 'number' }
    ],
    outputs: [
      { name: '结果', type: 'data', dataType: 'number' }
    ],
    defaultConfig: {}
  },
  {
    id: 'DivideNode',
    title: '除法',
    color: '#DDA0DD',
    category: '数学运算',
    description: '除法运算 (A / B)，计算两个数值的商（除数为零时返回零）。',
    inputs: [
      { name: 'A', type: 'data', dataType: 'number' },
      { name: 'B', type: 'data', dataType: 'number' }
    ],
    outputs: [
      { name: '结果', type: 'data', dataType: 'number' }
    ],
    defaultConfig: {}
  }
];

// ─── NodeRegistry ─────────────────────────────────────

let _nodeIdCounter = 0;

function _generateNodeId(type) {
  _nodeIdCounter++;
  return `${type}_${Date.now()}_${_nodeIdCounter}`;
}

function _clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

const NodeRegistry = {
  /**
   * 获取所有节点定义。
   * @returns {Array} 节点定义数组
   */
  getAll() {
    return _definitions;
  },

  /**
   * 获取所有分类名称列表。
   * @returns {string[]} 分类名称数组
   */
  getCategories() {
    const cats = [];
    for (const def of _definitions) {
      if (!cats.includes(def.category)) {
        cats.push(def.category);
      }
    }
    return cats;
  },

  /**
   * 获取指定分类下的所有节点定义。
   * @param {string} category - 分类名称
   * @returns {Array} 该分类下的节点定义数组
   */
  getNodesByCategory(category) {
    return _definitions.filter(def => def.category === category);
  },

  /**
   * 根据节点类型 ID 获取节点定义。
   * @param {string} type - 节点类型 ID（如 'DrawNode'）
   * @returns {object|undefined} 节点定义对象
   */
  getDefinition(type) {
    return _definitions.find(def => def.id === type);
  },

  /**
   * 创建一个新的节点实例对象。
   * @param {string} type - 节点类型 ID
   * @param {number} x - 在画布上的 X 坐标
   * @param {number} y - 在画布上的 Y 坐标
   * @returns {object} 节点实例
   */
  createNode(type, x = 0, y = 0) {
    const def = this.getDefinition(type);
    if (!def) {
      throw new Error(`未知节点类型: ${type}`);
    }
    return {
      id: _generateNodeId(type),
      type: def.id,
      title: def.title,
      color: def.color,
      category: def.category,
      description: def.description,
      inputs: _clone(def.inputs),
      outputs: _clone(def.outputs),
      config: _clone(def.defaultConfig),
      x,
      y
    };
  }
};

// ─── createDefaultNode ────────────────────────────────

/**
 * 创建一个完整渲染就绪的节点对象。
 *
 * 与 NodeRegistry.createNode 行为一致，作为独立工具函数提供。
 * 适用于从外部直接创建节点而无需引用 NodeRegistry。
 *
 * @param {string} type - 节点类型 ID
 * @param {number} x - 在画布上的 X 坐标
 * @param {number} y - 在画布上的 Y 坐标
 * @returns {object} 完整节点对象
 */
function createDefaultNode(type, x = 0, y = 0) {
  return NodeRegistry.createNode(type, x, y);
}
