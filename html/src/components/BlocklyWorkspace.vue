<template>
  <div class="workspace-wrapper">
    <div ref="blocklyDiv" class="blockly-container"></div>
    <Transition name="toast">
      <div v-if="toastMsg" class="blockly-toast" :class="toastType">
        <span class="toast-icon">{{ toastType === 'error' ? '🚫' : '⚠️' }}</span>
        {{ toastMsg }}
      </div>
    </Transition>
    <LuaCodeEditor
      :visible="luaEditorVisible"
      :code="luaEditorCode"
      @update:code="onLuaCodeUpdate"
      @close="luaEditorVisible = false"
    />
    <!-- Extension Selector Dialog -->
    <Teleport to="body">
      <div class="ext-overlay" v-if="extDialogVisible" @keydown.tab.prevent>
        <div class="ext-modal">
          <div class="ext-header">
            <span>🧩 {{ _b('选择扩展', 'Select Extensions') }}</span>
            <button class="ext-close" @click="extDialogVisible = false">✕</button>
          </div>
          <div class="ext-body">
            <div class="ext-section-title">{{ _b('官方扩展', 'Official Extensions') }}</div>
            <div class="ext-list">
              <div
                v-for="ext in registeredExts.filter(e => e.official)"
                :key="ext.id"
                class="ext-item"
                :class="{ active: isActive(ext.id) }"
                @click="toggleExt(ext.id)"
              >
                <span class="ext-check">{{ isActive(ext.id) ? '☑' : '☐' }}</span>
                <span class="ext-icon">{{ ext.icon }}</span>
                <span class="ext-name">{{ _b(ext.name, ext.nameEn) }}</span>
                <span class="ext-count">{{ ext.blocks.length }} {{ _b('个积木', 'blocks') }}</span>
              </div>
            </div>
            <div class="ext-section-title" style="margin-top: 12px;">{{ _b('自定义扩展', 'Custom Extensions') }}</div>
            <div class="ext-list">
              <div
                v-for="ext in registeredExts.filter(e => !e.official)"
                :key="ext.id"
                class="ext-item"
                :class="{ active: isActive(ext.id) }"
              >
                <span class="ext-check" @click="toggleExt(ext.id)">{{ isActive(ext.id) ? '☑' : '☐' }}</span>
                <span class="ext-icon">{{ ext.icon }}</span>
                <span class="ext-name">{{ _b(ext.name, ext.nameEn) }}</span>
                <span class="ext-count">{{ ext.blocks.length }} {{ _b('个积木', 'blocks') }}</span>
                <button class="ext-remove" @click="removeCustomExt(ext.id)">🗑️</button>
              </div>
              <div v-if="registeredExts.filter(e => !e.official).length === 0" class="ext-empty">
                {{ _b('暂无自定义扩展', 'No custom extensions') }}
              </div>
            </div>
            <div class="ext-import-row">
              <button class="ext-import-btn" @click="triggerImportExt">📥 {{ _b('导入扩展文件', 'Import Extension') }}</button>
              <button class="ext-import-btn" @click="showExtTutorial = true">📖 {{ _b('制作教程', 'Tutorial') }}</button>
            </div>
          </div>
          <div class="ext-footer">
            <button class="ext-btn confirm" @click="confirmExtensions">{{ _b('确定', 'OK') }}</button>
          </div>
        </div>
      </div>

      <!-- Extension Tutorial Dialog -->
      <div class="ext-overlay" v-if="showExtTutorial" @keydown.tab.prevent>
        <div class="ext-modal ext-tutorial-modal">
          <div class="ext-header">
            <span>📖 {{ _b('扩展制作教程', 'Extension Tutorial') }}</span>
            <button class="ext-close" @click="showExtTutorial = false">✕</button>
          </div>
          <div class="ext-body ext-tutorial-body">
            <div class="ext-tutorial-content">
              <h4>1. 扩展文件是什么？</h4>
              <p>扩展文件是一个 <code>.tacz-ext.json</code> 文件，一个文件 = 一个积木栏分类。</p>
              <p>导入后会自动在工具箱中添加一个新的积木分类。</p>

              <h4>2. 文件基本结构</h4>
              <pre class="ext-tutorial-code">{
  "id": "my_ext",          // 必填，唯一标识（英文+下划线）
  "name": "我的扩展",       // 必填，中文名
  "nameEn": "My Extension", // 必填，英文名
  "colour": "#FF6B6B",     // 必填，分类颜色（十六进制）
  "icon": "🚀",            // 必填，分类图标（emoji）
  "blocks": [ ... ],       // 必填，积木定义列表
  "generators": { ... }    // 必填，代码生成器
}</pre>

              <h4>3. 积木定义 (blocks)</h4>
              <p>每个积木定义包含以下字段：</p>
              <pre class="ext-tutorial-code">{
  "type": "my_block",        // 必填，积木唯一ID
  "message0": "🚀 我的积木 %1", // 必填，显示文本
  "args0": [ ... ],          // 参数列表（可选）
  "previousStatement": "action_stmt", // 上连接类型（可选）
  "nextStatement": "action_stmt",     // 下连接类型（可选）
  "output": "Boolean",       // 输出类型（可选）
  "colour": "#FF6B6B",       // 积木颜色
  "tooltip": "提示文字"       // 悬停提示
}</pre>

              <h4>4. 参数类型 (args0)</h4>
              <p><b>文本输入框：</b></p>
              <pre class="ext-tutorial-code">{ "type": "field_input", "name": "KEY", "text": "默认值" }</pre>
              <p><b>下拉选择：</b></p>
              <pre class="ext-tutorial-code">{ "type": "field_dropdown", "name": "MODE",
  "options": [["选项A","a"], ["选项B","b"]] }</pre>
              <p><b>数字输入：</b></p>
              <pre class="ext-tutorial-code">{ "type": "field_number", "name": "COUNT", "value": 1 }</pre>
              <p><b>值输入（接其他积木）：</b></p>
              <pre class="ext-tutorial-code">{ "type": "input_value", "name": "TIME", "check": "Number" }</pre>
              <p><b>语句输入（嵌套积木）：</b></p>
              <pre class="ext-tutorial-code">{ "type": "input_statement", "name": "DO", "check": "action_stmt" }</pre>

              <h4>5. 连接类型</h4>
              <ul>
                <li><code>"action_stmt"</code> — 动作积木链（播放动画、触发事件等）</li>
                <li><code>"state_stmt"</code> — 状态定义链（entry/update/exit）</li>
                <li><code>"Boolean"</code> — 布尔值输出</li>
                <li><code>"Number"</code> — 数值输出</li>
                <li><code>"String"</code> — 字符串输出</li>
              </ul>
              <p>有 previousStatement/nextStatement → 语句积木（上下连接）</p>
              <p>有 output → 值积木（输出到其他积木的输入口）</p>

              <h4>6. 代码生成器 (generators)</h4>
              <p>key = 积木 type，value = Lua 代码模板字符串</p>
              <p>用 <code>${字段名}</code> 引用积木字段值</p>
              <pre class="ext-tutorial-code">"generators": {
  "my_block": "  context:myMethod(\"${KEY}\", ${COUNT})"
}</pre>
              <p>语句积木模板以 2 空格缩进开头，值积木直接返回表达式：</p>
              <pre class="ext-tutorial-code">// 语句积木（有上下连接）
"my_action": "  context:doSomething(\"${VALUE}\")"

// 值积木（有输出）
"my_value": "context:getValue()"</pre>

              <h4>7. 完整示例</h4>
              <pre class="ext-tutorial-code">{
  "id": "custom_heal",
  "name": "治疗系统",
  "nameEn": "Heal System",
  "colour": "#4ECDC4",
  "icon": "💊",
  "blocks": [
    {
      "type": "heal_player",
      "message0": "💊 治疗 %1 点",
      "args0": [
        { "type": "field_number", "name": "AMOUNT", "value": 10 }
      ],
      "previousStatement": "action_stmt",
      "nextStatement": "action_stmt",
      "colour": "#4ECDC4",
      "tooltip": "治疗玩家指定点数"
    },
    {
      "type": "get_health",
      "message0": "💊 当前血量",
      "output": "Number",
      "colour": "#4ECDC4",
      "tooltip": "获取玩家当前血量"
    },
    {
      "type": "is_alive",
      "message0": "💊 存活?",
      "output": "Boolean",
      "colour": "#4ECDC4",
      "tooltip": "玩家是否存活"
    }
  ],
  "generators": {
    "heal_player": "  context:heal(${AMOUNT})",
    "get_health": "context:getHealth()",
    "is_alive": "context:isAlive()"
  }
}</pre>

              <h4>8. 可用的 context 方法</h4>
              <p>详见 TACZ 源码 <code>LuaGunAnimationConstant.java</code>，常用：</p>
              <ul>
                <li><code>context:runAnimation(name, track, blend, mode, time)</code></li>
                <li><code>context:stopAnimation(track)</code></li>
                <li><code>context:holdAnimation(track)</code></li>
                <li><code>context:trigger(input)</code></li>
                <li><code>context:getAmmoCount()</code></li>
                <li><code>context:isAiming()</code></li>
                <li><code>context:getNbtAccessor()</code></li>
                <li><code>context:getAttachment(type)</code></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <input ref="extFileInput" type="file" accept=".tacz-ext.json" style="display:none" @change="handleImportExt" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as Blockly from 'blockly'
import '../blocks'
import { taczTheme } from '../theme'
import { _b, i18n } from '../locales'
import LuaCodeEditor from './LuaCodeEditor.vue'
import {
  registerExtension, unregisterExtension, activateExtension, deactivateExtension,
  isActive, getRegisteredExtensions, getActiveExtensions,
  getExtensionGenerators, getExtensionToolboxCategories,
  type Extension, type GenFn,
} from '../extension-registry'
// Import official extensions (they self-register)
import '../extension-registry'
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

// ─── Lua Code Editor State ───
const luaEditorVisible = ref(false)
const luaEditorCode = ref('')
let editingBlock: Blockly.Block | null = null

// ─── Extension State ───
const extDialogVisible = ref(false)
const showExtTutorial = ref(false)
const registeredExts = ref<Extension[]>(getRegisteredExtensions())
const extFileInput = ref<HTMLInputElement>()

function openLuaEditor(block: Blockly.Block) {
  editingBlock = block
  luaEditorCode.value = block.getFieldValue('CODE') || '-- code'
  luaEditorVisible.value = true
}

function onLuaCodeUpdate(code: string) {
  if (editingBlock) {
    const field = editingBlock.getField('CODE')
    if (field) {
      field.setValue(code)
    }
  }
}

// ─── Extension Management ───
function toggleExt(id: string) {
  if (isActive(id)) {
    deactivateExtension(id)
  } else {
    activateExtension(id)
  }
  registeredExts.value = [...getRegisteredExtensions()]
}

function removeCustomExt(id: string) {
  if (!confirm(_b('确定删除此扩展？', 'Remove this extension?'))) return
  unregisterExtension(id)
  registeredExts.value = [...getRegisteredExtensions()]
  rebuildToolbox()
}

function confirmExtensions() {
  extDialogVisible.value = false
  rebuildToolbox()
}

function rebuildToolbox() {
  if (!workspace) return
  workspace.updateToolbox(buildToolbox())
  // Re-generate code with new extension generators
  handleWorkspaceChange({ type: '' } as any)
}

function triggerImportExt() {
  extFileInput.value?.click()
}

function handleImportExt(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    try {
      const data = JSON.parse(reader.result as string)
      if (!data.id || !data.blocks || !Array.isArray(data.blocks)) {
        throw new Error('Invalid extension format')
      }
      // Build generators from template strings
      const generators: Record<string, GenFn> = {}
      if (data.generators) {
        for (const [blockType, template] of Object.entries(data.generators)) {
          if (typeof template === 'string') {
            generators[blockType] = (block: Blockly.Block, indent = 0) => {
              let code = template as string
              // Replace ${FIELD} with block field values
              for (const field of block.inputList.flatMap(i => i.fieldRow)) {
                const name = (field as any).name
                if (name) {
                  code = code.replace(new RegExp(`\\$\\{${name}\\}`, 'g'), String(block.getFieldValue(name) ?? ''))
                }
              }
              // Apply indent
              const prefix = '  '.repeat(indent)
              return code.split('\n').map((line, i) => i === 0 ? prefix + line : prefix + line).join('\n')
            }
          }
        }
      }
      const ext: Extension = {
        id: data.id,
        name: data.name || data.id,
        nameEn: data.nameEn || data.name || data.id,
        colour: data.colour || '#FF6B6B',
        icon: data.icon || '🧩',
        official: false,
        blocks: data.blocks,
        generators,
        _rawJson: data,
      } as any
      registerExtension(ext)
      activateExtension(ext.id)
      registeredExts.value = [...getRegisteredExtensions()]
      showToast(_b(`扩展 "${ext.name}" 导入成功`, `Extension "${ext.nameEn}" imported`))
    } catch (err) {
      showToast(_b('扩展格式无效', 'Invalid extension format'), 'error')
    }
  }
  reader.readAsText(file)
  ;(e.target as HTMLInputElement).value = ''
}

// ─── Toast Notification ───
const toastMsg = ref('')
const toastType = ref<'warning' | 'error'>('warning')
let toastTimer: ReturnType<typeof setTimeout> | null = null
function showToast(msg: string, type: 'warning' | 'error' = 'warning') {
  toastMsg.value = msg
  toastType.value = type
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toastMsg.value = '' }, 3000)
}

// ─── Custom Connection Checker ───
let lastRejection = { reason: '', time: 0 }

function getBlockLabel(block: Blockly.Block): string {
  for (const input of block.inputList) {
    for (const field of input.fieldRow) {
      const t = field.getText()?.trim()
      if (t) return t
    }
  }
  return block.type
}

const typeCheckLabels: Record<string, string> = {
  'state_stmt': '状态定义',
  'action_stmt': '动作语句',
  'Boolean': '布尔值',
  'Number': '数值',
  'String': '字符串',
  'Array': '数组',
  'TrackLine': '轨道行',
  'Track': '轨道',
}

class TaczConnectionChecker extends Blockly.ConnectionChecker {
  doTypeChecks(a: Blockly.Connection, b: Blockly.Connection): boolean {
    const result = super.doTypeChecks(a, b)
    if (!result) {
      const aChecks = a.getCheck() || []
      const bChecks = b.getCheck() || []
      const aName = getBlockLabel(a.getSourceBlock())
      const bName = getBlockLabel(b.getSourceBlock())
      const aTypes = aChecks.map(c => typeCheckLabels[c] || c).join('/')
      const bTypes = bChecks.map(c => typeCheckLabels[c] || c).join('/')
      if (aChecks.length > 0 && bChecks.length > 0) {
        lastRejection = {
          reason: _b(
            `类型不匹配: "${bName}" 无法连接到 "${aName}"（需要 ${aTypes}，提供了 ${bTypes}）`,
            `Type mismatch: "${bName}" cannot connect to "${aName}" (requires ${aTypes}, provides ${bTypes})`
          ),
          time: Date.now()
        }
      } else if (aChecks.length > 0) {
        lastRejection = {
          reason: _b(
            `"${bName}" 无法连接到 "${aName}"（需要 ${aTypes} 类型）`,
            `"${bName}" cannot connect to "${aName}" (requires ${aTypes} type)`
          ),
          time: Date.now()
        }
      }
    }
    return result
  }
}

// Register custom checker before workspace creation
Blockly.registry.register('connectionChecker' as any, 'TaczChecker', TaczConnectionChecker)

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
          { kind: 'block', type: 'pause_animation' },
          { kind: 'block', type: 'resume_animation' },
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
          { kind: 'block', type: 'check_holding' },
          { kind: 'block', type: 'check_paused' },
          { kind: 'block', type: 'has_animation' },
          { kind: 'block', type: 'check_bullet_in_barrel' },
          { kind: 'block', type: 'check_aiming' },
          { kind: 'block', type: 'check_crawl' },
          { kind: 'block', type: 'check_crouching' },
          { kind: 'block', type: 'check_jumping' },
          { kind: 'block', type: 'check_reload_state' },
          { kind: 'block', type: 'check_fire_mode' },
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
          { kind: 'block', type: 'adjust_shoot_interval' },
        ],
      },
      {
        kind: 'category',
        name: _b('📊 数值', '📊 Values'),
        colour: '#9370DB',
        contents: [
          { kind: 'block', type: 'get_ammo_count' },
          { kind: 'block', type: 'get_max_ammo_count' },
          { kind: 'block', type: 'get_mag_extent_level' },
          { kind: 'block', type: 'get_aiming_progress' },
          { kind: 'block', type: 'get_fire_mode' },
          { kind: 'block', type: 'get_reload_state_type' },
          { kind: 'block', type: 'get_shoot_interval' },
          { kind: 'block', type: 'get_shoot_cooldown' },
          { kind: 'block', type: 'get_last_shoot_time' },
          { kind: 'block', type: 'get_current_timestamp' },
          { kind: 'block', type: 'get_walk_dist' },
          { kind: 'block', type: 'get_partial_ticks' },
          { kind: 'block', type: 'get_put_away_time' },
          { kind: 'block', type: 'get_state_machine_params' },
          { kind: 'block', type: 'should_hide_crosshair' },
        ],
      },
      {
        kind: 'category', name: _b('🛤️ 轨道系统', '🛤️ Track System'), colour: '#4A90E2',
        contents: [
          { kind: 'block', type: 'track_line' },
          { kind: 'block', type: 'get_track' },
          { kind: 'block', type: 'find_idle_track' },
          { kind: 'block', type: 'add_track_line' },
          { kind: 'block', type: 'assign_new_track' },
          { kind: 'block', type: 'ensure_track_line_size' },
          { kind: 'block', type: 'ensure_tracks_amount' },
          { kind: 'block', type: 'get_singleton_track' },
          { kind: 'block', type: 'get_track_line_size' },
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
      // Separator before extensions
      { kind: 'sep' },
      // Extension selector button (always visible)
      {
        kind: 'category',
        name: _b('🧩 扩展', '🧩 Extensions'),
        colour: '#8B5CF6',
        contents: [
          {
            kind: 'button',
            text: _b('📦 选择扩展...', '📦 Select Extensions...'),
            callbackKey: 'openExtDialog',
          } as any,
        ],
      },
      // Active extension categories
      ...getExtensionToolboxCategories(),
    ],
  }
}

// ─── Lua Code Generator ───
const luaGen: Record<string, (block: Blockly.Block, indent?: number) => string> = {}

// Helper: generate code for connected blocks (next chain)
function genNext(block: Blockly.Block | null, indent = 1): string {
  if (!block) return ''
  // Skip disabled blocks
  if (!block.isEnabled()) return genNext(block.getNextBlock(), indent)
  const extGens = getExtensionGenerators()
  const allGens = { ...luaGen, ...extGens }
  const func = allGens[block.type]
  if (!func) return genNext(block.getNextBlock(), indent)
  const lines: string[] = []
  let current: Blockly.Block | null = block
  while (current) {
    if (current.isEnabled()) {
      const fn = allGens[current.type]
      if (fn) {
        lines.push(fn(current, indent))
      }
    }
    current = current.getNextBlock()
  }
  return lines.join('\n')
}

// Helper: get value from a connected input block
function genValue(block: Blockly.Block, inputName: string): string {
  const target = block.getInputTargetBlock(inputName)
  if (!target || !target.isEnabled()) return 'nil'
  const extGens = getExtensionGenerators()
  const allGens = { ...luaGen, ...extGens }
  const func = allGens[target.type]
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
  const blend = block.getFieldValue('BLEND') || 'false'
  const blendTime = genValue(block, 'BLEND_TIME') || '0'
  return `${'  '.repeat(indent)}context:runAnimation("${anim}", ${track}, ${blend}, LOOP, ${blendTime})`
}

luaGen['set_progress'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  const progress = genValue(block, 'PROGRESS') || '0'
  const normalization = block.getFieldValue('NORMALIZATION') || 'false'
  return `${'  '.repeat(indent)}context:setAnimationProgress(${track}, ${progress}, ${normalization})`
}

luaGen['adjust_progress'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  const delta = genValue(block, 'DELTA') || '0'
  const normalization = block.getFieldValue('NORMALIZATION') || 'false'
  return `${'  '.repeat(indent)}context:adjustAnimationProgress(${track}, ${delta}, ${normalization})`
}

luaGen['play_blended'] = (block, indent = 0) => {
  const anim = block.getFieldValue('ANIM') || 'shoot'
  const line = block.getFieldValue('LINE') || 'STATIC_TRACK_LINE'
  const blend = block.getFieldValue('BLEND') || 'false'
  const mode = block.getFieldValue('MODE') || 'PLAY_ONCE_STOP'
  const blendTime = genValue(block, 'BLEND_TIME') || '0'
  return `${'  '.repeat(indent)}context:runAnimation("${anim}", context:findIdleTrack(${line}, true), ${blend}, ${mode}, ${blendTime})`
}
luaGen['pause_animation'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `${'  '.repeat(indent)}context:pauseAnimation(${track})`
}
luaGen['resume_animation'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `${'  '.repeat(indent)}context:resumeAnimation(${track})`
}

// Condition Check Blocks (correct TACZ API)
luaGen['check_ammo'] = () => 'context:hasAmmoToConsume()'
luaGen['check_ammo_count'] = (block) => {
  const op = block.getFieldValue('OP') || '>='
  const value = genValue(block, 'VALUE') || '0'
  return `context:getAmmoCount() ${op} ${value}`
}
luaGen['check_heat'] = () => 'context:isOverHeat()'
luaGen['check_ground'] = () => 'context:isOnGround()'
luaGen['check_stopped'] = (block) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `context:isStopped(${track})`
}
luaGen['check_cooldown'] = (block) => {
  const op = block.getFieldValue('OP') || '>='
  const value = genValue(block, 'VALUE') || '0'
  return `context:getShootCoolDown() ${op} ${value}`
}
luaGen['check_track_idle'] = (block) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `context:isStopped(${track})`
}
luaGen['check_walk_dir'] = (block) => {
  const dir = block.getFieldValue('DIR') || 'forward'
  const dirMap: Record<string, string> = {
    forward: 'context:isInputUp()',
    backward: 'context:isInputDown()',
    left: 'context:isInputLeft()',
    right: 'context:isInputRight()',
  }
  return dirMap[dir] || 'context:isInputUp()'
}
luaGen['check_running'] = () => 'context:isRunning()'
luaGen['check_holding'] = (block) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `context:isHolding(${track})`
}
luaGen['check_paused'] = (block) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `context:isPause(${track})`
}
luaGen['has_animation'] = (block) => {
  const name = block.getFieldValue('NAME') || 'idle'
  return `context:hasAnimationPrototype("${name}")`
}

// New condition blocks
luaGen['check_bullet_in_barrel'] = () => 'context:hasBulletInBarrel()'
luaGen['check_aiming'] = () => 'context:isAiming()'
luaGen['check_crawl'] = () => 'context:isCrawl()'
luaGen['check_crouching'] = () => 'context:isCrouching()'
luaGen['check_jumping'] = () => 'context:isInputJumping()'
luaGen['check_reload_state'] = (block) => {
  return `context:getReloadStateType() ${block.getFieldValue('OP')} ${block.getFieldValue('STATE')}`
}
luaGen['check_fire_mode'] = (block) => {
  return `context:getFireMode() ${block.getFieldValue('OP')} ${block.getFieldValue('MODE')}`
}

// Action Blocks (correct TACZ API)
luaGen['pop_shell'] = (block, indent = 0) => {
  const index = genValue(block, 'INDEX') || '1'
  return `${'  '.repeat(indent)}context:popShellFrom(${index})`
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
  return `${'  '.repeat(indent)}context:anchorWalkDist()`
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
  const prefix = block.getFieldValue('PREFIX') || 'melee_bayonet_'
  const counter = block.getFieldValue('COUNTER') || 'bayonet_counter'
  const max = genValue(block, 'MAX') || '3'
  return `${'  '.repeat(indent)}-- cycle melee: ${prefix} counter=${counter} max=${max}`
}
luaGen['track_hold'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `${'  '.repeat(indent)}context:holdAnimation(${track})`
}
luaGen['adjust_shoot_interval'] = (block, indent = 0) => {
  const delta = genValue(block, 'DELTA') || '0'
  return `${'  '.repeat(indent)}context:adjustClientShootInterval(${delta})`
}

// Value Output Blocks
luaGen['get_ammo_count'] = () => 'context:getAmmoCount()'
luaGen['get_max_ammo_count'] = () => 'context:getMaxAmmoCount()'
luaGen['get_aiming_progress'] = () => 'context:getAimingProgress()'
luaGen['get_fire_mode'] = () => 'context:getFireMode()'
luaGen['get_reload_state_type'] = () => 'context:getReloadStateType()'
luaGen['get_shoot_interval'] = () => 'context:getShootInterval()'
luaGen['get_shoot_cooldown'] = () => 'context:getShootCoolDown()'
luaGen['get_last_shoot_time'] = () => 'context:getLastShootTimestamp()'
luaGen['get_current_timestamp'] = () => 'context:getCurrentTimestamp()'
luaGen['get_mag_extent_level'] = () => 'context:getMagExtentLevel()'
luaGen['get_walk_dist'] = () => 'context:getWalkDist()'
luaGen['get_partial_ticks'] = () => 'context:getPartialTicks()'
luaGen['get_put_away_time'] = () => 'context:getPutAwayTime()'
luaGen['get_state_machine_params'] = () => 'context:getStateMachineParams()'
luaGen['should_hide_crosshair'] = () => 'context:shouldHideCrossHair()'

// Track System Blocks (correct TACZ API)
luaGen['track_line'] = () => '-- track_line'
luaGen['get_track'] = (block) => {
  const line = block.getFieldValue('LINE') || 'STATIC_TRACK_LINE'
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `-- get_track: ${line}, ${track}`
}
luaGen['find_idle_track'] = (block, indent = 0) => {
  const line = block.getFieldValue('LINE') || 'STATIC_TRACK_LINE'
  const interrupt = block.getFieldValue('INTERRUPT') || 'false'
  return `${'  '.repeat(indent)}context:findIdleTrack(${line}, ${interrupt})`
}
luaGen['add_track_line'] = () => 'context:addTrackLine()'
luaGen['assign_new_track'] = (block) => {
  const index = genValue(block, 'INDEX') || '0'
  return `context:assignNewTrack(${index})`
}
luaGen['ensure_track_line_size'] = (block, indent = 0) => {
  const size = genValue(block, 'SIZE') || '0'
  return `${'  '.repeat(indent)}context:ensureTrackLineSize(${size})`
}
luaGen['ensure_tracks_amount'] = (block, indent = 0) => {
  const index = genValue(block, 'INDEX') || '0'
  const amount = genValue(block, 'AMOUNT') || '0'
  return `${'  '.repeat(indent)}context:ensureTracksAmount(${index}, ${amount})`
}
luaGen['get_singleton_track'] = (block) => {
  const index = genValue(block, 'INDEX') || '0'
  return `context:getAsSingletonTrack(${index})`
}
luaGen['get_track_line_size'] = () => 'context:getTrackLineSize()'

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
luaGen['loop_mode'] = () => 'LOOP'
luaGen['play_once_stop'] = () => 'PLAY_ONCE_STOP'
luaGen['play_once_hold'] = () => 'PLAY_ONCE_HOLD'

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

  // Merge extension generators
  const extGens = getExtensionGenerators()
  const allGens = { ...luaGen, ...extGens }

  // Collect event hat blocks and other blocks (skip disabled)
  const eventBlocks: Blockly.Block[] = []
  const stateBlocks: Blockly.Block[] = []

  for (const block of topBlocks) {
    if (!block.isEnabled()) continue
    const type = block.type
    if (type.startsWith('event_')) {
      eventBlocks.push(block)
    } else if (type === 'entry' || type === 'update_node' || type === 'exit' || type === 'transition') {
      stateBlocks.push(block)
    }
  }

  const lines: string[] = []
  lines.push('local M = {}')
  lines.push('')

  // Initialize function
  lines.push('function M:initialize(context)')
  lines.push('end')
  lines.push('')

  // Exit function
  lines.push('function M:exit(context)')
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

// ─── Workspace Validation ───
let isValidating = false
// Track blocks disabled by the system (not by user)
const systemDisabledBlocks = new WeakSet<Blockly.Block>()
// Track blocks visually disabled because their hat block is disabled
const cascadeDisabledBlocks = new WeakSet<Blockly.Block>()

function isHatBlock(block: Blockly.Block): boolean {
  return block.type.startsWith('event_') || !block.previousConnection
}

function validateWorkspace() {
  if (!workspace || isValidating) return
  isValidating = true
  try {
    const blocks = workspace.getAllBlocks(true)

    // First pass: system validation
    for (const block of blocks) {
      const issue = validateBlock(block)
      if (issue) {
        if (block.isEnabled()) {
          block.setWarningText(issue)
          block.setEnabled(false)
          systemDisabledBlocks.add(block)
        }
      } else if (systemDisabledBlocks.has(block)) {
        block.setWarningText(null)
        block.setEnabled(true)
        systemDisabledBlocks.delete(block)
      }
    }

    // Second pass: cascade disabled state from hat blocks
    // Re-enable any previously cascade-disabled blocks first
    for (const block of blocks) {
      if (cascadeDisabledBlocks.has(block)) {
        block.setEnabled(true)
        cascadeDisabledBlocks.delete(block)
      }
    }

    // Then cascade: if a hat block is disabled, disable all blocks below it
    for (const block of blocks) {
      if (!block.isEnabled() && isHatBlock(block)) {
        let next = block.getNextBlock()
        while (next) {
          if (next.isEnabled()) {
            next.setEnabled(false)
            cascadeDisabledBlocks.add(next)
          }
          next = next.getNextBlock()
        }
      }
    }
  } finally {
    isValidating = false
  }
}

function validateBlock(block: Blockly.Block): string | null {
  return null
}

// ─── Workspace Change Handler ───
function handleWorkspaceChange(event: Blockly.Events.Abstract) {
  // Show toast for rejected connections
  if (event.type === Blockly.Events.BLOCK_MOVE) {
    if (lastRejection.reason && Date.now() - lastRejection.time < 1000) {
      showToast(lastRejection.reason, 'error')
      lastRejection.reason = ''
    }
  }

  // Validate workspace (debounce inside to avoid re-entrancy)
  if (!isValidating) {
    validateWorkspace()
  }

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
    plugins: {
      'connectionChecker': 'TaczChecker',
    },
  })

  // Register extension dialog button callback
  workspace.registerButtonCallback('openExtDialog', () => {
    registeredExts.value = [...getRegisteredExtensions()]
    extDialogVisible.value = true
  })

  // Expose workspace for save/load
  ;(window as any).__tacz_workspace = {
    clear() { workspace?.clear() },
    getXML() { return Blockly.Xml.workspaceToDom(workspace!) },
    loadXML(xml: string) {
      workspace?.clear()
      const dom = Blockly.utils.xml.textToDom(xml)
      Blockly.Xml.domToWorkspace(dom, workspace!)
    },
    getCode() { return generateCode() },
    set code(v: string) {},
    get code() { return generateCode() },
    openExtDialog() {
      registeredExts.value = [...getRegisteredExtensions()]
      extDialogVisible.value = true
    },
    getExtensionData() {
      const activeIds = getActiveExtensions().map(e => e.id)
      const customExts = getRegisteredExtensions().filter(e => !e.official)
      const customJsons = customExts.map(e => (e as any)._rawJson).filter(Boolean)
      return { activeIds, customExts: customJsons }
    },
    loadExtensionData(data: { activeIds?: string[], customExts?: any[] }) {
      if (data.customExts?.length) {
        for (const raw of data.customExts) {
          if (!raw.id || !raw.blocks) continue
          const generators: Record<string, GenFn> = {}
          if (raw.generators) {
            for (const [blockType, template] of Object.entries(raw.generators)) {
              if (typeof template === 'string') {
                generators[blockType] = (block: Blockly.Block, indent = 0) => {
                  let code = template as string
                  for (const field of block.inputList.flatMap(i => i.fieldRow)) {
                    const name = (field as any).name
                    if (name) code = code.replace(new RegExp(`\\$\\{${name}\\}`, 'g'), String(block.getFieldValue(name) ?? ''))
                  }
                  const prefix = '  '.repeat(indent)
                  return code.split('\n').map((line, i) => i === 0 ? prefix + line : prefix + line).join('\n')
                }
              }
            }
          }
          const ext: Extension = {
            id: raw.id, name: raw.name || raw.id, nameEn: raw.nameEn || raw.name || raw.id,
            colour: raw.colour || '#FF6B6B', icon: raw.icon || '🧩', official: false,
            blocks: raw.blocks, generators,
            _rawJson: raw,
          } as any
          try { registerExtension(ext) } catch {}
        }
      }
      if (data.activeIds?.length) {
        for (const id of data.activeIds) {
          try { activateExtension(id) } catch {}
        }
      }
      rebuildToolbox()
    },
  }

  // Listen for workspace changes
  workspace.addChangeListener(handleWorkspaceChange)

  // 语言切换：保存XML和扩展状态到localStorage，重载页面后恢复
  watch(() => i18n.value.lang, () => {
    const xml = Blockly.Xml.workspaceToDom(workspace!)
    const xmlStr = Blockly.Xml.domToText(xml)
    localStorage.setItem('tacz_workspace', xmlStr)
    // 保存激活的扩展ID列表
    const activeIds = getActiveExtensions().map(e => e.id)
    localStorage.setItem('tacz_active_exts', JSON.stringify(activeIds))
    // 保存自定义扩展的原始JSON数据
    const customExts = getRegisteredExtensions().filter(e => !e.official)
    const customJsons = customExts.map(e => (e as any)._rawJson).filter(Boolean)
    if (customJsons.length) localStorage.setItem('tacz_custom_exts', JSON.stringify(customJsons))
    window.location.reload()
  })

  // 页面加载后恢复之前保存的工作区
  const saved = localStorage.getItem('tacz_workspace')
  if (saved) {
    try {
      const xml = Blockly.utils.xml.textToDom(saved)
      Blockly.Xml.domToWorkspace(xml, workspace!)
    } catch {}
    localStorage.removeItem('tacz_workspace')
  }

  // 恢复自定义扩展
  const savedCustomExts = localStorage.getItem('tacz_custom_exts')
  if (savedCustomExts) {
    try {
      const extList = JSON.parse(savedCustomExts)
      for (const data of extList) {
        if (!data.id || !data.blocks) continue
        const generators: Record<string, GenFn> = {}
        if (data.generators) {
          for (const [blockType, template] of Object.entries(data.generators)) {
            if (typeof template === 'string') {
              generators[blockType] = (block: Blockly.Block, indent = 0) => {
                let code = template as string
                for (const field of block.inputList.flatMap(i => i.fieldRow)) {
                  const name = (field as any).name
                  if (name) code = code.replace(new RegExp(`\\$\\{${name}\\}`, 'g'), String(block.getFieldValue(name) ?? ''))
                }
                const prefix = '  '.repeat(indent)
                return code.split('\n').map((line, i) => i === 0 ? prefix + line : prefix + line).join('\n')
              }
            }
          }
        }
        const ext: Extension = {
          id: data.id, name: data.name || data.id, nameEn: data.nameEn || data.name || data.id,
          colour: data.colour || '#FF6B6B', icon: data.icon || '🧩', official: false,
          blocks: data.blocks, generators,
          _rawJson: data,
        } as any
        registerExtension(ext)
      }
    } catch {}
    localStorage.removeItem('tacz_custom_exts')
  }

  // 恢复激活的扩展
  const savedActiveExts = localStorage.getItem('tacz_active_exts')
  if (savedActiveExts) {
    try {
      const ids: string[] = JSON.parse(savedActiveExts)
      for (const id of ids) activateExtension(id)
    } catch {}
    localStorage.removeItem('tacz_active_exts')
  }

  // 恢复扩展后刷新工具箱
  if (savedCustomExts || savedActiveExts) {
    rebuildToolbox()
  }

  // Double-click on custom_lua block opens the code editor
  // Use Blockly's built-in gesture system
  let lastClickTime = 0
  let lastClickBlockId = ''
  workspace.addChangeListener((event: Blockly.Events.Abstract) => {
    if (event.type === Blockly.Events.CLICK) {
      const clickEvent = event as any
      if (clickEvent.blockId) {
        const now = Date.now()
        if (clickEvent.blockId === lastClickBlockId && now - lastClickTime < 400) {
          const block = workspace!.getBlockById(clickEvent.blockId)
          if (block && block.type === 'custom_lua') {
            openLuaEditor(block)
          }
          lastClickBlockId = ''
        } else {
          lastClickBlockId = clickEvent.blockId
        }
        lastClickTime = now
      }
    }
  })

  // Initial code generation
  handleWorkspaceChange({ type: '' } as any)
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
.workspace-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}
.blockly-container {
  width: 100%;
  height: 100%;
}
.blockly-toast {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  z-index: 100;
  pointer-events: none;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
}
.blockly-toast.warning {
  background: rgba(255, 152, 0, 0.92);
  color: white;
}
.blockly-toast.error {
  background: rgba(229, 57, 53, 0.92);
  color: white;
}
.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from { opacity: 0; transform: translateX(-50%) translateY(10px); }
.toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(10px); }

/* Extension Dialog */
.ext-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; display: flex; align-items: center; justify-content: center; }
.ext-modal { width: 420px; max-width: 90vw; max-height: 80vh; background: #1e1e2e; border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
.ext-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: #181825; border-bottom: 1px solid #313244; color: #cdd6f4; font-size: 14px; font-weight: 600; }
.ext-close { background: none; border: none; color: #6c7086; font-size: 18px; cursor: pointer; padding: 2px 6px; border-radius: 4px; }
.ext-close:hover { background: #313244; color: #cdd6f4; }
.ext-body { padding: 16px; overflow-y: auto; flex: 1; }
.ext-section-title { font-size: 12px; color: #6c7086; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.ext-list { display: flex; flex-direction: column; gap: 4px; }
.ext-item { display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 6px; cursor: pointer; transition: background 0.15s; font-size: 13px; color: #cdd6f4; }
.ext-item:hover { background: #313244; }
.ext-item.active { background: rgba(139, 92, 246, 0.15); }
.ext-check { font-size: 14px; min-width: 18px; }
.ext-icon { font-size: 16px; }
.ext-name { flex: 1; }
.ext-count { font-size: 11px; color: #6c7086; }
.ext-remove { background: none; border: none; cursor: pointer; font-size: 14px; padding: 2px 4px; border-radius: 4px; opacity: 0.5; }
.ext-remove:hover { opacity: 1; background: rgba(229, 57, 53, 0.2); }
.ext-empty { font-size: 12px; color: #6c7086; padding: 8px; text-align: center; }
.ext-import-row { display: flex; gap: 8px; margin-top: 12px; }
.ext-import-btn { flex: 1; padding: 8px 12px; background: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; font-size: 12px; cursor: pointer; transition: background 0.15s; }
.ext-import-btn:hover { background: #45475a; }
.ext-footer { padding: 10px 16px; background: #181825; border-top: 1px solid #313244; display: flex; justify-content: flex-end; }
.ext-btn { padding: 6px 20px; border-radius: 6px; border: none; font-size: 13px; cursor: pointer; transition: background 0.15s; }
.ext-btn.confirm { background: #8B5CF6; color: white; }
.ext-btn.confirm:hover { background: #7C3AED; }
.ext-tutorial-modal { width: 600px; max-width: 90vw; }
.ext-tutorial-body { max-height: 60vh; overflow-y: auto; }
.ext-tutorial-code { font-size: 12px; color: #cdd6f4; background: #181825; padding: 12px; border-radius: 8px; white-space: pre-wrap; word-break: break-all; line-height: 1.6; margin: 6px 0; font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace; }
.ext-tutorial-content h4 { color: #cba6f7; margin: 14px 0 6px 0; font-size: 14px; }
.ext-tutorial-content p { color: #bac2de; font-size: 12px; margin: 4px 0; line-height: 1.5; }
.ext-tutorial-content code { background: #313244; padding: 1px 5px; border-radius: 3px; font-size: 11px; color: #a6e3a1; }
.ext-tutorial-content ul { color: #bac2de; font-size: 12px; padding-left: 20px; margin: 4px 0; }
.ext-tutorial-content li { margin: 3px 0; line-height: 1.5; }
.ext-tutorial-content b { color: #f9e2af; }
</style>
