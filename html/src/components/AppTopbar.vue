<template>
  <div class="topbar">
    <div class="topbar-left">
      <span class="logo">🧩 TACZ Lua 编辑器</span>

      <div class="topbar-btn" @click="toggleMenu('file', $event)">
        {{ t('file') }} ▾
        <div class="dropdown" v-if="showFile" @click.stop>
          <div class="dropdown-item" @click="handleNew">📄 {{ t('newProject') }}</div>
          <div class="dropdown-item" @click="handleExportLua">📜 {{ t('exportLua') }}</div>
        </div>
      </div>

      <div class="topbar-btn" @click="toggleMenu('settings', $event)">
        {{ t('settings') }} ▾
        <div class="dropdown" v-if="showSettings" @click.stop>
          <div class="dropdown-item" @click="handleLang" style="display:flex;justify-content:space-between;align-items:center;">
            <span>🌐 {{ t('language') }}</span>
            <span style="color:#999;font-size:11px;">{{ langLabel }}</span>
          </div>
          <div class="dropdown-item" @click="handleHelp">📖 {{ t('help') }}</div>
          <div class="dropdown-sep"></div>
          <div class="dropdown-item" @click="handleAbout">ℹ️ {{ t('about') }}</div>
        </div>
      </div>
    </div>

    <div class="topbar-right">
      <label class="project-label">{{ t('projectName') }}</label>
      <input
        class="project-input"
        v-model="projectName"
        maxlength="15"
        placeholder="my_state_machine"
        spellcheck="false"
      />
    </div>

    <Teleport to="body">
      <!-- 帮助弹窗 -->
      <div class="modal-overlay" v-if="showHelp" @click="showHelp = false">
        <div class="modal" @click.stop>
          <h3>📖 {{ t('help') }}</h3>
          <div class="help-content">
            <p><b>TACZ Lua 状态机编辑器</b></p>
            <p class="help-section"><b>🎯 基本用法</b></p>
            <p>从左侧工具箱拖拽事件积木到画布，在下方拼接动作积木。</p>
            <p class="help-section"><b>⚡ 事件系统</b></p>
            <p>事件帽子积木定义状态机输入，当游戏内事件发生时触发状态转换。</p>
            <p class="help-section"><b>🎬 动画控制</b></p>
            <p>使用 runAnimation、stopAnimation 等积木控制武器动画播放。</p>
            <p class="help-section"><b>📥 导出</b></p>
            <p style="white-space:pre-line;">点击 文件 → 导出 Lua 文件 生成 .lua 脚本，放入 TACZ 枪械包即可使用。</p>
          </div>
          <button class="modal-btn" @click="showHelp = false">{{ t('ok') }}</button>
        </div>
      </div>

      <!-- 关于弹窗 -->
      <div class="modal-overlay" v-if="showAbout" @click="showAbout = false">
        <div class="modal" @click.stop>
          <h3>🧩 TACZ Lua 编辑器</h3>
          <p class="about-ver">版本 1.0.0</p>
          <p class="about-desc">{{ t('aboutDesc') }}</p>
          <p class="about-desc">{{ t('aboutStack') }}</p>
          <p class="about-author">xiaoou6630</p>
          <p class="about-copy">© 2026 TACZ Lua 编辑器</p>
          <button class="modal-btn" @click="showAbout = false">{{ t('ok') }}</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { t, i18n, setLang } from '../locales'

const projectName = ref('my_state_machine')
const showFile = ref(false)
const showSettings = ref(false)
const showHelp = ref(false)
const showAbout = ref(false)

const langLabel = computed(() => i18n.value.lang === 'zh' ? '中文' : 'English')

function toggleMenu(menu: string, e: MouseEvent) {
  e.stopPropagation()
  if (menu === 'file') { showFile.value = !showFile.value; showSettings.value = false }
  else { showSettings.value = !showSettings.value; showFile.value = false }
}
document.addEventListener('click', () => { showFile.value = false; showSettings.value = false })

function handleNew() {
  showFile.value = false
  const ws = (window as any).__tacz_workspace
  if (ws) ws.clear()
}

function handleExportLua() {
  showFile.value = false
  const code = (window as any).__tacz_workspace?.code || ''
  const blob = new Blob([code], { type: 'application/octet-stream' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = `${projectName.value}.lua`; a.click()
  URL.revokeObjectURL(url)
}

function handleLang() {
  showSettings.value = false
  setLang(i18n.value.lang === 'zh' ? 'en' : 'zh')
}

function handleHelp() { showSettings.value = false; showHelp.value = true }
function handleAbout() { showSettings.value = false; showAbout.value = true }
</script>

<style scoped>
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  height: 44px; padding: 0 16px;
  background: #2D2D3F; color: #E0E0E0;
  font-size: 13px; user-select: none; flex-shrink: 0;
  position: relative; z-index: 100;
}
.topbar-left { display: flex; align-items: center; gap: 4px; }
.logo { font-weight: 800; font-size: 15px; color: #FFD93D; margin-right: 12px; letter-spacing: 0.5px; }
.topbar-btn { position: relative; padding: 6px 14px; border-radius: 6px; cursor: pointer; transition: background 0.15s; font-weight: 500; }
.topbar-btn:hover { background: rgba(255,255,255,0.1); }

.dropdown {
  position: absolute; top: 100%; left: 0; margin-top: 4px;
  background: #3A3A50; border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  min-width: 200px; padding: 6px 0; z-index: 200;
  animation: dropIn 0.12s ease-out;
}
@keyframes dropIn { from { opacity:0; transform:translateY(-4px); } to { opacity:1; transform:translateY(0); } }
.dropdown-item { padding: 8px 16px; cursor: pointer; white-space: nowrap; transition: background 0.1s; font-size: 13px; }
.dropdown-item:hover { background: rgba(255,255,255,0.08); }
.dropdown-sep { height: 1px; background: rgba(255,255,255,0.1); margin: 4px 8px; }

.topbar-right { display: flex; align-items: center; gap: 8px; }
.project-label { font-weight: 500; color: #999; font-size: 12px; }
.project-input { background: #1E1E30; border: 1px solid #555; border-radius: 6px; padding: 4px 10px; color: #FFD93D; font-size: 13px; font-weight: 600; width: 160px; outline: none; transition: border-color 0.15s; }
.project-input:focus { border-color: #FFD93D; }
.project-input::placeholder { color: #666; font-weight: 400; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #2D2D3F; border-radius: 12px; padding: 24px 28px; max-width: 450px; width: 90%; color: #E0E0E0; box-shadow: 0 12px 40px rgba(0,0,0,0.4); max-height: 80vh; overflow-y: auto; }
.modal h3 { margin-bottom: 16px; font-size: 16px; color: #FFD93D; }

.help-content { font-size: 13px; color: #CCC; line-height: 1.8; }
.help-content p { margin-bottom: 4px; }
.help-section { color: #FFD93D; margin-top: 10px !important; margin-bottom: 2px !important; }

.about-ver { color: #999; font-size: 12px; margin-bottom: 8px; }
.about-desc { font-size: 13px; color: #CCC; margin-bottom: 4px; }
.about-copy { font-size: 11px; color: #666; margin-top: 12px; }
.modal-btn { margin-top: 16px; padding: 8px 24px; background: #FFD93D; color: #1E1E30; border: none; border-radius: 6px; font-weight: 700; font-size: 13px; cursor: pointer; float: right; transition: background 0.15s; }
.modal-btn:hover { background: #FFC107; }
</style>
