<template>
  <Teleport to="body">
    <div class="lua-editor-overlay" v-if="visible" @keydown.tab.prevent>
      <div class="lua-editor-modal">
        <div class="lua-editor-header">
          <span>📝 Lua 代码编辑器</span>
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
import { autocompletion, CompletionContext, completionKeymap, closeBrackets, closeBracketsKeymap, acceptCompletion, type CompletionResult } from '@codemirror/autocomplete'
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands'
import { searchKeymap, highlightSelectionMatches } from '@codemirror/search'
import { lineNumbers, highlightActiveLineGutter, highlightActiveLine, drawSelection, rectangularSelection, crosshairCursor } from '@codemirror/view'
import { allCompletions, type CompletionItem } from '../tacz-completions'

const props = defineProps<{
  visible: boolean
  code: string
}>()

const emit = defineEmits<{
  'update:code': [code: string]
  'close': []
}>()

const editorContainer = ref<HTMLDivElement>()
let editorView: EditorView | null = null

// VSCode-style TACZ completions
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

function createEditor(code: string) {
  if (!editorContainer.value) return
  destroyEditor()

  const extensions = [
    // Line numbers & gutters
    lineNumbers(),
    highlightActiveLineGutter(),
    foldGutter(),
    // Lua language
    StreamLanguage.define(lua),
    syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
    // Theme
    oneDark,
    // Active line highlight
    highlightActiveLine(),
    drawSelection(),
    rectangularSelection(),
    crosshairCursor(),
    // Autocompletion - VSCode style
    autocompletion({
      override: [taczCompletions],
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
    cmPlaceholder('-- 在此输入 Lua 代码...'),
    // Keymaps - Tab accepts completion, then other keys
    keymap.of([
      { key: 'Tab', run: acceptCompletion },
      ...completionKeymap,
      ...closeBracketsKeymap,
      ...defaultKeymap,
      ...searchKeymap,
      ...historyKeymap,
      // Ctrl+S to confirm
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
