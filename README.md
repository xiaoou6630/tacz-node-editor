# 🧩 TACZ Lua 编辑器 (Web版)

> 感谢 [YYN0114](https://github.com/YYN0114) 提供项目图标。

> 基于 Blockly 的 TACZ (Timeless and Classics Zero) 枪械动画状态机图形化编程工具。
> 拖拽积木，生成 Lua 状态机脚本 — 无需手写代码。

---

## ✨ 特性

- 🧩 **Blockly 积木编程** — Google Blockly 驱动的可视化编辑器，kitten 风格圆角主题
- ⌨️ **实时 Lua 生成** — 右侧 CodeMirror 面板即时显示生成的 Lua 状态机代码
- 🐢 **完整 TACZ API 覆盖** — 状态定义、输入事件、动画控制、条件检查、动作操作等 9 大类 50+ 种积木
- 🌐 **双语支持 (中文/English)** — 一键切换语言
- 🎨 **暗色 Kitten 主题** — 柔和配色，圆角设计
- 📦 **一键导出** — 导出为 `.lua` 文件，直接放入 TACZ 枪械包

## 🚀 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/xiaoou6630/tacz-node-editor.git
cd tacz-node-editor/html

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 打开浏览器访问 http://localhost:5173
```

### 生产构建

```bash
npm run build
# 输出: html/dist/ — 部署到任意静态服务器
```

## 📖 使用指南

### 基本流程

1. 从左侧工具箱拖拽 **事件帽子积木** 到画布（如「🎯 射击」）
2. 在事件积木下方拼接 **动作积木**（如「🎬 播放动画」）
3. 右侧面板自动生成对应的 Lua 代码
4. 点击 **文件 → 导出 Lua 文件** 下载 `.lua` 脚本

### 积木分类

| 分类 | 颜色 | 说明 |
|------|------|------|
| 🎯 输入事件 | `#87CEEB` | 23 种玩家操作事件（掏枪、射击、换弹等） |
| 📌 状态定义 | `#FF69B4` | Entry/Update/Exit/Transition 状态定义 |
| 🎬 动画控制 | `#32CD32` | 播放/停止/循环/进度控制动画 |
| 🔍 条件检查 | `#BA55D3` | 弹药、过热、瞄准、地面等条件判断 |
| ⚡ 动作操作 | `#FF8C00` | 抛壳、触发事件、隐藏准星等 |
| 🔗 轨道系统 | `#4A90E2` | 轨道行、轨道、空闲轨道查找 |
| 📐 逻辑控制 | `#FFB347` | If/Return 逻辑控制 |
| 🎞️ 动画模式 | `#98FB98` | 循环/播放一次等模式常量 |
| 🔢 数学运算 | `#DDA0DD` | 加减乘除运算 |

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| [Vue 3](https://vuejs.org/) (Composition API) | UI 框架 |
| [TypeScript](https://www.typescriptlang.org/) | 类型安全 |
| [Google Blockly](https://developers.google.com/blockly) | 积木编辑器引擎 |
| [CodeMirror 6](https://codemirror.net/) | Lua 代码编辑器 |
| [Vite](https://vitejs.dev/) | 构建工具 |

## 📂 项目结构

```
html/
├── index.html             # 入口页面
├── package.json           # 依赖配置
├── vite.config.ts         # Vite 配置
├── public/media/          # Blockly 图标资源
└── src/
    ├── main.ts            # Vue 应用入口
    ├── App.vue            # 主布局（双栏）
    ├── locales.ts         # 中英文语言包
    ├── theme.ts           # Kitten 暗色主题
    ├── blocks/
    │   ├── index.ts       # 积木注册入口
    │   └── tacz.ts        # TACZ 积木定义（50+ 种）
    ├── components/
    │   ├── AppTopbar.vue      # 顶栏组件
    │   ├── BlocklyWorkspace.vue  # Blockly 工作区
    │   └── CodeEditor.vue    # 代码编辑器
    └── styles/
        └── global.css    # 全局样式
```

## 🧊 TACZ API 覆盖

积木基于 TACZ 源码 `GunAnimationConstant.java` 和 `AnimationStateContext.java` 中的 API 设计：

- **事件常量**: `INPUT_DRAW`, `INPUT_SHOOT`, `INPUT_RELOAD` 等（来自 `GunAnimationConstant`）
- **动画方法**: `context:runAnimation()`, `context:stopAnimation()`, `context:setAnimationProgress()` 等
- **条件检查**: `context:hasAmmo()`, `context:isOnGround()`, `context:getAimingProgress()` 等
- **状态机格式**: 生成符合 `LuaStateMachineFactory` 标准的 `M:states()` 结构

## 📄 许可证

[MIT](../LICENSE) © 2026 xiaoou6630
