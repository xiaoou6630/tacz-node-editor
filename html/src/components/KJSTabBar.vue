<template>
  <div class="kjs-tab-bar" v-if="visible">
    <div
      v-for="tab in tabs"
      :key="tab.key"
      class="kjs-tab"
      :class="{ active: activeTab === tab.key }"
      @click="$emit('switch', tab.key)"
    >
      <span class="tab-icon">{{ tab.icon }}</span>
      <span class="tab-label">{{ tab.label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { currentMode, activeKJSTab, type KJSTab } from '../mode'

defineEmits<{ switch: [tab: KJSTab] }>()

const visible = computed(() => currentMode.value === 'kjs')
const activeTab = activeKJSTab

const tabs = [
  { key: 'server' as KJSTab, icon: '📜', label: '服务端脚本.js' },
  { key: 'client' as KJSTab, icon: '🖥️', label: '客户端脚本.js' },
  { key: 'startup' as KJSTab, icon: '🚀', label: '启动脚本.js' },
]
</script>

<style scoped>
.kjs-tab-bar {
  display: flex;
  gap: 2px;
  padding: 6px 12px 0;
  background: #2D2D3F;
  border-bottom: 1px solid #3a3a50;
  flex-shrink: 0;
  user-select: none;
}
.kjs-tab {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 14px;
  border-radius: 8px 8px 0 0;
  cursor: pointer;
  font-size: 12px;
  color: #999;
  background: transparent;
  transition: all 0.15s;
  border: 1px solid transparent;
  border-bottom: none;
  margin-bottom: -1px;
}
.kjs-tab:hover {
  color: #ccc;
  background: rgba(255,255,255,0.05);
}
.kjs-tab.active {
  color: #FFD93D;
  background: #1E1E30;
  border-color: #3a3a50;
  font-weight: 600;
}
.tab-icon { font-size: 14px; }
.tab-label { white-space: nowrap; }
</style>
