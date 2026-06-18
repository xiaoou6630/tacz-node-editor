<template>
  <div class="code-editor">
    <div class="editor-header">
      <span class="editor-title">{{ t('luaCode') }}</span>
      <div class="editor-actions">
        <button class="btn" @click="handleCopy">{{ t('copy') }}</button>
        <button class="btn" @click="handleDownload">{{ t('download') }}</button>
      </div>
    </div>
    <div ref="editorRef" class="editor-body"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { t } from '../locales'
import { EditorView, basicSetup } from 'codemirror'
import { oneDark } from '@codemirror/theme-one-dark'

const props = defineProps<{ code: string }>()

const editorRef = ref<HTMLDivElement | null>(null)
let view: EditorView | null = null

onMounted(() => {
  if (editorRef.value) {
    view = new EditorView({
      doc: props.code || '',
      extensions: [
        basicSetup,
        oneDark,
        EditorView.theme({
          '&': { backgroundColor: '#1E1E2E', height: '100%' },
          '.cm-scroller': { fontFamily: "'JetBrains Mono', 'Fira Code', monospace", fontSize: '13px' },
          '.cm-gutters': { backgroundColor: '#1E1E2E', border: 'none' },
          '.cm-activeLineGutter': { backgroundColor: '#2D2D3F' },
        }),
      ],
      parent: editorRef.value,
    })
  }
})

watch(
  () => props.code,
  (newCode) => {
    if (view && newCode !== undefined) {
      const current = view.state.doc.toString()
      if (newCode !== current) {
        view.dispatch({
          changes: { from: 0, to: current.length, insert: newCode },
        })
      }
    }
  }
)

onBeforeUnmount(() => {
  view?.destroy()
})

async function handleCopy() {
  try {
    await navigator.clipboard.writeText(props.code || '')
    // Simple visual feedback
    const btn = document.activeElement as HTMLElement
    if (btn) {
      const orig = btn.textContent
      btn.textContent = '✓'
      setTimeout(() => { btn.textContent = orig }, 800)
    }
  } catch {
    // fallback
    const ta = document.createElement('textarea')
    ta.value = props.code || ''
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
  }
}

function handleDownload() {
  const blob = new Blob([props.code || ''], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'state_machine.lua'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.code-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1E1E2E;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 40px;
  min-height: 40px;
  padding: 0 12px;
  background: #2D2D3F;
  border-bottom: 1px solid #45475A;
}

.editor-title {
  font-size: 13px;
  font-weight: 600;
}

.editor-actions {
  display: flex;
  gap: 6px;
}

.btn {
  background: #45475A;
  color: #CDD6F4;
  border: none;
  border-radius: 6px;
  padding: 4px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn:hover {
  background: #585B70;
}

.editor-body {
  flex: 1;
  overflow: auto;
}

.editor-body :deep(.cm-editor) {
  height: 100%;
}
</style>
