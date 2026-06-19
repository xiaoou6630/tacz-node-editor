/**
 * TACZ 积木扩展注册系统
 *
 * 扩展格式：
 * {
 *   id: string,           // 唯一标识
 *   name: string,         // 显示名称
 *   nameEn: string,       // 英文名称
 *   colour: string,       // 积木栏颜色
 *   icon: string,         // 图标 emoji
 *   official: boolean,    // 是否官方扩展
 *   blocks: BlockDef[],   // 积木定义列表
 *   generators: Record<string, GenFn>,  // 代码生成器
 * }
 */

import * as Blockly from 'blockly'
import { _b } from './locales'

export interface BlockFieldDef {
  name: string
  type: 'text' | 'dropdown' | 'number' | 'input'
  label?: string
  options?: [string, string][]  // for dropdown
  default?: string
  check?: string  // output type check
}

export interface BlockDef {
  type: string
  message0: string
  args0?: any[]  // Blockly args0 format
  previousStatement?: string | boolean
  nextStatement?: string | boolean
  output?: string | boolean
  colour?: string
  tooltip?: string
}

export type GenFn = (block: Blockly.Block, indent?: number) => string

export interface Extension {
  id: string
  name: string
  nameEn: string
  colour: string
  icon: string
  official: boolean
  blocks: BlockDef[]
  generators: Record<string, GenFn>
}

// ─── Registry ───
const registeredExtensions = new Map<string, Extension>()
const activeExtensions = new Set<string>()

export function registerExtension(ext: Extension) {
  if (registeredExtensions.has(ext.id)) {
    console.warn(`Extension "${ext.id}" already registered, overwriting`)
    unregisterExtension(ext.id)
  }
  registeredExtensions.set(ext.id, ext)
  // Register all blocks with Blockly
  for (const blockDef of ext.blocks) {
    Blockly.Blocks[blockDef.type] = {
      init() {
        this.jsonInit(blockDef)
      }
    }
  }
}

export function unregisterExtension(id: string) {
  const ext = registeredExtensions.get(id)
  if (!ext) return
  // Remove blocks from Blockly
  for (const blockDef of ext.blocks) {
    delete Blockly.Blocks[blockDef.type]
  }
  registeredExtensions.delete(id)
  activeExtensions.delete(id)
}

export function getRegisteredExtensions(): Extension[] {
  return Array.from(registeredExtensions.values())
}

export function activateExtension(id: string): boolean {
  const ext = registeredExtensions.get(id)
  if (!ext) return false
  activeExtensions.add(id)
  return true
}

export function deactivateExtension(id: string) {
  activeExtensions.delete(id)
}

export function isActive(id: string): boolean {
  return activeExtensions.has(id)
}

export function getActiveExtensions(): Extension[] {
  return Array.from(activeExtensions)
    .map(id => registeredExtensions.get(id))
    .filter((e): e is Extension => !!e)
}

export function getExtensionGenerators(): Record<string, GenFn> {
  const gens: Record<string, GenFn> = {}
  for (const id of activeExtensions) {
    const ext = registeredExtensions.get(id)
    if (ext) {
      Object.assign(gens, ext.generators)
    }
  }
  return gens
}

export function getExtensionToolboxCategories(): Blockly.utils.toolbox.ToolboxItemInfo[] {
  const categories: Blockly.utils.toolbox.ToolboxItemInfo[] = []
  for (const id of activeExtensions) {
    const ext = registeredExtensions.get(id)
    if (!ext) continue
    categories.push({
      kind: 'category',
      name: `${ext.icon} ${_b(ext.name, ext.nameEn)}`,
      colour: ext.colour,
      contents: ext.blocks.map(b => ({
        kind: 'block' as const,
        type: b.type,
      })),
    })
  }
  return categories
}

// ─── Official Extensions ───

// 1. NBT 数据访问扩展
registerExtension({
  id: 'nbt_accessor',
  name: 'NBT 数据',
  nameEn: 'NBT Data',
  colour: '#E06C75',
  icon: '💾',
  official: true,
  blocks: [
    {
      type: 'nbt_get_accessor',
      message0: '💾 获取NBT访问器',
      output: 'NbtAccessor',
      colour: '#E06C75',
      tooltip: _b('获取当前枪械的NBT数据访问器', 'Get NBT accessor for current gun'),
    },
    {
      type: 'nbt_get_int',
      message0: '💾 NBT整数 %1 %2',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
      ],
      output: 'Number',
      colour: '#E06C75',
      tooltip: _b('读取NBT整数值', 'Read NBT integer value'),
    },
    {
      type: 'nbt_get_double',
      message0: '💾 NBT双精度 %1 %2',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
      ],
      output: 'Number',
      colour: '#E06C75',
      tooltip: _b('读取NBT双精度浮点值', 'Read NBT double value'),
    },
    {
      type: 'nbt_get_float',
      message0: '💾 NBT浮点 %1 %2',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
      ],
      output: 'Number',
      colour: '#E06C75',
      tooltip: _b('读取NBT单精度浮点值', 'Read NBT float value'),
    },
    {
      type: 'nbt_get_long',
      message0: '💾 NBT长整数 %1 %2',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
      ],
      output: 'Number',
      colour: '#E06C75',
      tooltip: _b('读取NBT长整数值', 'Read NBT long value'),
    },
    {
      type: 'nbt_get_string',
      message0: '💾 NBT字符串 %1 %2',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
      ],
      output: 'String',
      colour: '#E06C75',
      tooltip: _b('读取NBT字符串值', 'Read NBT string value'),
    },
    {
      type: 'nbt_get_boolean',
      message0: '💾 NBT布尔 %1 %2',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
      ],
      output: 'Boolean',
      colour: '#E06C75',
      tooltip: _b('读取NBT布尔值（注意：实际API为getBoolean(nbt, key)）', 'Read NBT boolean value'),
    },
    {
      type: 'nbt_contains',
      message0: '💾 NBT包含 %1 %2',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
      ],
      output: 'Boolean',
      colour: '#E06C75',
      tooltip: _b('检查NBT是否包含指定key', 'Check if NBT contains key'),
    },
    {
      type: 'nbt_get_compound',
      message0: '💾 NBT子标签 %1 %2',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
      ],
      output: 'NbtAccessor',
      colour: '#E06C75',
      tooltip: _b('获取NBT子CompoundTag', 'Get NBT sub CompoundTag'),
    },
    {
      type: 'nbt_new_compound',
      message0: '💾 新建CompoundTag',
      output: 'NbtAccessor',
      colour: '#E06C75',
      tooltip: _b('创建一个新的空CompoundTag', 'Create a new empty CompoundTag'),
    },
    {
      type: 'nbt_put_int',
      message0: '💾 写入NBT整数 %1 %2 %3',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
        { type: 'input_value', name: 'VALUE', check: 'Number' },
      ],
      previousStatement: 'action_stmt',
      nextStatement: 'action_stmt',
      colour: '#E06C75',
      tooltip: _b('向NBT写入整数值', 'Write int value to NBT'),
    },
    {
      type: 'nbt_put_string',
      message0: '💾 写入NBT字符串 %1 %2 %3',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
        { type: 'input_value', name: 'VALUE', check: 'String' },
      ],
      previousStatement: 'action_stmt',
      nextStatement: 'action_stmt',
      colour: '#E06C75',
      tooltip: _b('向NBT写入字符串值', 'Write string value to NBT'),
    },
    {
      type: 'nbt_put_boolean',
      message0: '💾 写入NBT布尔 %1 %2 %3',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
        { type: 'input_value', name: 'VALUE', check: 'Boolean' },
      ],
      previousStatement: 'action_stmt',
      nextStatement: 'action_stmt',
      colour: '#E06C75',
      tooltip: _b('向NBT写入布尔值', 'Write boolean value to NBT'),
    },
    {
      type: 'nbt_put_compound',
      message0: '💾 写入NBT子标签 %1 %2 %3',
      args0: [
        { type: 'input_value', name: 'ACCESSOR', check: 'NbtAccessor' },
        { type: 'field_input', name: 'KEY', text: 'key' },
        { type: 'input_value', name: 'VALUE', check: 'NbtAccessor' },
      ],
      previousStatement: 'action_stmt',
      nextStatement: 'action_stmt',
      colour: '#E06C75',
      tooltip: _b('向NBT写入子CompoundTag', 'Write sub CompoundTag to NBT'),
    },
  ],
  generators: {
    nbt_get_accessor: () => 'context:getNbtAccessor()',
    nbt_get_int: (block) => {
      const key = block.getFieldValue('KEY') || 'key'
      return `(context:getNbtAccessor()):getInt("${key}")`
    },
    nbt_get_double: (block) => {
      const key = block.getFieldValue('KEY') || 'key'
      return `(context:getNbtAccessor()):getDouble("${key}")`
    },
    nbt_get_float: (block) => {
      const key = block.getFieldValue('KEY') || 'key'
      return `(context:getNbtAccessor()):getFloat("${key}")`
    },
    nbt_get_long: (block) => {
      const key = block.getFieldValue('KEY') || 'key'
      return `(context:getNbtAccessor()):getLong("${key}")`
    },
    nbt_get_string: (block) => {
      const key = block.getFieldValue('KEY') || 'key'
      return `(context:getNbtAccessor()):getString("${key}")`
    },
    // Note: TACZ API getBoolean(nbt, key) requires nbt as first param
    nbt_get_boolean: (block) => {
      const key = block.getFieldValue('KEY') || 'key'
      return `(context:getNbtAccessor()):getBoolean(context:getNbtAccessor(), "${key}")`
    },
    nbt_contains: (block) => {
      const key = block.getFieldValue('KEY') || 'key'
      return `(context:getNbtAccessor()):contains("${key}")`
    },
    nbt_get_compound: (block) => {
      const key = block.getFieldValue('KEY') || 'key'
      return `(context:getNbtAccessor()):getCompound("${key}")`
    },
    nbt_new_compound: () => '(context:getNbtAccessor()):newCompoundTag()',
    nbt_put_int: (block, indent = 0) => {
      const key = block.getFieldValue('KEY') || 'key'
      const val = '(0)'
      return `${'  '.repeat(indent)}(context:getNbtAccessor()):putInt("${key}", ${val})`
    },
    nbt_put_string: (block, indent = 0) => {
      const key = block.getFieldValue('KEY') || 'key'
      const val = '""'
      return `${'  '.repeat(indent)}(context:getNbtAccessor()):putString("${key}", ${val})`
    },
    nbt_put_boolean: (block, indent = 0) => {
      const key = block.getFieldValue('KEY') || 'key'
      const val = 'false'
      return `${'  '.repeat(indent)}(context:getNbtAccessor()):putBoolean("${key}", ${val})`
    },
    nbt_put_compound: (block, indent = 0) => {
      const key = block.getFieldValue('KEY') || 'key'
      const val = '(context:getNbtAccessor()):newCompoundTag()'
      return `${'  '.repeat(indent)}(context:getNbtAccessor()):putCompound("${key}", ${val})`
    },
  },
})

// 2. 配件系统扩展
registerExtension({
  id: 'attachment',
  name: '配件系统',
  nameEn: 'Attachments',
  colour: '#61AFEF',
  icon: '🔧',
  official: true,
  blocks: [
    {
      type: 'get_attachment',
      message0: '🔧 获取配件 %1',
      args0: [
        {
          type: 'field_dropdown',
          name: 'TYPE',
          options: [
            ['scope', 'scope'], ['muzzle', 'muzzle'], ['stock', 'stock'],
            ['grip', 'grip'], ['laser', 'laser'], ['magazine', 'magazine'],
            ['bayonet', 'bayonet'], ['flashlight', 'flashlight'],
          ],
        },
      ],
      output: 'String',
      colour: '#61AFEF',
      tooltip: _b('获取指定类型的配件ID，无配件返回tacz:empty', 'Get attachment ID by type, returns tacz:empty if none'),
    },
    {
      type: 'has_attachment',
      message0: '🔧 有配件? %1',
      args0: [
        {
          type: 'field_dropdown',
          name: 'TYPE',
          options: [
            ['scope', 'scope'], ['muzzle', 'muzzle'], ['stock', 'stock'],
            ['grip', 'grip'], ['laser', 'laser'], ['magazine', 'magazine'],
            ['bayonet', 'bayonet'], ['flashlight', 'flashlight'],
          ],
        },
      ],
      output: 'Boolean',
      colour: '#61AFEF',
      tooltip: _b('检查是否安装了指定类型配件', 'Check if attachment of type is installed'),
    },
    {
      type: 'get_mag_extent',
      message0: '🔧 扩容等级',
      args0: [],
      output: 'Number',
      colour: '#61AFEF',
      tooltip: _b('获取弹匣扩容等级 0~3', 'Get magazine extent level 0~3'),
    },
  ],
  generators: {
    get_attachment: (block) => {
      const type = block.getFieldValue('TYPE') || 'scope'
      return `context:getAttachment("${type}")`
    },
    has_attachment: (block) => {
      const type = block.getFieldValue('TYPE') || 'scope'
      return `context:getAttachment("${type}") ~= "tacz:empty"`
    },
    get_mag_extent: () => 'context:getMagExtentLevel()',
  },
})

// 3. 玩家输入扩展
registerExtension({
  id: 'player_input',
  name: '玩家输入',
  nameEn: 'Player Input',
  colour: '#C678DD',
  icon: '🎮',
  official: true,
  blocks: [
    {
      type: 'input_w',
      message0: '🎮 按键W',
      args0: [],
      output: 'Boolean',
      colour: '#C678DD',
      tooltip: _b('玩家是否按下W键', 'Is player pressing W'),
    },
    {
      type: 'input_s',
      message0: '🎮 按键S',
      args0: [],
      output: 'Boolean',
      colour: '#C678DD',
      tooltip: _b('玩家是否按下S键', 'Is player pressing S'),
    },
    {
      type: 'input_a',
      message0: '🎮 按键A',
      args0: [],
      output: 'Boolean',
      colour: '#C678DD',
      tooltip: _b('玩家是否按下A键', 'Is player pressing A'),
    },
    {
      type: 'input_d',
      message0: '🎮 按键D',
      args0: [],
      output: 'Boolean',
      colour: '#C678DD',
      tooltip: _b('玩家是否按下D键', 'Is player pressing D'),
    },
    {
      type: 'input_jump',
      message0: '🎮 跳跃中',
      args0: [],
      output: 'Boolean',
      colour: '#C678DD',
      tooltip: _b('玩家是否正在跳跃', 'Is player jumping'),
    },
    {
      type: 'is_crouching',
      message0: '🎮 蹲伏中',
      args0: [],
      output: 'Boolean',
      colour: '#C678DD',
      tooltip: _b('玩家是否蹲伏', 'Is player crouching'),
    },
    {
      type: 'is_crawl',
      message0: '🎮 匍匐中',
      args0: [],
      output: 'Boolean',
      colour: '#C678DD',
      tooltip: _b('玩家是否匍匐', 'Is player crawling'),
    },
    {
      type: 'should_slide',
      message0: '🎮 斜握枪械',
      args0: [],
      output: 'Boolean',
      colour: '#C678DD',
      tooltip: _b('是否应该斜握枪械', 'Should slide weapon'),
    },
  ],
  generators: {
    input_w: () => 'context:isInputUp()',
    input_s: () => 'context:isInputDown()',
    input_a: () => 'context:isInputLeft()',
    input_d: () => 'context:isInputRight()',
    input_jump: () => 'context:isInputJumping()',
    is_crouching: () => 'context:isCrouching()',
    is_crawl: () => 'context:isCrawl()',
    should_slide: () => 'context:shouldSlide()',
  },
})

// 4. 换弹状态扩展
registerExtension({
  id: 'reload_state',
  name: '换弹状态',
  nameEn: 'Reload State',
  colour: '#E5C07B',
  icon: '🔄',
  official: true,
  blocks: [
    {
      type: 'get_reload_state',
      message0: '🔄 换弹状态',
      args0: [],
      output: 'Number',
      colour: '#E5C07B',
      tooltip: _b('获取当前换弹状态(0=未换弹 1=空仓填装 2=空仓收尾 3=战术填装 4=战术收尾)', 'Get reload state ordinal'),
    },
    {
      type: 'is_reloading',
      message0: '🔄 换弹中?',
      args0: [],
      output: 'Boolean',
      colour: '#E5C07B',
      tooltip: _b('是否正在换弹', 'Is reloading'),
    },
    {
      type: 'is_empty_reload',
      message0: '🔄 空仓换弹?',
      args0: [],
      output: 'Boolean',
      colour: '#E5C07B',
      tooltip: _b('是否空仓换弹', 'Is empty reload'),
    },
    {
      type: 'get_fire_mode',
      message0: '🔄 开火模式',
      args0: [],
      output: 'Number',
      colour: '#E5C07B',
      tooltip: _b('获取开火模式(0=全自动 1=半自动 2=多连发)', 'Get fire mode ordinal'),
    },
  ],
  generators: {
    get_reload_state: () => 'context:getReloadStateType()',
    is_reloading: () => '(context:getReloadStateType() ~= 0)',
    is_empty_reload: () => '(context:getReloadStateType() == 1 or context:getReloadStateType() == 2)',
    get_fire_mode: () => 'context:getFireMode()',
  },
})

// 5. 时间与射击扩展
registerExtension({
  id: 'time_shoot',
  name: '时间射击',
  nameEn: 'Time & Shoot',
  colour: '#56B6C2',
  icon: '⏱️',
  official: true,
  blocks: [
    {
      type: 'get_shoot_interval',
      message0: '⏱️ 射击间隔',
      args0: [],
      output: 'Number',
      colour: '#56B6C2',
      tooltip: _b('获取射击间隔(ms)', 'Get shoot interval in ms'),
    },
    {
      type: 'get_cooldown',
      message0: '⏱️ 射击冷却',
      args0: [],
      output: 'Number',
      colour: '#56B6C2',
      tooltip: _b('获取射击冷却(ms)', 'Get shoot cooldown in ms'),
    },
    {
      type: 'adjust_shoot_interval',
      message0: '⏱️ 调整射击间隔 %1',
      args0: [
        { type: 'input_value', name: 'DELTA', check: 'Number' },
      ],
      previousStatement: 'action_stmt',
      nextStatement: 'action_stmt',
      colour: '#56B6C2',
      tooltip: _b('调整射击间隔(ms)，正数增加负数减少', 'Adjust shoot interval in ms'),
    },
    {
      type: 'get_current_time',
      message0: '⏱️ 当前时间',
      args0: [],
      output: 'Number',
      colour: '#56B6C2',
      tooltip: _b('获取当前系统时间(ms)', 'Get current timestamp in ms'),
    },
    {
      type: 'get_partial_ticks',
      message0: '⏱️ PartialTicks',
      args0: [],
      output: 'Number',
      colour: '#56B6C2',
      tooltip: _b('获取最后更新的partialTicks', 'Get last update partialTicks'),
    },
    {
      type: 'has_bullet_in_barrel',
      message0: '⏱️ 枪膛有弹?',
      args0: [],
      output: 'Boolean',
      colour: '#56B6C2',
      tooltip: _b('枪膛中是否有子弹', 'Is there a bullet in barrel'),
    },
    {
      type: 'get_last_shoot_time',
      message0: '⏱️ 上次射击时间',
      args0: [],
      output: 'Number',
      colour: '#56B6C2',
      tooltip: _b('上次射击的时间戳(ms)，切枪时重置为-1', 'Last shoot timestamp in ms, resets to -1 on gun switch'),
    },
  ],
  generators: {
    get_shoot_interval: () => 'context:getShootInterval()',
    get_cooldown: () => 'context:getShootCoolDown()',
    adjust_shoot_interval: (_block, indent = 0) => {
      // Note: value input is handled by genValue in the workspace
      return `${'  '.repeat(indent)}context:adjustClientShootInterval(0)`
    },
    get_current_time: () => 'context:getCurrentTimestamp()',
    get_partial_ticks: () => 'context:getPartialTicks()',
    has_bullet_in_barrel: () => 'context:hasBulletInBarrel()',
    get_last_shoot_time: () => 'context:getLastShootTimestamp()',
  },
})

// 6. 状态机参数扩展
registerExtension({
  id: 'state_params',
  name: '状态机参数',
  nameEn: 'State Params',
  colour: '#98C379',
  icon: '📊',
  official: true,
  blocks: [
    {
      type: 'get_state_params',
      message0: '📊 状态机参数',
      args0: [],
      output: 'LuaTable',
      colour: '#98C379',
      tooltip: _b('获取display中声明的状态机参数表', 'Get state machine params from display'),
    },
    {
      type: 'get_put_away_time',
      message0: '📊 收枪时长',
      args0: [],
      output: 'Number',
      colour: '#98C379',
      tooltip: _b('获取收起物品动画的建议时长', 'Get put away animation time'),
    },
    {
      type: 'get_walk_dist',
      message0: '📊 行走距离',
      args0: [],
      output: 'Number',
      colour: '#98C379',
      tooltip: _b('获取与锚点相对的行走距离', 'Get walk distance from anchor'),
    },
    {
      type: 'get_heat_progress',
      message0: '📊 过热进度',
      args0: [],
      output: 'Number',
      colour: '#98C379',
      tooltip: _b('获取过热进度 0~1', 'Get overheat progress 0~1'),
    },
    {
      type: 'get_ammo_count',
      message0: '📊 弹药数量',
      args0: [],
      output: 'Number',
      colour: '#98C379',
      tooltip: _b('获取弹匣备弹数', 'Get ammo count in magazine'),
    },
    {
      type: 'get_max_ammo',
      message0: '📊 最大弹药',
      args0: [],
      output: 'Number',
      colour: '#98C379',
      tooltip: _b('获取弹匣最大备弹数', 'Get max ammo count'),
    },
  ],
  generators: {
    get_state_params: () => 'context:getStateMachineParams()',
    get_put_away_time: () => 'context:getPutAwayTime()',
    get_walk_dist: () => 'context:getWalkDist()',
    get_heat_progress: () => 'context:getHeatProgress()',
    get_ammo_count: () => 'context:getAmmoCount()',
    get_max_ammo: () => 'context:getMaxAmmoCount()',
  },
})

// 7. 瞄准系统扩展
registerExtension({
  id: 'aiming',
  name: '瞄准系统',
  nameEn: 'Aiming',
  colour: '#F9E2AF',
  icon: '🎯',
  official: true,
  blocks: [
    {
      type: 'is_aiming',
      message0: '🎯 瞄准中?',
      args0: [],
      output: 'Boolean',
      colour: '#F9E2AF',
      tooltip: _b('玩家当前是否在瞄准', 'Is player currently aiming'),
    },
    {
      type: 'get_aiming_progress',
      message0: '🎯 瞄准进度',
      args0: [],
      output: 'Number',
      colour: '#F9E2AF',
      tooltip: _b('获取瞄准进度 0~1', 'Get aiming progress 0~1'),
    },
    {
      type: 'has_ammo_to_consume',
      message0: '🎯 有备弹?',
      args0: [],
      output: 'Boolean',
      colour: '#F9E2AF',
      tooltip: _b('玩家身上/虚拟备弹是否有弹药可消耗（创造模式直接返回true）', 'Has ammo to consume (creative mode returns true)'),
    },
  ],
  generators: {
    is_aiming: () => 'context:isAiming()',
    get_aiming_progress: () => 'context:getAimingProgress()',
    has_ammo_to_consume: () => 'context:hasAmmoToConsume()',
  },
})

// 8. 投掷物扩展（ThrowableAnimationStateContext）
registerExtension({
  id: 'throwable',
  name: '投掷物',
  nameEn: 'Throwable',
  colour: '#F38BA8',
  icon: '💣',
  official: true,
  blocks: [
    {
      type: 'throwable_stack_count',
      message0: '💣 堆叠数量',
      args0: [],
      output: 'Number',
      colour: '#F38BA8',
      tooltip: _b('获取投掷物堆叠数量', 'Get throwable stack count'),
    },
    {
      type: 'throwable_using_tick',
      message0: '💣 使用时长',
      args0: [],
      output: 'Number',
      colour: '#F38BA8',
      tooltip: _b('获取投掷物使用时长(tick)', 'Get throwable using tick count'),
    },
    {
      type: 'throwable_is_using',
      message0: '💣 使用中?',
      args0: [],
      output: 'Boolean',
      colour: '#F38BA8',
      tooltip: _b('投掷物是否正在使用', 'Is throwable being used'),
    },
  ],
  generators: {
    throwable_stack_count: () => 'context:getStackCount()',
    throwable_using_tick: () => 'context:getUsingTick()',
    throwable_is_using: () => 'context:isUsing()',
  },
})

// 9. 轨道管理扩展（AnimationStateContext 基类方法）
registerExtension({
  id: 'track_management',
  name: '轨道管理',
  nameEn: 'Track Mgmt',
  colour: '#89B4FA',
  icon: '🛤️',
  official: true,
  blocks: [
    {
      type: 'add_track_line',
      message0: '🛤️ 新建轨道行',
      args0: [],
      output: 'Number',
      colour: '#89B4FA',
      tooltip: _b('分配一个新的轨道行，返回下标', 'Allocate a new track line, returns index'),
    },
    {
      type: 'get_track_line_size',
      message0: '🛤️ 轨道行数',
      args0: [],
      output: 'Number',
      colour: '#89B4FA',
      tooltip: _b('获取轨道行数量', 'Get track line count'),
    },
    {
      type: 'assign_new_track',
      message0: '🛤️ 分配轨道 %1',
      args0: [
        { type: 'input_value', name: 'INDEX', check: 'Number' },
      ],
      output: 'Number',
      colour: '#89B4FA',
      tooltip: _b('为指定轨道行分配新轨道，返回轨道下标', 'Assign new track to track line, returns track index'),
    },
    {
      type: 'get_singleton_track',
      message0: '🛤️ 单例轨道 %1',
      args0: [
        { type: 'input_value', name: 'INDEX', check: 'Number' },
      ],
      output: 'Number',
      colour: '#89B4FA',
      tooltip: _b('获取只需一个轨道的轨道行（无则分配）', 'Get singleton track for track line'),
    },
    {
      type: 'should_hide_crosshair',
      message0: '🛤️ 准星隐藏?',
      args0: [],
      output: 'Boolean',
      colour: '#89B4FA',
      tooltip: _b('渲染时是否需要隐藏准心', 'Should crosshair be hidden'),
    },
  ],
  generators: {
    add_track_line: () => 'context:addTrackLine()',
    get_track_line_size: () => 'context:getTrackLineSize()',
    assign_new_track: (_block) => 'context:assignNewTrack(0)',
    get_singleton_track: (_block) => 'context:getAsSingletonTrack(0)',
    should_hide_crosshair: () => 'context:shouldHideCrossHair()',
  },
})
