<template>
  <Teleport to="body">
    <div class="lua-editor-overlay" v-if="visible" @keydown.tab.prevent>
      <div class="lua-editor-modal">
        <div class="lua-editor-header">
          <span>📝 {{ mode === 'kjs' ? 'JS 代码编辑器' : 'Lua 代码编辑器' }}</span>
          <button class="lua-editor-close" @click="cancel">✕</button>
        </div>
        <div class="lua-editor-body" ref="editorContainer"></div>
        <div class="lua-editor-footer">
          <span class="lua-editor-hint">输入自动补全 | Tab 确认</span>
          <div class="lua-editor-actions">
            <button class="lua-btn cancel" @click="cancel">取消</button>
            <button class="lua-btn confirm" @click="confirm">确定</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount, nextTick } from 'vue'
import { EditorView, keymap, placeholder as cmPlaceholder } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { syntaxHighlighting, defaultHighlightStyle, indentOnInput, bracketMatching, foldGutter, StreamLanguage } from '@codemirror/language'
import { oneDark } from '@codemirror/theme-one-dark'
import { lua } from '@codemirror/legacy-modes/mode/lua'
import { javascript } from '@codemirror/lang-javascript'
import { autocompletion, CompletionContext, completionKeymap, closeBrackets, closeBracketsKeymap, acceptCompletion, type CompletionResult } from '@codemirror/autocomplete'
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands'
import { searchKeymap, highlightSelectionMatches } from '@codemirror/search'
import { lineNumbers, highlightActiveLineGutter, highlightActiveLine, drawSelection, rectangularSelection, crosshairCursor } from '@codemirror/view'
import { allCompletions, type CompletionItem } from '../tacz-completions'

const props = defineProps<{
  visible: boolean
  code: string
  mode?: string
}>()

const emit = defineEmits<{
  'update:code': [code: string]
  'close': []
}>()

const editorContainer = ref<HTMLDivElement>()
let editorView: EditorView | null = null

// VSCode-style TACZ completions (Lua)
function taczCompletions(context: CompletionContext): CompletionResult | null {
  const word = context.matchBefore(/[\w:.]+/)
  if (!word || word.from === word.to) return null

  const text = word.text
  const from = word.from

  const filtered = allCompletions.filter(item =>
    item.label.toLowerCase().startsWith(text.toLowerCase())
  )

  if (filtered.length === 0) return null

  return {
    from,
    options: filtered.map(item => ({
      label: item.label,
      type: item.type === 'function' ? 'function' :
            item.type === 'constant' ? 'constant' :
            item.type === 'keyword' ? 'keyword' :
            'text',
      detail: item.detail,
      apply: item.insertText || item.label,
      boost: item.type === 'function' ? 2 : item.type === 'constant' ? 1 : 0,
    })),
    filter: true,
  }
}

// KubeJS/JS completions
const kjsCompletionsList = [
  // ─── KubeJS 事件 API ───
  { label: 'event.getEntity', type: 'function' as const, detail: '获取实体', insertText: 'event.getEntity()' },
  { label: 'event.getPlayer', type: 'function' as const, detail: '获取玩家', insertText: 'event.getPlayer()' },
  { label: 'event.getLevel', type: 'function' as const, detail: '获取世界', insertText: 'event.getLevel()' },
  { label: 'event.getBlock', type: 'function' as const, detail: '获取方块', insertText: 'event.getBlock()' },
  { label: 'event.getItem', type: 'function' as const, detail: '获取物品', insertText: 'event.getItem()' },
  { label: 'event.getServer', type: 'function' as const, detail: '获取服务器', insertText: 'event.getServer()' },
  { label: 'event.cancel', type: 'function' as const, detail: '取消事件', insertText: 'event.cancel()' },
  { label: 'event.exit', type: 'function' as const, detail: '退出并返回值', insertText: 'event.exit(${1:value})' },
  { label: 'event.getSource', type: 'function' as const, detail: '获取伤害源', insertText: 'event.getSource()' },
  { label: 'event.getDamage', type: 'function' as const, detail: '获取伤害值', insertText: 'event.getDamage()' },
  { label: 'event.setDamage', type: 'function' as const, detail: '设置伤害值', insertText: 'event.setDamage(${1:amount})' },
  { label: 'event.getGunId', type: 'function' as const, detail: '获取枪械ID (TaCZJS)', insertText: 'event.getGunId()' },
  { label: 'event.getGunItem', type: 'function' as const, detail: '获取枪械物品 (TaCZJS)', insertText: 'event.getGunItem()' },
  { label: 'event.remove', type: 'function' as const, detail: '移除配方/标签', insertText: 'event.remove(${1:filter})' },
  { label: 'event.add', type: 'function' as const, detail: '添加标签', insertText: 'event.add(${1:tag}, ${2:values})' },
  { label: 'event.getPosition', type: 'function' as const, detail: '获取位置', insertText: 'event.getPosition()' },
  { label: 'event.getSize', type: 'function' as const, detail: '获取爆炸大小', insertText: 'event.getSize()' },
  { label: 'event.getDrops', type: 'function' as const, detail: '获取掉落物', insertText: 'event.getDrops()' },
  { label: 'event.addDrop', type: 'function' as const, detail: '添加掉落物', insertText: 'event.addDrop(${1:stack})' },
  { label: 'console.log', type: 'function' as const, detail: '输出日志', insertText: 'console.log(${1:msg})' },
  // ─── KubeJS 事件名 ───
  { label: 'BlockEvents.rightClicked', type: 'function' as const, detail: '方块右键事件', insertText: 'BlockEvents.rightClicked((event) => {\n  ${1:// code}\n})' },
  { label: 'EntityEvents.death', type: 'function' as const, detail: '实体死亡事件', insertText: 'EntityEvents.death((event) => {\n  ${1:// code}\n})' },
  { label: 'PlayerEvents.loggedIn', type: 'function' as const, detail: '玩家登录事件', insertText: 'PlayerEvents.loggedIn((event) => {\n  ${1:// code}\n})' },
  { label: 'ServerEvents.recipes', type: 'function' as const, detail: '配方事件', insertText: 'ServerEvents.recipes((event) => {\n  ${1:// code}\n})' },
  { label: 'TaCZServerEvents.entityShoot', type: 'function' as const, detail: '实体射击事件 (TaCZJS)', insertText: 'TaCZServerEvents.entityShoot((event) => {\n  ${1:// code}\n})' },
  // ─── JS 关键字/语法 ───
  { label: 'if', type: 'keyword' as const, detail: 'if 语句', insertText: 'if (${1:condition}) {\n  ${2:// body}\n}' },
  { label: 'for', type: 'keyword' as const, detail: 'for 循环', insertText: 'for (let ${1:i}=0; ${1:i}<${2:n}; ${1:i}++) {\n  ${3:// body}\n}' },
  { label: 'for...of', type: 'keyword' as const, detail: 'for-of 循环', insertText: 'for (const ${1:item} of ${2:array}) {\n  ${3:// body}\n}' },
  { label: 'while', type: 'keyword' as const, detail: 'while 循环', insertText: 'while (${1:condition}) {\n  ${2:// body}\n}' },
  { label: 'function', type: 'keyword' as const, detail: '函数定义', insertText: 'function ${1:name}(${2:args}) {\n  ${3:// body}\n}' },
  { label: 'const', type: 'keyword' as const, detail: '常量声明', insertText: 'const ${1:name} = ${2:value}' },
  { label: 'let', type: 'keyword' as const, detail: '变量声明', insertText: 'let ${1:name} = ${2:value}' },
  { label: 'return', type: 'keyword' as const, detail: '返回值', insertText: 'return ${1:value}' },
  { label: 'try', type: 'keyword' as const, detail: 'try-catch', insertText: 'try {\n  ${1:// code}\n} catch (${2:err}) {\n  ${3:// handle}\n}' },
]

function kjsCompletions(context: CompletionContext): CompletionResult | null {
  const word = context.matchBefore(/[\w.]+/)
  if (!word || word.from === word.to) return null
  const text = word.text
  const filtered = kjsCompletionsList.filter(item =>
    item.label.toLowerCase().startsWith(text.toLowerCase())
  )
  if (filtered.length === 0) return null
  return {
    from: word.from,
    options: filtered.map(item => ({
      label: item.label,
      type: item.type,
      detail: item.detail,
      apply: (item.insertText || item.label).replace(/\$\{\d+:([^}]*)\}/g, '$1'),
    })),
    filter: true,
  }
}

function createEditor(code: string) {
  if (!editorContainer.value) return
  destroyEditor()

  const isKJS = props.mode === 'kjs'

  const extensions = [
    // Line numbers & gutters
    lineNumbers(),
    highlightActiveLineGutter(),
    foldGutter(),
    // Language
    ...(isKJS
      ? [javascript()]
      : [StreamLanguage.define(lua), syntaxHighlighting(defaultHighlightStyle, { fallback: true })]
    ),
    // Theme
    oneDark,
    // Active line highlight
    highlightActiveLine(),
    drawSelection(),
    rectangularSelection(),
    crosshairCursor(),
    // Autocompletion
    autocompletion({
      override: [isKJS ? kjsCompletions : taczCompletions],
      activateOnTyping: true,
      icons: true,
      maxRenderedOptions: 50,
      defaultKeymap: true,
    }),
    // Editor features
    history(),
    indentOnInput(),
    bracketMatching(),
    closeBrackets(),
    highlightSelectionMatches(),
    // Placeholder
    cmPlaceholder(isKJS ? '// 在此输入 JS 代码...' : '-- 在此输入 Lua 代码...'),
    // Keymaps
    keymap.of([
      { key: 'Tab', run: acceptCompletion },
      ...completionKeymap,
      ...closeBracketsKeymap,
      ...defaultKeymap,
      ...searchKeymap,
      ...historyKeymap,
      { key: 'Mod-s', run: () => { confirm(); return true } },
    ]),
    // Tab size
    EditorState.tabSize.of(2),
    // Make sure editor is editable
    EditorView.editable.of(true),
    EditorState.readOnly.of(false),
  ]

  editorView = new EditorView({
    state: EditorState.create({
      doc: code,
      extensions,
    }),
    parent: editorContainer.value,
  })
}

function destroyEditor() {
  if (editorView) {
    editorView.destroy()
    editorView = null
  }
}

function confirm() {
  if (editorView) {
    const code = editorView.state.doc.toString()
    emit('update:code', code)
  }
  emit('close')
}

function cancel() {
  // Auto-save on exit
  if (editorView) {
    const code = editorView.state.doc.toString()
    emit('update:code', code)
  }
  emit('close')
}

watch(() => props.visible, async (val) => {
  if (val) {
    await nextTick()
    createEditor(props.code)
    setTimeout(() => editorView?.focus(), 100)
  } else {
    destroyEditor()
  }
})

onBeforeUnmount(() => {
  destroyEditor()
})
</script>

<style scoped>
.lua-editor-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lua-editor-modal {
  width: 720px;
  max-width: 90vw;
  height: 540px;
  max-height: 80vh;
  background: #1e1e2e;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.lua-editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #181825;
  border-bottom: 1px solid #313244;
  font-size: 14px;
  color: #cdd6f4;
}

.lua-editor-close {
  background: none;
  border: none;
  color: #6c7086;
  font-size: 18px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
}
.lua-editor-close:hover {
  background: #313244;
  color: #cdd6f4;
}

.lua-editor-body {
  flex: 1;
  overflow: hidden;
}

.lua-editor-body :deep(.cm-editor) {
  height: 100%;
  font-size: 13.5px;
}

.lua-editor-body :deep(.cm-scroller) {
  font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
  overflow: auto;
}

/* Line numbers */
.lua-editor-body :deep(.cm-gutters) {
  border-right: 1px solid #313244;
  background: #181825;
  color: #6c7086;
  min-width: 40px;
}

.lua-editor-body :deep(.cm-lineNumbers .cm-gutterElement) {
  padding: 0 8px 0 12px;
  font-size: 12px;
}

/* Active line */
.lua-editor-body :deep(.cm-activeLine) {
  background: rgba(137, 180, 250, 0.06) !important;
}

.lua-editor-body :deep(.cm-activeLineGutter) {
  background: rgba(137, 180, 250, 0.1) !important;
  color: #cdd6f4;
}

/* VSCode-style autocomplete tooltip */
.lua-editor-body :deep(.cm-tooltip-autocomplete) {
  background: #1e1e2e !important;
  border: 1px solid #45475a !important;
  border-radius: 6px !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
  font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace !important;
  font-size: 13px !important;
  padding: 4px !important;
}

.lua-editor-body :deep(.cm-tooltip-autocomplete .cm-completionLabel) {
  color: #cdd6f4 !important;
}

.lua-editor-body :deep(.cm-tooltip-autocomplete .cm-completionDetail) {
  color: #6c7086 !important;
  font-style: normal !important;
  margin-left: 12px !important;
}

.lua-editor-body :deep(.cm-completionIcon) {
  width: 16px !important;
  height: 16px !important;
  margin-right: 4px !important;
}

.lua-editor-body :deep(.cm-completionIcon-function::after) {
  content: 'f';
  color: #89b4fa;
  font-weight: bold;
  font-size: 11px;
}

.lua-editor-body :deep(.cm-completionIcon-constant::after) {
  content: 'C';
  color: #f9e2af;
  font-weight: bold;
  font-size: 11px;
}

.lua-editor-body :deep(.cm-completionIcon-keyword::after) {
  content: 'K';
  color: #cba6f7;
  font-weight: bold;
  font-size: 11px;
}

.lua-editor-body :deep(.cm-completionIcon-text::after) {
  content: 'S';
  color: #a6e3a1;
  font-weight: bold;
  font-size: 11px;
}

.lua-editor-body :deep(.cm-tooltip-autocomplete li[aria-selected]) {
  background: #313244 !important;
  color: #cdd6f4 !important;
  border-radius: 4px !important;
}

.lua-editor-body :deep(.cm-tooltip-autocomplete li) {
  padding: 3px 8px !important;
  border-radius: 4px !important;
}

/* Cursor */
.lua-editor-body :deep(.cm-cursor) {
  border-left: 2px solid #89b4fa !important;
}

.lua-editor-body :deep(.cm-selectionBackground) {
  background: rgba(137, 180, 250, 0.2) !important;
}

.lua-editor-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: #181825;
  border-top: 1px solid #313244;
}

.lua-editor-hint {
  font-size: 11px;
  color: #6c7086;
}

.lua-editor-actions {
  display: flex;
  gap: 8px;
}

.lua-btn {
  padding: 5px 16px;
  border-radius: 6px;
  border: none;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s;
}
.lua-btn.cancel {
  background: #313244;
  color: #cdd6f4;
}
.lua-btn.cancel:hover {
  background: #45475a;
}
.lua-btn.confirm {
  background: #4d96ff;
  color: white;
}
.lua-btn.confirm:hover {
  background: #3b7ddb;
}
</style>
