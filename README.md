# TLM 编辑器

一款基于 PyQt6 的可视化 Lua 状态机编辑器，专为 **TACZ（Timeless and Classic Zero）** 武器状态机设计。

通过拖拽节点、连线的方式，无需编写代码即可生成完整的 Lua 状态机脚本。

---

## 快速导航

- [普通用户](#一普通用户下载即用)
- [二次开发者](#二二次开发者从源码运行)
- [如何扩展节点](#三如何扩展节点)
- [如何修改输出语言](#四如何修改输出语言如-lua-pythonjavascript)
- [如何打包发布](#五如何打包发布)

---

## 一、普通用户：下载即用

### 系统要求

- Windows 10/11（64 位）
- 无需安装 Python 环境

### 使用步骤

1. 前往 [Releases](https://github.com/xiaoou6630/tacz-node-editor/releases) 页面下载最新发行版（如 `TLM编辑器-build1.exe`）
2. 双击运行即可
3. 拖拽左侧节点到画布，连接端口，右侧自动显示生成的代码
4. 通过 **文件 -> 保存项目** 保存你的工作（`.json` 格式）

### 快捷键一览

| 操作 | 快捷键 |
|------|--------|
| 新建 | Ctrl+N |
| 保存 | Ctrl+S |
| 打开 | Ctrl+O |
| 生成代码 | Ctrl+G |
| 复制/粘贴 | Ctrl+C / Ctrl+V |
| 撤销/重做 | Ctrl+Z / Ctrl+Y |
| 切换主题 | Ctrl+T |
| 聚焦节点 | F |
| 居中显示 | Home |
| 取消选中 | Ctrl+D |
| 删除 | Delete / Backspace |
| 退出 | Ctrl+Q |

---

## 二、二次开发者：从源码运行

### 环境要求

- Python 3.13+
- Git

### 快速开始

```powershell
# 1. 克隆仓库
git clone https://github.com/xiaoou6630/tacz-node-editor.git
cd tacz-node-editor

# 2. 创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install PyQt6 cryptography

# 4. 运行
python -m pyqt6_editor.main
```

### 项目结构

```
block/
├── pyqt6_editor/          # 核心源码
│   ├── main.py            # 程序入口
│   ├── editor.py          # 编辑器主界面
│   ├── node.py            # 节点基类
│   ├── connection.py      # 连线系统
│   ├── codegen.py         # 代码生成器（Lua）
│   ├── registry.py        # 节点注册表
│   ├── tacz_nodes.py      # 节点定义（状态机节点库）
│   ├── crypto.py          # 加密系统
│   ├── protection.py      # 反调试/保护
│   └── logger.py          # 日志系统
├── mods/                  # 自定义模组目录（已废弃，功能已移除）
├── venv/                  # 虚拟环境（不提交）
├── build_single_file.py   # PyInstaller 打包脚本
├── config.json            # 配置文件
└── .gitignore
```

### 核心文件说明

| 文件 | 用途 | 修改频率 |
|------|------|----------|
| `tacz_nodes.py` | **定义所有节点类型**（状态定义、输入事件、动画控制等） | 添加新节点时改 |
| `codegen.py` | **将节点图转为代码**（目前输出 Lua） | 换输出语言时改 |
| `editor.py` | 主界面 UI、交互逻辑 | 改界面时改 |
| `node.py` | 节点基类、端口系统 | 一般不动 |

---

## 三、如何扩展节点

在 `pyqt6_editor/tacz_nodes.py` 中添加新节点：

```python
@register_node("分类名称", "#颜色码", "节点显示名称", "节点描述")
class MyNewNode(Node):
    """节点文档字符串"""

    def _init_ports(self):
        self.add_input("", PortType.EXEC, "exec")
        self.add_output("", PortType.EXEC, "exec")

    def _get_default_config(self):
        return {'param': 'value'}
```

**端口类型**：
- `PortType.EXEC` - 执行流（粉色圆点）
- `PortType.DATA` - 数据流（灰色圆点），可指定 `"bool"`、`"number"`、`"string"` 等

注册后重启编辑器，新节点会出现在左侧面板。

---

## 四、如何修改输出语言（如 Lua → Python/JavaScript/C#）

核心修改文件：**`pyqt6_editor/codegen.py`**

这是一个代码生成器，负责把节点图转成目标语言。你需要改写以下方法：

| 方法 | 当前作用 | 需要改什么 |
|------|----------|------------|
| `generate()` | 入口函数 | 保持入口不变，修改内部逻辑 |
| `_generate_track_definitions()` | 生成轨道常量定义 | 改为目标语言的常量语法 |
| `_generate_state_table()` | 生成状态表 | 改为目标语言的数据结构 |
| `_generate_state_methods()` | 生成状态方法 | 改为目标语言的函数定义 |
| `_generate_node_code()` | 为每个节点生成代码 | **核心！** 把 Lua API 调用改写为目标语言 |
| `_generate_transition_code()` | 生成状态转换代码 | 改为目标语言的条件判断语法 |

**举例**：如果你想生成 Python 而不是 Lua，需要把：
```lua
context:runAnimation("idle", track, true, PLAY_ONCE_STOP, 0)
```
改为：
```python
context.run_animation("idle", track, True, PlayOnceStop, 0)
```

`pyqt6_editor/tacz_nodes.py` **不需要改动**，因为节点定义与输出语言无关。

---

## 五、如何打包发布

### 方式一：PyInstaller（推荐）

```powershell
.\venv\Scripts\Activate.ps1
pip install pyarmor pyinstaller

python build_single_file.py
```

生成文件位于 `output/dist/TLM编辑器.exe`

**特点**：
- PyArmor 代码混淆（试用版）
- UPX 压缩
- 单文件分发

### 方式二：Nuitka（原生编译，体积小、启动快）

Nuitka 会把 Python 代码编译为 C++，再调用 MSVC 编译为原生 exe。

#### 环境要求（缺一不可）

**1. MSVC 编译器（cl.exe）**

下载地址：[Visual Studio Build Tools 2022](https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/)

安装时勾选：
- ✅ **C++ 桌面开发**（"Desktop development with C++"）
- ✅ **MSVC v143 生成工具**
- ✅ **Windows 11 SDK**（或 Windows 10 SDK）

安装完成后，确认能找到 `cl.exe`，例如：
```
"C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe"
```

**2. Windows SDK**

上面安装 "C++ 桌面开发" 时会自动包含。Nuitka 会自动检测。

**3. Nuitka 包**

```powershell
.\venv\Scripts\Activate.ps1
pip install nuitka
```

**4. UPX（可选，用于压缩）**

已包含在项目中 `upx/` 目录，无需额外安装。

#### 编译步骤

```powershell
.\venv\Scripts\Activate.ps1
pip install nuitka

python build_nuitka.py
```

生成文件位于 `output/nuitka_dist/TLM编辑器.exe`

#### 编译参数说明

`build_nuitka.py` 中使用的主要参数：

| 参数 | 作用 |
|------|------|
| `--standalone` | 独立运行模式，包含所有依赖 |
| `--onefile` | 打包为单个 exe |
| `--windows-console-mode=disable` | 隐藏控制台窗口 |
| `--lto=yes` | 链接时优化，减小体积 |
| `--include-package=cryptography` | 强制包含加密库 |
| `--include-package=PyQt6` | 强制包含 PyQt6 |
| `--nofollow-import-to=...` | 排除不需要的包，减小体积 |

#### 常见问题

**问题：提示找不到 cl.exe**

Nuitka 默认通过 `--msvc=latest` 自动检测。如果失败，需要先运行 VS 开发者命令行（"x64 Native Tools Command Prompt"）激活环境变量，再执行构建。

**问题：链接错误 LNK1104 / 找不到库**

确认 Windows SDK 已正确安装。可以在 PowerShell 中运行以下命令检查：
```powershell
# 检查 MSVC
Get-ChildItem "C:\Program Files\Microsoft Visual Studio" -Recurse -Filter "cl.exe" -ErrorAction SilentlyContinue

# 检查 Windows SDK
Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\Lib" -ErrorAction SilentlyContinue
```

---

## 技术栈

| 组件 | 技术 |
|------|------|
| GUI | PyQt6 |
| 代码保护 | PyArmor（试用版） |
| 压缩 | UPX |
| 打包 | PyInstaller / Nuitka |
| 加密 | cryptography.fernet |

---

## 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 联系方式

- GitHub：https://github.com/xiaoou6630/tacz-node-editor

---

**版本**: build1  
**构建日期**: 2026-06-06
