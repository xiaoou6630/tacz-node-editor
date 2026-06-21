<template>
  <div class="topbar">
    <div class="topbar-left">
      <img src="/src/TLV.png" class="logo-img" alt="logo" />
      <span class="logo">{{ isKJSMode ? 'KJS 编辑器' : 'TACZ Lua 编辑器' }}</span>

      <div class="topbar-btn" :class="{ 'kjs-active': isKJSMode }" @click="handleModeSwitch">
        🔄 {{ isKJSMode ? 'TACZ' : 'TaCZJS模式' }}
      </div>

      <div class="topbar-btn" @click="toggleMenu('file', $event)">
        {{ t('file') }} ▾
        <div class="dropdown" v-if="showFile" @click.stop>
          <div class="dropdown-item" @click="handleNew">📄 {{ t('newProject') }}</div>
          <div class="dropdown-sep"></div>
          <div class="dropdown-item" @click="handleExportProject">📦 {{ isKJSMode ? t('exportProjectKJS') : t('exportProject') }}</div>
          <div class="dropdown-item" @click="triggerImport">📥 {{ isKJSMode ? t('importProjectKJS') : t('importProject') }}</div>
          <div class="dropdown-sep"></div>
          <div class="dropdown-item" @click="isKJSMode ? handleExportJS() : handleExportLua()">📜 {{ isKJSMode ? t('exportJS') : t('exportLua') }}</div>
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
          <div class="dropdown-item" @click="handleEnv">🔧 {{ t('envCheck') }}</div>
          <div class="dropdown-sep"></div>
          <div class="dropdown-item" @click="handleAbout">ℹ️ {{ t('about') }}</div>
        </div>
      </div>

      <div class="topbar-btn topbar-ext-btn" @click="openExtDialog">
        🧩 {{ t('extensions') }}
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
      <span class="char-count">{{ projectName.length }}/15</span>
    </div>

    <input ref="fileInput" type="file" accept=".tlbw,.kjsw" style="display:none" @change="handleImport" />

    <Teleport to="body">
      <!-- 环境检测 -->
      <div class="modal-overlay" v-if="showEnv" @click="showEnv = false">
        <div class="modal" @click.stop>
          <h3>🔧 {{ t('envTitle') }}</h3>
          <p style="font-size:12px;color:#999;margin-bottom:12px;">{{ t('envDesc') }}</p>
          <div class="env-grid">
            <div v-for="item in envChecks" :key="item.name" class="env-item">
              <span>{{ item.icon }} {{ item.name }}</span>
              <span :class="item.ok ? 'ok' : item.warn ? 'warn' : 'err'">
                {{ item.ok ? '✓ ' + t('envSupport') : item.warn ? '△ ' + t('envPartial') : '✗ ' + t('envNot') }}
              </span>
            </div>
          </div>
          <button class="modal-btn" @click="showEnv = false">{{ t('ok') }}</button>
        </div>
      </div>

      <!-- 帮助 -->
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

      <!-- 关于 -->
      <div class="modal-overlay" v-if="showAbout" @click="showAbout = false">
        <div class="modal" @click.stop>
          <h3>🧩 {{ isKJSMode ? 'KubeJS / TaCZJS 编辑器' : 'TACZ Lua 编辑器' }}</h3>
          <p class="about-ver">版本 1.0.0</p>
          <p class="about-desc">{{ isKJSMode ? t('kjsAboutDesc') : t('aboutDesc') }}</p>
          <p class="about-desc">{{ t('aboutStack') }}</p>
          <p class="about-author">xiaoou6630</p>
          <p class="about-link" @click="openGitHub">🌐 {{ t('aboutGitHub') }}</p>
          <p class="about-copy">© 2026 {{ isKJSMode ? 'KubeJS / TaCZJS 编辑器' : 'TACZ Lua 编辑器' }}</p>
          <button class="modal-btn" @click="showAbout = false">{{ t('ok') }}</button>
        </div>
      </div>

      <!-- KJS 导出选择 -->
      <div class="modal-overlay" v-if="showKJSExport" @click="showKJSExport = false">
        <div class="modal" @click.stop>
          <h3>📜 {{ t('kjsExportTitle') }}</h3>
          <p style="font-size:12px;color:#999;margin-bottom:12px;">{{ t('kjsExportDesc') }}</p>
          <label class="kjs-export-item">
            <input type="checkbox" v-model="kjsExportSelection.server" />
            <span>📜 {{ t('kjsServerScript') }}.js</span>
          </label>
          <label class="kjs-export-item">
            <input type="checkbox" v-model="kjsExportSelection.client" />
            <span>🖥️ {{ t('kjsClientScript') }}.js</span>
          </label>
          <label class="kjs-export-item">
            <input type="checkbox" v-model="kjsExportSelection.startup" />
            <span>🚀 {{ t('kjsStartupScript') }}.js</span>
          </label>
          <div style="display:flex;gap:8px;margin-top:16px;">
            <button class="modal-btn" style="float:none;background:#555;" @click="showKJSExport = false">{{ t('ok') }}</button>
            <button class="modal-btn" style="float:none;" @click="confirmKJSExport">导出选中</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { t, i18n, setLang } from '../locales'
import { currentMode, switchToKJSMode, switchToTACZMode } from '../mode'

const projectName = ref('my_state_machine')
const showFile = ref(false)
const showSettings = ref(false)
const showHelp = ref(false)
const showAbout = ref(false)
const showEnv = ref(false)
const fileInput = ref<HTMLInputElement>()
const envChecks = ref<EnvItem[]>([])

interface EnvItem { icon: string; name: string; ok: boolean; warn: boolean }

const langLabel = computed(() => i18n.value.lang === 'zh' ? '中文' : 'English')

const isKJSMode = computed(() => currentMode.value === 'kjs')

const showKJSExport = ref(false)
const kjsExportSelection = ref({ server: true, client: false, startup: false })

function toggleMenu(menu: string, e: MouseEvent) {
  e.stopPropagation()
  if (menu === 'file') { showFile.value = !showFile.value; showSettings.value = false }
  else { showSettings.value = !showSettings.value; showFile.value = false }
}
document.addEventListener('click', () => { showFile.value = false; showSettings.value = false })

// Environment check
function handleEnv() {
  showSettings.value = false
  const w = screen.width; const h = screen.height
  envChecks.value = [
    { icon:'💾', name:t('envStorage'), ok:testLocalStorage(), warn:false },
    { icon:'🗄️', name:t('envIndexedDB'), ok:!!indexedDB, warn:!indexedDB },
    { icon:'📁', name:t('envFileAPI'), ok:!!(window.File && FileReader && Blob), warn:false },
    { icon:'📋', name:t('envClipboard'), ok:!!navigator.clipboard, warn:!navigator.clipboard },
    { icon:'⚙️', name:t('envWorker'), ok:!!Worker, warn:!Worker },
    { icon:'🌐', name:t('envHTTP'), ok:!!(fetch || XMLHttpRequest), warn:false },
    { icon:'🔌', name:t('envWebSocket'), ok:!!WebSocket, warn:!WebSocket },
    { icon:'🖥️', name:`${t('envScreen')} (${w}x${h})`, ok:w>=1024&&h>=600, warn:w<1024||h<600 },
    { icon:'👆', name:t('envTouch'), ok:!!(('ontouchstart' in document.documentElement) || (navigator.maxTouchPoints>0)), warn:false },
    { icon:'📡', name:t('envSW'), ok:!!('serviceWorker' in navigator), warn:false },
    { icon:'📝', name:t('envDOMParser'), ok:!!DOMParser, warn:false },
  ]
  showEnv.value = true
}
function testLocalStorage(): boolean {
  try { localStorage.setItem('_bt','1'); localStorage.removeItem('_bt'); return true }
  catch { return false }
}

// Project
function handleNew() {
  showFile.value = false
  if (!confirm(t('confirmNew'))) return
  if (isKJSMode.value) {
    const ws = (window as any).__tacz_workspace
    if (ws?.clearKJS) ws.clearKJS()
  } else {
    const ws = (window as any).__tacz_workspace
    if (ws) ws.clear()
  }
}

function handleModeSwitch() {
  if (currentMode.value === 'tacz') {
    if (!confirm(t('confirmKJS'))) return
    switchToKJSMode()
    const ws = (window as any).__tacz_workspace
    if (ws?.switchToKJS) ws.switchToKJS()
  } else {
    if (!confirm(t('confirmBackTACZ'))) return
    switchToTACZMode()
    const ws = (window as any).__tacz_workspace
    if (ws?.switchToTACZ) ws.switchToTACZ()
  }
}

function handleExportProject() {
  showFile.value = false
  const ws = (window as any).__tacz_workspace
  if (isKJSMode.value) {
    const tabsData = ws?.getKJSWorkspaceXMLs ? ws.getKJSWorkspaceXMLs() : {}
    const data = JSON.stringify({
      name: projectName.value, version: '1.0.0', mode: 'kjs',
      updated: new Date().toISOString(), tabs: tabsData,
    }, null, 2)
    const blob = new Blob([data], { type: 'application/octet-stream' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = `${projectName.value}.kjsw`; a.click()
    URL.revokeObjectURL(url)
    return
  }
  if (!ws?.getXML) return
  const serializer = new XMLSerializer()
  const extData = ws.getExtensionData ? ws.getExtensionData() : {}
  const data = JSON.stringify({
    name: projectName.value,
    version: '1.0.0',
    updated: new Date().toISOString(),
    xml: serializer.serializeToString(ws.getXML()),
    extensions: extData,
  }, null, 2)
  const blob = new Blob([data], { type: 'application/octet-stream' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = `${projectName.value}.tlbw`; a.click()
  URL.revokeObjectURL(url)
}

function triggerImport() { showFile.value = false; fileInput.value?.click() }

function handleImport(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]; if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    try {
      const p = JSON.parse(reader.result as string)
      // KJS 项目
      if (p.mode === 'kjs' && p.tabs) {
        switchToKJSMode()
        const ws = (window as any).__tacz_workspace
        if (ws?.switchToKJS) ws.switchToKJS()
        if (ws?.loadKJSProject && p.tabs) ws.loadKJSProject(p.tabs)
        projectName.value = p.name || 'KJS项目'
        return
      }
      // TACZ 项目
      if (!p.xml || !p.version) throw Error()
      const ws = (window as any).__tacz_workspace
      if (ws?.loadXML) ws.loadXML(p.xml)
      if (ws?.loadExtensionData && p.extensions) ws.loadExtensionData(p.extensions)
      projectName.value = p.name || '导入项目'
    } catch { alert(t('importFailed')) }
  }
  reader.readAsText(file); (e.target as HTMLInputElement).value = ''
}

function handleExportLua() {
  showFile.value = false
  const code = (window as any).__tacz_workspace?.code || ''
  const blob = new Blob([code], { type: 'application/octet-stream' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = `${projectName.value}.lua`; a.click()
  URL.revokeObjectURL(url)
}

function handleExportJS() {
  showFile.value = false
  showKJSExport.value = true
}

function confirmKJSExport() {
  const ws = (window as any).__tacz_workspace
  if (!ws?.getKJSCodes) return
  const codes = ws.getKJSCodes()
  const sel = kjsExportSelection.value
  const names: Record<string, string> = { server: '服务端脚本', client: '客户端脚本', startup: '启动脚本' }
  for (const [tab, code] of Object.entries(codes)) {
    if (sel[tab as keyof typeof sel] && code) {
      const blob = new Blob([String(code)], { type: 'application/javascript' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a'); a.href = url; a.download = `${names[tab]}.js`; a.click()
      URL.revokeObjectURL(url)
    }
  }
  showKJSExport.value = false
}

function handleLang() {
  showSettings.value = false
  setLang(i18n.value.lang === 'zh' ? 'en' : 'zh')
}

function handleHelp() { showSettings.value = false; showHelp.value = true }

function handleAbout() { showSettings.value = false; showAbout.value = true }

function openExtDialog() {
  showSettings.value = false
  showFile.value = false
  const ws = (window as any).__tacz_workspace
  if (ws?.openExtDialog) ws.openExtDialog()
}

function openGitHub() {
  window.open('https://github.com/xiaoou6630/tacz-node-editor/tree/web1.0.0', '_blank')
}
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
.logo-img { width: 22px; height: 22px; margin-right: 6px; border-radius: 4px; }
.logo { font-weight: 800; font-size: 15px; color: #FFD93D; margin-right: 12px; letter-spacing: 0.5px; }
.topbar-btn { position: relative; padding: 6px 14px; border-radius: 6px; cursor: pointer; transition: background 0.15s; font-weight: 500; }
.topbar-btn:hover { background: rgba(255,255,255,0.1); }

.dropdown {
  position: absolute; top: 100%; left: 0; margin-top: 4px;
  background: #3A3A50; border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  min-width: 210px; padding: 6px 0; z-index: 200;
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
.char-count { color: #666; font-size: 11px; min-width: 30px; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: #2D2D3F; border-radius: 12px; padding: 24px 28px; max-width: 450px; width: 90%; color: #E0E0E0; box-shadow: 0 12px 40px rgba(0,0,0,0.4); max-height: 80vh; overflow-y: auto; }
.modal h3 { margin-bottom: 16px; font-size: 16px; color: #FFD93D; }

.env-grid { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.env-item { display: flex; justify-content: space-between; padding: 7px 0; border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 13px; }
.env-item .ok { color: #4ECDC4; font-weight: 600; }
.env-item .warn { color: #F39C12; font-weight: 600; }
.env-item .err { color: #FF6B6B; font-weight: 600; }

.help-content { font-size: 13px; color: #CCC; line-height: 1.8; }
.help-content p { margin-bottom: 4px; }
.help-section { color: #FFD93D; margin-top: 10px !important; margin-bottom: 2px !important; }

.about-ver { color: #999; font-size: 12px; margin-bottom: 8px; }
.about-desc { font-size: 13px; color: #CCC; margin-bottom: 4px; }
.about-author { font-size: 13px; color: #FFD93D; margin-bottom: 4px; }
.about-link { font-size: 12px; color: #4D96FF; cursor: pointer; margin-bottom: 4px; }
.about-link:hover { text-decoration: underline; }
.about-copy { font-size: 11px; color: #666; margin-top: 12px; }
.modal-btn { margin-top: 16px; padding: 8px 24px; background: #FFD93D; color: #1E1E30; border: none; border-radius: 6px; font-weight: 700; font-size: 13px; cursor: pointer; float: right; transition: background 0.15s; }
.modal-btn:hover { background: #FFC107; }
.topbar-ext-btn { background: rgba(139, 92, 246, 0.2); border: 1px solid rgba(139, 92, 246, 0.4); }
.topbar-ext-btn:hover { background: rgba(139, 92, 246, 0.35); }
.kjs-active { background: rgba(139, 92, 246, 0.25); border: 1px solid rgba(139, 92, 246, 0.6); color: #C4B5FD; }
.kjs-export-item { display: flex; align-items: center; gap: 10px; padding: 10px 0; font-size: 14px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.06); }
.kjs-export-item input[type="checkbox"] { width: 16px; height: 16px; accent-color: #FFD93D; }
</style>
