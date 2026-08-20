# TaCZJS/KJS 模式积木补充与 Bug 修复计划

## 现状分析

根据 `k:\github\taczjs-mod-1.20.1`、`k:\github\KubeJS`、`k:\github\KubeJS-Create` 三个源码仓库的完整分析，当前已定义的积木覆盖了 **TaCZJS 全部事件**，但 **KubeJS 核心事件** 严重不足（仅实现了 ServerEvents/ClientEvents/StartupEvents 中极少数事件），且存在若干逻辑 Bug、界面 Bug 和文字错误。

---

## 一、需要补充的积木

### 1.1 服务端标签 —— 新增 KubeJS BlockEvents（非常常用）

**新分类 "📍 方块事件"**（colour: #56A34A）

| 积木 type | 事件名 | 生成代码 |
|---|---|---|
| `kjs_block_right_clicked` | `BlockEvents.rightClicked` | `BlockEvents.rightClicked((event) => { })` |
| `kjs_block_left_clicked` | `BlockEvents.leftClicked` | `BlockEvents.leftClicked((event) => { })` |
| `kjs_block_placed` | `BlockEvents.placed` | `BlockEvents.placed((event) => { })` |
| `kjs_block_broken` | `BlockEvents.broken` | `BlockEvents.broken((event) => { })` |
| `kjs_block_drops` | `BlockEvents.drops` | `BlockEvents.drops((event) => { })` |
| `kjs_block_farmland_trampled` | `BlockEvents.farmlandTrampled` | `BlockEvents.farmlandTrampled((event) => { })` |
| `kjs_block_random_tick` | `BlockEvents.randomTick` | `BlockEvents.randomTick((event) => { })` |

### 1.2 服务端标签 —— 新增 KubeJS EntityEvents（非常常用）

**新分类 "👹 实体事件"**（colour: #E06C75）

| 积木 type | 事件名 | 生成代码 |
|---|---|---|
| `kjs_entity_death` | `EntityEvents.death` | `EntityEvents.death((event) => { })` |
| `kjs_entity_before_hurt` | `EntityEvents.beforeHurt` | `EntityEvents.beforeHurt((event) => { })` |
| `kjs_entity_after_hurt` | `EntityEvents.afterHurt` | `EntityEvents.afterHurt((event) => { })` |
| `kjs_entity_spawned` | `EntityEvents.spawned` | `EntityEvents.spawned((event) => { })` |
| `kjs_entity_drops` | `EntityEvents.drops` | `EntityEvents.drops((event) => { })` |
| `kjs_entity_check_spawn` | `EntityEvents.checkSpawn` | `EntityEvents.checkSpawn((event) => { })` |

### 1.3 服务端标签 —— 新增 KubeJS PlayerEvents（非常常用）

**新分类 "👤 玩家事件"**（colour: #4B70DD）

| 积木 type | 事件名 | 生成代码 |
|---|---|---|
| `kjs_player_logged_in` | `PlayerEvents.loggedIn` | `PlayerEvents.loggedIn((event) => { })` |
| `kjs_player_logged_out` | `PlayerEvents.loggedOut` | `PlayerEvents.loggedOut((event) => { })` |
| `kjs_player_respawned` | `PlayerEvents.respawned` | `PlayerEvents.respawned((event) => { })` |
| `kjs_player_chat` | `PlayerEvents.chat` | `PlayerEvents.chat((event) => { })` |
| `kjs_player_advancement` | `PlayerEvents.advancement` | `PlayerEvents.advancement((event) => { })` |
| `kjs_player_inventory_changed` | `PlayerEvents.inventoryChanged` | `PlayerEvents.inventoryChanged((event) => { })` |
| `kjs_player_tick` | `PlayerEvents.tick` | `PlayerEvents.tick((event) => { })` |

### 1.4 服务端标签 —— 新增 KubeJS ItemEvents（常用）

**新分类 "📦 物品事件"**（colour: #F39C12）

| 积木 type | 事件名 | 生成代码 |
|---|---|---|
| `kjs_item_right_clicked` | `ItemEvents.rightClicked` | `ItemEvents.rightClicked((event) => { })` |
| `kjs_item_crafted` | `ItemEvents.crafted` | `ItemEvents.crafted((event) => { })` |
| `kjs_item_smelted` | `ItemEvents.smelted` | `ItemEvents.smelted((event) => { })` |
| `kjs_item_food_eaten` | `ItemEvents.foodEaten` | `ItemEvents.foodEaten((event) => { })` |
| `kjs_item_picked_up` | `ItemEvents.pickedUp` | `ItemEvents.pickedUp((event) => { })` |
| `kjs_item_dropped` | `ItemEvents.dropped` | `ItemEvents.dropped((event) => { })` |
| `kjs_item_modify_tooltips` | `ItemEvents.modifyTooltips` | `ItemEvents.modifyTooltips((event) => { })` |

### 1.5 服务端标签 —— 新增 KubeJS LevelEvents（常用）

**新分类 "🌍 世界事件"**（colour: #26A69A）

| 积木 type | 事件名 | 生成代码 |
|---|---|---|
| `kjs_level_loaded` | `LevelEvents.loaded` | `LevelEvents.loaded((event) => { })` |
| `kjs_level_tick` | `LevelEvents.tick` | `LevelEvents.tick((event) => { })` |
| `kjs_level_before_explosion` | `LevelEvents.beforeExplosion` | `LevelEvents.beforeExplosion((event) => { })` |
| `kjs_level_after_explosion` | `LevelEvents.afterExplosion` | `LevelEvents.afterExplosion((event) => { })` |
| `kjs_level_saved` | `LevelEvents.saved` | `LevelEvents.saved((event) => { })` |

### 1.6 服务端标签 —— 补充 KubeJS ServerEvents

在已有 "KubeJS 服务端事件" 中添加：

| 积木 type | 事件名 | 生成代码 |
|---|---|---|
| `kjs_server_unloaded` | `ServerEvents.unloaded` | `ServerEvents.unloaded((event) => { })` |
| `kjs_server_basic_command` | `ServerEvents.basicCommand` | `ServerEvents.basicCommand('cmd', (event) => { })` |

### 1.7 客户端标签 —— 新增 KeyBindEvents

**新分类 "⌨️ 按键绑定"**（colour: #7C3AED）

| 积木 type | 事件名 | 生成代码 |
|---|---|---|
| `kjs_keybind_pressed` | `KeyBindEvents.pressed` | `KeyBindEvents.pressed('key', (event) => { })` |

### 1.8 客户端标签 —— 新增 Debug/Highlight 事件

在已有 "KubeJS 客户端事件" 中添加：

| 积木 type | 事件名 | 生成代码 |
|---|---|---|
| `kjs_client_left_debug` | `ClientEvents.leftDebugInfo` | `ClientEvents.leftDebugInfo((event) => { })` |
| `kjs_client_right_debug` | `ClientEvents.rightDebugInfo` | `ClientEvents.rightDebugInfo((event) => { })` |
| `kjs_client_highlight` | `ClientEvents.highlight` | `ClientEvents.highlight((event) => { })` |

### 1.9 客户端标签 —— 新增 TaCZJS 客户端工具值积木

在已有 "🔧 操作+工具" 中添加值输出积木：

| 积木 type | 生成代码 | 说明 |
|---|---|---|
| `kjs_utils_gun_display` | `TaCZJSUtils.getGunDisplay()` | 获取枪械显示实例 |
| `kjs_utils_gun_operator` | `event.getGunOperator()` | 获取枪械操作器 |
| `kjs_utils_block_hit` | `event.getBlockHitResult()` | 方块击中结果 |
| `kjs_utils_entity_hit` | `event.getEntityHitResult()` | 实体击中结果 |
| `kjs_utils_can_interact` | `event.canInteractEntity()` | 能否交互实体 |

### 1.10 启动标签 —— 补充 KubeJS 启动事件

在已有 "KubeJS 启动事件" 中新增：

| 积木 type | 事件名 | 生成代码 |
|---|---|---|
| `kjs_item_modification` | `ItemEvents.modification` | `ItemEvents.modification((event) => { })` |
| `kjs_block_modification` | `BlockEvents.modification` | `BlockEvents.modification((event) => { })` |

---

## 二、逻辑 Bug 修复

### Bug 1: 模式切换丢失 TACZ 工作区

**问题**：从 TACZ 切到 KJS 再切回，TACZ 的积木和扩展全部丢失。

**方案**：在 `switchToKJS()` 中保存 TACZ 工作区 XML + 扩展状态，在 `switchToTACZ()` 中恢复。

### Bug 2: getKJSCodes() 修改工作区导致闪烁

**问题**：导出 JS 时临时切换工作区到不同标签，会导致界面闪烁（每次 `loadTabXML` 触发 `workspace.clear()` 和 `handleWorkspaceChange`）。

**方案**：改为从 `kjsWorkspaceXMLs` 中直接解析 XML 字符串，用 DOM 遍历方式生成代码，不操作真实 Blockly 工作区。

### Bug 3: CodeEditor 标题/下载绑死 Lua

**问题**：KJS 模式时标题仍显示"生成的 Lua 代码"，下载文件名始终是 `.lua`。

**方案**：CodeEditor 接受 `mode` prop，根据模式显示不同标题和下载后缀。（已包含在 Bug 9 文字错误中）

### Bug 4: 组件注册警告

**问题**：`Blockly.registry.register('connectionChecker' as any, 'TaczChecker', ...)` 在 KJS 模式可能产生无关的连接类型警告。

**方案**：TaczChecker 中忽略 `kjs_stmt` 连接类型检查（不做拦截也不显示错误提示）。

---

## 三、界面 Bug 修复

### Bug 5: CodeEditor 没有 JS 语法高亮

**问题**：CodeMirror 只使用了 `basicSetup`（纯文本），没有导入任何语言语法扩展。KJS 模式显示的 JS 代码没有高亮，阅读体验差。

**方案**：安装 `@codemirror/lang-javascript`，根据 mode prop 动态切换 Lua/JS 语法扩展。

### Bug 6: CodeEditor 下载后缀固定为 .lua

**问题**：`handleDownload()` 中 `a.download = 'state_machine.lua'` 写死。

**方案**：根据 mode 选择 `.lua` 或 `.js` 后缀，KJS 模式下文件名用当前激活标签名（如 `服务端脚本.js`）。

### Bug 7: 空工作区无引导提示

**问题**：初次切换到 KJS 模式，工作区一片空白，用户不知道要拖积木。

**方案**：在 Blockly 初始化后的空白工作区显示 CSS 叠加层引导文字："从左侧工具箱拖入事件积木开始编程"。

### Bug 8: 切换模式后代码面板未立即刷新

**问题**：`switchToKJS()` / `switchToTACZ()` 调用后，代码面板仍显示之前模式的代码。

**方案**：确认 `switchToKJS()` 和 `switchToTACZ()` 末尾主动调用 `handleWorkspaceChange()`，覆盖所有路径。

---

## 四、文字错误修复

### Bug 9: KJS 模式显示 "Lua" 字样

以下 UI 文本在 KJS 模式下显示错误：

| 位置 | 当前文本 | 应改为 |
|---|---|---|
| `AppTopbar.vue:5` 顶部 Logo | `TACZ Lua 编辑器` | KJS 模式时显示 `KJS 编辑器`，TACZ 模式时不变 |
| `locales.ts` `luaCode` 键 | `生成的 Lua 代码` | 新增 `jsCode` 键 → KJS 模式时用 `生成的 JS 代码` |
| `CodeEditor.vue:4` 标题 | `{{ t('luaCode') }}` | 根据 mode 选择 `t('luaCode')` 或 `t('jsCode')` |
| `AppTopbar.vue:97` 关于弹窗描述 | `专为 TACZ 设计的积木编程编辑器` | KJS 模式改为 `专为 KubeJS/TaCZJS 设计的积木编程编辑器` |

**方案**：
- locales.ts 新增 `jsCode` 和 `kjsAboutDesc` 键
- AppTopbar.vue logo 文字改为动态绑定
- CodeEditor.vue 标题根据 mode prop 动态显示

---

## 五、文件改动清单

| 文件 | 改动内容 |
|---|---|
| `package.json` | 添加 `@codemirror/lang-javascript` 依赖 |
| `src/blocks/taczjs.ts` | 新增 ~50 个积木定义（BlockEvents/EntityEvents/PlayerEvents/ItemEvents/LevelEvents/KeyBindEvents/补充事件 + 客户端工具值积木） |
| `src/components/BlocklyWorkspace.vue` | 修复 Bug 1/2/4/7/8；新增 kjsGen 生成器；更新 buildKJSToolbox 工具箱（5 个新分类）；引导提示 |
| `src/components/CodeEditor.vue` | 修复 Bug 5/6/9：接受 mode prop，动态标题/JS 语法高亮/下载名 |
| `src/components/AppTopbar.vue` | 修复 Bug 9：Logo 文字动态化，关于弹窗文字 |
| `src/App.vue` | 传递 currentMode 给 CodeEditor |
| `src/locales.ts` | 新增 `jsCode`、`kjsAboutDesc` 等 i18n 键 |

---

## 六、验证步骤

1. `npm install` — 安装 `@codemirror/lang-javascript`
2. `npm run build` — TypeScript 检查通过，构建成功
3. `npm run dev` — 启动开发服务器
4. 在 Edge 中测试：
   - KJS 模式：工具箱有新增 5 个分类，拖积木生成正确 JS 代码
   - 代码面板有 JS 语法高亮，标题显示"生成的 JS 代码"
   - 顶部 Logo 显示"KJS 编辑器"
   - 空工作区有引导提示
   - 下载按钮可导出 `.js` 文件
5. 测试模式切换：TACZ → KJS → TACZ，积木和扩展不丢失
6. 检查文字：KJS 模式下无 "Lua" 字样
