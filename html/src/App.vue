<template>
  <div class="app-root">
    <!-- Top Bar -->
    <header class="top-bar">
      <span class="app-title">🧩 {{ t('appName') }}</span>
    </header>

    <!-- Main Content -->
    <div class="main-content">
      <div class="workspace-panel">
        <BlocklyWorkspace @code-change="onCodeChange" />
      </div>
      <div class="editor-panel">
        <CodeEditor :code="code" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { t } from './locales'
import BlocklyWorkspace from './components/BlocklyWorkspace.vue'
import CodeEditor from './components/CodeEditor.vue'

const code = ref('')

function onCodeChange(newCode: string) {
  code.value = newCode
}
</script>

<style scoped>
.app-root {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background: #1E1E2E;
  color: #CDD6F4;
}

.top-bar {
  height: 44px;
  min-height: 44px;
  background: #2D2D3F;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid #45475A;
  user-select: none;
}

.app-title {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.workspace-panel {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.editor-panel {
  width: 40%;
  min-width: 300px;
  max-width: 800px;
  border-left: 1px solid #45475A;
  overflow: hidden;
}
</style>
