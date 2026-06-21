<template>
  <div class="app-root">
    <AppTopbar />
    <div class="app-container">
      <div class="workspace-panel">
        <KJSTabBar @switch="onKJSTabSwitch" />
        <BlocklyWorkspace ref="blocklyRef" @code-change="handleCodeChange" />
      </div>
      <div class="editor-panel">
        <CodeEditor :code="luaCode" :mode="currentMode" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import AppTopbar from './components/AppTopbar.vue'
import BlocklyWorkspace from './components/BlocklyWorkspace.vue'
import CodeEditor from './components/CodeEditor.vue'
import KJSTabBar from './components/KJSTabBar.vue'
import { currentMode, activeKJSTab, type KJSTab } from './mode'

const luaCode = ref('-- 在此添加积木，代码将自动生成')
const hasContent = ref(false)

const handleCodeChange = (code: string) => {
  luaCode.value = code || '-- 在此添加积木，代码将自动生成'
  hasContent.value = !!code && code.trim().length > 0
  const ws = (window as any).__tacz_workspace
  if (ws) ws.code = luaCode.value
}

function onKJSTabSwitch(tab: KJSTab) {
  activeKJSTab.value = tab
}

const beforeUnloadHandler = (e: BeforeUnloadEvent) => {
  if (hasContent.value) {
    e.preventDefault()
  }
}

onMounted(() => window.addEventListener('beforeunload', beforeUnloadHandler))
onUnmounted(() => window.removeEventListener('beforeunload', beforeUnloadHandler))
</script>

<style scoped>
.app-root { display: flex; flex-direction: column; width: 100vw; height: 100vh; overflow: hidden; }
.app-container { display: flex; flex: 1; min-height: 0; overflow: hidden; }
.workspace-panel { display: flex; flex-direction: column; flex: 1; min-width: 0; background: #1E1E2E; }
.editor-panel { width: 40%; min-width: 300px; max-width: 800px; background: #1E1E2E; }
</style>
