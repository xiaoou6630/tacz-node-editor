# TaCZJS/KubeJS 编辑模式 — 实施计划（v3 续）

## 当前状态总结

### 已完成（上一轮会话）
| # | 文件 | 状态 |
|---|------|------|
| 1 | `src/mode.ts` | ✅ 已创建 — EditorMode/KJSTab 状态管理 |
| 2 | `src/blocks/taczjs.ts` | ✅ 已创建 — ~50个KJS积木定义（13类） |
| 3 | `src/components/KJSTabBar.vue` | ✅ 已创建 — 三标签文件栏组件 |
| 4a | `src/components/AppTopbar.vue` 模板部分 | ⚠️ 部分完成 — KJS按钮HTML + v-if隐藏扩展 |

### 待完成（本轮实施）
| # | 文件 | 具体工作 |
|---|------|----------|
| **4b** | `AppTopbar.vue` 脚本部分 | import mode、isKJSMode computed、handleModeSwitch、KJS导出弹窗、handleExportJS、kjs-active样式 |
| **5** | `blocks/index.ts` | 添加 `import './taczjs'` 注册积木 |
| **6** | `BlocklyWorkspace.vue` | kjsGen代码生成器 + buildKJSToolbox() + generateKJSCode() + 多工作区切换 + 模式感知generateCode() + watch activeKJSTab |
| **7** | `App.vue` | 引入KJSTabBar放置在workspace-panel上方 |
| **8** | `locales.ts` | 添加KJS相关i18n键 |

---

## Step 4b: AppTopbar.vue 脚本补充

### 4b-1: `<script setup>` 区块修改

在现有 imports 后添加：
```typescript
import { currentMode } from '../mode'
```

添加 computed：
```typescript
const isKJSMode = computed(() => currentMode.value === 'kjs')
```

添加 handleModeSwitch：
```typescript
function handleModeSwitch() {
  if (currentMode.value === 'tacz') {
    // TACZ → KJS
    if (!confirm('切换到KJS模式将清空工作区，确定继续？')) return
    switchToKJSMode()
    // 通知 BlocklyWorkspace 切换到 KJS 模式
    const ws = (window as any).__tacz_workspace
    if (ws?.switchToKJS) ws.switchToKJS()
  } else {
    // KJS → TACZ
    if (!confirm('切回TACZ模式将清空KJS工作区，确定继续？')) return
    switchToTACZMode()
    const ws = (window as any).__tacz_workspace
    if (ws?.switchToTACZ) ws.switchToTACZ()
  }
}
```

添加 KJS 导出弹窗状态：
```typescript
const showKJSExport = ref(false)
const kjsExportSelection = ref({ server: true, client: false, startup: false })
```

添加 handleExportJS：
```typescript
function handleExportJS() {
  showFile.value = false
  const ws = (window as any).__tacz_workspace
  if (!ws?.getKJSCodes) return
  // 显示导出选择弹窗
  showKJSExport.value = true
}
function confirmKJSExport() {
  const ws = (window as any).__tacz_workspace
  if (!ws?.getKJSCodes) return
  const codes = ws.getKJSCodes()
  const sel = kjsExportSelection.value
  // 逐个下载选中的文件
  for (const [tab, code] of Object.entries(codes)) {
    if (sel[tab as keyof typeof sel] && code) {
      const names = { server: '服务端脚本', client: '客户端脚本', startup: '启动脚本' }
      const blob = new Blob([code], { type: 'application/javascript' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a'); a.href = url; a.download = `${names[tab as keyof typeof names]}.js`; a.click()
      URL.revokeObjectURL(url)
    }
  }
  showKJSExport.value = false
}
```

修改 handleNew — KJS模式下也要能新建：
```typescript
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
```

### 4b-2: 模板修改

1. 导出Lua按钮改为条件显示：
```html
<!-- KJS模式显示"导出JS"，TACZ模式显示"导出Lua" -->
<div class="dropdown-item" @click="isKJSMode ? handleExportJS() : handleExportLua()">
  📜 {{ isKJSMode ? '导出 JS 文件' : t('exportLua') }}
</div>
```

2. 在 Teleport 区域末尾添加 KJS 导出选择弹窗：
```html
<!-- KJS 导出选择 -->
<div class="modal-overlay" v-if="showKJSExport" @click="showKJSExport = false">
  <div class="modal" @click.stop>
    <h3>📜 选择要导出的脚本</h3>
    <p style="font-size:12px;color:#999;margin-bottom:12px;">勾选需要下载的 .js 文件</p>
    <label class="kjs-export-item">
      <input type="checkbox" v-model="kjsExportSelection.server" />
      <span>📜 服务端脚本.js</span>
    </label>
    <label class="kjs-export-item">
      <input type="checkbox" v-model="kjsExportSelection.client" />
      <span>🖥️ 客户端脚本.js</span>
    </label>
    <label class="kjs-export-item">
      <input type="checkbox" v-model="kjsExportSelection.startup" />
      <span>🚀 启动脚本.js</span>
    </label>
    <div style="display:flex;gap:8px;margin-top:16px;">
      <button class="modal-btn" style="float:none;background:#555;" @click="showKJSExport = false">取消</button>
      <button class="modal-btn" style="float:none;" @click="confirmKJSExport">导出选中</button>
    </div>
  </div>
</div>
```

3. 项目导入支持 KJS 格式 — handleImport 中增加 mode 判断：
```typescript
// 在 handleImport 的 reader.onload 里增加：
if (p.mode === 'kjs') {
  // KJS项目恢复
  switchToKJSMode()
  const ws = (window as any).__tacz_workspace
  if (ws?.loadKJSProject && p.tabs) ws.loadKJSProject(p.tabs)
  projectName.value = p.name || 'KJS项目'
} else {
  // 原有TACZ逻辑不变
}
```

4. 项目导出也支持 KJS 格式 — handleExportProject 中增加：
```typescript
if (isKJSMode.value) {
  const ws = (window as any).__tacz_workspace
  const tabsData = ws?.getKJSWorkspaceXMLs ? ws.getKJSWorkspaceXMLs() : {}
  data = JSON.stringify({
    name: projectName.value,
    version: '1.0.0',
    mode: 'kjs',
    updated: new Date().toISOString(),
    tabs: tabsData,
  }, null, 2)
  download as `${projectName.value}.tlbw`
}
```

### 4b-3: 样式补充

```css
.kjs-active {
  background: rgba(139, 92, 246, 0.25);
  border: 1px solid rgba(139, 92, 246, 0.6);
  color: #C4B5FD;
}
.kjs-export-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  font-size: 14px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.kjs-export-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #FFD93D;
}
```

---

## Step 5: blocks/index.ts — 注册 taczjs 积木

```diff
 import './tacz'
+import './taczjs'
```

仅此一行。确保积木定义在 workspace 创建前加载。

---

## Step 6: BlocklyWorkspace.vue — 核心改造

这是最复杂的一步。需要：

### 6-1: 新增 imports

```typescript
import { currentMode, activeKJSTab, kjsWorkspaceXMLs, type KJSTab } from '../mode'
import '../blocks/taczjs'  // 确保 KJS 积木注册
```

### 6-2: 新增 kjsGen 代码生成器对象

参照 luaGen 的模式，为所有 taczjs.ts 定义的积木编写 JS 代码生成器。

关键生成规则：
- **事件帽子积木** → 生成对应的事件回调函数包装
  - TaCZJS Server Events: `TaCZServerEvents.entityShoot((event) => { ... })`
  - TaCZJS Client Events: `TaCZClientEvents.playerShoot((event) => { ... })`
  - TaCZJS Startup Events: `TaCZStartupEvents.recipeLoad((event) => { ... })`
  - KubeJS Server Events: `ServerEvents.loaded((event) => { ... })`
  - KubeJS Client Events: `ClientEvents.loggedIn((event) => { ... })`
  - KubeJS Startup Events: `StartupEvents.init((event) => { ... })`
  - Create Events: `CreateEvents.boilerHeatHandler((event) => { ... })`

- **操作积木** → 生成 event 方法调用
  - cancel_*: `event.cancelXxx()`
  - get_*: `event.getXxx()` 或直接返回值
  - set_json: `event.setJson(${JSON})`
  - remove_*: `event.removeXxx()`
  - put_recipe: `event.putRecipe(${ID}, ${JSON})`
  - kill_entity: `event.getEntity().kill()`

- **Utils**: `TaCZJSUtils.openRefitScreen()` 等
- **逻辑控制**: 标准 JS (if/for/变量)
- **自定义代码**: 直接输出 CODE 字段内容
- **值输出**: 直接返回表达式

具体 kjsGen 定义（完整列表）：

```typescript
const kjsGen: Record<string, (block: Blockly.Block, indent?: number) => string> = {}

// ── Helper functions for KJS ──
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

function genKJSValue(block: Blockly.Block, inputName: string): string {
  const target = block.getInputTargetBlock(inputName)
  if (!target || !target.isEnabled()) return "''"
  const fn = kjsGen[target.type]
  if (!fn) return "''"
  return fn(target)
}

function genKJSStatements(block: Blockly.Block, inputName: string, indent = 1): string {
  const target = block.getInputTargetBlock(inputName)
  if (!target) return ''
  return genKJSNext(target, indent)
}

// ── TaCZJS Server Event Hats ──
kjsGen['kjs_tacz_s_entity_shoot'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'entityShoot')
kjsGen['kjs_tacz_s_entity_aim'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'entityAim')
kjsGen['kjs_tacz_s_entity_melee'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'entityMelee')
kjsGen['kjs_tacz_s_entity_reload'] = (b, i=0) => hatGen(b, i, 'TaCZServerEvents', 'entityReload')

// ── TaCZJS Server Load Event Hats ──
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

// 通用帽子生成函数
function hatGen(block: Blockly.Block, _indent: number, ns: string, method: string): string {
  const body = genKJSNext(block.getNextBlock(), 1)
  return `${ns}.${method}((event) => {\n${body || ''}})`
}

// ── Event Action Blocks ──
kjsGen['kjs_ev_cancel_shoot'] = (_b,i) => `${'  '.repeat(i)}event.cancelShoot()`
kjsGen['kjs_ev_cancel_aim'] = (_b,i) => `${'  '.repeat(i)}event.cancelAim()`
kjsGen['kjs_ev_cancel_melee'] = (_b,i) => `${'  '.repeat(i)}event.cancelMelee()`
kjsGen['kjs_ev_cancel_reload'] = (_b,i) => `${'  '.repeat(i)}event.cancelReload()`
kjsGen['kjs_ev_set_vanilla'] = (_b,i) => `${'  '.repeat(i)}event.setVanillaInteract(true)`
kjsGen['kjs_ev_is_vanilla'] = () => `event.isVanillaInteract()`
kjsGen['kjs_ev_get_entity'] = () => `event.getEntity()`
kjsGen['kjs_ev_get_shooter'] = () => `event.getShooter()`
kjsGen['kjs_ev_get_gun_id'] = () => `event.getGunId().toString()`
kjsGen['kjs_ev_get_gun_item'] = () => `event.getGunItem()`
kjsGen['kjs_ev_get_id'] = () => `event.getId().toString()`
kjsGen['kjs_ev_get_json'] = () => `event.getJson()`
kjsGen['kjs_ev_get_std_json'] = () => `event.getStdJson()`
kjsGen['kjs_ev_set_json'] = (b,i) => `${'  '.repeat(i)}event.setJson(${genKJSValue(b,'JSON')})`
kjsGen['kjs_ev_get_gun_data'] = () => `event.getGunData()`
kjsGen['kjs_ev_get_attach_data'] = () => `event.getAttachmentData()`
kjsGen['kjs_ev_get_pojo'] = () => `event.getPOJO()`
kjsGen['kjs_ev_get_attach_tags'] = () => `event.getAttachmentTags()`
kjsGen['kjs_ev_get_table_recipe'] = () => `event.getTableRecipe()`
kjsGen['kjs_ev_remove_gun'] = (_b,i) => `${'  '.repeat(i)}event.removeGunData()`
kjsGen['kjs_ev_remove_attachment'] = (_b,i) => `${'  '.repeat(i)}event.removeAttachmentData()`
kjsGen['kjs_ev_remove_recipe'] = (_b,i) => `${'  '.repeat(i)}event.removeRecipe()`
kjsGen['kjs_ev_remove_all_recipes'] = (_b,i) => `${'  '.repeat(i)}event.removeAllRecipes()`
kjsGen['kjs_ev_put_recipe'] = (b,i) => `${'  '.repeat(i)}event.putRecipe(${genKJSValue(b,'ID')}, ${genKJSValue(b,'JSON')})`
kjsGen['kjs_ev_kill_entity'] = (_b,i) => `${'  '.repeat(i)}event.getEntity().kill()`

// ── Utils Blocks ──
kjsGen['kjs_utils_open_refit'] = (_b,i) => `${'  '.repeat(i)}TaCZJSUtils.openRefitScreen()`
kjsGen['kjs_utils_hold_gun'] = () => `TaCZJSUtils.mainHandHoldGun(event.getEntity())`
kjsGen['kjs_utils_get_gun_idx'] = (b) => `TaCZJSUtils.getGunIndex(${genKJSValue(b,'ID')})`
kjsGen['kjs_utils_get_ammo_idx'] = (b) => `TaCZJSUtils.getAmmoIndex(${genKJSValue(b,'ID')})`
kjsGen['kjs_utils_get_attach_idx'] = (b) => `TaCZJSUtils.getAttachmentIndex(${genKJSValue(b,'ID')})`

// ── JS Logic Blocks ──
kjsGen['kjs_if'] = (b, i) => {
  const cond = genKJSValue(b, 'COND') || 'true'
  const doBlk = genKJSStatements(b, 'DO', i+1)
  const elseBlk = genKJSStatements(b, 'ELSE', i+1)
  let code = `${'  '.repeat(i)}if (${cond}) {\n${doBlk}${doBlk?'\n':''}${'  '.repeat(i)}}`
  if (elseBlk) code += ` else {\n${elseBlk}\n${'  '.repeat(i)}}`
  return code + '}'
}
kjsGen['kjs_for_each'] = (b, i) => {
  const v = b.getFieldValue('VAR') || 'item'
  const arr = genKJSValue(b, 'ARR') || '[]'
  const body = genKJSStatements(b, 'DO', i+1)
  return `${'  '.repeat(i)}for (const ${v} of ${arr}) {\n${body||''}\n${'  '.repeat(i)}}`
}
kjsGen['kjs_var_set'] = (b, i) => {
  const v = b.getFieldValue('VAR') || 'myVar'
  const val = genKJSValue(b, 'VAL') || 'null'
  return `${'  '.repeat(i)}let ${v} = ${val}`
}
kjsGen['kjs_var_get'] = (b) => b.getFieldValue('VAR') || 'myVar'
kjsGen['kjs_comment'] = (b, i) => {
  const text = b.getFieldValue('TEXT') || ''
  return `${'  '.repeat(i)}// ${text}`
}
kjsGen['kjs_console_log'] = (b, i) => {
  const val = genKJSValue(b, 'VAL') || "''"
  return `${'  '.repeat(i)}console.log(${val})`
}

// ── Custom JS Block ──
kjsGen['kjs_custom_js'] = (b, i) => {
  const code = b.getFieldValue('CODE') || '// code'
  const lines = code.split('\n')
  return lines.map(l => `${'  '.repeat(i)}${l}`).join('\n')
}

// ── Value Output Blocks ──
kjsGen['kjs_res_loc'] = (b) => `'${b.getFieldValue('LOC') || 'minecraft:dirt'}'`
kjsGen['kjs_json_literal'] = (b) => b.getFieldValue('JSON') || '{}'

// 复用内置积木的生成器（Number/String/Boolean/Logic）
kjsGen['math_number'] = (b) => String(b.getFieldValue('NUM') || '0')
kjsGen['text'] = (b) => `"${(b.getFieldValue('TEXT') || '').replace(/"/g, '\\"')}"`
kjsGen['logic_boolean'] = (b) => (b.getFieldValue('BOOL') === 'TRUE' ? 'true' : 'false')
kjsGen['logic_compare'] = (b) => {
  const a = genKJSValue(b, 'A') || '0'; const g = genKJSValue(b, 'B') || '0'
  const op = b.getFieldValue('OP') || 'EQ'
  const m: Record<string,string> = { EQ:'==', NEQ:'!=', LT:'<', GT:'>', LTE:'<=', GTE:'>=' }
  return `(${a} ${m[op]} ${g})`
}
kjsGen['logic_operation'] = (b) => {
  const a = genKJSValue(b, 'A') || 'false'; const g = genKJSValue(b, 'B') || 'false'
  return `(${a} ${b.getFieldValue('OP')==='AND'?'&&':'||'} ${g})`
}
kjsGen['logic_negate'] = (b) => `!(${genKJSValue(b,'BOOL') || 'false'})`
```

### 6-3: buildKJSToolbox(tab) 函数

根据传入的 KJSTab 返回对应的工具箱定义：

**server 工具箱结构：**
- 📌 TaCZJS 服务端事件 (#FF69B4) — 10个事件帽子
- 📌 KubeJS 服务端事件 (#61AFEF) — 6个事件帽子
- 🔧 事件操作 (#DDA0DD) — ~20个操作积木
- 🔧 工具类 (#61AFEF) — 5个utils积木
- 📐 JS 逻辑控制 (#98C379) — 6个逻辑积木
- 📝 数值/文本/布尔 (复用TACZ颜色)
- 💻 自定义代码 (#9C27B0)

**client 工具箱结构：**
- 📌 TaCZJS 客户端事件 (#4ECDC4) — 5个事件帽子
- 📌 KubeJS 客户端事件 (#87CEEB) — 4个事件帽子
- 🔧 操作+工具 (#DDA0DD/#61AFEF) — 客户端特有操作
- 📐 JS 逻辑 + 数值 + 自定义 (同上)

**startup 工具箱结构：**
- 📌 TaCZJS 启动事件 (#FFD93D) — 9个事件帽子
- 📌 KubeJS 启动事件 (#FF8C00) — 4个事件帽子
- 📌 Create 事件 (#E06C75) — 3个事件帽子
- 🔧 事件操作 (#DDA0DD) — 启动阶段可用操作
- 📐 JS 逻辑 + 数值 + 自定义 (同上)

### 6-4: generateKJSCode() 函数

收集所有顶层 kjs 事件帽子积木，逐个调用 kjsGen 生成代码，拼接返回。

```typescript
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
```

### 6-5: 多工作区 Tab 切换机制

```typescript
// 监听标签切换
watch(activeKJSTab, (newTab, oldTab) => {
  if (currentMode.value !== 'kjs' || !workspace) return
  saveCurrentTabXML(oldTab!)
  loadTabXML(newTab)
  rebuildToolbox()
  handleWorkspaceChange({ type: '' } as any)
})

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
```

### 6-6: 模式切换 API（暴露给 AppTopbar 调用）

在 `(window as any).__tacz_workspace` 上新增方法：

```typescript
switchToKJS() {
  if (!workspace) return
  // 保存 TACZ XML 到 localStorage（可选）
  this.saveTaczXML()
  workspace.clear()
  rebuildToolbox()
  handleWorkspaceChange({ type: '' } as any)
},
switchToTACZ() {
  if (!workspace) return
  workspace.clear()
  // 恢复 TACZ 工具箱和可能的保存内容
  rebuildToolbox()
  handleWorkspaceChange({ type: '' } as any)
},
clearKJS() {
  if (!workspace) return
  workspace.clear()
  // 清空所有标签的 XML
  kjsWorkspaceXMLs.value = { server: '', client: '', startup: '' }
  handleWorkspaceChange({ type: '' } as any)
},
getKJSCodes() {
  // 先保存当前标签
  saveCurrentTabXML(activeKJSTab.value)
  // 为每个标签生成代码
  const result: Record<KJSTab, string> = { server: '', client: '', startup: '' }
  // 临时切换每个标签获取代码... 需要特殊处理
  // 更好的方式：直接从已保存的 XML 解析或切换标签后取
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
```

### 6-7: generateCode() 改造

```typescript
function generateCode(): string {
  if (currentMode.value === 'kjs') {
    return generateKJSCode()
  }
  // 原有 TACZ Lua 生成逻辑不变...
}
```

### 6-8: buildToolbox() 改造

将现有 buildToolbox 重命名为 buildTaczToolbox，新增 buildKJSToolbox，buildToolbox 做分发：

```typescript
function buildToolbox(): Blockly.utils.toolbox.ToolboxDefinition {
  if (currentMode.value === 'kjs') {
    return buildKJSToolbox(activeKJSTab.value)
  }
  return buildTaczToolbox()
}
```

---

## Step 7: App.vue — 引入 KJSTabBar

```vue
<template>
  <div class="app-root">
    <AppTopbar />
    <div class="app-container">
      <div class="workspace-panel">
        <KJSTabBar @switch="onKJSTabSwitch" />
        <BlocklyWorkspace ref="blocklyRef" @code-change="handleCodeChange" />
      </div>
      <div class="editor-panel">
        <CodeEditor :code="luaCode" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ... existing imports ...
import KJSTabBar from './components/KJSTabBar.vue'
import { activeKJSTab, type KJSTab } from './mode'

function onKJSTabSwitch(tab: KJSTab) {
  activeKJSTab.value = tab
}
</script>

<style scoped>
/* workspace-panel 增加 flex-direction: column 让 tab bar 和 workspace 垂直排列 */
.workspace-panel {
  display: flex;
  flex-direction: column;
  /* ... 其他样式保持 */
}
</style>
```

---

## Step 8: locales.ts — KJS i18n 键

在 zh/en 字典中追加：

```typescript
// zh 追加
kjsMode: 'KJS模式',
exportJS: '导出 JS 文件',
kjsExportTitle: '选择要导出的脚本',
kjsExportDesc: '勾选需要下载的 .js 文件',
kjsServerScript: '服务端脚本',
kjsClientScript: '客户端脚本',
kjsStartupScript: '启动脚本',
confirmKJS: '切换到KJS模式将清空工作区，确定继续？',
confirmBackTACZ: '切回TACZ模式将清空KJS工作区，确定继续？',

// en 追加
kjsMode: 'KJS Mode',
exportJS: 'Export JS File',
kjsExportTitle: 'Select scripts to export',
kjsExportDesc: 'Check the .js files you want to download',
kjsServerScript: 'Server Script',
kjsClientScript: 'Client Script',
kjsStartupScript: 'Startup Script',
confirmKJS: 'Switch to KJS mode will clear workspace. Continue?',
confirmBackTACZ: 'Switch back to TACZ will clear KJS workspace. Continue?',
```

---

## 执行顺序建议

按依赖关系排序：

1. **Step 5** (`blocks/index.ts`) — 1行改动，先让积木注册
2. **Step 8** (`locales.ts`) — 纯数据追加，无风险
3. **Step 4b** (`AppTopbar.vue`) — 补全脚本+模板+样式
4. **Step 6** (`BlocklyWorkspace.vue`) — 最核心最复杂的改造
5. **Step 7** (`App.vue`) — 最后组装

## 验证步骤

1. `npm run dev` 启动无报错
2. 点击「KJS模式」→ confirm → 出现三标签栏
3. 默认「服务端」标签，工具箱含 TaCZJS Server + KubeJS Server 分类
4. 切「客户端」→ 工具箱变 Client Events；切「启动」→ Startup + Create
5. 各标签拖积木 → 右侧显示 JS 代码
6. 切标签再切回 → 内容保留
7. 点「导出JS」→ 弹多选框 → 勾选 → 下载 .js 文件
8. 切回「TACZ」→ 一切复原
9. 导入含 `mode:"kjs"` 的 .tlbw → 三标签正确恢复
