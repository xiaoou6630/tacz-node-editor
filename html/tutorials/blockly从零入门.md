# 从零开始做 Blockly 图形化代码生成器

> 本教程教你如何用 Google 的 Blockly 库，从空目录开始做出一个"拖积木 → 生成代码"的可视化编程工具。
> 内容完全通用，不绑定任何特定语言。TACZ Lua 编辑器只是它的一个应用实例，最后一章会讲如何套用。

---

## 目录

1. [第一部分：准备工作（装环境）](#第一部分准备工作装环境)
2. [第二部分：Blockly 核心概念（必须先懂）](#第二部分blockly核心概念必须先懂)
3. [第三部分：定义自己的积木](#第三部分定义自己的积木)
4. [第四部分：代码生成器（通用方法论，重点）](#第四部分代码生成器通用方法论重点)
5. [第五部分：工具箱与工作区](#第五部分工具箱与工作区)
6. [第六部分：做成完整应用（Vue 集成）](#第六部分做成完整应用vue-集成)
7. [第七部分：做成通用可扩展系统（进阶）](#第七部分做成通用可扩展系统进阶)
8. [第八部分：实战——生成你自己的语言 / 迁移到 TACZ](#第八部分实战生成你自己的语言--迁移到-tacz)
9. [结尾：这套方法论一句话总结](#结尾这套方法论一句话总结)

---

## 第一部分：准备工作（装环境）

### 1.1 需要什么软件

| 软件 | 用途 | 怎么确认装好了 |
|------|------|----------------|
| Node.js（版本 ≥ 18） | 运行开发服务器、管理依赖 | 打开终端输入 `node -v`，会显示版本号 |
| 浏览器 | 打开调试页面 | Chrome / Edge 都行 |
| VSCode（推荐） | 写代码 | 可选，记事本也行 |

Windows 下装 Node.js：去 nodejs.org 下载 LTS 版本安装包，一路下一步即可。
装完**必须重新打开终端**才能生效。

> ⚠️ **先别急着点"下一步"**：安装位置有一堆坑，装到 C 盘会让你几年后想骂人。
> 看下一节「1.2 安装位置的忠告」再动手，这是全教程最重要的一节。

### 1.2 安装位置的忠告（Windows 必读）

> 这一节讲的全是"当时没事、几年后才发现被坑"的事。**现在就做对，省得以后重装系统。**

#### ① 为什么不能无脑装 C 盘

Windows 默认把所有东西塞进 C 盘：程序、缓存、全局包、项目……
C 盘一满，电脑就变卡、更新失败、游戏装不下。而**绝大多数人 C 盘分区很小**。

装了 Node 之后，会往 C 盘写这么几个地方（记不住没关系，知道"它们都在 C 盘"就行）：

| 东西 | 默认位置 | 会多大 | 能换吗 |
|------|----------|--------|--------|
| Node.js 程序本身 | `C:\Program Files\nodejs` | ~100MB | 安装时选路径 |
| npm 全局包 | `C:\Users\你的用户名\AppData\Roaming\npm` | 越装越大 | 能，见下 |
| npm 下载缓存 | `C:\Users\你的用户名\AppData\Local\npm-cache` | 随随便便几个 G | 能，见下 |
| VSCode 插件 | `C:\Users\你的用户名\.vscode\extensions` | 几个 G | 能，见下 |
| 以后你的项目 | `C:\Users\你的用户名\...` | 无限大 | 建项目时选路径 |

#### ② Node.js 装到 D 盘

用官方安装包时，安装向导选 **Custom（自定义）**，把安装路径改成：

```
D:\Program Files\nodejs
```

> 路径里**不要有中文和空格**（`D:\编程工具\nodejs` 这种会在某些工具里出莫名其妙的 bug）。

#### ③ npm 全局包和缓存改到 D 盘

装完 Node 后打开终端，先建两个文件夹，然后：

```bash
# 告诉 npm：全局包装哪、缓存放哪
npm config set prefix "D:\nodejs\npm-global"
npm config set cache  "D:\nodejs\npm-cache"

# 检查是否生效（会打印两行路径）
npm config get prefix
npm config get cache
```

> 这些配置写在 `C:\Users\你的用户名\.npmrc` 里，**别删它**。

以后 `npm install -g 某某` 装的东西全在 `D:\nodejs\npm-global`，C 盘就不会被悄悄塞爆。

> 如果之前已经装过了、C 盘被塞了一堆缓存，清理命令：
> ```bash
> npm cache clean --force
> ```
> （只删缓存，不影响任何项目。）

#### ④ 用 nvm 管理 Node 版本（推荐，进阶但值得）

nvm（Node Version Manager）能让你随时切换 Node 版本，以后某个项目要老版本、某个要新版，不用卸载重装。推荐 `nvm-windows`（github.com/coreybutler/nvm-windows），安装时同样选 D 盘。

好处：版本不对 → `nvm use 18` 一键切换；重装系统不慌。
坏处：多学一个工具。**如果嫌麻烦，装固定版本 + 改 prefix 也完全可以。**

#### ⑤ 项目不要放在同步盘/中文路径

- **不要**放在 `OneDrive` 同步文件夹里（各种权限问题、同步冲突会搞疯你）
- **不要**放在带中文的路径（`D:\我的项目`）里——Vite、Git、Docker 都可能不认
- 建议：`D:\projects\my-block-editor` 这种，全英文、无空格

#### ⑥ VSCode 插件目录改到 D 盘（可选）

桌面快捷方式右键 → 目标后面加参数（VSCode 的快捷方式图标里改"目标"）：

```
"C:\...\Code.exe" --extensions-dir "D:\vscode-extensions"
```

#### ⑦ 记住两个概念，免得几年后迷惑

- **PATH（环境变量）**：终端输入 `node` 能运行，靠的就是 PATH 告诉系统"node 在哪"。
  安装器会自动帮你把 Node 目录加进 PATH。**所以"重开终端"才生效**——PATH 是在打开终端那一刻读的。
- **node_modules 是可以删的**：一个项目的依赖几百 MB，但只要有 `package.json`，
  删掉 `node_modules` 后跑一遍 `npm install` 就全回来了。
  **所以不要把它备份到网盘，不要把它提交到 Git 仓库**，省空间又省时间。

> 这套"安装即改路径"的习惯，不只适用于本教程。以后装 Python、装 conda、装 VS Code 全按这个思路来：
> **凡是会持续增大的东西（缓存、全局包、虚拟环境），一律放非系统盘。**

### 1.3 创建项目

打开终端，进入你想放项目的目录，然后运行：

```bash
npm create vite@latest my-block-editor -- --template vue-ts
```

> `vite` 是一个前端开发工具：写完代码保存，浏览器自动刷新，不用手动编译。
> `vue-ts` 是模板类型：Vue 3 框架 + TypeScript 语言（带类型检查，能帮我们提前发现错误）。

运行过程中会问一些问题，一路回车默认即可。

### 1.4 安装依赖

```bash
cd my-block-editor
npm install
npm install blockly
```

> 🧨 **`npm install` 特别慢？** 国内网络访问国外源很慢，换镜像一次解决：
> ```bash
> npm config set registry https://registry.npmmirror.com
> ```
> 之后所有项目都走国内镜像，秒装。

关键就一个库：**blockly**。它自己会带上所有需要的渲染、拖拽、保存功能。
你的项目（对比项目里的 `html/package.json`）最终 dependencies 大概长这样：

```json
{
  "dependencies": {
    "blockly": "^11.1.1",
    "vue": "^3.4.0"
  }
}
```

### 1.5 启动并确认

```bash
npm run dev
```

终端会打印一个地址，一般是 `http://localhost:5173`，浏览器打开它。
看到 Vite 的默认页面就说明环境 OK 了。

> 🧨 **`node` 不是内部或外部命令？** 两个原因：
> 1. 装完 Node 后**没重开终端**（PATH 是打开终端那一刻读取的）——先重开试试。
> 2. 安装时没勾选 "Add to PATH"——重装时勾上，或手动把 `node` 所在目录加进系统环境变量。

### 1.6 项目结构长什么样（以本仓库为例）

```
html/
├── index.html            # 入口页面，就一个 <div id="app"> + 加载 main.ts
├── package.json          # 依赖和命令
├── vite.config.ts        # 构建配置
└── src/
    ├── main.ts           # 程序入口，挂载 Vue 应用
    ├── App.vue           # 根组件
    ├── blocks/           # ★ 积木定义（长什么样）
    │   ├── index.ts      #   汇总导入
    │   └── tacz.ts       #   TACZ 的积木都定义在这里
    ├── generators/       # ★ 代码生成器（生成什么代码）——注意！它实际是空的
    ├── components/       # Vue 界面组件
    │   └── BlocklyWorkspace.vue  # ★ 积木画布 + 工具箱 + 全部生成逻辑
    ├── extension-registry.ts     # ★ 可插拔扩展系统
    ├── mode.ts           # 编辑模式状态（TACZ/KJS 切换）
    ├── locales.ts        # 中英文翻译
    └── theme.ts          # 画布主题
```

> 划重点：真正的"代码生成器"在 `BlocklyWorkspace.vue` 里的 `luaGen` 和 `kjsGen` 两个对象中，
> `generators/` 目录反而是空的（历史遗留）。你新建项目时不用管目录叫什么，**先理解职责**：
> - **积木定义** = "积木长什么样"
> - **代码生成器** = "这块积木生成什么代码"
> - 两者通过积木的 `type`（字符串名字）对应起来。

### 1.7 环境层面的"长线坑"（现在不做，几年后必后悔）

> 这些坑的共同特征：**当时没事、不报错，但会在几年后某一天突然反噬你。** 所以现在就得养成习惯。

| 坑 | 说明 | 现在就做 |
|----|------|----------|
| 全装 C 盘 | 当时没事，几年后 C 盘满、系统更新失败 | 按 1.2 节来，安装即改路径 |
| 不学 Git | 改坏代码只能靠复制备份，越改越乱，最后重开项目 | 从第一个项目就 `git init`，每完成一个小功能 `git commit` 存个档 |
| 不读报错 | 出错了就重装、就删 node_modules，从不看报错内容 | 先读报错**第一行**；`node_modules` 删了能重建，别慌 |
| 依赖库永远升到最新 | 新版本可能改了 API，项目突然跑不了 | 看 `package.json` 锁版本；升级前查 changelog |
| 复制粘贴的黑魔法不求甚解 | 代码能用但不懂，遇到变体就不会改 | 每个读不懂的 API 都去官方文档查一次，本教程第 2 部分就是为此而写 |

---

## 第二部分：Blockly 核心概念（必须先懂）

这一部分是全教程的地基，**不读懂这里，后面写代码会一脸懵**。先读概念，再看第三部分的代码。

### 2.1 积木到底是什么

积木（Block）是一块"带插头和插孔的图形组件"。它本质上就是**一个数据结构 + 一张图**：

- **数据结构**：积木有一个 `type`（唯一名字，比如 `"run_animation"`），还有若干字段（字段值）、若干输入（其他积木）。
- **一张图**：Blockly 把它画在画布上，你可以拖拽、拼插、连线。

最关键的一句话：
> **积木 ≠ 代码。** 积木只是一堆"信息"。**代码生成器**负责把这堆信息翻译成文本代码。

### 2.2 积木的类型（必须分清）

积木的"类型"由**连接口的组合**决定，共 5 种。记住它们的接口形状，之后写代码全凭这个：

#### 类型 A：帽子积木（Hat Block）
形状是**圆顶**的，**只有下面一个接口**，通常是整段程序的起点。

- 作用：表示"事件触发时执行"（如"开枪时"、"页面加载时"）
- 接口：只有 `nextStatement`，**没有** `previousStatement`
- 类比：**监听器**。它挂一个事件，下面串一串语句。
- 项目实例：`event_shoot`、`event_reload`（`tacz.ts:103-105`，`setPreviousStatement(false)`）

#### 类型 B：语句积木（Statement Block）
形状像"带凹槽的砖块"，**上下都有接口**，可以串成一列。

```
┌──────────────┐
│  上接口（previousStatement）│
│  播放动画            │
│  下接口（nextStatement）  │
└──────────────┘
```

- 作用：表示"执行一句话"（如"播放动画"、"换弹"）
- 接口：`previousStatement`（上面凹槽）+ `nextStatement`（下面凸起）
- 类比：**段落里的句子**。一句接一句组成一段。
- 项目实例：`run_animation`（`tacz.ts:115`）、`stop_animation`（`tacz.ts:127`）

#### 类型 C：块状语句积木（Nested Statement Block）
像**开了个大肚子**的砖块——除上下接口外，**肚子里面还有"语句插孔"**，能装一整串别的语句。这是"条件/循环"积木的标配。

```
┌──────────────────────┐
│  上接口 │ ❓ 如果 [条件]   │
│        ├─ 成立: ────────┤
│        │   [嵌套的语句]    │   ← 语句插孔（input_statement）
│        └───────────────┤
│  下接口                 │
└──────────────────────┘
```

- 作用：表示"结构控制"（if / for / while / try）
- 接口：`previousStatement` + `nextStatement` + 一个或多个 `input_statement`
- 类比：**带括号的代码块**。肚子里的内容自动缩进一层。
- 项目实例：`if_node`（`tacz.ts:640`，有 `DO` 和 `ELSE` 两个语句插孔）

#### 类型 D：值积木（Value Block）
形状像"插头"，**右边有个凸起接口**。

```
┌──────────────┐
│   5   ───▶    │
└──────────────┘
```

- 作用：表示"一个值/一个表达式"（如数字 5、`ammoCount`、`true`）
- 接口：`output`，并标注输出类型（Number / Boolean / String）
- 类比：**名词或表达式**。它必须插进别的积木的"插孔"里。
- 项目实例：`math_number`（`tacz.ts:696`，输出 Number）、`logic_boolean`（输出 Boolean）

#### 类型 E：终止积木（Terminal Block）
像**带尖底的砖块**，**只有上面一个接口**，串在语句链末尾，表示"这里结束"。

- 作用：表示"跳出/返回/结束"（如 `return`、`break`）
- 接口：只有 `previousStatement`，**没有** `nextStatement`
- 类比：**句号**。句子链在这里到头，下面接不了东西。
- 项目实例：`return_state`（`tacz.ts:649`，但项目里给它加了 next 以便灵活摆放——典型终止积木应去掉 next）

> 判断口诀：**圆顶 = 帽子；上下能串 = 语句；带大肚子能装语句 = 块状；右边插头 = 值；尖底 = 终止。**

> 🧨 **值积木和语句积木可以共存**（一个积木既有 `output` 又有 `previous/next`）。
> 这种"两用积木" Blockly 允许，但会带来歧义：它既当值又当语句，新手容易接错。**建议一个积木只当一种用**，保持清晰。

### 2.3 积木的连接口（Connection）

连接口有 4 种类型（Blockly 内部枚举），加上 2 种"输入插孔"（Input），组合起来决定"哪块能插哪块"：

| 连接口 | 位置 | 作用 |
|--------|------|------|
| `previousStatement` | 上 | 允许别人串在它上面 |
| `nextStatement` | 下 | 允许自己串在别人下面 |
| `output` | 右 | 允许被插进插孔（它是值积木） |
| `input_value`（插孔） | 内部 | 接收一个值积木 |
| `input_statement`（插孔） | 内部 | 接收一串语句积木 |

> 说明：`input_value` / `input_statement` 是"插孔"（Input），内部复用 `nextStatement` 连接类型，
> 所以 Blockly 的 `ConnectionType` 枚举只有 4 种。教程表格把插孔也列出来是因为写代码时你只需要记这 5 个名字。
>
> 项目里实际有**三条连接链**，别搞混：
> - `action_stmt` 链：普通动作语句（`run_animation`、`if_node` 等，`tacz.ts:115/640`）
> - `state_stmt` 链：状态定义专用（`entry`/`update_node`/`exit`，`tacz.ts:49/60/70`），与动作链隔离，防止把状态定义拼进动作串
> - 值积木链：按类型标签（Number / Boolean / String）匹配
>
> 新手最常犯的错：把 `state_stmt` 积木往 `action_stmt` 链上拼——因为两边的连接口外观一模一样，全靠标签在拦。

**连接类型检查**：连接口上可以标一个"类型标签"，比如语句积木标 `'action_stmt'`、值积木标 `'Boolean'`。
Blockly 用标签决定哪些积木能接在一起，这样用户就不会把"数字"插到"条件"里去。

> 🧨 **三个容易被坑的细节（务必记牢）：**
> 1. **类型检查是"交集匹配"不是"精确匹配"**。接口 A 的检查列表只要和接口 B 的检查列表有**交集**就能连上。
>    比如输出标了 `['Boolean','Number']` 的积木，能插进只标 `'Boolean'` 的孔。你写条件判断时别假设"一定只会收到纯布尔"。
> 2. **没设检查类型的连接口 = 通吃**。只要一边没写 `setCheck`，任何积木都能插进来。
>    项目里 `logic_compare` 的 A/B 插孔（`tacz.ts:736`）就没设类型——这是"宽容模式"，新手很容易以为类型系统是强制生效的，其实不是。
> 3. **`previousStatement` 是上面的接口，`nextStatement` 是下面的接口**。
>    新手常写反，结果积木只能往下长、不能串到别人下面。记住英文：previous = 前一个（在上面），next = 下一个（在下面）。

项目里有个自写的检查器 `TaczConnectionChecker`（`BlocklyWorkspace.vue:479`），
它干的事就是：当两个积木接不上时，弹出一条中文提示告诉用户"需要什么类型"。

### 2.4 积木上的零件（Field）

积木表面还能放"输入框"，叫 Field：

| Field | 样子 | 代码 | 读取值 |
|-------|------|------|--------|
| 文本框 | 可直接打字的框 | `new Blockly.FieldTextInput('默认值')` | `block.getFieldValue('名字')` |
| 下拉框 | 点开选一项 | `new Blockly.FieldDropdown([['显示','实际值'],...])` | `block.getFieldValue('名字')` |
| 数字框 | 只能输数字 | `new Blockly.FieldNumber(0)` | `block.getFieldValue('名字')` |

下拉框数组的格式是 `[['显示文字', '实际值'], ['显示文字2', '实际值2']]`。
显示文字可以写中文（用户看到），实际值写代码里的真值（生成代码用）。

> 🧨 **`getFieldValue('下拉框名')` 返回的是第二列"实际值"，不是显示文字。**
> 比如上面 `[['大声', 'LOUD'], ['小声', 'QUIET']]`，你拿到的永远是 `'LOUD'` / `'QUIET'`。
> 这点和 HTML 的 `<select>` 行为一样，别在生成器里拿它去匹配"大声"这种中文，永远匹配不上。

---

## 第三部分：定义自己的积木

### 3.1 最简单的积木

代码格式永远是这样（在 `src/blocks/myblocks.ts` 里写）：

```ts
import * as Blockly from 'blockly'

// 定义一个 type 为 'my_hello' 的积木
Blockly.Blocks['my_hello'] = {
  init() {
    // init() 是"这块积木被创建时"调用一次，用来搭积木的外形
    this.appendDummyInput()          // 加一行"装饰行"
      .appendField('👋 打个招呼')    // 在行上放一段文字
    this.setPreviousStatement(true, 'action_stmt')  // 有上接口
    this.setNextStatement(true, 'action_stmt')      // 有下接口
    this.setColour('#32CD32')        // 颜色
  }
}
```

要点：
- 每个积木注册到 `Blockly.Blocks['类型名']`，类型名**全局唯一**。
- `init()` 里用 `this.xxx()` 的方法搭外形。
- `setPreviousStatement(true, 'action_stmt')` 第一个参数是"有没有这个接口"，第二个是"连接类型标签"。

> 🧨 **`Blockly.Blocks` 是一个全局共享的命名空间。**
> 两个扩展如果定义了**同名的 type**，后注册的那个会**静默覆盖**先注册的，不报任何错。
> 所以 type 命名要有规律、防冲突，比如 `tacz_run_animation`、`my_heal_player`。
> 项目里就真实踩过：`check_aiming` 被定义了两次（`tacz.ts:223` 和 `313`），第一个版本成了死代码，工具箱里两个同名积木拖出来是同一个。
> 另外：**积木定义必须在创建 workspace 之前注册**，否则工具箱里的积木会渲染不出来/报错（`newBlock` 抛 "Block not found"），拖不动。

### 3.2 有零件的积木（字段 Field）

```ts
Blockly.Blocks['my_say'] = {
  init() {
    this.appendDummyInput()
      .appendField('💬 说：')
      .appendField(new Blockly.FieldTextInput('你好'), 'TEXT')   // 文本框，名字叫 TEXT
    this.appendDummyInput()
      .appendField('音调：')
      .appendField(
        new Blockly.FieldDropdown([['大声', 'LOUD'], ['小声', 'QUIET']]),
        'VOLUME'
      )                                                          // 下拉框，名字叫 VOLUME
    this.setPreviousStatement(true, 'action_stmt')
    this.setNextStatement(true, 'action_stmt')
    this.setColour('#FF8C00')
  }
}
```

### 3.3 有插孔的积木（Input）

插孔有两种，都用 `appendXxxInput` 添加：

```ts
Blockly.Blocks['my_if'] = {
  init() {
    // 值插孔：接一个"条件"值积木，要求类型是 Boolean
    this.appendValueInput('COND')
      .setCheck('Boolean')              // ← 只允许输出 Boolean 的积木插进来
      .appendField('❓ 如果')           // ← 插孔前也可以放文字

    // 语句插孔：接一串语句积木，要求类型是 action_stmt
    this.appendStatementInput('DO')
      .setCheck('action_stmt')
      .appendField('成立')

    this.setPreviousStatement(true, 'action_stmt')
    this.setNextStatement(true, 'action_stmt')
    this.setColour('#FFB347')
  }
}
```

### 3.4 值积木（输出积木）

```ts
Blockly.Blocks['my_number'] = {
  init() {
    this.appendDummyInput()
      .appendField(new Blockly.FieldNumber(0), 'NUM')
    this.setOutput(true, 'Number')    // 声明：我是值积木，输出 Number
    this.setColour('#4B70DD')
  }
}
```

### 3.5 帽子积木（事件触发）

```ts
Blockly.Blocks['my_event'] = {
  init() {
    this.setPreviousStatement(false)             // 帽子没有上接口
    this.appendDummyInput().appendField('🚀 启动时')
    this.setNextStatement(true, 'action_stmt')   // 下面可以串语句
    this.setColour('#87CEEB')
  }
}
```

> 本项目里事件帽子很多，`tacz.ts:90-112` 用一个数组 + forEach 批量注册，避免手写 20 遍。
> 这是重要技巧：**积木有规律时，用数据驱动批量生成**。

---

## 第四部分：代码生成器（通用方法论，重点）

### 4.1 生成器是什么

积木定义好之后，Blockly 只知道"图形长什么样"，**不知道生成什么代码**。
生成器就是一堆函数：

```ts
const myGen: Record<string, (block: Blockly.Block, indent?: number) => string> = {}

// 每个积木 type 对应一个函数
// 入参：block（这块积木）、indent（当前缩进层级）
// 出参：生成的代码文本
myGen['my_say'] = (block, indent = 0) => {
  const text = block.getFieldValue('TEXT')      // 读字段值
  const vol  = block.getFieldValue('VOLUME')    // 读下拉值
  return `${'  '.repeat(indent)}say("${text}", ${vol})`
}
```

核心思想：**生成器 = 把积木的字段值 + 子积木生成的代码，拼成一段字符串。**

### 4.2 三个万能助手函数（本教程最重要的套路）

看图写生成器太痛苦？不用怕。任何语言的代码生成器，只需要三个函数，照着套：

```ts
// 助手1：genNext —— 遍历一条语句链（积木串成一列的情况）
// 输入：链上的第一块积木
// 输出：把链上每块积木生成的代码用换行拼起来
function genNext(block: Blockly.Block | null, indent = 1): string {
  if (!block) return ''
  const lines: string[] = []
  let current: Blockly.Block | null = block
  while (current) {
    const fn = myGen[current.type]          // 找这块积木的生成器
    if (fn) lines.push(fn(current, indent)) // 生成一行代码
    current = current.getNextBlock()        // 跳到下一块
  }
  return lines.join('\n')
}

// 助手2：genValue —— 读取某个插孔里插的值积木
// 输入：宿主积木、插孔名
// 输出：值积木生成的表达式字符串（没有就返回默认值）
function genValue(block: Blockly.Block, inputName: string): string {
  const target = block.getInputTargetBlock(inputName)  // 取插孔里的积木
  if (!target) return 'nil'                            // 没插 → 默认值
  const fn = myGen[target.type]
  if (!fn) return 'nil'                                // 生成器没注册 → 也返回默认值，别炸
  return fn(target)                                    // 生成表达式
}

// 助手3：genStatements —— 读取某个语句插孔里的整串语句
// 输入：宿主积木、插孔名、缩进层级
// 输出：嵌套的语句代码
function genStatements(block: Blockly.Block, inputName: string, indent = 1): string {
  const target = block.getInputTargetBlock(inputName)
  if (!target) return ''
  return genNext(target, indent)
}
```

> 这仨函数在项目里就是 `genNext` / `genValue` / `genStatements`（`BlocklyWorkspace.vue:1186-1224`）。
> 无论你生成 Lua、JS、Python、JSON，**结构完全一样**，只是字符串拼接方式不同。

### 4.3 动手写：完整例子（生成一门假想的"说唱语言"）

定义积木（第 3 部分的那些），再写生成器：

```ts
// 1) 帽子：启动时
myGen['my_event'] = (block, indent = 0) => {
  const body = genNext(block.getNextBlock(), indent + 1)  // 生成它下面整串
  return `onStart: do\n${body}\nend`
}

// 2) 语句：说一句话
myGen['my_say'] = (block, indent = 0) => {
  const text = block.getFieldValue('TEXT') || 'hi'
  const vol  = block.getFieldValue('VOLUME') || 'LOUD'
  return `${'  '.repeat(indent)}say("${text}", ${vol})`   // 注意缩进
}

// 3) 语句：如果...那么...
myGen['my_if'] = (block, indent = 0) => {
  const cond  = genValue(block, 'COND')                    // 读条件
  const doBlk = genStatements(block, 'DO', indent + 1)     // 读嵌套语句
  return `${'  '.repeat(indent)}if ${cond} then\n`
       + `${doBlk}\n`
       + `${'  '.repeat(indent)}end`
}

// 4) 值：数字
myGen['my_number'] = (block) => {
  return String(block.getFieldValue('NUM') || '0')
}

// 5) 值：逻辑与（AND）
myGen['my_and'] = (block) => {
  const a = genValue(block, 'A')
  const b = genValue(block, 'B')
  return `(${a} and ${b})`
}

// 6) 值：比较 ≥（比较积木要自己定义，套路同 my_number：输出 Boolean）
myGen['my_compare'] = (block) => {
  const a = genValue(block, 'A')
  const b = genValue(block, 'B')
  return `(${a} >= ${b})`
}
```

> 例子里的"≥ 比较积木"就是上面的 `my_compare`——**生成器能用的积木必须都注册过**，
> 别在示例里引用不存在的积木类型，否则 `myGen[target.type]` 会拿到 `undefined` 直接报错。

假设用户拼了这样一块积木：

```
🚀 启动时
  ├─ ❓ 如果 [5] ≥ [3]（用数字积木拼的）
  │    └─ 成立: 💬 说："成功"，音调：大声
```

调用 `myGen['my_event'](hatBlock)`，输出：

```
onStart: do
  if (5 >= 3) then
    say("成功", LOUD)
  end
end
```

> 关键点：**缩进是用 `'  '.repeat(indent)` 拼出来的**。层级越深缩进越多，代码才可读。

### 4.4 关于生成的执行流程（重要概念）

生成器函数**互相调用**的层次就是积木嵌套的层次：

```
你调用 myGen['my_event'](帽子积木)   ← 生成入口（注意：不是 init()！）
  └─ genNext()         → 找到语句链第一块（if 积木）
       └─ myGen['my_if']() → 调 genValue() 拿条件
       │                  └─ myGen['my_number']() → 返回 "5"
       │                  └─ myGen['my_compare']() → 返回 "(5 >= 3)"
       └─ 调 genStatements() 拿成立部分
            └─ genNext() → 找到 say 积木
                 └─ myGen['my_say']() → 返回 'say("成功", LOUD)'
```

> 🧨 **生成时调用的不是 `init()`！** `init()` 只在积木**被创建**时执行一次（用来搭外形）。
> 每次生成代码，都是从你的入口函数（如 `generateCode` 里的 `myGen[b.type](b)`）开始递归的。
> 把两者混为一谈是新手最常见的概念错误。

### 4.5 值积木的缺省值

`genValue` 返回什么，取决于你写的默认值。不同场景默认值不同：
- 条件没填 → `'true'`（当成总是成立）
- 数字没填 → `'0'`
- 字符串没填 → `'""'`
- 复杂表达式没填 → `'nil'`（Lua）/ `'null'`（JS）

> 🧨 **为什么必须写缺省值？** 因为积木的插孔没接积木时，`getInputTargetBlock()` 返回 `null`，
> 你不写 `|| 默认值`，拼出来的代码里就会冒出 `undefined` 三个字母（字符串拼接 null/undefined 会变成 `"undefined"`），
> 而生成的代码**根本不会报错**——是运行时才炸，查起来极其痛苦。
>
> 🧨 **但 `|| 默认值` 这种写法可能根本不生效！** 这取决于 `genValue` 空插孔时返回什么：
> - 如果 `genValue` 返回**空字符串** `''`，那 `genValue(...) || '0'` 能生效（`''` 是 falsy）；
> - 如果 `genValue` 返回字符串 `'nil'`（项目实际就是这么写的，`BlocklyWorkspace.vue:1211`），
>   **`'nil'` 是非空字符串、是 truthy**，`|| '0'` 永远不会触发！空条件会生成 `if nil then`（恒为假），
>   和上面"条件没填 → 总是成立"的意思**正好相反**。
>
> 稳妥写法是让 `genValue` 自己接受默认值参数：
> ```ts
> function genValue(block, inputName, fallback = '') {
>   const target = block.getInputTargetBlock(inputName)
>   if (!target) return fallback   // 空插孔直接返回传入的默认值
>   const fn = myGen[target.type]
>   return fn ? fn(target) : fallback
> }
> // 用的时候：genValue(block, 'COND', 'true')
> ```
> 项目代码里 `|| 'true'` 从不触发是真实存在的旧写法，别学它。

### 4.6 生成 Lua 时的语义陷阱（生成器写错一行，用户受害一年）

> 你当年学 Python 被 "`try` 后面居然不用写异常类型参数" 坑过——这类坑的共同特征是：
> **它不报错、能跑通，但你的理解是错的，直到某天遇到边缘情况才炸。**
> 生成器里的每条规则都直接影响用户的代码，下面这些必须现在就懂，别让用户被你坑：

| 你以为 | Lua 实际 | 后果 |
|--------|----------|------|
| `0` 是假（和大多数语言一样） | **Lua 里 `0` 是真的**，只有 `false` 和 `nil` 是假 | 生成 `if ammoCount then` 判断"有弹药"永远成立，包括 0 发 |
| 数组从 0 开始 | **Lua 数组从 1 开始** | 生成 `for i = 0, n` 遍历会少/多一个元素 |
| 不等于写 `!=` | Lua 写 `~=` | 生成器里拼错，用户拿到直接报错 |
| `a and b` 返回布尔 | **返回的是 a 或 b 本身**（a 为假返回 a，否则返回 b） | 生成的条件参与运算时类型不对 |
| 字符串拼接用 `+` | 用 `..` | 数字 `+` 字符串不自动转换，直接报错 |
| `continue` 可以跳过循环 | **Lua 5.1/5.2 没有 `continue`** | 用户代码报错；只能改用 `if` 包住后续 |
| 整数除法结果 | 是浮点数 | 显示 2.5 而不是 2，比较时要小心 |

> 对应到生成器：**当你生成 `a == 0` 这种条件时，要意识到用户可能误以为"0 是假"。**
> 好的生成器会显式写 `a == 0`（而不是 `not a`），把语义写清楚，不给用户挖坑。

---

## 第五部分：工具箱与工作区

### 5.1 工具箱（Toolbox）

工具箱是左侧的积木列表。它是**纯 JSON 结构**，三层：

```ts
const toolbox = {
  kind: 'categoryToolbox',          // 顶层：分类式工具箱
  contents: [
    {                               // 第一层：分类
      kind: 'category',
      name: '🎬 动作',
      colour: '#32CD32',            // 分类标题颜色
      contents: [                   // 第二层：里面的积木
        { kind: 'block', type: 'my_say' },
        { kind: 'block', type: 'my_if' },
      ],
    },
    {                               // 第二个分类
      kind: 'category',
      name: '🔢 数值',
      colour: '#4B70DD',
      contents: [
        { kind: 'block', type: 'my_number' },
      ],
    },
    { kind: 'sep' },                // 分隔线（可选）
  ],
}
```

对照项目 `buildTaczToolbox()`（`BlocklyWorkspace.vue:526`）就是这样一个大对象，
里面十几个分类对应游戏里的各种功能。

> 🧨 **工具箱里点了积木却拖不出来？** 九成是工具箱 JSON 里的 `type` 和注册的 `Blockly.Blocks['type']` 名字不一致
> （比如工具箱里写 `'run_animation '` 多了个空格）。先 grep 两边名字，一模一样才行。

### 5.2 工作区（Workspace）创建

```ts
import * as Blockly from 'blockly'

const workspace = Blockly.inject('blocklyDiv', {
  toolbox: toolbox,          // 上面的工具箱
  theme: Blockly.Themes.Classic,   // 主题
  zoom: { controls: true, wheel: true },  // 允许滚轮缩放
})
```

`Blockly.inject` 会在 `id="blocklyDiv"` 的 HTML 元素里画出完整编辑器（工具箱 + 画布）。
项目里把这段逻辑放在了 Vue 组件的 `onMounted` 里（`BlocklyWorkspace.vue` 的 workspace 初始化）。

### 5.3 监听变化 → 重新生成代码

```ts
workspace.addChangeListener(() => {
  const code = generateCode(workspace)  // 每次用户改动积木，重新生成
  editor.value = code                   // 更新右侧预览
})

function generateCode(ws: Blockly.Workspace): string {
  const topBlocks = ws.getTopBlocks(true)   // 取画布上所有"最顶层"的积木
  return topBlocks.map(b => myGen[b.type](b)).join('\n')
}
```

### 5.4 保存 / 加载（XML）

Blockly 自带序列化格式，存成 XML 文本，下次原样还原：

```ts
// 保存：积木 → XML 文本
const xml = Blockly.Xml.workspaceToDom(workspace)
const text = Blockly.Xml.domToText(xml)
// 存到 localStorage 或文件里

// 加载：XML 文本 → 积木
const dom = Blockly.Xml.textToDom(text)
Blockly.Xml.domToWorkspace(dom, workspace)
```

项目里甚至为"TACZ / KJS"两种模式各自保存了一份 XML（`mode.ts` 的 `kjsWorkspaceXMLs`），
切换模式时恢复对应的工作区。

---

## 第六部分：做成完整应用（Vue 集成）

### 6.1 一个最小的 Vue 组件

`src/App.vue`：

```vue
<template>
  <div style="display:flex; height:100vh;">
    <!-- 左：积木画布 -->
    <div id="blocklyDiv" style="flex:1;"></div>
    <!-- 右：生成代码预览 -->
    <pre id="codePreview" style="flex:1; overflow:auto;"></pre>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import * as Blockly from 'blockly'
import './blocks/myblocks'      // 1. 导入积木定义（注册到 Blockly）
import { myGen, generateCode } from './generators/mygen'  // 2. 导入生成器

onMounted(() => {
  // 3. 创建工作区
  const ws = Blockly.inject('blocklyDiv', { toolbox })

  // 4. 变化即刷新预览
  const preview = document.getElementById('codePreview')!
  ws.addChangeListener(() => {
    preview.textContent = generateCode(ws)
  })
})
</script>
```

> 这是**全部的核心**。剩下的功能（菜单、保存、导出、主题、多语言）都是在这个骨架上加肉。

### 6.2 本仓库的实际组织方式

项目比上面的最小例子多了几层，但本质相同：

```
main.ts            → 创建 Vue 应用
App.vue            → 布局 + 顶部工具栏 + 左右分栏
BlocklyWorkspace.vue → 一切 Blockly 逻辑的集合地
  ├─ buildTaczToolbox()     工具箱
  ├─ luaGen / kjsGen        两类生成器
  ├─ handleWorkspaceChange  监听变化 → 生成 → emit 给父组件
  ├─ 扩展管理                导入/激活扩展、重建工具箱
  └─ 连接检查器              中文错误提示
CodeEditor.vue / LuaCodeEditor.vue → 右侧代码编辑器（用 CodeMirror 做高亮）
```

---

## 第七部分：做成通用可扩展系统（进阶）

> 这一部分是你项目最精华、也是"能越做越 nb"的地方。
> 目标：**不写代码也能加新积木**——只要提供一个 JSON 文件。

### 7.1 注册表模式

先定一个"扩展"的数据结构：

```ts
interface Extension {
  id: string                      // 唯一标识
  name: string                    // 中文名
  nameEn: string                  // 英文名
  colour: string                  // 分类颜色
  icon: string                    // 分类图标
  blocks: BlockDef[]              // 积木定义列表
  generators: Record<string, GenFn>  // 每个积木的生成器
}
```

再做一个注册表，用一个 Map 存所有扩展：

```ts
const registered = new Map<string, Extension>()
const active = new Set<string>()          // 哪些被用户勾选激活

function registerExtension(ext: Extension) {
  // 把 ext.blocks 逐个注册给 Blockly
  for (const def of ext.blocks) {
    Blockly.Blocks[def.type] = { init() { this.jsonInit(def) } }
  }
  registered.set(ext.id, ext)
}
```

### 7.2 JSON 定义积木（Blockly 内置黑魔法：jsonInit）

关键在 `jsonInit`：积木定义可以直接写 JSON，不用写 init() 代码。
一个积木的 JSON 是这样的：

```json
{
  "type": "heal_player",
  "message0": "💊 治疗 %1 点",       // %1 = 第一个参数的位置
  "args0": [
    { "type": "field_number", "name": "AMOUNT", "value": 10 }
  ],
  "previousStatement": "action_stmt",
  "nextStatement": "action_stmt",
  "colour": "#4ECDC4",
  "tooltip": "治疗玩家指定点数"
}
```

于是积木定义部分**完全数据化**，用户可以用一个文件描述整个分类：

```json
{
  "id": "heal_system",
  "name": "治疗系统",
  "nameEn": "Heal System",
  "colour": "#4ECDC4",
  "icon": "💊",
  "blocks": [
    { "type": "heal_player", "message0": "💊 治疗 %1 点",
      "args0": [{ "type": "field_number", "name": "AMOUNT", "value": 10 }],
      "previousStatement": "action_stmt", "nextStatement": "action_stmt",
      "colour": "#4ECDC4" }
  ],
  "generators": {
    "heal_player": "  context:heal(${AMOUNT})"
  }
}
```

### 7.3 生成器也数据化

JSON 里 `generators` 直接写字符串模板，运行时编译成函数：

```ts
// 读 JSON → 生成器函数
generators[blockType] = (block, indent = 0) => {
  let code = template   // 如 "  context:heal(${AMOUNT})"
  // 把 ${字段名} 替换成积木字段的实际值
  for (const field of block.inputList.flatMap(i => i.fieldRow)) {
    const name = field.name
    if (name) {
      code = code.replace(new RegExp(`\\$\\{${name}\\}`, 'g'),
                          String(block.getFieldValue(name) ?? ''))
    }
  }
  // 统一处理缩进
  return code.split('\n').map(l => '  '.repeat(indent) + l).join('\n')
}
```

### 7.4 工具箱动态生成

```ts
function getExtensionToolboxCategories() {
  return [...active].map(id => ({
    kind: 'category',
    name: `${ext.icon} ${ext.name}`,
    colour: ext.colour,
    contents: ext.blocks.map(b => ({ kind: 'block', type: b.type })),
  }))
}
```

用户导入一个 JSON → 注册 → 激活 → 重建工具箱 → 新分类立刻出现。
**这就是你项目"导入 .tacz-ext.json 就能加积木"的原理**（`extension-registry.ts` + `BlocklyWorkspace.vue` 的 `handleImportExt`）。

> 🧨 **扩展系统的三个坑：**
> 1. **导入没反应**：JSON 必须含 `id` 和 `blocks` 数组；`generators` 的 key 必须和积木 `type` 完全一致，错一个就静默失效。
> 2. **卸载扩展 ≠ 清空画布**：`unregisterExtension` 只删了 `Blockly.Blocks` 里的定义，画布上**已经存在**的同名积木不受影响，旧项目文件可能因此打不开——保存项目时要把扩展 id 一起存进去（项目就是这么做的）。
> 3. **模板字符串里的 `\${}` 是占位符**：`"  context:heal(\${AMOUNT})"` 里的 `${AMOUNT}` 会被替换成积木字段值；但如果你写 JS 模板字符串（反引号）来构造这段 JSON，`${}` 会被 JS 抢先求值——项目里弹窗的扩展教程就用 `"$" + "{AMOUNT}"` 拼字符串避开（项目源码 `BlocklyWorkspace.vue:238`），7.4 节里的导入代码也是先把 `${FIELD}` 替换成 `" + field + "` 再拼接。这个坑真实存在：**在 JS 里构造生成器模板时，反引号模板字符串和 JSON 模板的 `${}` 语法撞车**。

---

## 第八部分：实战——生成你自己的语言 / 迁移到 TACZ

### 8.1 生成自己语言，只需改一层

到这一步你应该发现：**积木定义、工具箱、注册表全都不变**，
唯一要换的是 `myGen` 里拼的字符串。

比如同样的积木，生成 Python 和 Lua 只差一行：

```ts
// Python 版
myGen['my_say'] = (block, i = 0) => `${'  '.repeat(i)}print(${JSON.stringify(block.getFieldValue('TEXT'))})`

// Lua 版
myGen['my_say'] = (block, i = 0) => `${'  '.repeat(i)}print("${block.getFieldValue('TEXT')}")`
```

> 所以想扩展成"生成任意语言"，设计成**多套生成器 + 一个模式开关**即可。
> 项目就是这么干的：`mode.ts` 一个 `currentMode` 变量，`luaGen` / `kjsGen` 两套生成器，
> 界面右上角切换，工具箱、生成器、甚至保存的 XML 全部跟着切。

> 🧨 **生成 JS 时的语义陷阱**（同 4.6 的道理——生成器写错一行，用户受害一年）：
>
> | 你以为 | JS 实际 | 后果 |
> |--------|---------|------|
> | `==` 比较"值" | 会做**类型转换**（`1 == "1"` 是真的） | 生成器里拼 `==`，用户的比较全走样，应该用 `===` |
> | 变量作用域按块 | 老式 `var` 提升到函数顶 | 循环里用 `var` 会共享同一个变量；生成器应生成 `let`/`const` |
> | 数组/对象赋值是复制 | 是**引用**，改一个另一个也变 | 需要复制得手动 `slice`/`spread` |
> | 回调里的 `this` 是外层的 | 是**调用者** | 生成事件回调时用箭头函数 `=>`，别用 `function` |
> | `0.1 + 0.2` | 是 `0.30000000000000004` | 涉及浮点比较时提醒用户用误差范围 |

### 8.2 迁移到 TACZ：把"通用积木"映射到"游戏 API"

拿项目的例子对照（左边通用概念，右边 TACZ 实现）：

| 通用概念 | TACZ 具体实现 |
|----------|----------------|
| 帽子积木（事件） | `event_shoot` → 生成 `if input == INPUT_SHOOT then ... end` |
| 语句积木（动作） | `run_animation` → 生成 `context:runAnimation("idle", MAIN_TRACK, false, PLAY_ONCE_STOP, 0.2)` |
| 值积木（条件） | `check_ammo_count` → 生成 `context:getAmmoCount() >= 5` |
| 值积木（数字） | `math_number` → 生成 `5` |
| 逻辑积木 | `logic_compare` → 生成 `(a >= b)` |
| 语句嵌套 | `if_node` → 生成 `if cond then ... else ... end` |

生成器例子（`BlocklyWorkspace.vue:1283`）：

```ts
luaGen['run_animation'] = (block, indent = 0) => {
  const anim = block.getFieldValue('ANIM') || 'idle'
  const track = block.getFieldValue('TRACK') || 'MAIN_TRACK'
  const blend = block.getFieldValue('BLEND') || 'false'
  const mode = block.getFieldValue('MODE') || 'PLAY_ONCE_STOP'
  const blendTime = genValue(block, 'BLEND_TIME') || '0.2'
  return `${'  '.repeat(indent)}context:runAnimation("${anim}", ${track}, ${blend}, ${mode}, ${blendTime})`
}
```

帽子积木生成器（`BlocklyWorkspace.vue:1243`）——注意它把下面串的语句放进 if 块里：

```ts
eventTypes.forEach(([id]) => {
  luaGen[`event_${id}`] = (block, indent = 0) => {
    const constName = eventToConst[id]
    const body = genNext(block.getNextBlock(), indent + 1)
    let code = `${'  '.repeat(indent)}if input == ${constName} then\n`
    if (body) code += body + '\n'
    code += `${'  '.repeat(indent)}end`
    return code
  }
})
```

### 8.3 新功能的完整流程（怎么"越做越 nb"）

想给游戏加一个新玩法，完整流程是：

1. **查 API**：去 TACZ 源码 `LuaGunAnimationConstant.java` 找到对应方法，比如 `context:setShouldHideCrossHair(boolean)`。
2. **定义积木**：在 `tacz.ts` 或一个扩展 JSON 里加一个积木：
   ```json
   {
     "type": "hide_crosshair",
     "message0": "🎯 隐藏准星 %1",
     "args0": [{ "type": "field_dropdown", "name": "HIDE",
       "options": [["是","true"],["否","false"]] }],
     "previousStatement": "action_stmt",
     "nextStatement": "action_stmt",
     "colour": "#FF8C00"
   }
   ```
3. **写生成器**：
   ```json
   "generators": { "hide_crosshair": "  context:setShouldHideCrossHair(${HIDE})" }
   ```
4. **加入工具箱**：在 `buildTaczToolbox` 的对应分类里加一行 `{ kind: 'block', type: 'hide_crosshair' }`。
5. **验证**：拼积木 → 看右侧生成的 Lua → 拖进游戏测试。

> 🧨 两件容易漏的事：
> 1. **中英文切换后积木没翻译？** 用项目里的 `_b('中文', 'English')` 包住积木和工具箱里**所有显示文字**，
>    字段值、tooltip 也一样。忘了包，切到英文版界面就剩一堆乱码式的混合文字。
> 2. **缩进乱？** 所有生成器里写代码行的地方，统一用 `'  '.repeat(indent)` 开头，嵌套层级必须 `indent + 1`。
>    混用 tab 和空格也会让代码对不齐，永远只用空格。

---

## 结尾：这套方法论一句话总结

> **定义积木（图形） → 写生成器（翻译） → 组工具箱（展示） → 监听变化重新生成（联动） → 用注册表做成可插拔（扩展）。**
> 五步走完，任何"积木 → 代码"的工具都能做出来。
>
> 最后送你一句话：**工具是拿来理解的，不是拿来崇拜的。** 装环境时多想一步装到哪、
> 写代码时多问一句"它到底返回什么"，几年后你只会感谢现在的自己。