# KJS 扩展制作教程
# KJS Extension Tutorial

## 1. KJS 扩展文件是什么？
## What is a KJS Extension File?

KJS 扩展文件是一个 `.kjs-ext.json` 文件，一个文件 = 一个积木栏分类。
导入后会自动在 KJS 模式工具箱中添加一个新的积木分类。
扩展文件只能用于 KJS 模式（TaCZJS/KubeJS），不能用于 TACZ Lua 模式。

A KJS extension file is a `.kjs-ext.json` file. One file = one block category.
After importing, it automatically adds a new block category to the KJS mode toolbox.
Extension files can only be used in KJS mode (TaCZJS/KubeJS), not in TACZ Lua mode.

## 2. 最简单的示例
## Minimal Example

```json
{
  "id": "my_first_ext",
  "name": "我的第一个扩展",
  "nameEn": "My First Extension",
  "colour": "#FF6B6B",
  "icon": "🌟",
  "blocks": [
    {
      "type": "my_hello",
      "message0": "🌟 说你好 %1",
      "args0": [
        { "type": "field_input", "name": "NAME", "text": "世界" }
      ],
      "previousStatement": "kjs_stmt",
      "nextStatement": "kjs_stmt",
      "colour": "#FF6B6B",
      "tooltip": "输出一段问候"
    }
  ],
  "generators": {
    "my_hello": "  console.log('你好, ' + ${NAME})"
  }
}
```

## 3. 字段类型 (args0)
## Field Types (args0)

支持以下字段类型 / Supported field types:

- `field_input` — 文本输入框，用 `name` 指定字段名，`text` 指定默认值 / Text input field, use `name` for field name, `text` for default value
- `field_number` — 数字输入框，用 `name` 指定字段名，`value` 指定默认值 / Number input field, use `name` for field name, `value` for default value
- `field_dropdown` — 下拉选择框，用 `name` 指定字段名，`options` 为 `[["显示名", "值"], ...]` / Dropdown select, use `name` for field name, `options` as `[["Display Name", "value"], ...]`
- `field_checkbox` — 复选框，用 `name` 指定字段名，`checked` 指定默认值 / Checkbox, use `name` for field name, `checked` for default value
- `input_value` — 值输入插口（可连接其他值积木），用 `name` 指定插口名，`check` 指定类型检查 / Value input socket (can connect to other value blocks), use `name` for socket name, `check` for type check
- `input_statement` — 语句输入插口（可连接语句积木），用 `name` 指定插口名，`check` 指定连接类型 / Statement input socket (can connect to statement blocks), use `name` for socket name, `check` for connection type

## 4. 连接类型
## Connection Types

积木的连接类型决定了它们如何拼接 / Block connection types determine how they snap together:

- 事件帽子积木（顶部无连接，底部可接）/ Event hat block (no top connection, bottom is connectable):
  ```json
  "previousStatement": null,
  "nextStatement": "kjs_stmt"
  ```
- 普通语句积木（上下都可接）/ Normal statement block (connectable both ends):
  ```json
  "previousStatement": "kjs_stmt",
  "nextStatement": "kjs_stmt"
  ```
- 值积木（有输出插口）/ Value block (has output socket):
  ```json
  "output": "String"
  ```

## 5. 代码生成器 (generators)
## Code Generators (generators)

key = 积木 type，value = JS 代码模板字符串
用 `${字段名}` 引用积木字段值
语句积木模板以 2 空格缩进开头，值积木直接返回表达式：

key = block type, value = JS code template string
Use `${fieldName}` to reference block field values
Statement block templates start with 2-space indent, value blocks return expressions directly:

```json
"generators": {
  "my_action": "  console.log('${VALUE}')",
  "my_value": "'${VALUE}'"
}
```

## 6. KJS 模式可用的事件 API
## Available Event APIs in KJS Mode

KJS 模式生成的代码运行在 KubeJS 环境中，可使用以下事件 API / Code generated in KJS mode runs in the KubeJS environment, the following event APIs are available:

- `BlockEvents.rightClicked((event) => { ... })`
- `EntityEvents.death((event) => { ... })`
- `PlayerEvents.loggedIn((event) => { ... })`
- `ItemEvents.crafted((event) => { ... })`
- `LevelEvents.loaded((event) => { ... })`
- `ServerEvents.recipes((event) => { ... })`
- `ClientEvents.tick((event) => { ... })`
- `StartupEvents.init((event) => { ... })`

以及 TaCZJS 特有事件 / And TaCZJS-specific events:
- `TaCZServerEvents.entityShoot((event) => { ... })`
- `TaCZClientEvents.playerShoot((event) => { ... })`
- `TaCZStartupEvents.gunDataLoad((event) => { ... })`

事件对象上的常用方法 / Common methods on event objects:
- `event.getEntity()` — 获取实体 / Get entity
- `event.getPlayer()` — 获取玩家 / Get player
- `event.getLevel()` — 获取世界 / Get level
- `event.getBlock()` — 获取方块 / Get block
- `event.getItem()` — 获取物品 / Get item
- `event.cancel()` — 取消事件 / Cancel event

## 7. 完整示例
## Complete Example

```json
{
  "id": "custom_heal_kjs",
  "name": "治疗系统",
  "nameEn": "Heal System",
  "colour": "#4ECDC4",
  "icon": "💊",
  "blocks": [
    {
      "type": "heal_player_kjs",
      "message0": "💊 治疗 %1 点",
      "args0": [
        { "type": "field_number", "name": "AMOUNT", "value": 10 }
      ],
      "previousStatement": "kjs_stmt",
      "nextStatement": "kjs_stmt",
      "colour": "#4ECDC4",
      "tooltip": "治疗玩家指定点数"
    },
    {
      "type": "get_health_kjs",
      "message0": "💊 当前血量",
      "output": "Number",
      "colour": "#4ECDC4",
      "tooltip": "获取玩家当前血量"
    }
  ],
  "generators": {
    "heal_player_kjs": "  event.getEntity()?.heal(${AMOUNT})",
    "get_health_kjs": "event.getEntity()?.getHealth()"
  }
}
```
