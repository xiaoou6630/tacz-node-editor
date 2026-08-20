<template>
  <div class="workspace-wrapper">
    <div ref="blocklyDiv" class="blockly-container"></div>
    <div v-if="showEmptyHint" class="workspace-hint">{{ _b('从左侧工具箱拖入事件积木开始编程', 'Drag blocks from the toolbox to start') }}</div>
    <Transition name="toast">
      <div v-if="toastMsg" class="blockly-toast" :class="toastType">
        <span class="toast-icon">{{ toastType === 'error' ? '🚫' : '⚠️' }}</span>
        {{ toastMsg }}
      </div>
    </Transition>
    <LuaCodeEditor
      :visible="luaEditorVisible"
      :code="luaEditorCode"
      :mode="currentMode"
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
                v-for="ext in registeredExts.filter(e => e.official && (currentMode !== 'kjs' ? true : !!e.kjsGenerators))"
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
            <div class="ext-tutorial-mode-banner">{{ currentMode === 'kjs' ? _b('📌 当前模式: KJS — 使用 .kjs-ext.json 格式', '📌 Mode: KJS — Use .kjs-ext.json format') : _b('📌 当前模式: TACZ — 使用 .tacz-ext.json 格式', '📌 Mode: TACZ — Use .tacz-ext.json format') }}</div>
            <div class="ext-tutorial-content">
              <h4>1. 扩展文件是什么？</h4>
              <p>扩展文件是一个 <code>{{ currentMode === 'kjs' ? '.kjs-ext.json' : '.tacz-ext.json' }}</code> 文件，一个文件 = 一个积木栏分类。</p>
              <p>导入后会自动在{{ currentMode === 'kjs' ? 'KJS 模式' : 'TACZ 模式' }}工具箱中添加一个新的积木分类。</p>

              <h4>2. 文件基本结构</h4>
              <pre class="ext-tutorial-code">{{ currentMode === 'kjs' ? `{
  "id": "my_ext",          // 必填，唯一标识（英文+下划线）
  "name": "我的扩展",       // 必填，中文名
  "nameEn": "My Extension", // 必填，英文名
  "colour": "#FF6B6B",     // 必填，分类颜色（十六进制）
  "icon": "🚀",            // 必填，分类图标（emoji）
  "blocks": [ ... ],       // 必填，积木定义列表
  "generators": { ... }    // 必填，JS 代码生成器
}` : `{
  "id": "my_ext",
  "name": "我的扩展",
  "nameEn": "My Extension",
  "colour": "#FF6B6B",
  "icon": "🚀",
  "blocks": [ ... ],
  "generators": { ... }
}` }}</pre>

              <h4>3. 积木定义 (blocks)</h4>
              <p>每个积木定义包含以下字段：</p>
              <pre class="ext-tutorial-code">{{ currentMode === 'kjs' ? `{
  "type": "my_block",
  "message0": "🚀 我的积木 %1",
  "args0": [ ... ],
  "previousStatement": "kjs_stmt",
  "nextStatement": "kjs_stmt",
  "output": "Boolean",
  "colour": "#FF6B6B",
  "tooltip": "提示文字"
}` : `{
  "type": "my_block",
  "message0": "🚀 我的积木 %1",
  "args0": [ ... ],
  "previousStatement": "action_stmt",
  "nextStatement": "action_stmt",
  "output": "Boolean",
  "colour": "#FF6B6B",
  "tooltip": "提示文字"
}` }}</pre>

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
                <li><code>{{ currentMode === 'kjs' ? '"kjs_stmt"' : '"action_stmt"' }}</code> — {{ currentMode === 'kjs' ? _b('KJS 语句链', 'KJS statement chain') : _b('动作积木链（播放动画、触发事件等）', 'Action statement chain') }}</li>
                <li><code>"state_stmt"</code> — {{ _b('状态定义链（entry/update/exit）', 'State definition chain') }}</li>
                <li><code>"Boolean"</code> — {{ _b('布尔值输出', 'Boolean output') }}</li>
                <li><code>"Number"</code> — {{ _b('数值输出', 'Number output') }}</li>
                <li><code>"String"</code> — {{ _b('字符串输出', 'String output') }}</li>
              </ul>
              <p>有 previousStatement/nextStatement → 语句积木（上下连接）</p>
              <p>有 output → 值积木（输出到其他积木的输入口）</p>

              <h4>6. 代码生成器 (generators)</h4>
              <p>key = 积木 type，value = {{ currentMode === 'kjs' ? 'JS' : 'Lua' }} 代码模板字符串</p>
              <p>用 <code>${字段名}</code> 引用积木字段值</p>
              <pre class="ext-tutorial-code">"generators": {
  "my_block": {{ currentMode === 'kjs' ? '"  console.log(\\"${KEY}\\", ${COUNT})"' : '"  context:myMethod(\\"${KEY}\\", ${COUNT})"' }}
}</pre>
              <p>语句积木模板以 2 空格缩进开头，值积木直接返回表达式：</p>
              <pre class="ext-tutorial-code">// 语句积木（有上下连接）
{{ currentMode === 'kjs' ? '"my_action": "  console.log(\\"${VALUE}\\")"' : '"my_action": "  context:doSomething(\\"${VALUE}\\")"' }}

// 值积木（有输出）
{{ currentMode === 'kjs' ? '"my_value": "event.getEntity()"' : '"my_value": "context:getValue()"' }}</pre>

              <template v-if="currentMode === 'kjs'">
              <h4>7. 可用的 JS API</h4>
              <p>KJS 模式生成的代码运行在 KubeJS 环境中，支持以下事件组：</p>
              <p><b>KubeJS 核心事件：</b></p>
              <ul>
                <li><code>BlockEvents.rightClicked/leftClicked/placed/broken/drops/farmlandTrampled/randomTick</code></li>
                <li><code>EntityEvents.death/beforeHurt/afterHurt/spawned/drops/checkSpawn</code></li>
                <li><code>PlayerEvents.loggedIn/loggedOut/respawned/chat/advancement/inventoryChanged/tick</code></li>
                <li><code>ItemEvents.rightClicked/crafted/smelted/foodEaten/pickedUp/dropped/modifyTooltips</code></li>
                <li><code>LevelEvents.loaded/saved/unloaded/tick/beforeExplosion/afterExplosion</code></li>
                <li><code>ServerEvents.loaded/unloaded/tick/recipes/afterRecipes/tags/command/basicCommand</code></li>
                <li><code>ClientEvents.loggedIn/loggedOut/tick/lang/leftDebugInfo/rightDebugInfo/highlight</code></li>
                <li><code>StartupEvents.init/postInit/registry/modifyCreativeTab</code></li>
              </ul>
              <p><b>TaCZJS 事件：</b></p>
              <ul>
                <li><code>TaCZServerEvents.entityShoot/entityAim/entityMelee/entityReload</code></li>
                <li><code>TaCZServerEvents.gunDataLoad/attachmentDataLoad/attachmentTagsLoad</code></li>
                <li><code>TaCZServerEvents.gunIndexLoad/ammoIndexLoad/attachmentIndexLoad</code></li>
                <li><code>TaCZClientEvents.gunIndexLoad/playerAim/playerShoot/playerMelee/playerReload</code></li>
                <li><code>TaCZStartupEvents.recipeLoadBegin/recipeLoad/recipeLoadEnd</code></li>
                <li><code>TaCZStartupEvents.gunDataLoad/attachmentDataLoad/attachmentTagsLoad</code></li>
                <li><code>TaCZStartupEvents.gunIndexLoad/ammoIndexLoad/attachmentIndexLoad</code></li>
              </ul>
              <p><b>KubeJS-Create 事件：</b></p>
              <ul>
                <li><code>CreateEvents.boilerHeatHandler/pipeFluidEffect/spoutHandler</code></li>
              </ul>
              <p><b>事件对象常用方法：</b></p>
              <ul>
                <li><code>event.getEntity()</code> — 获取实体</li>
                <li><code>event.getPlayer()</code> / <code>event.getLevel()</code> — 获取玩家/世界</li>
                <li><code>event.getBlock()</code> / <code>event.getItem()</code> / <code>event.getSource()</code> — 获取方块/物品/伤害源</li>
                <li><code>event.getGunId()</code> / <code>event.getGunItem()</code> — 获取枪械信息（TaCZJS）</li>
                <li><code>event.cancel()</code> / <code>event.exit(value)</code> — 取消/退出事件</li>
                <li><code>event.getDamage()</code> / <code>event.setDamage(value)</code> — 获取/设置伤害</li>
                <li><code>event.remove(filter)</code> / <code>event.add(tag, values)</code> — 配方/标签操作</li>
              </ul>
              </template>
              <template v-else>
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
    "heal_player": "  context:heal($" + "{AMOUNT})",
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
              </template>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <input ref="extFileInput" type="file" :accept="currentMode === 'kjs' ? '.kjs-ext.json' : '.tacz-ext.json'" style="display:none" @change="handleImportExt" />
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
// KJS 模式状态
import { currentMode, activeKJSTab, kjsWorkspaceXMLs, type KJSTab } from '../mode'

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
// 保存 TACZ 模式状态（用于模式切换恢复）
let savedTaczXml = ''
let savedTaczExts: string[] = []
const showEmptyHint = ref(true)

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
      const kjsGenerators: Record<string, GenFn> = {}
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
      // 读取 KJS 生成器（扩展可同时包含两种生成器）
      if (data.kjsGenerators) {
        for (const [blockType, template] of Object.entries(data.kjsGenerators)) {
          if (typeof template === 'string') {
            kjsGenerators[blockType] = (block: Blockly.Block, indent = 0) => {
              let code = template as string
              for (const field of block.inputList.flatMap(i => i.fieldRow)) {
                const name = (field as any).name
                if (name) {
                  code = code.replace(new RegExp(`\\$\\{${name}\\}`, 'g'), String(block.getFieldValue(name) ?? ''))
                }
              }
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
        kjsGenerators: Object.keys(kjsGenerators).length > 0 ? kjsGenerators : undefined,
        _rawJson: data,
      } as any
      registerExtension(ext)
      activateExtension(ext.id)
      registeredExts.value = [...getRegisteredExtensions()]
      rebuildToolbox()
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
    // 忽略 kjs_stmt 连接类型（KJS 模式使用）
    const aChecks = a.getCheck() || []
    const bChecks = b.getCheck() || []
    if (aChecks.includes('kjs_stmt') || bChecks.includes('kjs_stmt')) return true
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
  if (currentMode.value === 'kjs') {
    return buildKJSToolbox(activeKJSTab.value)
  }
  return buildTaczToolbox()
}

function buildTaczToolbox(): Blockly.utils.toolbox.ToolboxDefinition {
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
          { kind: 'block', type: 'check_aim_progress' },
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

// ─── KJS Toolbox ───
function buildKJSToolbox(tab: KJSTab): Blockly.utils.toolbox.ToolboxDefinition {
  // 通用积木分类（所有标签共享）
  const jsLogicCategory = {
    kind: 'category' as const, name: _b('📐 JS 逻辑控制', '📐 JS Logic'), colour: '#98C379',
    contents: [
      { kind: 'block', type: 'kjs_if' },
      { kind: 'block', type: 'kjs_for_each' },
      { kind: 'block', type: 'kjs_var_set' },
      { kind: 'block', type: 'kjs_var_get' },
      { kind: 'block', type: 'kjs_comment' },
      { kind: 'block', type: 'kjs_console_log' },
      { kind: 'block', type: 'kjs_while' },
      { kind: 'block', type: 'kjs_do_while' },
      { kind: 'block', type: 'kjs_for' },
      { kind: 'block', type: 'kjs_switch' },
      { kind: 'block', type: 'kjs_case' },
      { kind: 'block', type: 'kjs_default' },
      { kind: 'block', type: 'kjs_try' },
      { kind: 'block', type: 'kjs_break' },
      { kind: 'block', type: 'kjs_continue' },
      { kind: 'block', type: 'kjs_throw' },
    ],
  }
  const mathCategory = {
    kind: 'category' as const, name: _b('🔢 数学运算', '🔢 Math'), colour: '#DDA0DD',
    contents: [
      { kind: 'block', type: 'math_add' },
      { kind: 'block', type: 'math_sub' },
      { kind: 'block', type: 'math_mul' },
      { kind: 'block', type: 'math_div' },
    ],
  }
  const valuesCategory = {
    kind: 'category' as const, name: _b('📝 数值/文本', '📝 Values'), colour: '#4B70DD',
    contents: [
      { kind: 'block', type: 'math_number' },
      { kind: 'block', type: 'text' },
      { kind: 'block', type: 'logic_boolean' },
      { kind: 'block', type: 'logic_compare' },
      { kind: 'block', type: 'logic_operation' },
      { kind: 'block', type: 'logic_negate' },
      { kind: 'block', type: 'kjs_res_loc' },
      { kind: 'block', type: 'kjs_json_literal' },
    ],
  }
  const customCategory = {
    kind: 'category' as const, name: _b('💻 自定义代码', '💻 Custom Code'), colour: '#9C27B0',
    contents: [
      { kind: 'block', type: 'kjs_custom_js' },
    ],
  }

  // 服务端特有分类
  const serverCategories = [
    // 1. TaCZJS 事件（合并服务端事件 + 加载事件）
    {
      kind: 'category' as const, name: _b('📌 TaCZJS 服务端事件', '📌 TaCZJS Server Events'), colour: '#FF69B4',
      contents: [
        { kind: 'block', type: 'kjs_tacz_s_entity_shoot' },
        { kind: 'block', type: 'kjs_tacz_s_entity_aim' },
        { kind: 'block', type: 'kjs_tacz_s_entity_melee' },
        { kind: 'block', type: 'kjs_tacz_s_entity_reload' },
        { kind: 'block', type: 'kjs_tacz_s_gun_data_load' },
        { kind: 'block', type: 'kjs_tacz_s_attachment_data_load' },
        { kind: 'block', type: 'kjs_tacz_s_attachment_tags_load' },
        { kind: 'block', type: 'kjs_tacz_s_gun_index_load' },
        { kind: 'block', type: 'kjs_tacz_s_ammo_index_load' },
        { kind: 'block', type: 'kjs_tacz_s_attachment_index_load' },
      ],
    },
    // 2. KubeJS 服务端事件
    {
      kind: 'category' as const, name: _b('📌 KubeJS 服务端事件', '📌 KubeJS Server Events'), colour: '#61AFEF',
      contents: [
        { kind: 'block', type: 'kjs_server_loaded' },
        { kind: 'block', type: 'kjs_server_unloaded' },
        { kind: 'block', type: 'kjs_server_tick' },
        { kind: 'block', type: 'kjs_server_recipes' },
        { kind: 'block', type: 'kjs_server_after_recipes' },
        { kind: 'block', type: 'kjs_server_tags' },
        { kind: 'block', type: 'kjs_server_command' },
        { kind: 'block', type: 'kjs_server_basic_command' },
      ],
    },
    // 3～7. 各种事件
    {
      kind: 'category' as const, name: _b('📍 方块事件', '📍 Block Events'), colour: '#56A34A',
      contents: [
        { kind: 'block', type: 'kjs_block_right_clicked' },
        { kind: 'block', type: 'kjs_block_left_clicked' },
        { kind: 'block', type: 'kjs_block_placed' },
        { kind: 'block', type: 'kjs_block_broken' },
        { kind: 'block', type: 'kjs_block_drops' },
        { kind: 'block', type: 'kjs_block_farmland_trampled' },
        { kind: 'block', type: 'kjs_block_random_tick' },
      ],
    },
    {
      kind: 'category' as const, name: _b('👹 实体事件', '👹 Entity Events'), colour: '#E06C75',
      contents: [
        { kind: 'block', type: 'kjs_entity_death' },
        { kind: 'block', type: 'kjs_entity_before_hurt' },
        { kind: 'block', type: 'kjs_entity_after_hurt' },
        { kind: 'block', type: 'kjs_entity_spawned' },
        { kind: 'block', type: 'kjs_entity_drops' },
        { kind: 'block', type: 'kjs_entity_check_spawn' },
      ],
    },
    {
      kind: 'category' as const, name: _b('👤 玩家事件', '👤 Player Events'), colour: '#4B70DD',
      contents: [
        { kind: 'block', type: 'kjs_player_logged_in' },
        { kind: 'block', type: 'kjs_player_logged_out' },
        { kind: 'block', type: 'kjs_player_respawned' },
        { kind: 'block', type: 'kjs_player_chat' },
        { kind: 'block', type: 'kjs_player_advancement' },
        { kind: 'block', type: 'kjs_player_inventory_changed' },
        { kind: 'block', type: 'kjs_player_tick' },
      ],
    },
    {
      kind: 'category' as const, name: _b('📦 物品事件', '📦 Item Events'), colour: '#F39C12',
      contents: [
        { kind: 'block', type: 'kjs_item_right_clicked' },
        { kind: 'block', type: 'kjs_item_crafted' },
        { kind: 'block', type: 'kjs_item_smelted' },
        { kind: 'block', type: 'kjs_item_food_eaten' },
        { kind: 'block', type: 'kjs_item_picked_up' },
        { kind: 'block', type: 'kjs_item_dropped' },
        { kind: 'block', type: 'kjs_item_modify_tooltips' },
      ],
    },
    {
      kind: 'category' as const, name: _b('🌍 世界事件', '🌍 Level Events'), colour: '#26A69A',
      contents: [
        { kind: 'block', type: 'kjs_level_loaded' },
        { kind: 'block', type: 'kjs_level_tick' },
        { kind: 'block', type: 'kjs_level_saved' },
        { kind: 'block', type: 'kjs_level_before_explosion' },
        { kind: 'block', type: 'kjs_level_after_explosion' },
      ],
    },
    // 8. 事件操作 + 工具（合并为一个大分类）
    {
      kind: 'category' as const, name: _b('🔧 操作与工具', '🔧 Actions & Utils'), colour: '#DDA0DD',
      contents: [
        { kind: 'block', type: 'kjs_ev_cancel_shoot' },
        { kind: 'block', type: 'kjs_ev_cancel_aim' },
        { kind: 'block', type: 'kjs_ev_cancel_melee' },
        { kind: 'block', type: 'kjs_ev_cancel_reload' },
        { kind: 'block', type: 'kjs_ev_get_entity' },
        { kind: 'block', type: 'kjs_ev_get_shooter' },
        { kind: 'block', type: 'kjs_ev_get_gun_id' },
        { kind: 'block', type: 'kjs_ev_get_gun_item' },
        { kind: 'block', type: 'kjs_ev_get_heat_progress' },
        { kind: 'block', type: 'kjs_ev_get_heat_amount' },
        { kind: 'block', type: 'kjs_ev_get_id' },
        { kind: 'block', type: 'kjs_ev_get_json' },
        { kind: 'block', type: 'kjs_ev_get_std_json' },
        { kind: 'block', type: 'kjs_ev_set_json' },
        { kind: 'block', type: 'kjs_ev_get_gun_data' },
        { kind: 'block', type: 'kjs_ev_get_attach_data' },
        { kind: 'block', type: 'kjs_ev_get_pojo' },
        { kind: 'block', type: 'kjs_ev_get_attach_tags' },
        { kind: 'block', type: 'kjs_ev_get_table_recipe' },
        { kind: 'block', type: 'kjs_ev_remove_gun' },
        { kind: 'block', type: 'kjs_ev_remove_attachment' },
        { kind: 'block', type: 'kjs_ev_remove_recipe' },
        { kind: 'block', type: 'kjs_ev_remove_all_recipes' },
        { kind: 'block', type: 'kjs_ev_put_recipe' },
        { kind: 'block', type: 'kjs_ev_kill_entity' },
        { kind: 'block', type: 'kjs_utils_open_refit' },
        { kind: 'block', type: 'kjs_utils_hold_gun' },
        { kind: 'block', type: 'kjs_utils_get_gun_idx' },
        { kind: 'block', type: 'kjs_utils_get_ammo_idx' },
        { kind: 'block', type: 'kjs_utils_get_attach_idx' },
        { kind: 'block', type: 'kjs_util_get_all_players' },
        { kind: 'block', type: 'kjs_util_send_msg' },
        { kind: 'block', type: 'kjs_util_run_cmd' },
        { kind: 'block', type: 'kjs_util_schedule' },
        // 通用值积木
        { kind: 'block', type: 'kjs_ev_get_player' },
        { kind: 'block', type: 'kjs_ev_get_level' },
        { kind: 'block', type: 'kjs_ev_get_block' },
        { kind: 'block', type: 'kjs_ev_get_item' },
        { kind: 'block', type: 'kjs_ev_get_server' },
        { kind: 'block', type: 'kjs_ev_get_source' },
        { kind: 'block', type: 'kjs_ev_get_hand' },
        { kind: 'block', type: 'kjs_ev_get_facing' },
        { kind: 'block', type: 'kjs_ev_get_message' },
        { kind: 'block', type: 'kjs_ev_get_username' },
        { kind: 'block', type: 'kjs_ev_get_random' },
        { kind: 'block', type: 'kjs_ev_get_damage' },
        { kind: 'block', type: 'kjs_ev_set_damage' },
        { kind: 'block', type: 'kjs_ev_get_position' },
        { kind: 'block', type: 'kjs_ev_get_size' },
        { kind: 'block', type: 'kjs_ev_set_size' },
        { kind: 'block', type: 'kjs_ev_get_affected_entities' },
        { kind: 'block', type: 'kjs_ev_get_affected_blocks' },
        { kind: 'block', type: 'kjs_ev_remove_knockback' },
        { kind: 'block', type: 'kjs_ev_get_drops' },
        { kind: 'block', type: 'kjs_ev_add_drop' },
        { kind: 'block', type: 'kjs_ev_is_recently_hit' },
        { kind: 'block', type: 'kjs_ev_get_chat_component' },
        { kind: 'block', type: 'kjs_ev_set_chat_component' },
        { kind: 'block', type: 'kjs_ev_cancel' },
        { kind: 'block', type: 'kjs_ev_set_result' },
        { kind: 'block', type: 'kjs_ev_log' },
      ],
    },
    // 9. 配方/标签/阶段
    {
      kind: 'category' as const, name: _b('📝 配方操作', '📝 Recipe Ops'), colour: '#E06C75',
      contents: [
        { kind: 'block', type: 'kjs_recipe_remove' },
        { kind: 'block', type: 'kjs_recipe_replace_input' },
        { kind: 'block', type: 'kjs_recipe_replace_output' },
      ],
    },
    {
      kind: 'category' as const, name: _b('🏷️ 标签操作', '🏷️ Tag Ops'), colour: '#98C379',
      contents: [
        { kind: 'block', type: 'kjs_tag_add' },
        { kind: 'block', type: 'kjs_tag_remove' },
        { kind: 'block', type: 'kjs_tag_remove_all' },
      ],
    },
    {
      kind: 'category' as const, name: _b('🎯 玩家阶段', '🎯 Player Stages'), colour: '#4B70DD',
      contents: [
        { kind: 'block', type: 'kjs_stage_get' },
        { kind: 'block', type: 'kjs_stage_add' },
        { kind: 'block', type: 'kjs_stage_remove' },
      ],
    },
    // 10. Create 配方
    {
      kind: 'category' as const, name: _b('🔧 Create 配方', '🔧 Create Recipes'), colour: '#E06C75',
      contents: [
        { kind: 'block', type: 'kjs_create_rc_crushing' },
        { kind: 'block', type: 'kjs_create_rc_milling' },
        { kind: 'block', type: 'kjs_create_rc_cutting' },
        { kind: 'block', type: 'kjs_create_rc_mixing' },
        { kind: 'block', type: 'kjs_create_rc_compacting' },
        { kind: 'block', type: 'kjs_create_rc_pressing' },
        { kind: 'block', type: 'kjs_create_rc_filling' },
        { kind: 'block', type: 'kjs_create_rc_emptying' },
        { kind: 'block', type: 'kjs_create_rc_splashing' },
        { kind: 'block', type: 'kjs_create_rc_haunting' },
        { kind: 'block', type: 'kjs_create_rc_deploying' },
        { kind: 'block', type: 'kjs_create_rc_item_app' },
      ],
    },
  ]

  // 客户端特有分类
  const clientCategories = [
    {
      kind: 'category' as const, name: _b('📌 TaCZJS 客户端事件', '📌 TaCZJS Client Events'), colour: '#4ECDC4',
      contents: [
        { kind: 'block', type: 'kjs_tacz_c_client_gun_index' },
        { kind: 'block', type: 'kjs_tacz_c_client_aim' },
        { kind: 'block', type: 'kjs_tacz_c_client_shoot' },
        { kind: 'block', type: 'kjs_tacz_c_client_melee' },
        { kind: 'block', type: 'kjs_tacz_c_client_reload' },
      ],
    },
    {
      kind: 'category' as const, name: _b('📌 KubeJS 客户端事件', '📌 KubeJS Client Events'), colour: '#87CEEB',
      contents: [
        { kind: 'block', type: 'kjs_client_logged_in' },
        { kind: 'block', type: 'kjs_client_logged_out' },
        { kind: 'block', type: 'kjs_client_tick' },
        { kind: 'block', type: 'kjs_client_lang' },
        { kind: 'block', type: 'kjs_client_left_debug' },
        { kind: 'block', type: 'kjs_client_right_debug' },
        { kind: 'block', type: 'kjs_client_highlight' },
      ],
    },
    {
      kind: 'category' as const, name: _b('🔧 操作+工具', '🔧 Actions & Utils'), colour: '#DDA0DD',
      contents: [
        { kind: 'block', type: 'kjs_ev_cancel_shoot' },
        { kind: 'block', type: 'kjs_ev_cancel_aim' },
        { kind: 'block', type: 'kjs_ev_cancel_melee' },
        { kind: 'block', type: 'kjs_ev_cancel_reload' },
        { kind: 'block', type: 'kjs_ev_set_vanilla' },
        { kind: 'block', type: 'kjs_ev_is_vanilla' },
        { kind: 'block', type: 'kjs_ev_get_entity' },
        { kind: 'block', type: 'kjs_ev_get_gun_id' },
        { kind: 'block', type: 'kjs_utils_open_refit' },
        { kind: 'block', type: 'kjs_utils_hold_gun' },
        { kind: 'block', type: 'kjs_utils_get_gun_idx' },
        { kind: 'block', type: 'kjs_utils_get_ammo_idx' },
        { kind: 'block', type: 'kjs_utils_get_attach_idx' },
        { kind: 'block', type: 'kjs_utils_gun_display' },
        { kind: 'block', type: 'kjs_utils_gun_operator' },
        { kind: 'block', type: 'kjs_utils_block_hit' },
        { kind: 'block', type: 'kjs_utils_entity_hit' },
        { kind: 'block', type: 'kjs_utils_can_interact' },
        { kind: 'block', type: 'kjs_ev_get_level' },
        { kind: 'block', type: 'kjs_ev_log' },
        { kind: 'block', type: 'kjs_ev_cancel' },
        { kind: 'block', type: 'kjs_ev_get_source' },
        { kind: 'block', type: 'kjs_ev_get_hand' },
        { kind: 'block', type: 'kjs_ev_get_facing' },
        { kind: 'block', type: 'kjs_ev_get_message' },
        { kind: 'block', type: 'kjs_ev_get_username' },
        { kind: 'block', type: 'kjs_ev_get_random' },
        { kind: 'block', type: 'kjs_ev_get_position' },
        { kind: 'block', type: 'kjs_ev_get_drops' },
        { kind: 'block', type: 'kjs_ev_add_drop' },
        { kind: 'block', type: 'kjs_ev_get_chat_component' },
      ],
    },
    {
      kind: 'category' as const, name: _b('🌐 语言文件', '🌐 Lang'), colour: '#87CEEB',
      contents: [
        { kind: 'block', type: 'kjs_lang_add' },
        { kind: 'block', type: 'kjs_lang_rename_item' },
        { kind: 'block', type: 'kjs_lang_rename_block' },
      ],
    },
  ]

  // 启动特有分类
  const startupCategories = [
    {
      kind: 'category' as const, name: _b('📌 TaCZJS 启动事件', '📌 TaCZJS Startup Events'), colour: '#FFD93D',
      contents: [
        { kind: 'block', type: 'kjs_tacz_u_recipe_begin' },
        { kind: 'block', type: 'kjs_tacz_u_recipe_load' },
        { kind: 'block', type: 'kjs_tacz_u_recipe_end' },
        { kind: 'block', type: 'kjs_tacz_u_startup_gun_data' },
        { kind: 'block', type: 'kjs_tacz_u_startup_attach_data' },
        { kind: 'block', type: 'kjs_tacz_u_startup_gun_index' },
        { kind: 'block', type: 'kjs_tacz_u_startup_ammo_index' },
        { kind: 'block', type: 'kjs_tacz_u_startup_attach_index' },
      ],
    },
    {
      kind: 'category' as const, name: _b('📌 KubeJS 启动事件', '📌 KubeJS Startup Events'), colour: '#FF8C00',
      contents: [
        { kind: 'block', type: 'kjs_startup_init' },
        { kind: 'block', type: 'kjs_startup_post_init' },
        { kind: 'block', type: 'kjs_startup_registry' },
        { kind: 'block', type: 'kjs_startup_creative_tab' },
        { kind: 'block', type: 'kjs_item_modification' },
        { kind: 'block', type: 'kjs_block_modification' },
      ],
    },
    {
      kind: 'category' as const, name: _b('📌 Create 事件', '📌 Create Events'), colour: '#E06C75',
      contents: [
        { kind: 'block', type: 'kjs_create_boiler' },
        { kind: 'block', type: 'kjs_create_fluid' },
        { kind: 'block', type: 'kjs_create_spout' },
        { kind: 'block', type: 'kjs_create_boiler_add' },
        { kind: 'block', type: 'kjs_create_fluid_add' },
        { kind: 'block', type: 'kjs_create_spout_add' },
        { kind: 'block', type: 'kjs_create_heat_return' },
        { kind: 'block', type: 'kjs_create_fluid_apply' },
        { kind: 'block', type: 'kjs_cb_block' },
        { kind: 'block', type: 'kjs_cb_level' },
        { kind: 'block', type: 'kjs_cb_aabb' },
        { kind: 'block', type: 'kjs_cb_fluid' },
        { kind: 'block', type: 'kjs_cb_simulate' },
        { kind: 'block', type: 'kjs_create_heat_no_heat' },
      ],
    },
    {
      kind: 'category' as const, name: _b('🔧 事件操作', '🔧 Event Actions'), colour: '#DDA0DD',
      contents: [
        { kind: 'block', type: 'kjs_ev_get_id' },
        { kind: 'block', type: 'kjs_ev_get_json' },
        { kind: 'block', type: 'kjs_ev_get_std_json' },
        { kind: 'block', type: 'kjs_ev_set_json' },
        { kind: 'block', type: 'kjs_ev_get_gun_data' },
        { kind: 'block', type: 'kjs_ev_get_attach_data' },
        { kind: 'block', type: 'kjs_ev_get_pojo' },
        { kind: 'block', type: 'kjs_ev_get_table_recipe' },
        { kind: 'block', type: 'kjs_ev_remove_gun' },
        { kind: 'block', type: 'kjs_ev_remove_attachment' },
        { kind: 'block', type: 'kjs_ev_remove_recipe' },
        { kind: 'block', type: 'kjs_ev_remove_all_recipes' },
        { kind: 'block', type: 'kjs_ev_put_recipe' },
        { kind: 'block', type: 'kjs_ev_get_player' },
        { kind: 'block', type: 'kjs_ev_get_level' },
        { kind: 'block', type: 'kjs_ev_get_block' },
        { kind: 'block', type: 'kjs_ev_get_item' },
        { kind: 'block', type: 'kjs_ev_get_server' },
        { kind: 'block', type: 'kjs_ev_cancel' },
        { kind: 'block', type: 'kjs_ev_set_result' },
        { kind: 'block', type: 'kjs_ev_log' },
        { kind: 'block', type: 'kjs_ev_get_damage' },
        { kind: 'block', type: 'kjs_ev_set_damage' },
        { kind: 'block', type: 'kjs_ev_get_source' },
        { kind: 'block', type: 'kjs_ev_get_hand' },
        { kind: 'block', type: 'kjs_ev_get_facing' },
        { kind: 'block', type: 'kjs_ev_get_message' },
        { kind: 'block', type: 'kjs_ev_get_username' },
        { kind: 'block', type: 'kjs_ev_get_random' },
        { kind: 'block', type: 'kjs_ev_get_position' },
        { kind: 'block', type: 'kjs_ev_get_drops' },
        { kind: 'block', type: 'kjs_ev_add_drop' },
        { kind: 'block', type: 'kjs_ev_get_chat_component' },
      ],
    },
    {
      kind: 'category' as const, name: _b('⌨️ 按键绑定', '⌨️ Key Bindings'), colour: '#7C3AED',
      contents: [
        { kind: 'block', type: 'kjs_keybind_pressed' },
      ],
    },
  ]

  let tabCategories: any[] = []
  if (tab === 'server') tabCategories = serverCategories
  else if (tab === 'client') tabCategories = clientCategories
  else tabCategories = startupCategories

  const extCategories = getExtensionToolboxCategories('kjs')
  return {
    kind: 'categoryToolbox',
    contents: [
      ...tabCategories,
      jsLogicCategory,
      mathCategory,
      valuesCategory,
      customCategory,
      ...extCategories,
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
  const extGens = getExtensionGenerators(currentMode.value)
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
function genValue(block: Blockly.Block, inputName: string, fallback = ''): string {
  const target = block.getInputTargetBlock(inputName)
  if (!target || !target.isEnabled()) return fallback
  const extGens = getExtensionGenerators(currentMode.value)
  const allGens = { ...luaGen, ...extGens }
  const func = allGens[target.type]
  if (!func) return fallback
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
  const cond = genValue(block, 'COND', 'true')
  return `${'  '.repeat(indent)}-- transition: ${from} → ${to} if ${cond}`
}

// Animation Blocks (correct TACZ API)
luaGen['run_animation'] = (block, indent = 0) => {
  const anim = block.getFieldValue('ANIM') || 'idle'
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  const blend = block.getFieldValue('BLEND') || 'false'
  const mode = block.getFieldValue('MODE') || 'PLAY_ONCE_STOP'
  const blendTime = genValue(block, 'BLEND_TIME', '0.2')
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
  const blendTime = genValue(block, 'BLEND_TIME', '0')
  return `${'  '.repeat(indent)}context:runAnimation("${anim}", ${track}, ${blend}, LOOP, ${blendTime})`
}

luaGen['set_progress'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  const progress = genValue(block, 'PROGRESS', '0')
  const normalization = block.getFieldValue('NORMALIZATION') || 'false'
  return `${'  '.repeat(indent)}context:setAnimationProgress(${track}, ${progress}, ${normalization})`
}

luaGen['adjust_progress'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  const delta = genValue(block, 'DELTA', '0')
  const normalization = block.getFieldValue('NORMALIZATION') || 'false'
  return `${'  '.repeat(indent)}context:adjustAnimationProgress(${track}, ${delta}, ${normalization})`
}

luaGen['play_blended'] = (block, indent = 0) => {
  const anim = block.getFieldValue('ANIM') || 'shoot'
  const line = block.getFieldValue('LINE') || 'STATIC_TRACK_LINE'
  const blend = block.getFieldValue('BLEND') || 'false'
  const mode = block.getFieldValue('MODE') || 'PLAY_ONCE_STOP'
  const blendTime = genValue(block, 'BLEND_TIME', '0')
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
  const value = genValue(block, 'VALUE', '0')
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
  const value = genValue(block, 'VALUE', '0')
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
luaGen['check_aim_progress'] = (block) => {
  const progress = genValue(block, 'PROGRESS', '0')
  return `context:getAimingProgress() >= ${progress}`
}
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
  const index = genValue(block, 'INDEX', '1')
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
  const time = genValue(block, 'TIME', '0')
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
  const max = genValue(block, 'MAX', '3')
  return `${'  '.repeat(indent)}-- cycle melee: ${prefix} counter=${counter} max=${max}`
}
luaGen['track_hold'] = (block, indent = 0) => {
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  return `${'  '.repeat(indent)}context:holdAnimation(${track})`
}
luaGen['adjust_shoot_interval'] = (block, indent = 0) => {
  const delta = genValue(block, 'DELTA', '0')
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
  const index = genValue(block, 'INDEX', '0')
  return `context:assignNewTrack(${index})`
}
luaGen['ensure_track_line_size'] = (block, indent = 0) => {
  const size = genValue(block, 'SIZE', '0')
  return `${'  '.repeat(indent)}context:ensureTrackLineSize(${size})`
}
luaGen['ensure_tracks_amount'] = (block, indent = 0) => {
  const index = genValue(block, 'INDEX', '0')
  const amount = genValue(block, 'AMOUNT', '0')
  return `${'  '.repeat(indent)}context:ensureTracksAmount(${index}, ${amount})`
}
luaGen['get_singleton_track'] = (block) => {
  const index = genValue(block, 'INDEX', '0')
  return `context:getAsSingletonTrack(${index})`
}
luaGen['get_track_line_size'] = () => 'context:getTrackLineSize()'

// Logic Blocks
luaGen['if_node'] = (block, indent = 0) => {
  const cond = genValue(block, 'COND', 'true')
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
  const a = genValue(block, 'A', '0')
  const b = genValue(block, 'B', '0')
  return `(${a} + ${b})`
}
luaGen['math_sub'] = (block) => {
  const a = genValue(block, 'A', '0')
  const b = genValue(block, 'B', '0')
  return `(${a} - ${b})`
}
luaGen['math_mul'] = (block) => {
  const a = genValue(block, 'A', '0')
  const b = genValue(block, 'B', '0')
  return `(${a} * ${b})`
}
luaGen['math_div'] = (block) => {
  const a = genValue(block, 'A', '0')
  const b = genValue(block, 'B', '0')
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
  const a = genValue(block, 'A', 'nil')
  const b = genValue(block, 'B', 'nil')
  const op = block.getFieldValue('OP') || 'EQ'
  const opMap: Record<string, string> = { EQ: '==', NEQ: '~=', LT: '<', GT: '>', LTE: '<=', GTE: '>=' }
  return `(${a} ${opMap[op] || '=='} ${b})`
}
luaGen['logic_operation'] = (block) => {
  const a = genValue(block, 'A', 'false')
  const b = genValue(block, 'B', 'false')
  const op = block.getFieldValue('OP') || 'AND'
  return `(${a} ${op === 'AND' ? 'and' : 'or'} ${b})`
}
luaGen['logic_negate'] = (block) => {
  const a = genValue(block, 'BOOL', 'false')
  return `(not ${a})`
}

// ═══════════════════════════════════════════════════════════
// ─── KJS Code Generator ───
// ═══════════════════════════════════════════════════════════

const kjsGen: Record<string, (block: Blockly.Block, indent?: number) => string> = {}

// KJS Helper functions
function genKJSNext(block: Blockly.Block | null, indent = 1): string {
  if (!block) return ''
  if (!block.isEnabled()) return genKJSNext(block.getNextBlock(), indent)
  const fn = kjsGen[block.type]
  if (!fn) return genKJSNext(block.getNextBlock(), indent)
  const lines: string[] = []
  let current: Blockly.Block | null = block
  while (current) {
    if (current.isEnabled()) {
      const f = kjsGen[current.type]
      if (f) lines.push(f(current, indent))
    }
    current = current.getNextBlock()
  }
  return lines.join('\n')
}

function genKJSValue(block: Blockly.Block, inputName: string, fallback = ''): string {
  const target = block.getInputTargetBlock(inputName)
  if (!target || !target.isEnabled()) return fallback
  const fn = kjsGen[target.type]
  if (!fn) return fallback
  return fn(target)
}

function genKJSStatements(block: Blockly.Block, inputName: string, indent = 1): string {
  const target = block.getInputTargetBlock(inputName)
  if (!target) return ''
  return genKJSNext(target, indent)
}

// 通用帽子生成函数
function hatGen(block: Blockly.Block, _indent: number, ns: string, method: string): string {
  const body = genKJSNext(block.getNextBlock(), 1)
  return `${ns}.${method}((event) => {\n${body || ''}})`
}

// ── TaCZJS Server Event Hats ──
kjsGen['kjs_tacz_s_entity_shoot'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'entityShoot')
kjsGen['kjs_tacz_s_entity_aim'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'entityAim')
kjsGen['kjs_tacz_s_entity_melee'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'entityMelee')
kjsGen['kjs_tacz_s_entity_reload'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'entityReload')
kjsGen['kjs_tacz_s_gun_data_load'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'gunDataLoad')
kjsGen['kjs_tacz_s_attachment_data_load'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'attachmentDataLoad')
kjsGen['kjs_tacz_s_attachment_tags_load'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'attachmentTagsLoad')
kjsGen['kjs_tacz_s_gun_index_load'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'gunIndexLoad')
kjsGen['kjs_tacz_s_ammo_index_load'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'ammoIndexLoad')
kjsGen['kjs_tacz_s_attachment_index_load'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'attachmentIndexLoad')

// ── TaCZJS Client Event Hats ──
kjsGen['kjs_tacz_c_client_gun_index'] = (b, i=0) => hatGen(b, i, 'TaCZClientEvents', 'gunIndexLoad')
kjsGen['kjs_tacz_c_client_aim'] = (b, i=0) => hatGen(b, i, 'TaCZClientEvents', 'playerAim')
kjsGen['kjs_tacz_c_client_shoot'] = (b, i=0) => hatGen(b, i, 'TaCZClientEvents', 'playerShoot')
kjsGen['kjs_tacz_c_client_melee'] = (b, i=0) => hatGen(b, i, 'TaCZClientEvents', 'playerMelee')
kjsGen['kjs_tacz_c_client_reload'] = (b, i=0) => hatGen(b, i, 'TaCZClientEvents', 'playerReload')

// ── TaCZJS Startup Event Hats ──
kjsGen['kjs_tacz_u_recipe_begin'] = (b, i=0) => hatGen(b, i, 'TaCZStartupEvents', 'recipeLoadBegin')
kjsGen['kjs_tacz_u_recipe_load'] = (b, i=0) => hatGen(b, i, 'TaCZStartupEvents', 'recipeLoad')
kjsGen['kjs_tacz_u_recipe_end'] = (b, i=0) => hatGen(b, i, 'TaCZStartupEvents', 'recipeLoadEnd')
kjsGen['kjs_tacz_u_startup_gun_data'] = (b, i=0) => hatGen(b, i, 'TaCZStartupEvents', 'gunDataLoad')
kjsGen['kjs_tacz_u_startup_attach_data'] = (b, i=0) => hatGen(b, i, 'TaCZStartupEvents', 'attachmentDataLoad')
kjsGen['kjs_tacz_u_startup_gun_index'] = (b, i=0) => hatGen(b, i, 'TaCZStartupEvents', 'gunIndexLoad')
kjsGen['kjs_tacz_u_startup_ammo_index'] = (b, i=0) => hatGen(b, i, 'TaCZStartupEvents', 'ammoIndexLoad')
kjsGen['kjs_tacz_u_startup_attach_index'] = (b, i=0) => hatGen(b, i, 'TaCZStartupEvents', 'attachmentIndexLoad')

// ── KubeJS Server Event Hats ──
kjsGen['kjs_server_loaded'] = (b, i=0) => hatGen(b, i, 'ServerEvents', 'loaded')
kjsGen['kjs_server_tick'] = (b, i=0) => hatGen(b, i, 'ServerEvents', 'tick')
kjsGen['kjs_server_recipes'] = (b, i=0) => hatGen(b, i, 'ServerEvents', 'recipes')
kjsGen['kjs_server_after_recipes'] = (b, i=0) => hatGen(b, i, 'ServerEvents', 'afterRecipes')
kjsGen['kjs_server_tags'] = (b, i=0) => hatGen(b, i, 'ServerEvents', 'tags')
kjsGen['kjs_server_command'] = (b, i=0) => {
  const cmd = b.getFieldValue('CMD') || 'mycmd'
  const body = genKJSNext(b.getNextBlock(), 1)
  return `ServerEvents.command('${cmd}', (event) => {\n${body || ''}})`
}

// ── KubeJS Client Event Hats ──
kjsGen['kjs_client_logged_in'] = (b, i=0) => hatGen(b, i, 'ClientEvents', 'loggedIn')
kjsGen['kjs_client_logged_out'] = (b, i=0) => hatGen(b, i, 'ClientEvents', 'loggedOut')
kjsGen['kjs_client_tick'] = (b, i=0) => hatGen(b, i, 'ClientEvents', 'tick')
kjsGen['kjs_client_lang'] = (b, i=0) => {
  const key = b.getFieldValue('KEY') || 'item.modid.xxx'
  const body = genKJSNext(b.getNextBlock(), 1)
  return `ClientEvents.lang('${key}', (event) => {\n${body || ''}})`
}

// ── KubeJS Startup Event Hats ──
kjsGen['kjs_startup_init'] = (b, i=0) => hatGen(b, i, 'StartupEvents', 'init')
kjsGen['kjs_startup_post_init'] = (b, i=0) => hatGen(b, i, 'StartupEvents', 'postInit')
kjsGen['kjs_startup_registry'] = (b, i=0) => {
  const type = b.getFieldValue('TYPE') || 'minecraft:item'
  const body = genKJSNext(b.getNextBlock(), 1)
  return `StartupEvents.registry('${type}', (event) => {\n${body || ''}})`
}
kjsGen['kjs_startup_creative_tab'] = (b, i=0) => {
  const tabId = b.getFieldValue('TABID') || 'minecraft:combat'
  const body = genKJSNext(b.getNextBlock(), 1)
  return `StartupEvents.modifyCreativeTab('${tabId}', (event) => {\n${body || ''}})`
}

// ── Create Event Hats ──
kjsGen['kjs_create_boiler'] = (b, i=0) => hatGen(b, i, 'CreateEvents', 'boilerHeatHandler')
kjsGen['kjs_create_fluid'] = (b, i=0) => hatGen(b, i, 'CreateEvents', 'pipeFluidEffect')
kjsGen['kjs_create_spout'] = (b, i=0) => hatGen(b, i, 'CreateEvents', 'spoutHandler')

// ── KubeJS-Create ──
kjsGen['kjs_create_boiler_add'] = (b,i=0) => `${'  '.repeat(i)}event.add(${genKJSValue(b, 'BLOCK', "''")}, (block) => {\n${genKJSStatements(b,'HANDLER',1)}\n${'  '.repeat(i)}})`
kjsGen['kjs_create_fluid_add'] = (b,i=0) => `${'  '.repeat(i)}event.add(${genKJSValue(b, 'FLUID', "''")}, (level, aabb, fluid) => {\n${genKJSStatements(b,'HANDLER',1)}\n${'  '.repeat(i)}})`
kjsGen['kjs_create_spout_add'] = (b,i=0) => `${'  '.repeat(i)}event.add(${genKJSValue(b, 'PATH', "''")}, ${genKJSValue(b, 'BLOCK', "''")}, (block, fluid, simulate) => {\n${genKJSStatements(b,'HANDLER',1)}\n${'  '.repeat(i)}})`
kjsGen['kjs_create_heat_return'] = (b,i=0) => `${'  '.repeat(i)}return ${genKJSValue(b, 'HEAT', "''")}`
kjsGen['kjs_create_fluid_apply'] = (b,i=0) => `${'  '.repeat(i)}// apply fluid effect: ${genKJSValue(b, 'FLUID', "''")}`

// ── Create 回调变量 ──
kjsGen['kjs_cb_block'] = () => `block`
kjsGen['kjs_cb_level'] = () => `level`
kjsGen['kjs_cb_aabb'] = () => `aabb`
kjsGen['kjs_cb_fluid'] = () => `fluid`
kjsGen['kjs_cb_simulate'] = () => `simulate`
kjsGen['kjs_create_heat_no_heat'] = () => `0`

// ── Create 配方注册（支持动态多输出）──
function genCreateOutput(b: Blockly.Block): string {
  const items: string[] = []
  for (let i = 1; i <= 3; i++) {
    const item = b.getFieldValue(`OUTPUT${i}_ITEM`)
    if (item && item.trim()) {
      const chance = parseFloat(b.getFieldValue(`OUTPUT${i}_CHANCE`) || '100') / 100
      items.push(`{"item":"${item}","chance":${chance}}`)
    }
  }
  return items.length > 0 ? `[${items.join(',')}]` : "''"
}
kjsGen['kjs_create_rc_crushing'] = (b,i=0) => `${'  '.repeat(i)}event.recipes.createCrushing(${genCreateOutput(b)}, '${b.getFieldValue('INPUT') || "''"}')`
kjsGen['kjs_create_rc_milling'] = (b,i=0) => `${'  '.repeat(i)}event.recipes.createMilling(${genCreateOutput(b)}, '${b.getFieldValue('INPUT') || "''"}')`
kjsGen['kjs_create_rc_cutting'] = (b,i=0) => `${'  '.repeat(i)}event.recipes.createCutting(${genCreateOutput(b)}, '${b.getFieldValue('INPUT') || "''"}')`
kjsGen['kjs_create_rc_mixing'] = (b,i=0) => {
  const inputs: string[] = []
  for (let j = 1; j <= 5; j++) {
    const item = b.getFieldValue(`INPUT${j}_ITEM`)
    if (item && item.trim()) inputs.push(`'${item.trim()}'`)
  }
  return `${'  '.repeat(i)}event.recipes.createMixing(${genCreateOutput(b)}, [${inputs.join(',')}])`
}
kjsGen['kjs_create_rc_compacting'] = (b,i=0) => {
  const inputs: string[] = []
  for (let j = 1; j <= 5; j++) {
    const item = b.getFieldValue(`INPUT${j}_ITEM`)
    if (item && item.trim()) inputs.push(`'${item.trim()}'`)
  }
  return `${'  '.repeat(i)}event.recipes.createCompacting(${genCreateOutput(b)}, [${inputs.join(',')}])`
}
kjsGen['kjs_create_rc_pressing'] = (b,i=0) => `${'  '.repeat(i)}event.recipes.createPressing('${b.getFieldValue('OUTPUT') || "''"}', '${b.getFieldValue('INPUT') || "''"}')`
kjsGen['kjs_create_rc_filling'] = (b,i=0) => `${'  '.repeat(i)}event.recipes.createFilling('${b.getFieldValue('OUTPUT') || "''"}', '${b.getFieldValue('INPUT') || "''"}', '${b.getFieldValue('FLUID') || "''"}')`
kjsGen['kjs_create_rc_emptying'] = (b,i=0) => `${'  '.repeat(i)}event.recipes.createEmptying('${b.getFieldValue('OUTPUT') || "''"}', '${b.getFieldValue('FLUID') || "''"}', '${b.getFieldValue('INPUT') || "''"}')`
kjsGen['kjs_create_rc_splashing'] = (b,i=0) => `${'  '.repeat(i)}event.recipes.createSplashing(${genCreateOutput(b)}, '${b.getFieldValue('INPUT') || "''"}')`
kjsGen['kjs_create_rc_haunting'] = (b,i=0) => `${'  '.repeat(i)}event.recipes.createHaunting(${genCreateOutput(b)}, '${b.getFieldValue('INPUT') || "''"}')`
kjsGen['kjs_create_rc_deploying'] = (b,i=0) => `${'  '.repeat(i)}event.recipes.createDeploying('${b.getFieldValue('OUTPUT') || "''"}', '${b.getFieldValue('INPUT') || "''"}', '${b.getFieldValue('HAND') || "''"}')`
kjsGen['kjs_create_rc_item_app'] = (b,i=0) => `${'  '.repeat(i)}event.recipes.createItemApplication('${b.getFieldValue('OUTPUT') || "''"}', '${b.getFieldValue('INPUT') || "''"}', '${b.getFieldValue('HAND') || "''"}')`

// ── Event Action Blocks ──
kjsGen['kjs_ev_cancel_shoot'] = (_b,i=0) => `${'  '.repeat(i)}event.cancelShoot()`
kjsGen['kjs_ev_cancel_aim'] = (_b,i=0) => `${'  '.repeat(i)}event.cancelAim()`
kjsGen['kjs_ev_cancel_melee'] = (_b,i=0) => `${'  '.repeat(i)}event.cancelMelee()`
kjsGen['kjs_ev_cancel_reload'] = (_b,i=0) => `${'  '.repeat(i)}event.cancelReload()`
kjsGen['kjs_ev_set_vanilla'] = (_b,i=0) => `${'  '.repeat(i)}event.setVanillaInteract(true)`
kjsGen['kjs_ev_is_vanilla'] = () => `event.isVanillaInteract()`
kjsGen['kjs_ev_get_entity'] = () => `event.getEntity()`
kjsGen['kjs_ev_get_shooter'] = () => `event.getShooter()`
kjsGen['kjs_ev_get_gun_id'] = () => `event.getGunId().toString()`
kjsGen['kjs_ev_get_gun_item'] = () => `event.getGunItem()`
kjsGen['kjs_ev_get_heat_progress'] = () => `(function(){ var _gi = event.getGunItem(); if (!_gi) return 0; var _IGun = Java.loadClass('com.tacz.guns.api.item.IGun'); var _gun = _IGun.getIGunOrNull(_gi); if (!_gun) return 0; var _max = _gun.getMaxHeatAmount(_gi); return _max > 0 ? _gun.getHeatAmount(_gi) / _max : 0 })()`
kjsGen['kjs_ev_get_heat_amount'] = () => `(function(){ var _gi = event.getGunItem(); if (!_gi) return 0; var _IGun = Java.loadClass('com.tacz.guns.api.item.IGun'); var _gun = _IGun.getIGunOrNull(_gi); return _gun ? _gun.getHeatAmount(_gi) : 0 })()`
kjsGen['kjs_ev_get_id'] = () => `event.getId().toString()`
kjsGen['kjs_ev_get_json'] = () => `event.getJson()`
kjsGen['kjs_ev_get_std_json'] = () => `event.getStdJson()`
kjsGen['kjs_ev_set_json'] = (b,i=0) => `${'  '.repeat(i)}event.setJson(${genKJSValue(b, 'JSON', "''")})`
kjsGen['kjs_ev_get_gun_data'] = () => `event.getGunData()`
kjsGen['kjs_ev_get_attach_data'] = () => `event.getAttachmentData()`
kjsGen['kjs_ev_get_pojo'] = () => `event.getPOJO()`
kjsGen['kjs_ev_get_attach_tags'] = () => `event.getAttachmentTags()`
kjsGen['kjs_ev_get_table_recipe'] = () => `event.getTableRecipe()`
kjsGen['kjs_ev_remove_gun'] = (_b,i=0) => `${'  '.repeat(i)}event.removeGunData()`
kjsGen['kjs_ev_remove_attachment'] = (_b,i=0) => `${'  '.repeat(i)}event.removeAttachmentData()`
kjsGen['kjs_ev_remove_recipe'] = (_b,i=0) => `${'  '.repeat(i)}event.removeRecipe()`
kjsGen['kjs_ev_remove_all_recipes'] = (_b,i=0) => `${'  '.repeat(i)}event.removeAllRecipes()`
kjsGen['kjs_ev_put_recipe'] = (b,i=0) => `${'  '.repeat(i)}event.putRecipe(${genKJSValue(b, 'ID', "''")}, ${genKJSValue(b, 'JSON', "''")})`
kjsGen['kjs_ev_kill_entity'] = (_b,i=0) => `${'  '.repeat(i)}event.getEntity().kill()`

// ── Utils Blocks ──
kjsGen['kjs_utils_open_refit'] = (_b,i=0) => `${'  '.repeat(i)}TaCZJSUtils.openRefitScreen()`
kjsGen['kjs_utils_hold_gun'] = () => `TaCZJSUtils.mainHandHoldGun(event.getEntity())`
kjsGen['kjs_utils_get_gun_idx'] = (b) => `TaCZJSUtils.getGunIndex(${genKJSValue(b, 'ID', "''")})`
kjsGen['kjs_utils_get_ammo_idx'] = (b) => `TaCZJSUtils.getAmmoIndex(${genKJSValue(b, 'ID', "''")})`
kjsGen['kjs_utils_get_attach_idx'] = (b) => `TaCZJSUtils.getAttachmentIndex(${genKJSValue(b, 'ID', "''")})`

// ── Block Events Hats ──
kjsGen['kjs_block_right_clicked'] = (b, i=0) => hatGen(b, i, 'BlockEvents', 'rightClicked')
kjsGen['kjs_block_left_clicked'] = (b, i=0) => hatGen(b, i, 'BlockEvents', 'leftClicked')
kjsGen['kjs_block_placed'] = (b, i=0) => hatGen(b, i, 'BlockEvents', 'placed')
kjsGen['kjs_block_broken'] = (b, i=0) => hatGen(b, i, 'BlockEvents', 'broken')
kjsGen['kjs_block_drops'] = (b, i=0) => hatGen(b, i, 'BlockEvents', 'drops')
kjsGen['kjs_block_farmland_trampled'] = (b, i=0) => hatGen(b, i, 'BlockEvents', 'farmlandTrampled')
kjsGen['kjs_block_random_tick'] = (b, i=0) => hatGen(b, i, 'BlockEvents', 'randomTick')

// ── Entity Events Hats ──
kjsGen['kjs_entity_death'] = (b, i=0) => hatGen(b, i, 'EntityEvents', 'death')
kjsGen['kjs_entity_before_hurt'] = (b, i=0) => hatGen(b, i, 'EntityEvents', 'beforeHurt')
kjsGen['kjs_entity_after_hurt'] = (b, i=0) => hatGen(b, i, 'EntityEvents', 'afterHurt')
kjsGen['kjs_entity_spawned'] = (b, i=0) => hatGen(b, i, 'EntityEvents', 'spawned')
kjsGen['kjs_entity_drops'] = (b, i=0) => hatGen(b, i, 'EntityEvents', 'drops')
kjsGen['kjs_entity_check_spawn'] = (b, i=0) => hatGen(b, i, 'EntityEvents', 'checkSpawn')

// ── Player Events Hats ──
kjsGen['kjs_player_logged_in'] = (b, i=0) => hatGen(b, i, 'PlayerEvents', 'loggedIn')
kjsGen['kjs_player_logged_out'] = (b, i=0) => hatGen(b, i, 'PlayerEvents', 'loggedOut')
kjsGen['kjs_player_respawned'] = (b, i=0) => hatGen(b, i, 'PlayerEvents', 'respawned')
kjsGen['kjs_player_chat'] = (b, i=0) => hatGen(b, i, 'PlayerEvents', 'chat')
kjsGen['kjs_player_advancement'] = (b, i=0) => hatGen(b, i, 'PlayerEvents', 'advancement')
kjsGen['kjs_player_inventory_changed'] = (b, i=0) => hatGen(b, i, 'PlayerEvents', 'inventoryChanged')
kjsGen['kjs_player_tick'] = (b, i=0) => hatGen(b, i, 'PlayerEvents', 'tick')

// ── Item Events Hats ──
kjsGen['kjs_item_right_clicked'] = (b, i=0) => hatGen(b, i, 'ItemEvents', 'rightClicked')
kjsGen['kjs_item_crafted'] = (b, i=0) => hatGen(b, i, 'ItemEvents', 'crafted')
kjsGen['kjs_item_smelted'] = (b, i=0) => hatGen(b, i, 'ItemEvents', 'smelted')
kjsGen['kjs_item_food_eaten'] = (b, i=0) => hatGen(b, i, 'ItemEvents', 'foodEaten')
kjsGen['kjs_item_picked_up'] = (b, i=0) => hatGen(b, i, 'ItemEvents', 'pickedUp')
kjsGen['kjs_item_dropped'] = (b, i=0) => hatGen(b, i, 'ItemEvents', 'dropped')
kjsGen['kjs_item_modify_tooltips'] = (b, i=0) => hatGen(b, i, 'ItemEvents', 'modifyTooltips')

// ── Level Events Hats ──
kjsGen['kjs_level_loaded'] = (b, i=0) => hatGen(b, i, 'LevelEvents', 'loaded')
kjsGen['kjs_level_tick'] = (b, i=0) => hatGen(b, i, 'LevelEvents', 'tick')
kjsGen['kjs_level_saved'] = (b, i=0) => hatGen(b, i, 'LevelEvents', 'saved')
kjsGen['kjs_level_before_explosion'] = (b, i=0) => hatGen(b, i, 'LevelEvents', 'beforeExplosion')
kjsGen['kjs_level_after_explosion'] = (b, i=0) => hatGen(b, i, 'LevelEvents', 'afterExplosion')

// ── KeyBind Events Hats ──
kjsGen['kjs_keybind_pressed'] = (b, i=0) => {
  const key = b.getFieldValue('KEY') || 'my_key'
  const body = genKJSNext(b.getNextBlock(), 1)
  return `KeyBindEvents.pressed('${key}', (event) => {\n${body || ''}})`
}

// ── KubeJS 补充事件 Hats ──
kjsGen['kjs_server_unloaded'] = (b, i=0) => hatGen(b, i, 'ServerEvents', 'unloaded')
kjsGen['kjs_server_basic_command'] = (b, i=0) => {
  const cmd = b.getFieldValue('CMD') || 'mycmd'
  const body = genKJSNext(b.getNextBlock(), 1)
  return `ServerEvents.basicCommand('${cmd}', (event) => {\n${body || ''}})`
}
kjsGen['kjs_client_left_debug'] = (b, i=0) => hatGen(b, i, 'ClientEvents', 'leftDebugInfo')
kjsGen['kjs_client_right_debug'] = (b, i=0) => hatGen(b, i, 'ClientEvents', 'rightDebugInfo')
kjsGen['kjs_client_highlight'] = (b, i=0) => hatGen(b, i, 'ClientEvents', 'highlight')
kjsGen['kjs_item_modification'] = (b, i=0) => hatGen(b, i, 'ItemEvents', 'modification')
kjsGen['kjs_block_modification'] = (b, i=0) => hatGen(b, i, 'BlockEvents', 'modification')

// ── 客户端工具值积木 ──
kjsGen['kjs_utils_gun_display'] = () => `TaCZJSUtils.getGunDisplay()`
kjsGen['kjs_utils_gun_operator'] = () => `event.getGunOperator()`
kjsGen['kjs_utils_block_hit'] = () => `event.getBlockHitResult()`
kjsGen['kjs_utils_entity_hit'] = () => `event.getEntityHitResult()`
kjsGen['kjs_utils_can_interact'] = () => `event.canInteractEntity()`

// ── JS Logic Blocks ──
kjsGen['kjs_if'] = (b, i=0) => {
  const cond = genKJSValue(b, 'COND', 'true')
  const doBlk = genKJSStatements(b, 'DO', i+1)
  const elseBlk = genKJSStatements(b, 'ELSE', i+1)
  let code = `${'  '.repeat(i)}if (${cond}) {\n${doBlk}${doBlk?'\n':''}${'  '.repeat(i)}}`
  if (elseBlk) code += ` else {\n${elseBlk}\n${'  '.repeat(i)}}`
  return code
}
kjsGen['kjs_for_each'] = (b, i=0) => {
  const v = b.getFieldValue('VAR') || 'item'
  const arr = genKJSValue(b, 'ARR', '[]')
  const body = genKJSStatements(b, 'DO', i+1)
  return `${'  '.repeat(i)}for (const ${v} of ${arr}) {\n${body||''}\n${'  '.repeat(i)}}`
}
kjsGen['kjs_var_set'] = (b, i=0) => {
  const v = b.getFieldValue('VAR') || 'myVar'
  const val = genKJSValue(b, 'VAL', 'null')
  return `${'  '.repeat(i)}let ${v} = ${val}`
}
kjsGen['kjs_var_get'] = (b) => b.getFieldValue('VAR') || 'myVar'
kjsGen['kjs_comment'] = (b, i=0) => `${'  '.repeat(i)}// ${b.getFieldValue('TEXT') || ''}`
kjsGen['kjs_console_log'] = (b, i=0) => `${'  '.repeat(i)}console.log(${genKJSValue(b, 'VAL', "''")})`

// ── JS 补充逻辑 ──
kjsGen['kjs_while'] = (b,i=0) => {
  const cond = genKJSValue(b, 'COND', 'true')
  const body = genKJSStatements(b,'DO',i+1)
  return `${'  '.repeat(i)}while (${cond}) {\n${body||''}\n${'  '.repeat(i)}}`
}
kjsGen['kjs_do_while'] = (b,i=0) => {
  const body = genKJSStatements(b,'DO',i+1)
  const cond = genKJSValue(b, 'COND', 'true')
  return `${'  '.repeat(i)}do {\n${body||''}\n${'  '.repeat(i)}} while (${cond})`
}
kjsGen['kjs_for'] = (b,i=0) => {
  const from = genKJSValue(b, 'FROM', '0')
  const to = b.getFieldValue('TO_NUM') || '10'
  const step = b.getFieldValue('STEP_NUM') || '1'
  const body = genKJSStatements(b,'DO',i+1)
  return `${'  '.repeat(i)}for (let i = ${from}; i < ${to}; i += ${step}) {\n${body||''}\n${'  '.repeat(i)}}`
}
kjsGen['kjs_switch'] = (b,i=0) => {
  const val = genKJSValue(b, 'VALUE', "''")
  const cases = genKJSStatements(b,'CASES',i+1)
  return `${'  '.repeat(i)}switch (${val}) {\n${cases||''}\n${'  '.repeat(i)}}`
}
kjsGen['kjs_case'] = (b,i=0) => {
  const val = genKJSValue(b, 'VALUE', "''")
  const body = genKJSStatements(b,'DO',i+1)
  return `${'  '.repeat(i)}case ${val}:\n${body||''}\n${'  '.repeat(i)}break`
}
kjsGen['kjs_default'] = (b,i=0) => {
  const body = genKJSStatements(b,'DO',i+1)
  return `${'  '.repeat(i)}default:\n${body||''}`
}
kjsGen['kjs_try'] = (b,i=0) => {
  const tryBody = genKJSStatements(b,'TRY',i+1)
  const catchBody = genKJSStatements(b,'CATCH',i+1)
  return `${'  '.repeat(i)}try {\n${tryBody||''}\n${'  '.repeat(i)}} catch (e) {\n${catchBody||''}\n${'  '.repeat(i)}}`
}
kjsGen['kjs_break'] = (_b,i=0) => `${'  '.repeat(i)}break`
kjsGen['kjs_continue'] = (_b,i=0) => `${'  '.repeat(i)}continue`
kjsGen['kjs_throw'] = (b,i=0) => `${'  '.repeat(i)}throw ${genKJSValue(b, 'ERR', 'new Error()')}`

// ── Built-in Block Generators for JS ──
kjsGen['math_number'] = (b) => b.getFieldValue('NUM') || '0'
kjsGen['math_arithmetic'] = (b) => {
  const a = genKJSValue(b, 'A', '0')
  const op = b.getFieldValue('OP') || 'ADD'
  const bv = genKJSValue(b, 'B', '0')
  const OPS: Record<string, string> = { ADD: '+', MINUS: '-', MULTIPLY: '*', DIVIDE: '/', POWER: '**' }
  return `(${a} ${OPS[op] || '+'} ${bv})`
}
kjsGen['text'] = (b) => `'${(b.getFieldValue('TEXT') || '').replace(/'/g, "\\'")}'`
kjsGen['logic_boolean'] = (b) => b.getFieldValue('BOOL') === 'TRUE' ? 'true' : 'false'
kjsGen['logic_compare'] = (b) => {
  const a = genKJSValue(b, 'A', '0')
  const op = b.getFieldValue('OP') || 'EQ'
  const bv = genKJSValue(b, 'B', '0')
  const OPS: Record<string, string> = { EQ: '===', NEQ: '!==', LT: '<', GT: '>', LTE: '<=', GTE: '>=' }
  return `(${a} ${OPS[op] || '==='} ${bv})`
}
kjsGen['logic_operation'] = (b) => {
  const a = genKJSValue(b, 'A', 'true')
  const op = b.getFieldValue('OP') || 'AND'
  const bv = genKJSValue(b, 'B', 'true')
  return `(${a} ${op === 'AND' ? '&&' : '||'} ${bv})`
}
kjsGen['logic_negate'] = (b) => `!(${genKJSValue(b, 'BOOL', 'true')})`

// ── Custom JS Block ──
kjsGen['kjs_custom_js'] = (b, i=0) => {
  const code = b.getFieldValue('CODE') || '// code'
  return code.split('\n').map((l: string) => `${'  '.repeat(i)}${l}`).join('\n')
}

// ── Value Output Blocks ──
kjsGen['kjs_res_loc'] = (b) => `'${b.getFieldValue('LOC') || 'minecraft:dirt'}'`
kjsGen['kjs_json_literal'] = (b) => b.getFieldValue('JSON') || '{}'

// 复用内置积木的 KJS 生成器
kjsGen['math_number'] = (b) => String(b.getFieldValue('NUM') || '0')
kjsGen['math_add'] = (b) => `(${genKJSValue(b, 'A', '0')} + ${genKJSValue(b, 'B', '0')})`
kjsGen['math_sub'] = (b) => `(${genKJSValue(b, 'A', '0')} - ${genKJSValue(b, 'B', '0')})`
kjsGen['math_mul'] = (b) => `(${genKJSValue(b, 'A', '0')} * ${genKJSValue(b, 'B', '0')})`
kjsGen['math_div'] = (b) => `(${genKJSValue(b, 'A', '0')} / ${genKJSValue(b, 'B', '0')})`
kjsGen['text'] = (b) => `"${(b.getFieldValue('TEXT') || '').replace(/"/g, '\\"')}"`
kjsGen['logic_boolean'] = (b) => (b.getFieldValue('BOOL') === 'TRUE' ? 'true' : 'false')
kjsGen['logic_compare'] = (b) => {
  const a = genKJSValue(b, 'A', '0'); const g = genKJSValue(b, 'B', '0')
  const op = b.getFieldValue('OP') || 'EQ'
  const m: Record<string,string> = { EQ:'==', NEQ:'!=', LT:'<', GT:'>', LTE:'<=', GTE:'>=' }
  return `(${a} ${m[op]} ${g})`
}
kjsGen['logic_operation'] = (b) => {
  const a = genKJSValue(b, 'A', 'false'); const g = genKJSValue(b, 'B', 'false')
  return `(${a} ${b.getFieldValue('OP')==='AND'?'&&':'||'} ${g})`
}
kjsGen['logic_negate'] = (b) => `!(${genKJSValue(b, 'BOOL', 'false')})`

// ── 补充通用事件值 ──
kjsGen['kjs_ev_get_source'] = () => `event.getSource()`
kjsGen['kjs_ev_get_hand'] = () => `event.getHand()`
kjsGen['kjs_ev_get_facing'] = () => `event.getFacing()`
kjsGen['kjs_ev_get_message'] = () => `event.getMessage()`
kjsGen['kjs_ev_get_username'] = () => `event.getUsername()`
kjsGen['kjs_ev_get_random'] = () => `event.getRandom()`

// ── 配方操作 ──
kjsGen['kjs_recipe_remove'] = (b,i=0) => `${'  '.repeat(i)}event.remove(${genKJSValue(b, 'FILTER', "''")})`
kjsGen['kjs_recipe_replace_input'] = (b,i=0) => `${'  '.repeat(i)}event.replaceInput(${genKJSValue(b, 'FILTER', "''")}, ${genKJSValue(b, 'FROM', "''")}, ${genKJSValue(b, 'TO', "''")})`
kjsGen['kjs_recipe_replace_output'] = (b,i=0) => `${'  '.repeat(i)}event.replaceOutput(${genKJSValue(b, 'FILTER', "''")}, ${genKJSValue(b, 'FROM', "''")}, ${genKJSValue(b, 'TO', "''")})`

// ── 标签操作 ──
kjsGen['kjs_tag_add'] = (b,i=0) => `${'  '.repeat(i)}event.add(${genKJSValue(b, 'TAG', "''")}, ${genKJSValue(b, 'VALUES', "''")})`
kjsGen['kjs_tag_remove'] = (b,i=0) => `${'  '.repeat(i)}event.remove(${genKJSValue(b, 'TAG', "''")}, ${genKJSValue(b, 'VALUES', "''")})`
kjsGen['kjs_tag_remove_all'] = (b,i=0) => `${'  '.repeat(i)}event.removeAll(${genKJSValue(b, 'TAG', "''")})`

// ── 阶段操作 ──
kjsGen['kjs_stage_get'] = () => `event.getStage()`
kjsGen['kjs_stage_add'] = (b,i=0) => `${'  '.repeat(i)}var _ps = event.getPlayerStages(); if (_ps) { _ps.add(${genKJSValue(b, 'STAGE', "''")}) }`
kjsGen['kjs_stage_remove'] = (b,i=0) => `${'  '.repeat(i)}var _ps = event.getPlayerStages(); if (_ps) { _ps.remove(${genKJSValue(b, 'STAGE', "''")}) }`

// ── 语言文件 ──
kjsGen['kjs_lang_add'] = (b,i=0) => `${'  '.repeat(i)}event.add(${genKJSValue(b, 'KEY', "''")}, ${genKJSValue(b, 'VALUE', "''")})`
kjsGen['kjs_lang_rename_item'] = (b,i=0) => `${'  '.repeat(i)}event.renameItem(${genKJSValue(b, 'ITEM', "''")}, ${genKJSValue(b, 'NAME', "''")})`
kjsGen['kjs_lang_rename_block'] = (b,i=0) => `${'  '.repeat(i)}event.renameBlock(${genKJSValue(b, 'BLOCK', "''")}, ${genKJSValue(b, 'NAME', "''")})`

// ── 爆炸/世界事件值 ──
kjsGen['kjs_ev_get_position'] = () => `event.getPosition()`
kjsGen['kjs_ev_get_size'] = () => `event.getSize()`
kjsGen['kjs_ev_set_size'] = (b,i=0) => `${'  '.repeat(i)}event.setSize(${genKJSValue(b, 'SIZE', "''")})`
kjsGen['kjs_ev_get_affected_entities'] = () => `event.getAffectedEntities()`
kjsGen['kjs_ev_get_affected_blocks'] = () => `event.getAffectedBlocks()`
kjsGen['kjs_ev_remove_knockback'] = (_b,i=0) => `${'  '.repeat(i)}event.removeKnockback()`

// ── 实体掉落 ──
kjsGen['kjs_ev_get_drops'] = () => `event.getDrops()`
kjsGen['kjs_ev_add_drop'] = (b,i=0) => `${'  '.repeat(i)}event.addDrop(${genKJSValue(b, 'STACK', "''")})`
kjsGen['kjs_ev_is_recently_hit'] = () => `event.isRecentlyHit()`

// ── 聊天消息 ──
kjsGen['kjs_ev_get_chat_component'] = () => `event.getComponent()`
kjsGen['kjs_ev_set_chat_component'] = (b,i=0) => `${'  '.repeat(i)}event.setComponent(${genKJSValue(b, 'COMPONENT', "''")})`

// ── 新通用事件值积木 ──
kjsGen['kjs_ev_get_player'] = () => `(function(){ var _e = event.getEntity(); return (_e && _e.getPlayer) ? _e.getPlayer() : null })()`
kjsGen['kjs_ev_get_level'] = () => `event.getLevel()`
kjsGen['kjs_ev_get_block'] = () => `event.getBlock()`
kjsGen['kjs_ev_get_item'] = () => `event.getItem()`
kjsGen['kjs_ev_get_server'] = () => `event.getServer()`
kjsGen['kjs_ev_cancel'] = (_b,i=0) => `${'  '.repeat(i)}event.cancel()`
kjsGen['kjs_ev_set_result'] = (b,i=0) => `${'  '.repeat(i)}event.exit(${genKJSValue(b, 'VALUE', "''")})`
kjsGen['kjs_ev_log'] = (b,i=0) => `${'  '.repeat(i)}console.log(${genKJSValue(b, 'MSG', "''")})`
kjsGen['kjs_ev_get_damage'] = () => `event.getDamage()`
kjsGen['kjs_ev_set_damage'] = (b,i=0) => `${'  '.repeat(i)}event.setDamage(${genKJSValue(b, 'DAMAGE', "''")})`

// ── 服务端工具积木 ──
kjsGen['kjs_util_get_all_players'] = () => `(function(){ var _s = event.getServer(); if (!_s) return []; var _pl = _s.getPlayerList(); return (_pl && _pl.getPlayers) ? _pl.getPlayers() : [] })()`
kjsGen['kjs_util_send_msg'] = (b,i=0) => {
  const msg = genKJSValue(b, 'MSG', "''")
  return `${'  '.repeat(i)}var _ent = event.getEntity(); if (_ent) { _ent.tell(${msg || "'hello'"}) }`
}
kjsGen['kjs_util_run_cmd'] = (b,i=0) => `${'  '.repeat(i)}var _srv = event.getServer(); if (_srv) { _srv.command(false, ${genKJSValue(b, 'CMD', "''")}) }`
kjsGen['kjs_util_schedule'] = (b,i=0) => {
  const ticks = genKJSValue(b, 'TICKS', '1')
  const body = genKJSStatements(b, 'DO', 2)
  return `${'  '.repeat(i)}var _srv = event.getServer(); if (_srv) { _srv.schedule(${ticks}, (cb) => {\n${body || ''}\n${'  '.repeat(i)}}) }`
}

// ─── Generate KJS Code ───
function generateKJSCode(): string {
  if (!workspace) return ''
  const topBlocks = workspace.getTopBlocks(true)
  const lines: string[] = []
  for (const block of topBlocks) {
    if (!block.isEnabled()) continue
    const fn = kjsGen[block.type]
    if (fn) {
      lines.push(fn(block))
      lines.push('')
    }
  }
  return lines.join('\n')
}

// ─── Multi-workspace Tab Switching ───
function saveCurrentTabXML(tab: KJSTab) {
  if (!workspace) return
  const xml = Blockly.Xml.workspaceToDom(workspace)
  kjsWorkspaceXMLs.value[tab] = Blockly.Xml.domToText(xml)
}

function loadTabXML(tab: KJSTab) {
  if (!workspace) return
  workspace.clear()
  const saved = kjsWorkspaceXMLs.value[tab]
  if (saved) {
    try {
      const dom = Blockly.utils.xml.textToDom(saved)
      Blockly.Xml.domToWorkspace(dom, workspace)
    } catch {}
  }
}

// Watch tab switching
watch(activeKJSTab, (newTab, oldTab) => {
  if (currentMode.value !== 'kjs' || !workspace) return
  if (oldTab) saveCurrentTabXML(oldTab)
  loadTabXML(newTab)
  rebuildToolbox()
  handleWorkspaceChange({ type: '' } as any)
})

// ─── Generate Code from Workspace ───
function generateCode(): string {
  if (!workspace) return ''
  if (currentMode.value === 'kjs') {
    return generateKJSCode()
  }
  const topBlocks = workspace.getTopBlocks(true)

  // Merge extension generators
  const extGens = getExtensionGenerators(currentMode.value)
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

  // Update empty workspace hint
  if (workspace) {
    showEmptyHint.value = workspace.getTopBlocks(true).length === 0
  }

  const code = generateCode()
  emit('code-change', code)
}

// ─── Initialize Blockly ───
onMounted(() => {
  if (!blocklyDiv.value) return

  // 设置 Blockly 中文界面（右键菜单等）
  Blockly.setLocale(zhHans as unknown as { [key: string]: string })

  // 恢复保存的模式状态（必须在 workspace 创建之前，因为 buildToolbox 依赖 currentMode）
  // 恢复 KJS 标签数据（如果有），但默认启动始终为 TACZ 模式
  const savedTabs = localStorage.getItem('bt_kjs_tabs')
  if (savedTabs) {
    try { kjsWorkspaceXMLs.value = JSON.parse(savedTabs) } catch {}
  }
  const savedActiveTab = localStorage.getItem('bt_kjs_active_tab') as KJSTab | null
  if (savedActiveTab && ['server','client','startup'].includes(savedActiveTab)) {
    activeKJSTab.value = savedActiveTab
  }
  localStorage.removeItem('bt_editor_mode')

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
    // ── KJS Mode API ──
    switchToKJS() {
      if (!workspace) return
      // 保存 TACZ 工作区和扩展状态
      savedTaczXml = Blockly.Xml.domToText(Blockly.Xml.workspaceToDom(workspace))
      savedTaczExts = getActiveExtensions().map(e => e.id)
      workspace.clear()
      rebuildToolbox()
      handleWorkspaceChange({ type: '' } as any)
    },
    switchToTACZ() {
      if (!workspace) return
      workspace.clear()
      kjsWorkspaceXMLs.value = { server: '', client: '', startup: '' }
      // 恢复 TACZ 工作区
      // 先清理 KJS 扩展状态，恢复 TACZ 扩展
      const allExts = getRegisteredExtensions()
      for (const ext of allExts) deactivateExtension(ext.id)
      if (savedTaczExts.length > 0) {
        for (const id of savedTaczExts) activateExtension(id)
      }
      rebuildToolbox()
      // 恢复工作区 XML
      if (savedTaczXml) {
        try {
          const dom = Blockly.utils.xml.textToDom(savedTaczXml)
          Blockly.Xml.domToWorkspace(dom, workspace!)
        } catch {}
      }
      savedTaczXml = ''
      savedTaczExts = []
      handleWorkspaceChange({ type: '' } as any)
    },
    clearKJS() {
      if (!workspace) return
      workspace.clear()
      kjsWorkspaceXMLs.value = { server: '', client: '', startup: '' }
      handleWorkspaceChange({ type: '' } as any)
    },
    getKJSCodes(): Record<string, string> {
      if (!workspace) return { server: '', client: '', startup: '' }
      saveCurrentTabXML(activeKJSTab.value)
      const result: Record<string, string> = { server: '', client: '', startup: '' }
      const currentTab = activeKJSTab.value
      for (const tab of ['server', 'client', 'startup'] as KJSTab[]) {
        const xml = kjsWorkspaceXMLs.value[tab]
        if (!xml) continue
        if (tab !== currentTab) {
          workspace.clear()
          try {
            const dom = Blockly.utils.xml.textToDom(xml)
            Blockly.Xml.domToWorkspace(dom, workspace)
          } catch {}
        }
        result[tab] = generateKJSCode()
      }
      // 恢复当前标签
      workspace.clear()
      if (kjsWorkspaceXMLs.value[currentTab]) {
        try {
          const dom = Blockly.utils.xml.textToDom(kjsWorkspaceXMLs.value[currentTab])
          Blockly.Xml.domToWorkspace(dom, workspace)
        } catch {}
      }
      return result
    },
    getKJSWorkspaceXMLs() {
      saveCurrentTabXML(activeKJSTab.value)
      return { ...kjsWorkspaceXMLs.value }
    },
    loadKJSProject(tabs: Record<string, string>) {
      for (const [tab, xml] of Object.entries(tabs)) {
        if (tab in kjsWorkspaceXMLs.value) {
          kjsWorkspaceXMLs.value[tab as KJSTab] = xml
        }
      }
      loadTabXML(activeKJSTab.value)
      rebuildToolbox()
      handleWorkspaceChange({ type: '' } as any)
    },
  }

  // Listen for workspace changes
  workspace.addChangeListener(handleWorkspaceChange)

  // 语言切换：保存所有模式的工作区状态到localStorage，重载页面后恢复
  watch(() => i18n.value.lang, () => {
    // 保存当前模式
    localStorage.setItem('bt_editor_mode', currentMode.value)
    // 保存 KJS 工作区（总是保存，以保护跨模式切换的数据）
    saveCurrentTabXML(activeKJSTab.value)
    localStorage.setItem('bt_kjs_tabs', JSON.stringify(kjsWorkspaceXMLs.value))
    localStorage.setItem('bt_kjs_active_tab', activeKJSTab.value)
    // 保存 TACZ 工作区
    const xml = Blockly.Xml.workspaceToDom(workspace!)
    localStorage.setItem('bt_tacz_workspace', Blockly.Xml.domToText(xml))
    // 保存扩展状态
    const activeIds = getActiveExtensions().map(e => e.id)
    localStorage.setItem('bt_tacz_active_exts', JSON.stringify(activeIds))
    const customExts = getRegisteredExtensions().filter(e => !e.official)
    const customJsons = customExts.map(e => (e as any)._rawJson).filter(Boolean)
    if (customJsons.length) localStorage.setItem('bt_tacz_custom_exts', JSON.stringify(customJsons))
    window.location.reload()
  })

  // 恢复工作区内容（基于已保存的模式）
  if (currentMode.value === 'kjs') {
    const xml = kjsWorkspaceXMLs.value[activeKJSTab.value]
    if (xml) {
      try {
        const dom = Blockly.utils.xml.textToDom(xml)
        Blockly.Xml.domToWorkspace(dom, workspace!)
      } catch {}
    }
  } else {
    const saved = localStorage.getItem('bt_tacz_workspace')
    if (saved) {
      try {
        const xml = Blockly.utils.xml.textToDom(saved)
        Blockly.Xml.domToWorkspace(xml, workspace!)
      } catch {}
    }
  }

  // 清理旧版 localStorage key
  localStorage.removeItem('tacz_workspace')
  localStorage.removeItem('tacz_active_exts')
  localStorage.removeItem('tacz_custom_exts')

  // 恢复自定义扩展
  const savedCustomExts = localStorage.getItem('bt_tacz_custom_exts')
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
    localStorage.removeItem('bt_tacz_custom_exts')
  }

  // 恢复激活的扩展
  const savedActiveExts = localStorage.getItem('bt_tacz_active_exts')
  if (savedActiveExts) {
    try {
      const ids: string[] = JSON.parse(savedActiveExts)
      for (const id of ids) activateExtension(id)
    } catch {}
    localStorage.removeItem('bt_tacz_active_exts')
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
          if (block && (block.type === 'custom_lua' || block.type === 'kjs_custom_js')) {
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
.workspace-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #666;
  font-size: 15px;
  text-align: center;
  pointer-events: none;
  user-select: none;
  z-index: 10;
  background: rgba(30,30,46,0.8);
  padding: 20px 32px;
  border-radius: 12px;
  border: 1px dashed #555;
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
.ext-tutorial-mode-banner { background: rgba(139,92,246,0.2); border: 1px solid rgba(139,92,246,0.4); border-radius: 8px; padding: 8px 14px; margin-bottom: 12px; font-size: 13px; color: #C4B5FD; text-align: center; }

</style>
