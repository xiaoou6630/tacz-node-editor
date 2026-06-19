import * as Blockly from 'blockly'
import { _b } from '../locales'

const DIR_OPTIONS: [string, string][] = [
  ['forward', 'forward'], ['backward', 'backward'], ['strafe', 'strafe'],
]
const BOOL_OPTIONS: [string, string][] = [['true', 'true'], ['false', 'false']]
const OPERATOR_OPTIONS: [string, string][] = [
  ['==', '=='], ['~=', '~='], ['<', '<'], ['>', '>'], ['<=', '<='], ['>=', '>='],
]
const TRACK_OPTIONS: [string, string][] = [
  ['MAIN_TRACK', 'MAIN_TRACK'], ['MOVEMENT_TRACK', 'MOVEMENT_TRACK'],
  ['BASE_TRACK', 'BASE_TRACK'], ['ADS_TRACK', 'ADS_TRACK'],
  ['SPRINT_TRACK', 'SPRINT_TRACK'], ['BOLT_CAUGHT_TRACK', 'BOLT_CAUGHT_TRACK'],
]
const TRACK_LINE_OPTIONS: [string, string][] = [
  ['STATIC_TRACK_LINE', 'STATIC_TRACK_LINE'], ['GUN_KICK_TRACK_LINE', 'GUN_KICK_TRACK_LINE'],
  ['BLENDING_TRACK_LINE', 'BLENDING_TRACK_LINE'],
]
const MODE_OPTIONS: [string, string][] = [
  ['PLAY_ONCE_STOP', 'PLAY_ONCE_STOP'], ['PLAY_ONCE_HOLD', 'PLAY_ONCE_HOLD'],
  ['LOOP', 'LOOP'],
]
const RELOAD_OPTIONS: [string, string][] = [['tactical', 'tactical'], ['empty', 'empty']]
const RELOAD_STATE_OPTIONS: [string, string][] = [
  ['NOT_RELOADING', 'NOT_RELOADING'], ['EMPTY_RELOAD_FEEDING', 'EMPTY_RELOAD_FEEDING'],
  ['EMPTY_RELOAD_FINISHING', 'EMPTY_RELOAD_FINISHING'], ['TACTICAL_RELOAD_FEEDING', 'TACTICAL_RELOAD_FEEDING'],
  ['TACTICAL_RELOAD_FINISHING', 'TACTICAL_RELOAD_FINISHING'],
]
const FIRE_MODE_OPTIONS: [string, string][] = [
  ['AUTO', 'AUTO'], ['SEMI', 'SEMI'], ['BURST', 'BURST'], ['UNKNOWN', 'UNKNOWN'],
]
const WALK_DIR_OPTIONS: [string, string][] = [
  ['forward', 'forward'], ['backward', 'backward'], ['left', 'left'], ['right', 'right'],
]

// ─── State Definition Blocks ───
Blockly.Blocks['state_define'] = {
  init() {
    this.appendDummyInput().appendField(_b('📌 状态定义', '📌 State Define'))
    this.setOutput(true, 'Array')
    this.setColour('#FF69B4')
  }
}
Blockly.Blocks['entry'] = {
  init() {
    this.appendDummyInput().appendField(_b('▶️ 进入状态', '▶️ Entry'))
      .appendField(new Blockly.FieldTextInput('idle'), 'STATE')
    this.setPreviousStatement(true, 'state_stmt')
    this.setNextStatement(true, 'state_stmt')
    this.setColour('#FF69B4')
    this.setTooltip(_b('状态开始时执行', 'Executed when state starts'))
  }
}
Blockly.Blocks['update_node'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔄 更新状态', '🔄 Update'))
      .appendField(new Blockly.FieldTextInput('idle'), 'STATE')
    this.appendValueInput('COND').setCheck('Boolean').appendField(_b('条件', 'Condition'))
    this.setPreviousStatement(true, 'state_stmt')
    this.setNextStatement(true, 'state_stmt')
    this.setColour('#FF69B4')
    this.setTooltip(_b('每帧执行，可设条件仅条件满足时执行', 'Executed every frame, optional condition'))
  }
}
Blockly.Blocks['exit'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏹️ 退出状态', '⏹️ Exit'))
      .appendField(new Blockly.FieldTextInput('idle'), 'STATE')
    this.setPreviousStatement(true, 'state_stmt')
    this.setNextStatement(true, 'state_stmt')
    this.setColour('#FF69B4')
    this.setTooltip(_b('状态结束时执行', 'Executed when state ends'))
  }
}
Blockly.Blocks['transition'] = {
  init() {
    this.appendDummyInput().appendField(_b('↔️ 状态转换', '↔️ Transition'))
      .appendField(new Blockly.FieldTextInput('idle'), 'FROM')
      .appendField(_b('→', '→'))
      .appendField(new Blockly.FieldTextInput('idle'), 'TO')
    this.appendValueInput('COND').setCheck('Boolean').appendField(_b('条件', 'Condition'))
    this.setPreviousStatement(true, 'state_stmt')
    this.setNextStatement(true, 'state_stmt')
    this.setColour('#FF69B4')
  }
}

// ─── Event Hat Blocks ───
const eventTypes: [string, string, string][] = [
  ['draw', '掏枪', 'Draw'], ['shoot', '射击', 'Shoot'], ['reload', '换弹', 'Reload'],
  ['inspect', '检视', 'Inspect'], ['bolt', '拉栓', 'Bolt'], ['aim', '瞄准', 'Aim'],
  ['run', '奔跑', 'Run'], ['walk', '行走', 'Walk'], ['sprint', '冲刺', 'Sprint'],
  ['slide', '下蹲', 'Slide'], ['put_away', '丢枪', 'Put Away'], ['idle_input', '闲置', 'Idle'],
  ['fire_select', '快慢机', 'Fire Select'], ['over_heat', '过热', 'Over Heat'],
  ['cooling', '冷却', 'Cooling'], ['spin', '转管', 'Spin'],
  ['bayonet_muzzle', '枪口近战', 'Bayonet Muzzle'], ['bayonet_stock', '枪托肘击', 'Bayonet Stock'],
  ['bayonet_push', '推击', 'Bayonet Push'], ['bolt_caught', '空挂触发', 'Bolt Caught'],
  ['bolt_normal', '解除空挂', 'Bolt Normal'],
  ['inspect_retreat', '检视退出', 'Inspect Retreat'], ['aim_retreat', '瞄准退出', 'Aim Retreat'],
]
eventTypes.forEach(([id, zh, en]) => {
  Blockly.Blocks[`event_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(`🎯 ${_b(zh, en)}`)
      this.setNextStatement(true, 'action_stmt')
      this.setColour('#87CEEB')
      this.setTooltip(_b(`当玩家${zh}时触发`, `Triggered on ${en}`))
    }
  }
})

// ─── Animation Control Blocks ───
Blockly.Blocks['run_animation'] = {
  init() {
    this.appendDummyInput().appendField(_b('🎬 播放动画', '🎬 Run Animation'))
    this.appendDummyInput().appendField(_b('动画', 'Anim')).appendField(new Blockly.FieldTextInput('idle'), 'ANIM')
    this.appendDummyInput().appendField(_b('轨道', 'Track')).appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.appendDummyInput().appendField(_b('混合', 'Blend')).appendField(new Blockly.FieldDropdown(BOOL_OPTIONS), 'BLEND')
    this.appendDummyInput().appendField(_b('模式', 'Mode')).appendField(new Blockly.FieldDropdown(MODE_OPTIONS), 'MODE')
    this.appendValueInput('BLEND_TIME').setCheck('Number').appendField(_b('过渡时间', 'Blend Time'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#32CD32')
  }
}
Blockly.Blocks['stop_animation'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏹️ 停止动画', '⏹️ Stop Animation'))
      .appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#32CD32')
  }
}
Blockly.Blocks['loop_animation'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔁 循环动画', '🔁 Loop Animation'))
    this.appendDummyInput().appendField(_b('动画', 'Anim')).appendField(new Blockly.FieldTextInput('idle'), 'ANIM')
    this.appendDummyInput().appendField(_b('轨道', 'Track')).appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.appendDummyInput().appendField(_b('混合', 'Blend')).appendField(new Blockly.FieldDropdown(BOOL_OPTIONS), 'BLEND')
    this.appendValueInput('BLEND_TIME').setCheck('Number').appendField(_b('过渡时间', 'Blend Time'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#32CD32')
  }
}
Blockly.Blocks['set_progress'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏩ 设置进度', '⏩ Set Progress'))
      .appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.appendValueInput('PROGRESS').setCheck('Number').appendField(_b('进度', 'Progress'))
    this.appendDummyInput().appendField(_b('归一化', 'Normalize')).appendField(new Blockly.FieldDropdown(BOOL_OPTIONS), 'NORMALIZATION')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#32CD32')
    this.setTooltip(_b('设置动画绝对进度，归一化=true时进度为0~1', 'Set absolute progress, normalize=true means 0~1'))
  }
}
Blockly.Blocks['adjust_progress'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏪ 调整进度', '⏪ Adjust Progress'))
      .appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.appendValueInput('DELTA').setCheck('Number').appendField(_b('偏移', 'Delta'))
    this.appendDummyInput().appendField(_b('归一化', 'Normalize')).appendField(new Blockly.FieldDropdown(BOOL_OPTIONS), 'NORMALIZATION')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#32CD32')
    this.setTooltip(_b('相对调整进度，归一化=true时偏移为-1~1', 'Adjust progress relatively, normalize=true means -1~1'))
  }
}
Blockly.Blocks['play_blended'] = {
  init() {
    this.appendDummyInput().appendField(_b('🎯 混合动画', '🎯 Play Blended'))
    this.appendDummyInput().appendField(_b('动画', 'Anim')).appendField(new Blockly.FieldTextInput('shoot'), 'ANIM')
    this.appendDummyInput().appendField(_b('轨道行', 'Track Line')).appendField(new Blockly.FieldDropdown(TRACK_LINE_OPTIONS), 'LINE')
    this.appendDummyInput().appendField(_b('混合', 'Blend')).appendField(new Blockly.FieldDropdown(BOOL_OPTIONS), 'BLEND')
    this.appendDummyInput().appendField(_b('模式', 'Mode')).appendField(new Blockly.FieldDropdown(MODE_OPTIONS), 'MODE')
    this.appendValueInput('BLEND_TIME').setCheck('Number').appendField(_b('过渡时间', 'Blend Time'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#32CD32')
  }
}
Blockly.Blocks['pause_animation'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏸️ 暂停动画', '⏸️ Pause Animation'))
      .appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#32CD32')
    this.setTooltip(_b('暂停动画，关键帧仍影响模型', 'Pause animation, keyframes still affect model'))
  }
}
Blockly.Blocks['resume_animation'] = {
  init() {
    this.appendDummyInput().appendField(_b('▶️ 恢复动画', '▶️ Resume Animation'))
      .appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#32CD32')
    this.setTooltip(_b('恢复暂停的动画', 'Resume a paused animation'))
  }
}

// ─── Condition Check Blocks ───
Blockly.Blocks['check_ammo'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔫 有弹药?', '🔫 Has Ammo?'))
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
  }
}
Blockly.Blocks['check_ammo_count'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔢 弹药数量', '🔢 Ammo Count'))
      .appendField(new Blockly.FieldDropdown(OPERATOR_OPTIONS), 'OP')
    this.appendValueInput('VALUE').setCheck('Number')
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
  }
}
Blockly.Blocks['check_heat'] = {
  init() {
    this.appendDummyInput().appendField(_b('🌡️ 过热?', '🌡️ Overheated?'))
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
  }
}
Blockly.Blocks['check_aiming'] = {
  init() {
    this.appendDummyInput().appendField(_b('🎯 瞄准进度 ≥', '🎯 Aim Progress ≥'))
    this.appendValueInput('PROGRESS').setCheck('Number')
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
  }
}
Blockly.Blocks['check_ground'] = {
  init() {
    this.appendDummyInput().appendField(_b('🌍 在地面?', '🌍 On Ground?'))
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
  }
}
Blockly.Blocks['check_stopped'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏹️ 动画停止?', '⏹️ Anim Stopped?'))
      .appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
  }
}
Blockly.Blocks['check_cooldown'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏱️ 射击冷却', '⏱️ Shoot Cooldown'))
      .appendField(new Blockly.FieldDropdown(OPERATOR_OPTIONS), 'OP')
    this.appendValueInput('VALUE').setCheck('Number')
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
  }
}
Blockly.Blocks['check_track_idle'] = {
  init() {
    this.appendDummyInput().appendField(_b('🆓 轨道空闲?', '🆓 Track Idle?'))
      .appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
  }
}
Blockly.Blocks['check_walk_dir'] = {
  init() {
    this.appendDummyInput().appendField(_b('🚶 行走方向', '🚶 Walk Direction'))
      .appendField(new Blockly.FieldDropdown(WALK_DIR_OPTIONS), 'DIR')
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
  }
}
Blockly.Blocks['check_running'] = {
  init() {
    this.appendDummyInput().appendField(_b('🏃 奔跑中?', '🏃 Running?'))
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
  }
}
Blockly.Blocks['check_holding'] = {
  init() {
    this.appendDummyInput().appendField(_b('📌 动画挂起?', '📌 Anim Holding?'))
      .appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
    this.setTooltip(_b('指定轨道是否被挂起（定格在最后一帧）', 'Is the track held at the last frame'))
  }
}
Blockly.Blocks['check_paused'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏸️ 动画暂停?', '⏸️ Anim Paused?'))
      .appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
    this.setTooltip(_b('指定轨道是否暂停', 'Is the track paused'))
  }
}
Blockly.Blocks['has_animation'] = {
  init() {
    this.appendDummyInput().appendField(_b('🎞️ 动画存在?', '🎞️ Has Animation?'))
      .appendField(new Blockly.FieldTextInput('idle'), 'NAME')
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
    this.setTooltip(_b('检查动画文件中是否存在指定动画', 'Check if animation prototype exists'))
  }
}
Blockly.Blocks['check_bullet_in_barrel'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔫 枪膛有弹?', '🔫 Bullet In Barrel?'))
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
    this.setTooltip(_b('枪膛中是否有子弹，开膛待击枪械返回false', 'Whether there is a bullet in the barrel'))
  }
}
Blockly.Blocks['check_aiming'] = {
  init() {
    this.appendDummyInput().appendField(_b('🎯 正在瞄准?', '🎯 Is Aiming?'))
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
    this.setTooltip(_b('玩家当前是否在瞄准', 'Whether the player is aiming'))
  }
}
Blockly.Blocks['check_crawl'] = {
  init() {
    this.appendDummyInput().appendField(_b('🧎 匍匐中?', '🧎 Is Crawling?'))
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
    this.setTooltip(_b('玩家当前是否正在匍匐', 'Whether the player is crawling'))
  }
}
Blockly.Blocks['check_crouching'] = {
  init() {
    this.appendDummyInput().appendField(_b('🦵 蹲伏中?', '🦵 Is Crouching?'))
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
    this.setTooltip(_b('玩家是否蹲伏', 'Whether the player is crouching'))
  }
}
Blockly.Blocks['check_jumping'] = {
  init() {
    this.appendDummyInput().appendField(_b('⬆️ 跳跃中?', '⬆️ Is Jumping?'))
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
    this.setTooltip(_b('玩家是否按下跳跃键', 'Whether the player is pressing jump'))
  }
}
Blockly.Blocks['check_reload_state'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔄 换弹状态', '🔄 Reload State'))
      .appendField(new Blockly.FieldDropdown(OPERATOR_OPTIONS), 'OP')
      .appendField(new Blockly.FieldDropdown(RELOAD_STATE_OPTIONS), 'STATE')
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
    this.setTooltip(_b('检查当前换弹状态', 'Check current reload state'))
  }
}
Blockly.Blocks['check_fire_mode'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔫 开火模式', '🔫 Fire Mode'))
      .appendField(new Blockly.FieldDropdown(OPERATOR_OPTIONS), 'OP')
      .appendField(new Blockly.FieldDropdown(FIRE_MODE_OPTIONS), 'MODE')
    this.setOutput(true, 'Boolean')
    this.setColour('#BA55D3')
    this.setTooltip(_b('检查当前开火模式', 'Check current fire mode'))
  }
}

// ─── Action Blocks ───
Blockly.Blocks['pop_shell'] = {
  init() {
    this.appendDummyInput().appendField(_b('💥 抛壳', '💥 Pop Shell'))
    this.appendValueInput('INDEX').setCheck('Number').appendField(_b('位置', 'Index'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FF8C00')
  }
}
Blockly.Blocks['trigger_event'] = {
  init() {
    this.appendDummyInput().appendField(_b('⚡ 触发事件', '⚡ Trigger'))
      .appendField(new Blockly.FieldTextInput('INPUT_RELOAD'), 'EVENT')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FF8C00')
  }
}
Blockly.Blocks['custom_lua'] = {
  init() {
    this.appendDummyInput().appendField(_b('📝 自定义代码', '📝 Custom Lua'))
    this.appendDummyInput().appendField(new Blockly.FieldTextInput('-- code'), 'CODE')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#9C27B0')
  }
}
Blockly.Blocks['hide_crosshair'] = {
  init() {
    this.appendDummyInput().appendField(_b('🎯 隐藏准星', '🎯 Hide Crosshair'))
      .appendField(new Blockly.FieldDropdown(BOOL_OPTIONS), 'HIDE')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FF8C00')
  }
}
Blockly.Blocks['anchor_walk'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔒 锁定行走', '🔒 Anchor Walk'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FF8C00')
  }
}
Blockly.Blocks['play_put_away'] = {
  init() {
    this.appendDummyInput().appendField(_b('📥 播放丢枪', '📥 Play Put Away'))
    this.appendValueInput('TIME').setCheck('Number').appendField(_b('时长', 'Time'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FF8C00')
  }
}
Blockly.Blocks['play_reload'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔄 播放换弹', '🔄 Play Reload'))
      .appendField(new Blockly.FieldDropdown(RELOAD_OPTIONS), 'TYPE')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FF8C00')
  }
}
Blockly.Blocks['play_inspect'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔍 播放检视', '🔍 Play Inspect'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FF8C00')
  }
}
Blockly.Blocks['cycle_melee'] = {
  init() {
    this.appendDummyInput().appendField(_b('⚔️ 循环近战', '⚔️ Cycle Melee'))
    this.appendDummyInput().appendField(_b('前缀', 'Prefix')).appendField(new Blockly.FieldTextInput('melee_bayonet_'), 'PREFIX')
    this.appendDummyInput().appendField(_b('计数器', 'Counter')).appendField(new Blockly.FieldTextInput('bayonet_counter'), 'COUNTER')
    this.appendValueInput('MAX').setCheck('Number').appendField(_b('最大数', 'Max Count'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FF8C00')
  }
}
Blockly.Blocks['track_hold'] = {
  init() {
    this.appendDummyInput().appendField(_b('📌 轨道占位', '📌 Track Hold'))
      .appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FF8C00')
  }
}
Blockly.Blocks['adjust_shoot_interval'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏱️ 调整射击间隔', '⏱️ Adjust Shoot Interval'))
    this.appendValueInput('DELTA').setCheck('Number').appendField(_b('偏移(ms)', 'Delta(ms)'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FF8C00')
    this.setTooltip(_b('调整客户端射击间隔，正数增加负数减少', 'Adjust client shoot interval, positive adds, negative reduces'))
  }
}

// ─── Value Output Blocks ───
Blockly.Blocks['get_ammo_count'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔢 弹药数量', '🔢 Ammo Count'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取弹匣中的备弹数', 'Get ammo count in magazine'))
  }
}
Blockly.Blocks['get_max_ammo_count'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔢 最大弹药数', '🔢 Max Ammo Count'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取弹匣最大备弹数', 'Get max ammo count'))
  }
}
Blockly.Blocks['get_aiming_progress'] = {
  init() {
    this.appendDummyInput().appendField(_b('🎯 瞄准进度', '🎯 Aiming Progress'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取瞄准进度0~1', 'Get aiming progress 0~1'))
  }
}
Blockly.Blocks['get_fire_mode'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔫 开火模式值', '🔫 Fire Mode Value'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取FireMode枚举值', 'Get FireMode ordinal'))
  }
}
Blockly.Blocks['get_reload_state_type'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔄 换弹状态值', '🔄 Reload State Value'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取ReloadState枚举值', 'Get ReloadState ordinal'))
  }
}
Blockly.Blocks['get_shoot_interval'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏱️ 射击间隔', '⏱️ Shoot Interval'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取射击间隔(ms)', 'Get shoot interval in ms'))
  }
}
Blockly.Blocks['get_shoot_cooldown'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏱️ 射击冷却值', '⏱️ Shoot Cooldown Value'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取射击冷却(ms)', 'Get shoot cooldown in ms'))
  }
}
Blockly.Blocks['get_last_shoot_time'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏱️ 上次射击时间', '⏱️ Last Shoot Time'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取上次射击的系统时间戳(ms)，切枪时重置为-1', 'Get last shoot timestamp, resets to -1 on weapon switch'))
  }
}
Blockly.Blocks['get_current_timestamp'] = {
  init() {
    this.appendDummyInput().appendField(_b('🕐 当前时间戳', '🕐 Current Timestamp'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取当前系统时间(ms)', 'Get current system timestamp in ms'))
  }
}
Blockly.Blocks['get_mag_extent_level'] = {
  init() {
    this.appendDummyInput().appendField(_b('📦 扩容等级', '📦 Mag Extent Level'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取扩容等级0~3', 'Get magazine extent level 0~3'))
  }
}
Blockly.Blocks['get_walk_dist'] = {
  init() {
    this.appendDummyInput().appendField(_b('🚶 行走距离', '🚶 Walk Distance'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取与锚点相对的行走距离', 'Get walk distance relative to anchor'))
  }
}
Blockly.Blocks['get_partial_ticks'] = {
  init() {
    this.appendDummyInput().appendField(_b('🕐 插值时间', '🕐 Partial Ticks'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取最后一次更新时的partialTicks', 'Get partial ticks of last update'))
  }
}
Blockly.Blocks['get_put_away_time'] = {
  init() {
    this.appendDummyInput().appendField(_b('📥 收枪时长', '📥 Put Away Time'))
    this.setOutput(true, 'Number'); this.setColour('#9370DB')
    this.setTooltip(_b('获取收起物品动画的建议时长', 'Get suggested put-away animation duration'))
  }
}
Blockly.Blocks['get_state_machine_params'] = {
  init() {
    this.appendDummyInput().appendField(_b('📋 状态机参数', '📋 State Machine Params'))
    this.setOutput(true, 'Table'); this.setColour('#9370DB')
    this.setTooltip(_b('获取display中声明的状态机参数', 'Get state machine params declared in display'))
  }
}
Blockly.Blocks['should_hide_crosshair'] = {
  init() {
    this.appendDummyInput().appendField(_b('🎯 需隐藏准星?', '🎯 Should Hide Crosshair?'))
    this.setOutput(true, 'Boolean'); this.setColour('#9370DB')
    this.setTooltip(_b('查询是否需要隐藏准星', 'Query whether crosshair should be hidden'))
  }
}

// ─── Track System Blocks ───
Blockly.Blocks['track_line'] = {
  init() {
    this.appendDummyInput().appendField(_b('📊 轨道行', '📊 Track Line'))
    this.setOutput(true, 'TrackLine'); this.setColour('#4A90E2')
  }
}
Blockly.Blocks['get_track'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔗 获取轨道', '🔗 Get Track'))
    this.appendDummyInput().appendField(new Blockly.FieldDropdown(TRACK_LINE_OPTIONS), 'LINE')
    this.appendDummyInput().appendField(new Blockly.FieldDropdown(TRACK_OPTIONS), 'TRACK')
    this.setOutput(true, 'Track'); this.setColour('#4A90E2')
  }
}
Blockly.Blocks['find_idle_track'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔍 找空闲轨道', '🔍 Find Idle Track'))
    this.appendDummyInput().appendField(new Blockly.FieldDropdown(TRACK_LINE_OPTIONS), 'LINE')
    this.appendDummyInput().appendField(_b('打断挂起', 'Interrupt')).appendField(new Blockly.FieldDropdown(BOOL_OPTIONS), 'INTERRUPT')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#4A90E2')
    this.setTooltip(_b('寻找空闲轨道，打断挂起=true时可以占用挂起的轨道', 'Find idle track, interrupt=true can take held tracks'))
  }
}
Blockly.Blocks['add_track_line'] = {
  init() {
    this.appendDummyInput().appendField(_b('➕ 添加轨道行', '➕ Add Track Line'))
    this.setOutput(true, 'Number'); this.setColour('#4A90E2')
    this.setTooltip(_b('分配一个新的轨道行，返回下标', 'Allocate a new track line, returns index'))
  }
}
Blockly.Blocks['assign_new_track'] = {
  init() {
    this.appendDummyInput().appendField(_b('➕ 分配轨道', '➕ Assign New Track'))
    this.appendValueInput('INDEX').setCheck('Number').appendField(_b('轨道行', 'Track Line'))
    this.setOutput(true, 'Number'); this.setColour('#4A90E2')
    this.setTooltip(_b('为指定轨道行分配新轨道，返回轨道下标', 'Assign new track to track line, returns track index'))
  }
}
Blockly.Blocks['ensure_track_line_size'] = {
  init() {
    this.appendDummyInput().appendField(_b('📏 确保轨道行数', '📏 Ensure Track Line Size'))
    this.appendValueInput('SIZE').setCheck('Number').appendField(_b('数量', 'Size'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#4A90E2')
    this.setTooltip(_b('确保轨道行的数量', 'Ensure the number of track lines'))
  }
}
Blockly.Blocks['ensure_tracks_amount'] = {
  init() {
    this.appendDummyInput().appendField(_b('📏 确保轨道数', '📏 Ensure Tracks Amount'))
    this.appendValueInput('INDEX').setCheck('Number').appendField(_b('轨道行', 'Track Line'))
    this.appendValueInput('AMOUNT').setCheck('Number').appendField(_b('数量', 'Amount'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#4A90E2')
    this.setTooltip(_b('保证指定轨道行有足够的轨道数量', 'Ensure enough tracks in a track line'))
  }
}
Blockly.Blocks['get_singleton_track'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔗 单例轨道', '🔗 Singleton Track'))
    this.appendValueInput('INDEX').setCheck('Number').appendField(_b('轨道行', 'Track Line'))
    this.setOutput(true, 'Number'); this.setColour('#4A90E2')
    this.setTooltip(_b('获取单轨道行中的轨道，没有则分配', 'Get singleton track from track line, allocates if none'))
  }
}
Blockly.Blocks['get_track_line_size'] = {
  init() {
    this.appendDummyInput().appendField(_b('📊 轨道行数', '📊 Track Line Size'))
    this.setOutput(true, 'Number'); this.setColour('#4A90E2')
    this.setTooltip(_b('获取轨道行的数量', 'Get the number of track lines'))
  }
}

// ─── Logic Blocks ───
Blockly.Blocks['if_node'] = {
  init() {
    this.appendValueInput('COND').setCheck('Boolean').appendField(_b('❓ 如果', '❓ If'))
    this.appendStatementInput('DO').setCheck('action_stmt').appendField(_b('成立', 'True'))
    this.appendStatementInput('ELSE').setCheck('action_stmt').appendField(_b('不成立', 'False'))
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FFB347')
  }
}
Blockly.Blocks['return_state'] = {
  init() {
    this.appendDummyInput().appendField(_b('↩️ 返回状态', '↩️ Return State'))
      .appendField(new Blockly.FieldTextInput('idle'), 'STATE')
    this.setPreviousStatement(true, 'action_stmt'); this.setNextStatement(true, 'action_stmt')
    this.setColour('#FFB347')
  }
}

// ─── Animation Mode Blocks ───
Blockly.Blocks['loop_mode'] = {
  init() {
    this.appendDummyInput().appendField(_b('🔁 循环模式', '🔁 Loop Mode'))
    this.setOutput(true, 'String'); this.setColour('#98FB98')
  }
}
Blockly.Blocks['play_once_stop'] = {
  init() {
    this.appendDummyInput().appendField(_b('▶️ 播放一次停止', '▶️ Play Once Stop'))
    this.setOutput(true, 'String'); this.setColour('#98FB98')
  }
}
Blockly.Blocks['play_once_hold'] = {
  init() {
    this.appendDummyInput().appendField(_b('⏸️ 播放一次保持', '⏸️ Play Once Hold'))
    this.setOutput(true, 'String'); this.setColour('#98FB98')
  }
}

// ─── Math Blocks ───
const mathOps = [['add', '+', '+'], ['sub', '-', '-'], ['mul', '×', '×'], ['div', '÷', '÷']]
mathOps.forEach(([id, zh, en]) => {
  Blockly.Blocks[`math_${id}`] = {
    init() {
      this.appendValueInput('A').setCheck('Number')
      this.appendDummyInput().appendField(` ${zh} `)
      this.appendValueInput('B').setCheck('Number')
      this.setInputsInline(true)
      this.setOutput(true, 'Number')
      this.setColour('#DDA0DD')
    }
  }
})
