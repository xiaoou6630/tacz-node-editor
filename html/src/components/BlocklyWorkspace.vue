<template>
  <div ref="blocklyDiv" class="blockly-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as Blockly from 'blockly'
import '../blocks'
import { taczTheme } from '../theme'
import { _b } from '../locales'
// Blockly 中文语言包（右键菜单等）
import * as zhHans from 'blockly/msg/zh-hans'

// Event types list (shared between toolbox and codegen)
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

const emit = defineEmits<{ 'code-change': [code: string] }>()

const blocklyDiv = ref<HTMLDivElement | null>(null)
let workspace: Blockly.WorkspaceSvg | null = null

// ─── Build Toolbox ───
function buildToolbox(): Blockly.utils.toolbox.ToolboxDefinition {
  return {
    kind: 'categoryToolbox',
    contents: [
      {
        kind: 'category',
        name: _b('📌 状态定义', '📌 State Define'),
        colour: '#FF69B4',
        contents: [
          { kind: 'block', type: 'entry' },
          { kind: 'block', type: 'update_node' },
          { kind: 'block', type: 'exit' },
          { kind: 'block', type: 'transition' },
          { kind: 'block', type: 'state_define' },
        ],
      },
      {
        kind: 'category',
        name: _b('🎯 输入事件', '🎯 Input Events'),
        colour: '#87CEEB',
        contents: [
          { kind: 'block', type: 'event_draw' },
          { kind: 'block', type: 'event_shoot' },
          { kind: 'block', type: 'event_reload' },
          { kind: 'block', type: 'event_inspect' },
          { kind: 'block', type: 'event_bolt' },
          { kind: 'block', type: 'event_aim' },
          { kind: 'block', type: 'event_run' },
          { kind: 'block', type: 'event_walk' },
          { kind: 'block', type: 'event_sprint' },
          { kind: 'block', type: 'event_slide' },
          { kind: 'block', type: 'event_put_away' },
          { kind: 'block', type: 'event_idle_input' },
          { kind: 'block', type: 'event_fire_select' },
          { kind: 'block', type: 'event_over_heat' },
          { kind: 'block', type: 'event_cooling' },
          { kind: 'block', type: 'event_spin' },
          { kind: 'block', type: 'event_bayonet_muzzle' },
          { kind: 'block', type: 'event_bayonet_stock' },
          { kind: 'block', type: 'event_bayonet_push' },
          { kind: 'block', type: 'event_bolt_caught' },
          { kind: 'block', type: 'event_bolt_normal' },
          { kind: 'block', type: 'event_inspect_retreat' },
          { kind: 'block', type: 'event_aim_retreat' },
        ],
      },
      {
        kind: 'category',
        name: _b('🎬 动画控制', '🎬 Animation'),
        colour: '#32CD32',
        contents: [
          { kind: 'block', type: 'run_animation' },
          { kind: 'block', type: 'stop_animation' },
          { kind: 'block', type: 'loop_animation' },
          { kind: 'block', type: 'set_progress' },
          { kind: 'block', type: 'adjust_progress' },
          { kind: 'block', type: 'play_blended' },
        ],
      },
      {
        kind: 'category',
        name: _b('🔍 条件检查', '🔍 Conditions'),
        colour: '#BA55D3',
        contents: [
          { kind: 'block', type: 'check_ammo' },
          { kind: 'block', type: 'check_ammo_count' },
          { kind: 'block', type: 'check_heat' },
          { kind: 'block', type: 'check_aiming' },
          { kind: 'block', type: 'check_ground' },
          { kind: 'block', type: 'check_stopped' },
          { kind: 'block', type: 'check_cooldown' },
          { kind: 'block', type: 'check_track_idle' },
          { kind: 'block', type: 'check_walk_dir' },
          { kind: 'block', type: 'check_running' },
        ],
      },
      {
        kind: 'category',
        name: _b('⚡ 动作操作', '⚡ Actions'),
        colour: '#FF8C00',
        contents: [
          { kind: 'block', type: 'pop_shell' },
          { kind: 'block', type: 'trigger_event' },
          { kind: 'block', type: 'custom_lua' },
          { kind: 'block', type: 'hide_crosshair' },
          { kind: 'block', type: 'anchor_walk' },
          { kind: 'block', type: 'play_put_away' },
          { kind: 'block', type: 'play_reload' },
          { kind: 'block', type: 'play_inspect' },
          { kind: 'block', type: 'cycle_melee' },
          { kind: 'block', type: 'track_hold' },
        ],
      },
      {
        kind: 'category',
        name: _b('🔗 轨道系统', '🔗 Tracks'),
        colour: '#4A90E2',
        contents: [
          { kind: 'block', type: 'track_line' },
          { kind: 'block', type: 'get_track' },
          { kind: 'block', type: 'find_idle_track' },
        ],
      },
      {
        kind: 'category',
        name: _b('📐 逻辑控制', '📐 Logic Ctrl'),
        colour: '#FFB347',
        contents: [
          { kind: 'block', type: 'if_node' },
          { kind: 'block', type: 'return_state' },
        ],
      },
      {
        kind: 'category',
        name: _b('🎞️ 动画模式', '🎞️ Anim Mode'),
        colour: '#98FB98',
        contents: [
          { kind: 'block', type: 'loop_mode' },
          { kind: 'block', type: 'play_once_stop' },
          { kind: 'block', type: 'play_once_hold' },
        ],
      },
      {
        kind: 'category',
        name: _b('🔢 数学运算', '🔢 Math'),
        colour: '#DDA0DD',
        contents: [
          { kind: 'block', type: 'math_add' },
          { kind: 'block', type: 'math_sub' },
          { kind: 'block', type: 'math_mul' },
          { kind: 'block', type: 'math_div' },
        ],
      },
      {
        kind: 'category',
        name: _b('🧠 逻辑运算', '🧠 Logic'),
        colour: '#5CB85C',
        contents: [
          { kind: 'block', type: 'logic_boolean' },
          { kind: 'block', type: 'logic_compare' },
          { kind: 'block', type: 'logic_operation' },
          { kind: 'block', type: 'logic_negate' },
        ],
      },
      {
        kind: 'category',
        name: _b('🔢 数值', '🔢 Number'),
        colour: '#4B70DD',
        contents: [
          { kind: 'block', type: 'math_number' },
        ],
      },
      {
        kind: 'category',
        name: _b('📝 文本', '📝 Text'),
        colour: '#4C9A8F',
        contents: [
          { kind: 'block', type: 'text' },
        ],
      },
    ],
  }
}

// ─── Lua Code Generator ───
const luaGen: Record<string, (block: Blockly.Block, indent?: number) => string> = {}

// Helper: generate code for connected blocks (next chain)
function genNext(block: Blockly.Block | null, indent = 1): string {
  if (!block) return ''
  const func = luaGen[block.type]
  if (!func) return genNext(block.getNextBlock(), indent)
  const lines: string[] = []
  let current: Blockly.Block | null = block
  while (current) {
    const fn = luaGen[current.type]
    if (fn) {
      lines.push(fn(current, indent))
    }
    current = current.getNextBlock()
  }
  return lines.join('\n')
}

// Helper: get value from a connected input block
function genValue(block: Blockly.Block, inputName: string): string {
  const target = block.getInputTargetBlock(inputName)
  if (!target) return 'nil'
  const func = luaGen[target.type]
  if (!func) return 'nil'
  return func(target)
}

// Helper: get statements from a statement input
function genStatements(block: Blockly.Block, inputName: string, indent = 1): string {
  const target = block.getInputTargetBlock(inputName)
  if (!target) return ''
  return genNext(target, indent)
}

// ─── Register Lua generators for custom blocks ───

// Event ID → TACZ constant name mapping (from GunAnimationConstant.java)
const eventToConst: Record<string, string> = {
  draw: 'INPUT_DRAW', shoot: 'INPUT_SHOOT', reload: 'INPUT_RELOAD',
  inspect: 'INPUT_INSPECT', bolt: 'INPUT_BOLT',
  run: 'INPUT_RUN', walk: 'INPUT_WALK', idle_input: 'INPUT_IDLE',
  put_away: 'INPUT_PUT_AWAY', fire_select: 'INPUT_FIRE_SELECT',
  bayonet_muzzle: 'INPUT_BAYONET_MUZZLE', bayonet_stock: 'INPUT_BAYONET_STOCK',
  bayonet_push: 'INPUT_BAYONET_PUSH',
  bolt_caught: 'INPUT_BOLT_CAUGHT', bolt_normal: 'INPUT_BOLT_NORMAL',
  over_heat: 'INPUT_OVER_HEAT', cooling: 'INPUT_COOLING_HEAT',
  inspect_retreat: 'INPUT_INSPECT_RETREAT', aim_retreat: 'INPUT_AIM_RETREAT',
  spin: 'INPUT_SPIN', sprint: 'INPUT_SPRINT', slide: 'INPUT_SLIDE',
}

// ─── Event Hat Blocks: generate transition code ───
eventTypes.forEach(([id]) => {
  luaGen[`event_${id}`] = (block, indent = 0) => {
    const constName = eventToConst[id] || `INPUT_${id.toUpperCase()}`
    const body = genNext(block.getNextBlock(), indent + 1)
    let code = `${'  '.repeat(indent)}if input == ${constName} then\n`
    if (body) code += body + '\n'
    code += `${'  '.repeat(indent)}end`
    return code
  }
})

// State Definition
luaGen['state_define'] = () => '-- state_define placeholder'

luaGen['entry'] = (block, indent = 0) => {
  const state = block.getFieldValue('STATE') || 'idle'
  const body = genNext(block.getNextBlock(), indent + 1)
  return `${'  '.repeat(indent)}function M:onStateEntry(${state})\n${body}${body ? '\n' : ''}${'  '.repeat(indent)}end`
}

luaGen['update_node'] = (block, indent = 0) => {
  const state = block.getFieldValue('STATE') || 'idle'
  const body = genNext(block.getNextBlock(), indent + 1)
  return `${'  '.repeat(indent)}function M:onStateUpdate(${state})\n${body}${body ? '\n' : ''}${'  '.repeat(indent)}end`
}

luaGen['exit'] = (block, indent = 0) => {
  const state = block.getFieldValue('STATE') || 'idle'
  const body = genNext(block.getNextBlock(), indent + 1)
  return `${'  '.repeat(indent)}function M:onStateExit(${state})\n${body}${body ? '\n' : ''}${'  '.repeat(indent)}end`
}

luaGen['transition'] = (block, indent = 0) => {
  const from = block.getFieldValue('FROM') || 'idle'
  const to = block.getFieldValue('TO') || 'idle'
  const cond = genValue(block, 'COND') || 'true'
  return `${'  '.repeat(indent)}-- transition: ${from} → ${to} if ${cond}`
}

// Animation Blocks (correct TACZ API)
luaGen['run_animation'] = (block, indent = 0) => {
  const anim = block.getFieldValue('ANIM') || 'idle'
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  const blend = block.getFieldValue('BLEND') || 'false'
  const mode = block.getFieldValue('MODE') || 'PLAY_ONCE_STOP'
  const blendTime = genValue(block, 'BLEND_TIME') || '0.2'
  return `${'  '.repeat(indent)}context:runAnimation("${anim}", ${track}, ${blend}, ${mode}, ${blendTime})`
}

luaGen['stop_animation'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `${'  '.repeat(indent)}context:stopAnimation(${track})`
}

luaGen['loop_animation'] = (block, indent = 0) => {
  const anim = block.getFieldValue('ANIM') || 'idle'
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `${'  '.repeat(indent)}context:runAnimation("${anim}", ${track}, false, LOOP, 0)`
}

luaGen['set_progress'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  const progress = genValue(block, 'PROGRESS') || '0'
  const hold = block.getFieldValue('HOLD') || 'false'
  return `${'  '.repeat(indent)}context:setAnimationProgress(${track}, ${progress}, ${hold})`
}

luaGen['adjust_progress'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  const delta = genValue(block, 'DELTA') || '0'
  const hold = block.getFieldValue('HOLD') || 'false'
  return `${'  '.repeat(indent)}context:adjustAnimationProgress(${track}, ${delta}, ${hold})`
}

luaGen['play_blended'] = (block, indent = 0) => {
  const anim = block.getFieldValue('ANIM') || 'shoot'
  const line = block.getFieldValue('LINE') || 'STATIC_TRACK_LINE'
  const blend = block.getFieldValue('BLEND') || 'false'
  const mode = block.getFieldValue('MODE') || 'PLAY_ONCE_STOP'
  return `${'  '.repeat(indent)}context:runAnimation("${anim}", context:findIdleTrack(${line}, true), ${blend}, ${mode}, 0)`
}

// Condition Check Blocks (correct TACZ API)
luaGen['check_ammo'] = () => 'context:hasAmmo()'
luaGen['check_ammo_count'] = (block) => {
  const op = block.getFieldValue('OP') || '>='
  const value = genValue(block, 'VALUE') || '0'
  return `context:getAmmoCount() ${op} ${value}`
}
luaGen['check_heat'] = () => 'context:isOverHeated()'
luaGen['check_aiming'] = (block) => {
  const value = genValue(block, 'PROGRESS') || '0'
  return `context:getAimingProgress() >= ${value}`
}
luaGen['check_ground'] = () => 'context:isOnGround()'
luaGen['check_stopped'] = (block) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `context:isStopped(${track})`
}
luaGen['check_cooldown'] = (block) => {
  const op = block.getFieldValue('OP') || '>='
  const value = genValue(block, 'VALUE') || '0'
  return `context:getShootCooldown() ${op} ${value}`
}
luaGen['check_track_idle'] = (block) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `context:isStopped(${track})`
}
luaGen['check_walk_dir'] = (block) => {
  const dir = block.getFieldValue('DIR') || 'forward'
  return `context:getWalkDirection() == "${dir}"`
}
luaGen['check_running'] = () => 'context:isRunning()'

// Action Blocks (correct TACZ API)
luaGen['pop_shell'] = (block, indent = 0) => {
  const index = genValue(block, 'INDEX') || '1'
  return `${'  '.repeat(indent)}context:popShell(${index})`
}
luaGen['trigger_event'] = (block, indent = 0) => {
  const event = block.getFieldValue('EVENT') || 'INPUT_RELOAD'
  return `${'  '.repeat(indent)}context:trigger("${event}")`
}
luaGen['custom_lua'] = (block, indent = 0) => {
  const code = block.getFieldValue('CODE') || '-- code'
  return `${'  '.repeat(indent)}${code}`
}
luaGen['hide_crosshair'] = (block, indent = 0) => {
  const hide = block.getFieldValue('HIDE') || 'false'
  return `${'  '.repeat(indent)}context:setShouldHideCrossHair(${hide})`
}
luaGen['anchor_walk'] = (_block, indent = 0) => {
  return `${'  '.repeat(indent)}-- anchorWalk (handled by context)`
}
luaGen['play_put_away'] = (block, indent = 0) => {
  const time = genValue(block, 'TIME') || '0'
  return `${'  '.repeat(indent)}-- put_away_time: ${time}`
}
luaGen['play_reload'] = (block, indent = 0) => {
  const type = block.getFieldValue('TYPE') || 'tactical'
  return `${'  '.repeat(indent)}-- reload type: ${type}`
}
luaGen['play_inspect'] = (_block, indent = 0) => {
  return `${'  '.repeat(indent)}-- play inspect animation`
}
luaGen['cycle_melee'] = (block, indent = 0) => {
  const prefix = block.getFieldValue('PREFIX') || 'melee_'
  const max = genValue(block, 'MAX') || '3'
  return `${'  '.repeat(indent)}-- cycle melee: ${prefix}1..${max}`
}
luaGen['track_hold'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `${'  '.repeat(indent)}context:holdAnimation(${track})`
}

// Track System Blocks (correct TACZ API)
luaGen['track_line'] = () => '-- track_line'
luaGen['get_track'] = (block) => {
  const line = block.getFieldValue('LINE') || 'STATIC_TRACK_LINE'
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `-- get_track: ${line}, ${track}`
}
luaGen['find_idle_track'] = (block, indent = 0) => {
  const line = block.getFieldValue('LINE') || 'STATIC_TRACK_LINE'
  const blend = block.getFieldValue('BLEND') || 'false'
  return `${'  '.repeat(indent)}context:findIdleTrack(${line}, ${blend})`
}

// Logic Blocks
luaGen['if_node'] = (block, indent = 0) => {
  const cond = genValue(block, 'COND') || 'true'
  const doBlock = genStatements(block, 'DO', indent + 1)
  const elseBlock = genStatements(block, 'ELSE', indent + 1)
  let code = `${'  '.repeat(indent)}if ${cond} then\n${doBlock}${doBlock ? '\n' : ''}${'  '.repeat(indent)}end`
  if (elseBlock) {
    code = `${'  '.repeat(indent)}if ${cond} then\n${doBlock}${doBlock ? '\n' : ''}${'  '.repeat(indent)}else\n${elseBlock}\n${'  '.repeat(indent)}end`
  }
  return code
}
luaGen['return_state'] = (block, indent = 0) => {
  const state = block.getFieldValue('STATE') || 'idle'
  return `${'  '.repeat(indent)}return "${state}"`
}

// Animation Mode Blocks (outputs)
luaGen['loop_mode'] = () => '"LOOP"'
luaGen['play_once_stop'] = () => '"PLAY_ONCE_STOP"'
luaGen['play_once_hold'] = () => '"PLAY_ONCE_HOLD"'

// Math Blocks
luaGen['math_add'] = (block) => {
  const a = genValue(block, 'A') || '0'
  const b = genValue(block, 'B') || '0'
  return `(${a} + ${b})`
}
luaGen['math_sub'] = (block) => {
  const a = genValue(block, 'A') || '0'
  const b = genValue(block, 'B') || '0'
  return `(${a} - ${b})`
}
luaGen['math_mul'] = (block) => {
  const a = genValue(block, 'A') || '0'
  const b = genValue(block, 'B') || '0'
  return `(${a} * ${b})`
}
luaGen['math_div'] = (block) => {
  const a = genValue(block, 'A') || '0'
  const b = genValue(block, 'B') || '0'
  return `(${a} / ${b})`
}

// Built-in Standard Blocks (Blockly default generators for Lua-like output)
luaGen['math_number'] = (block) => {
  return String(block.getFieldValue('NUM') || '0')
}
luaGen['text'] = (block) => {
  return `"${(block.getFieldValue('TEXT') || '').replace(/"/g, '\\"')}"`
}
luaGen['logic_boolean'] = (block) => {
  return block.getFieldValue('BOOL') === 'TRUE' ? 'true' : 'false'
}
luaGen['logic_compare'] = (block) => {
  const a = genValue(block, 'A') || 'nil'
  const b = genValue(block, 'B') || 'nil'
  const op = block.getFieldValue('OP') || 'EQ'
  const opMap: Record<string, string> = { EQ: '==', NEQ: '~=', LT: '<', GT: '>', LTE: '<=', GTE: '>=' }
  return `(${a} ${opMap[op] || '=='} ${b})`
}
luaGen['logic_operation'] = (block) => {
  const a = genValue(block, 'A') || 'false'
  const b = genValue(block, 'B') || 'false'
  const op = block.getFieldValue('OP') || 'AND'
  return `(${a} ${op === 'AND' ? 'and' : 'or'} ${b})`
}
luaGen['logic_negate'] = (block) => {
  const a = genValue(block, 'BOOL') || 'false'
  return `(not ${a})`
}

// ─── Generate Code from Workspace ───
function generateCode(): string {
  if (!workspace) return ''
  const topBlocks = workspace.getTopBlocks(true)

  // Collect event hat blocks and other blocks
  const eventBlocks: Blockly.Block[] = []
  const stateBlocks: Blockly.Block[] = []
  const initBlocks: Blockly.Block[] = []
  const exitBlocks: Blockly.Block[] = []

  for (const block of topBlocks) {
    const type = block.type
    if (type.startsWith('event_')) {
      eventBlocks.push(block)
    } else if (type === 'entry' || type === 'update_node' || type === 'exit') {
      stateBlocks.push(block)
    } else if (type === 'transition') {
      stateBlocks.push(block)
    } else if (luaGen[type]) {
      // Other blocks at top level
    }
  }

  const lines: string[] = []
  lines.push('local M = {}')
  lines.push('')

  // Initialize function
  lines.push('function M:initialize(context)')
  for (const b of initBlocks) {
    const code = luaGen[b.type]?.(b, 1)
    if (code) lines.push(code)
  }
  lines.push('end')
  lines.push('')

  // Exit function
  lines.push('function M:exit(context)')
  for (const b of exitBlocks) {
    const code = luaGen[b.type]?.(b, 1)
    if (code) lines.push(code)
  }
  lines.push('end')
  lines.push('')

  // States function
  lines.push('function M:states()')
  lines.push('  return {')

  // Generate a single state that contains all entry/update/exit/transition logic
  lines.push('    {')
  lines.push('      entry = function(context)')
  // Entry blocks
  for (const b of stateBlocks) {
    if (b.type === 'entry') {
      const code = luaGen[b.type]?.(b, 2)
      if (code) lines.push(code)
    }
  }
  lines.push('      end,')

  lines.push('      update = function(context)')
  for (const b of stateBlocks) {
    if (b.type === 'update_node') {
      const code = luaGen[b.type]?.(b, 2)
      if (code) lines.push(code)
    }
  }
  lines.push('      end,')

  lines.push('      exit = function(context)')
  for (const b of stateBlocks) {
    if (b.type === 'exit') {
      const code = luaGen[b.type]?.(b, 2)
      if (code) lines.push(code)
    }
  }
  lines.push('      end,')

  // Transition function with all event handlers
  lines.push('      transition = function(context, input)')
  for (const b of eventBlocks) {
    lines.push('        -- event handler')
    const code = luaGen[b.type]?.(b, 2)
    if (code) lines.push(code)
  }
  for (const b of stateBlocks) {
    if (b.type === 'transition') {
      const code = luaGen[b.type]?.(b, 2)
      if (code) lines.push(code)
    }
  }
  lines.push('        return nil')
  lines.push('      end,')
  lines.push('    }')
  lines.push('  }')
  lines.push('end')
  lines.push('')

  lines.push('return M')

  return lines.join('\n')
}

// ─── Workspace Change Handler ───
function handleWorkspaceChange() {
  const code = generateCode()
  emit('code-change', code)
}

// ─── Initialize Blockly ───
onMounted(() => {
  if (!blocklyDiv.value) return

  // 设置 Blockly 中文界面（右键菜单等）
  Blockly.setLocale(zhHans as unknown as { [key: string]: string })

  workspace = Blockly.inject(blocklyDiv.value, {
    toolbox: buildToolbox(),
    theme: taczTheme,
    grid: {
      spacing: 20,
      length: 3,
      colour: '#313244',
      snap: true,
    },
    zoom: {
      controls: true,
      wheel: true,
      startScale: 0.9,
      maxScale: 3,
      minScale: 0.3,
      scaleSpeed: 1.1,
    },
    trashcan: true,
    renderer: 'zelos',
    media: '/media/',
  })

  // Expose workspace for save/load
  ;(window as any).__tacz_workspace = workspace

  // Listen for workspace changes
  workspace.addChangeListener(handleWorkspaceChange)

  // Initial code generation
  handleWorkspaceChange()
})

onBeforeUnmount(() => {
  if (workspace) {
    ;(window as any).__tacz_workspace = undefined
    workspace.dispose()
    workspace = null
  }
})
</script>

<style scoped>
.blockly-container {
  width: 100%;
  height: 100%;
}
</style>
