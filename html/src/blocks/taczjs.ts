/**
 * TaCZJS / KubeJS 积木定义
 * 覆盖 TaCZJS + KubeJS 核心 + KubeJS-Create API
 * 使用独立连接类型 kjs_stmt，避免与 TACZ 的 action_stmt 混用
 */

import * as Blockly from 'blockly'
import { _b } from '../locales'

// 自定义可点击文本字段（用于加减按钮）
class ClickableLabel extends Blockly.FieldLabel {
  private callback_: () => void;
  constructor(text: string, callback: () => void) {
    super(text);
    this.callback_ = callback;
  }
  isClickable(): boolean { return true; }
  onMouseDown_(e: PointerEvent): void {
    e.preventDefault();
    e.stopPropagation();
    if (this.callback_) this.callback_();
  }
}

// ─── 通用选项 ───

const BOOL_OPTS: [string, string][] = [['true', 'true'], ['false', 'false']]
const COMPARE_OPS: [string, string][] = [
  ['==', '=='], ['!=', '!='], ['<', '<'], ['>', '>'], ['<=', '<='], ['>=', '>='],
]

// ═══════════════════════════════════════════════════════════
//  1. TaCZJS Server Events（服务端事件帽子）
// ═══════════════════════════════════════════════════════════

const serverEvents = [
  ['entity_shoot', '⚡ 实体射击'],
  ['entity_aim', '⚡ 实体瞄准'],
  ['entity_melee', '⚡ 实体近战'],
  ['entity_reload', '⚡ 实体换弹'],
]
serverEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_tacz_s_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#FF69B4')
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  2. TaCZJS Server Load Events（服务端数据加载事件帽子）
// ═══════════════════════════════════════════════════════════

const serverLoadEvents = [
  ['gun_data_load', '📋 枪械数据加载'],
  ['attachment_data_load', '📋 配件数据加载'],
  ['attachment_tags_load', '📋 配件标签加载'],
  ['gun_index_load', '📋 枪械索引加载'],
  ['ammo_index_load', '📋 弹药索引加载'],
  ['attachment_index_load', '📋 配件索引加载'],
]
serverLoadEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_tacz_s_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#FF69B4')
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  3. TaCZJS Client Events（客户端事件帽子）
// ═══════════════════════════════════════════════════════════

const clientEvents = [
  ['client_gun_index', '🖥️ 枪械索引加载'],
  ['client_aim', '🖥️ 玩家瞄准'],
  ['client_shoot', '🖥️ 玩家射击'],
  ['client_melee', '🖥️ 玩家近战'],
  ['client_reload', '🖥️ 玩家换弹'],
]
clientEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_tacz_c_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#4ECDC4')
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  4. TaCZJS Startup Events（启动事件帽子）
// ═══════════════════════════════════════════════════════════

const startupEvents = [
  ['recipe_begin', '🔧 配方加载开始'],
  ['recipe_load', '🔧 配方加载中'],
  ['recipe_end', '🔧 配方加载结束'],
  ['startup_gun_data', '📋 枪械数据加载'],
  ['startup_attach_data', '📋 配件数据加载'],
  ['startup_gun_index', '📋 枪械索引加载'],
  ['startup_ammo_index', '📋 弹药索引加载'],
  ['startup_attach_index', '📋 配件索引加载'],
]
startupEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_tacz_u_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#FFD93D')
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  5. KubeJS Server Events（KubeJS 服务端事件帽子）
// ═══════════════════════════════════════════════════════════

const kjsServerEvents = [
  ['loaded', '✅ 服务端加载'],
  ['tick', '⏱️ 服务端Tick'],
  ['recipes', '🔧 配方管理'],
  ['after_recipes', '🔧 配方加载后'],
  ['tags', '🏷️ 标签管理'],
  ['command', '💻 自定义命令'],
  ['unloaded', '⏹️ 服务端卸载'],
  ['basic_command', '💻 简单命令'],
]
kjsServerEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_server_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      if (id === 'command') {
        this.appendDummyInput().appendField('命令名').appendField(new Blockly.FieldTextInput('mycmd'), 'CMD')
      }
      if (id === 'basic_command') {
        this.appendDummyInput().appendField('命令名').appendField(new Blockly.FieldTextInput('mycmd'), 'CMD')
      }
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#61AFEF')
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  6. KubeJS Client Events（KubeJS 客户端事件帽子）
// ═══════════════════════════════════════════════════════════

const kjsClientEvents = [
  ['logged_in', '✅ 玩家登录'],
  ['logged_out', '❌ 玩家登出'],
  ['tick', '⏱️ 客户端Tick'],
  ['lang', '🌐 语言修改'],
  ['left_debug', '📊 左侧调试信息'],
  ['right_debug', '📊 右侧调试信息'],
  ['highlight', '✨ 方块高亮'],
]
kjsClientEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_client_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      if (id === 'lang') {
        this.appendDummyInput().appendField('key').appendField(new Blockly.FieldTextInput('item.modid.xxx'), 'KEY')
      }
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#87CEEB')
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  7. KubeJS Startup Events（KubeJS 启动事件帽子）
// ═══════════════════════════════════════════════════════════

const kjsStartupEvents = [
  ['init', '🚀 初始化'],
  ['post_init', '🚀 后初始化'],
  ['registry', '📦 注册表注册'],
  ['creative_tab', '🎨 修改创造标签'],
  ['item_modification', '📦 物品属性修改'],
  ['block_modification', '🧱 方块属性修改'],
]
kjsStartupEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_startup_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      if (id === 'registry') {
        this.appendDummyInput().appendField('类型').appendField(new Blockly.FieldTextInput('minecraft:item'), 'TYPE')
      }
      if (id === 'creative_tab') {
        this.appendDummyInput().appendField('标签ID').appendField(new Blockly.FieldTextInput('minecraft:combat'), 'TABID')
      }
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#FF8C00')
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  8. Create Events（Create 模组事件帽子）
// ═══════════════════════════════════════════════════════════

const createEvents = [
  ['boiler', '🔥 锅炉加热处理'],
  ['fluid', '💧 管道流体特效'],
  ['spout', '🚿 喷口处理器'],
]
createEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_create_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#E06C75')
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  9. 事件操作积木 — Event Actions
// ═══════════════════════════════════════════════════════════

// --- 取消操作 (仅 client/server shooter events) ---
const cancelBlocks = [
  ['cancel_shoot', '❌ 取消射击'],
  ['cancel_aim', '❌ 取消瞄准'],
  ['cancel_melee', '❌ 取消近战'],
  ['cancel_reload', '❌ 取消换弹'],
]
cancelBlocks.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_ev_${id}`] = {
    init() {
      this.appendDummyInput().appendField(label)
      this.setPreviousStatement(true, 'kjs_stmt')
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#DDA0DD')
    },
  }
})

// --- 客户端特有 ---
Blockly.Blocks['kjs_ev_set_vanilla'] = {
  init() {
    this.appendDummyInput().appendField('✅ 设为原版交互')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD')
  },
}
Blockly.Blocks['kjs_ev_is_vanilla'] = {
  init() {
    this.appendDummyInput().appendField('❓ 是原版交互?')
    this.setOutput(true, 'Boolean')
    this.setColour('#DDA0DD')
  },
}

// --- Shooter 公共方法 ---
Blockly.Blocks['kjs_ev_get_entity'] = {
  init() {
    this.appendDummyInput().appendField('👤 获取实体')
    this.setOutput(true, 'Entity')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_shooter'] = {
  init() {
    this.appendDummyInput().appendField('👤 获取射手')
    this.setOutput(true, 'Entity')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_gun_id'] = {
  init() {
    this.appendDummyInput().appendField('🆔 获取枪械ID')
    this.setOutput(true, 'String')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_gun_item'] = {
  init() {
    this.appendDummyInput().appendField('🔫 获取枪械物品')
    this.setOutput(true, 'ItemStack')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_heat_progress'] = {
  init() {
    this.appendDummyInput().appendField('🌡️ 获取过热进度')
    this.setOutput(true, 'Number')
    this.setColour('#FF6B6B');
  },
}
Blockly.Blocks['kjs_ev_get_heat_amount'] = {
  init() {
    this.appendDummyInput().appendField('🔥 获取过热值')
    this.setOutput(true, 'Number')
    this.setColour('#FF6B6B');
  },
}

// --- Load 公共方法 ---
Blockly.Blocks['kjs_ev_get_id'] = {
  init() {
    this.appendDummyInput().appendField('🆔 获取资源ID')
    this.setOutput(true, 'String')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_json'] = {
  init() {
    this.appendDummyInput().appendField('📄 获取原始JSON')
    this.setOutput(true, 'String')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_std_json'] = {
  init() {
    this.appendDummyInput().appendField('📄 获取标准JSON')
    this.setOutput(true, 'String')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_set_json'] = {
  init() {
    this.appendDummyInput().appendField('📝 设置JSON %1')
    this.appendValueInput('JSON').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD');
  },
}

// --- 数据获取 ---
Blockly.Blocks['kjs_ev_get_gun_data'] = {
  init() {
    this.appendDummyInput().appendField('📋 获取枪械数据')
    this.setOutput(true, 'GunData')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_attach_data'] = {
  init() {
    this.appendDummyInput().appendField('📋 获取配件数据')
    this.setOutput(true, 'AttachmentData')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_pojo'] = {
  init() {
    this.appendDummyInput().appendField('📋 获取POJO')
    this.setOutput(true, 'POJO')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_attach_tags'] = {
  init() {
    this.appendDummyInput().appendField('📋 获取配件标签')
    this.setOutput(true, 'Array')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_table_recipe'] = {
  init() {
    this.appendDummyInput().appendField('📋 获取配方数据')
    this.setOutput(true, 'TableRecipe')
    this.setColour('#DDA0DD');
  },
}

// --- 删除/移除操作 ---
Blockly.Blocks['kjs_ev_remove_gun'] = {
  init() {
    this.appendDummyInput().appendField('🗑️ 移除枪械')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_remove_attachment'] = {
  init() {
    this.appendDummyInput().appendField('🗑️ 移除配件')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_remove_recipe'] = {
  init() {
    this.appendDummyInput().appendField('🗑️ 移除配方')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_remove_all_recipes'] = {
  init() {
    this.appendDummyInput().appendField('🗑️ 移除全部配方')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_put_recipe'] = {
  init() {
    this.appendDummyInput().appendField('📝 添加配方 ID:%1')
    this.appendValueInput('ID').setCheck('String')
    this.appendDummyInput().appendField('JSON:%2')
    this.appendValueInput('JSON').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_kill_entity'] = {
  init() {
    this.appendDummyInput().appendField('💀 杀死实体')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD');
  },
}

// ═══════════════════════════════════════════════════════════
//  10. Utils 工具类积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_utils_open_refit'] = {
  init() {
    this.appendDummyInput().appendField('🔧 打开改装界面')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#61AFEF');
  },
}
Blockly.Blocks['kjs_utils_hold_gun'] = {
  init() {
    this.appendDummyInput().appendField('🔫 主手持枪?')
    this.setOutput(true, 'Boolean')
    this.setColour('#61AFEF');
  },
}
Blockly.Blocks['kjs_utils_get_gun_idx'] = {
  init() {
    this.appendDummyInput().appendField('📋 获取枪械索引 %1')
    this.appendValueInput('ID').setCheck('String')
    this.setOutput(true, 'GunIndex')
    this.setColour('#61AFEF');
  },
}
Blockly.Blocks['kjs_utils_get_ammo_idx'] = {
  init() {
    this.appendDummyInput().appendField('📋 获取弹药索引 %1')
    this.appendValueInput('ID').setCheck('String')
    this.setOutput(true, 'AmmoIndex')
    this.setColour('#61AFEF');
  },
}
Blockly.Blocks['kjs_utils_get_attach_idx'] = {
  init() {
    this.appendDummyInput().appendField('📋 获取配件索引 %1')
    this.appendValueInput('ID').setCheck('String')
    this.setOutput(true, 'AttachmentIndex')
    this.setColour('#61AFEF');
  },
}

// ═══════════════════════════════════════════════════════════
//  11. JS 逻辑控制积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_if'] = {
  init() {
    this.appendValueInput('COND').setCheck('Boolean').appendField('❓ 如果')
    this.appendStatementInput('DO').setCheck('kjs_stmt').appendField('成立')
    this.appendStatementInput('ELSE').setCheck('kjs_stmt').appendField('否则')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}
Blockly.Blocks['kjs_for_each'] = {
  init() {
    this.appendDummyInput()
      .appendField('🔄 for (const ')
      .appendField(new Blockly.FieldTextInput('item'), 'VAR')
      .appendField(' of ')
    this.appendValueInput('ARR').setCheck('Array').appendField(')')
    this.appendStatementInput('DO').setCheck('kjs_stmt')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}
Blockly.Blocks['kjs_var_set'] = {
  init() {
    this.appendDummyInput()
      .appendField('📦 设 ')
      .appendField(new Blockly.FieldTextInput('myVar'), 'VAR')
      .appendField(' = ')
    this.appendValueInput('VAL')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}
Blockly.Blocks['kjs_var_get'] = {
  init() {
    this.appendDummyInput()
      .appendField('📦 变量 ')
      .appendField(new Blockly.FieldTextInput('myVar'), 'VAR')
    this.setOutput(true, 'Any')
    this.setColour('#98C379');
  },
}
Blockly.Blocks['kjs_comment'] = {
  init() {
    this.appendDummyInput()
      .appendField('💬 // ')
      .appendField(new Blockly.FieldTextInput('注释'), 'TEXT')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}
Blockly.Blocks['kjs_console_log'] = {
  init() {
    this.appendDummyInput().appendField('📝 console.log(%1)')
    this.appendValueInput('VAL')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}

// ═══════════════════════════════════════════════════════════
//  12. 自定义 JS 代码积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_custom_js'] = {
  init() {
    this.appendDummyInput().appendField('📝 自定义代码')
    this.appendDummyInput()
      .appendField(new Blockly.FieldTextInput('// code here'), 'CODE')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#9C27B0');
  },
}

// ═══════════════════════════════════════════════════════════
//  13. 值输出积木（复用 TACZ 的连接类型）
// ═══════════════════════════════════════════════════════════

// ResourceLocation
Blockly.Blocks['kjs_res_loc'] = {
  init() {
    this.appendDummyInput().appendField('🆔 资源位置')
    this.appendDummyInput().appendField(new Blockly.FieldTextInput('minecraft:dirt'), 'LOC')
    this.setOutput(true, 'ResourceLocation')
    this.setColour('#4B70DD');
  },
}

// JSON 字面量
Blockly.Blocks['kjs_json_literal'] = {
  init() {
    this.appendDummyInput().appendField('{} JSON')
    this.appendDummyInput().appendField(new Blockly.FieldTextInput('{}'), 'JSON')
    this.setOutput(true, 'String')
    this.setColour('#4B70DD');
  },
}

// ═══════════════════════════════════════════════════════════
//  14. KubeJS BlockEvents（方块事件帽子）
// ═══════════════════════════════════════════════════════════

const blockEvents = [
  ['right_clicked', '📍 右键点击方块'],
  ['left_clicked', '📍 左键点击方块'],
  ['placed', '📍 放置方块'],
  ['broken', '📍 破坏方块'],
  ['drops', '📍 方块掉落'],
  ['farmland_trampled', '📍 耕地被踩'],
  ['random_tick', '📍 方块随机刻'],
]
blockEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_block_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#56A34A');
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  15. KubeJS EntityEvents（实体事件帽子）
// ═══════════════════════════════════════════════════════════

const entityEvents = [
  ['death', '💀 实体死亡'],
  ['before_hurt', '💥 实体受伤前'],
  ['after_hurt', '💥 实体受伤后'],
  ['spawned', '✨ 实体生成'],
  ['drops', '🎁 实体掉落'],
  ['check_spawn', '❓ 检查生成'],
]
entityEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_entity_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#E06C75');
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  16. KubeJS PlayerEvents（玩家事件帽子）
// ═══════════════════════════════════════════════════════════

const playerEvents = [
  ['logged_in', '🔵 玩家登录'],
  ['logged_out', '🔴 玩家登出'],
  ['respawned', '🔄 玩家重生'],
  ['chat', '💬 聊天消息'],
  ['advancement', '🏆 获得进度'],
  ['inventory_changed', '📦 物品栏变化'],
  ['tick', '⏱️ 玩家Tick'],
]
playerEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_player_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#4B70DD');
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  17. KubeJS ItemEvents（物品事件帽子）
// ═══════════════════════════════════════════════════════════

const itemEvents = [
  ['right_clicked', '🖱️ 右键使用物品'],
  ['crafted', '🔨 合成物品'],
  ['smelted', '🔥 烧炼物品'],
  ['food_eaten', '🍔 食用食物'],
  ['picked_up', '📥 拾取物品'],
  ['dropped', '📤 丢弃物品'],
  ['modify_tooltips', '💬 修改提示'],
]
itemEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_item_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#F39C12');
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  18. KubeJS LevelEvents（世界事件帽子）
// ═══════════════════════════════════════════════════════════

const levelEvents = [
  ['loaded', '🌍 世界加载'],
  ['tick', '⏱️ 世界Tick'],
  ['saved', '💾 世界保存'],
  ['before_explosion', '💥 爆炸前'],
  ['after_explosion', '💥 爆炸后'],
]
levelEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_level_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#26A69A');
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  19. KubeJS KeyBindEvents（按键绑定事件帽子）
// ═══════════════════════════════════════════════════════════

const keybindEvents = [
  ['pressed', '⌨️ 按键按下'],
]
keybindEvents.forEach(([id, label]) => {
  Blockly.Blocks[`kjs_keybind_${id}`] = {
    init() {
      this.setPreviousStatement(false)
      this.appendDummyInput().appendField(label)
      this.appendDummyInput().appendField('键名').appendField(new Blockly.FieldTextInput('my_key'), 'KEY')
      this.setNextStatement(true, 'kjs_stmt')
      this.setColour('#7C3AED');
    },
  }
})

// ═══════════════════════════════════════════════════════════
//  20. TaCZJS 客户端工具值积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_utils_gun_display'] = {
  init() {
    this.appendDummyInput().appendField('🔫 枪械显示实例')
    this.setOutput(true, 'GunDisplay')
    this.setColour('#61AFEF');
  },
}
Blockly.Blocks['kjs_utils_gun_operator'] = {
  init() {
    this.appendDummyInput().appendField('🎮 枪械操作器')
    this.setOutput(true, 'GunOperator')
    this.setColour('#61AFEF');
  },
}
Blockly.Blocks['kjs_utils_block_hit'] = {
  init() {
    this.appendDummyInput().appendField('🧱 方块击中结果')
    this.setOutput(true, 'BlockHitResult')
    this.setColour('#61AFEF');
  },
}
Blockly.Blocks['kjs_utils_entity_hit'] = {
  init() {
    this.appendDummyInput().appendField('👤 实体击中结果')
    this.setOutput(true, 'EntityHitResult')
    this.setColour('#61AFEF');
  },
}
Blockly.Blocks['kjs_utils_can_interact'] = {
  init() {
    this.appendDummyInput().appendField('❓ 能否交互实体')
    this.setOutput(true, 'Boolean')
    this.setColour('#61AFEF');
  },
}

// ═══════════════════════════════════════════════════════════
//  21. 通用事件值积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_ev_get_player'] = {
  init() {
    this.appendDummyInput().appendField('👤 获取玩家')
    this.setOutput(true, 'Player')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_level'] = {
  init() {
    this.appendDummyInput().appendField('🌍 获取世界')
    this.setOutput(true, 'Level')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_block'] = {
  init() {
    this.appendDummyInput().appendField('🧱 获取方块')
    this.setOutput(true, 'Block')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_item'] = {
  init() {
    this.appendDummyInput().appendField('📦 获取物品')
    this.setOutput(true, 'ItemStack')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_server'] = {
  init() {
    this.appendDummyInput().appendField('🖥️ 获取服务器')
    this.setOutput(true, 'Server')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_cancel'] = {
  init() {
    this.appendDummyInput().appendField('🚫 取消事件')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_set_result'] = {
  init() {
    this.appendDummyInput().appendField('✅ 设置结果')
    this.appendValueInput('VALUE')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD');
  },
}

// ═══════════════════════════════════════════════════════════
//  22. 服务端工具积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_util_get_all_players'] = {
  init() {
    this.appendDummyInput().appendField('👥 获取所有玩家')
    this.setOutput(true, 'Array')
    this.setColour('#61AFEF');
  },
}
Blockly.Blocks['kjs_util_send_msg'] = {
  init() {
    this.appendDummyInput().appendField('💬 发送消息')
    this.appendValueInput('MSG').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#61AFEF');
  },
}
Blockly.Blocks['kjs_util_run_cmd'] = {
  init() {
    this.appendDummyInput().appendField('⚡ 执行命令')
    this.appendValueInput('CMD').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#61AFEF');
  },
}
Blockly.Blocks['kjs_util_schedule'] = {
  init() {
    this.appendDummyInput().appendField('⏰ 延迟Tick %1')
    this.appendValueInput('TICKS').setCheck('Number')
    this.appendStatementInput('DO').setCheck('kjs_stmt')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#61AFEF');
  },
}

// ═══════════════════════════════════════════════════════════
//  23. 事件操作积木的补充
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_ev_log'] = {
  init() {
    this.appendDummyInput().appendField('📝 日志输出')
    this.appendValueInput('MSG').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_damage'] = {
  init() {
    this.appendDummyInput().appendField('💥 获取伤害值')
    this.setOutput(true, 'Number')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_set_damage'] = {
  init() {
    this.appendDummyInput().appendField('💥 设置伤害值 %1')
    this.appendValueInput('DAMAGE').setCheck('Number')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#DDA0DD');
  },
}

// ═══════════════════════════════════════════════════════════
//  24. 通用事件值积木（补充）
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_ev_get_source'] = {
  init() {
    this.appendDummyInput().appendField('💥 获取伤害源')
    this.setOutput(true, 'DamageSource')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_hand'] = {
  init() {
    this.appendDummyInput().appendField('✋ 获取手部')
    this.setOutput(true, 'InteractionHand')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_facing'] = {
  init() {
    this.appendDummyInput().appendField('🧭 获取方向')
    this.setOutput(true, 'Direction')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_message'] = {
  init() {
    this.appendDummyInput().appendField('💬 获取消息文本')
    this.setOutput(true, 'String')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_username'] = {
  init() {
    this.appendDummyInput().appendField('👤 获取用户名')
    this.setOutput(true, 'String')
    this.setColour('#DDA0DD');
  },
}
Blockly.Blocks['kjs_ev_get_random'] = {
  init() {
    this.appendDummyInput().appendField('🎲 获取随机源')
    this.setOutput(true, 'RandomSource')
    this.setColour('#DDA0DD');
  },
}

// ═══════════════════════════════════════════════════════════
//  25. 配方操作积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_recipe_remove'] = {
  init() {
    this.appendDummyInput().appendField('🗑️ 移除配方')
    this.appendValueInput('FILTER').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_recipe_replace_input'] = {
  init() {
    this.appendDummyInput().appendField('🔀 替换配方输入 %1 → %2')
    this.appendValueInput('FILTER').setCheck('String')
    this.appendValueInput('FROM').setCheck('String')
    this.appendValueInput('TO').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_recipe_replace_output'] = {
  init() {
    this.appendDummyInput().appendField('🔀 替换配方输出 %1 → %2')
    this.appendValueInput('FILTER').setCheck('String')
    this.appendValueInput('FROM').setCheck('String')
    this.appendValueInput('TO').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}

// ═══════════════════════════════════════════════════════════
//  26. 标签操作积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_tag_add'] = {
  init() {
    this.appendDummyInput().appendField('🏷️ 添加标签 %1 %2')
    this.appendValueInput('TAG').setCheck('String')
    this.appendValueInput('VALUES')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}
Blockly.Blocks['kjs_tag_remove'] = {
  init() {
    this.appendDummyInput().appendField('🏷️ 移除标签 %1 %2')
    this.appendValueInput('TAG').setCheck('String')
    this.appendValueInput('VALUES')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}
Blockly.Blocks['kjs_tag_remove_all'] = {
  init() {
    this.appendDummyInput().appendField('🏷️ 清空标签 %1')
    this.appendValueInput('TAG').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}

// ═══════════════════════════════════════════════════════════
//  27. 阶段与进度积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_stage_get'] = {
  init() {
    this.appendDummyInput().appendField('🎯 获取阶段名称')
    this.setOutput(true, 'String')
    this.setColour('#4B70DD');
  },
}
Blockly.Blocks['kjs_stage_add'] = {
  init() {
    this.appendDummyInput().appendField('🎯 添加阶段 %1')
    this.appendValueInput('STAGE').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#4B70DD');
  },
}
Blockly.Blocks['kjs_stage_remove'] = {
  init() {
    this.appendDummyInput().appendField('🎯 移除阶段 %1')
    this.appendValueInput('STAGE').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#4B70DD');
  },
}

// ═══════════════════════════════════════════════════════════
//  28. 语言文件积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_lang_add'] = {
  init() {
    this.appendDummyInput().appendField('🌐 添加翻译 %1 = %2')
    this.appendValueInput('KEY').setCheck('String')
    this.appendValueInput('VALUE').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#87CEEB');
  },
}
Blockly.Blocks['kjs_lang_rename_item'] = {
  init() {
    this.appendDummyInput().appendField('🌐 重命名物品 %1 → %2')
    this.appendValueInput('ITEM').setCheck('String')
    this.appendValueInput('NAME').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#87CEEB');
  },
}
Blockly.Blocks['kjs_lang_rename_block'] = {
  init() {
    this.appendDummyInput().appendField('🌐 重命名方块 %1 → %2')
    this.appendValueInput('BLOCK').setCheck('String')
    this.appendValueInput('NAME').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#87CEEB');
  },
}

// ═══════════════════════════════════════════════════════════
//  28. 爆炸/世界事件值积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_ev_get_position'] = {
  init() {
    this.appendDummyInput().appendField('📍 获取位置')
    this.setOutput(true, 'Vec3')
    this.setColour('#26A69A');
  },
}
Blockly.Blocks['kjs_ev_get_size'] = {
  init() {
    this.appendDummyInput().appendField('📏 获取爆炸大小')
    this.setOutput(true, 'Number')
    this.setColour('#26A69A');
  },
}
Blockly.Blocks['kjs_ev_set_size'] = {
  init() {
    this.appendDummyInput().appendField('📏 设置爆炸大小 %1')
    this.appendValueInput('SIZE').setCheck('Number')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#26A69A');
  },
}
Blockly.Blocks['kjs_ev_get_affected_entities'] = {
  init() {
    this.appendDummyInput().appendField('👥 获取受影响的实体')
    this.setOutput(true, 'Array')
    this.setColour('#26A69A');
  },
}
Blockly.Blocks['kjs_ev_get_affected_blocks'] = {
  init() {
    this.appendDummyInput().appendField('🧱 获取受影响的方块')
    this.setOutput(true, 'Array')
    this.setColour('#26A69A');
  },
}
Blockly.Blocks['kjs_ev_remove_knockback'] = {
  init() {
    this.appendDummyInput().appendField('🚫 移除爆炸击退')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#26A69A');
  },
}

// ═══════════════════════════════════════════════════════════
//  29. 实体掉落积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_ev_get_drops'] = {
  init() {
    this.appendDummyInput().appendField('🎁 获取掉落物列表')
    this.setOutput(true, 'Array')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_ev_add_drop'] = {
  init() {
    this.appendDummyInput().appendField('🎁 添加掉落物 %1')
    this.appendValueInput('STACK').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_ev_is_recently_hit'] = {
  init() {
    this.appendDummyInput().appendField('🎁 近期被击中?')
    this.setOutput(true, 'Boolean')
    this.setColour('#E06C75');
  },
}

// ═══════════════════════════════════════════════════════════
//  30. 聊天消息积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_ev_get_chat_component'] = {
  init() {
    this.appendDummyInput().appendField('💬 获取聊天组件')
    this.setOutput(true, 'Component')
    this.setColour('#4B70DD');
  },
}
Blockly.Blocks['kjs_ev_set_chat_component'] = {
  init() {
    this.appendDummyInput().appendField('💬 设置聊天组件 %1')
    this.appendValueInput('COMPONENT')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#4B70DD');
  },
}

// ═══════════════════════════════════════════════════════════
//  31. KubeJS-Create 注册块
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_create_boiler_add'] = {
  init() {
    this.appendDummyInput().appendField('🔥 注册锅炉加热器')
    this.appendValueInput('BLOCK').setCheck('String').appendField('方块ID')
    this.appendStatementInput('HANDLER').setCheck('kjs_stmt').appendField('加热回调')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_create_fluid_add'] = {
  init() {
    this.appendDummyInput().appendField('💧 注册管道流体特效')
    this.appendValueInput('FLUID').setCheck('String').appendField('流体ID')
    this.appendStatementInput('HANDLER').setCheck('kjs_stmt').appendField('特效回调')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_create_spout_add'] = {
  init() {
    this.appendDummyInput().appendField('🚿 注册喷口处理器')
    this.appendValueInput('PATH').setCheck('String').appendField('路径')
    this.appendValueInput('BLOCK').setCheck('String').appendField('方块')
    this.appendStatementInput('HANDLER').setCheck('kjs_stmt').appendField('处理回调')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_create_heat_return'] = {
  init() {
    this.appendDummyInput().appendField('🔥 返回热量 %1')
    this.appendValueInput('HEAT').setCheck('Number')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_create_fluid_apply'] = {
  init() {
    this.appendDummyInput().appendField('💧 应用流体效果')
    this.appendValueInput('FLUID').setCheck('String')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}

// ═══════════════════════════════════════════════════════════
//  32. KubeJS-Create 回调变量积木
// ═══════════════════════════════════════════════════════════

Blockly.Blocks['kjs_cb_block'] = {
  init() {
    this.appendDummyInput().appendField('🧱 回调方块对象')
    this.setOutput(true, 'LevelBlock')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_cb_level'] = {
  init() {
    this.appendDummyInput().appendField('🌍 回调世界对象')
    this.setOutput(true, 'Level')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_cb_aabb'] = {
  init() {
    this.appendDummyInput().appendField('📦 回调AABB范围')
    this.setOutput(true, 'AABB')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_cb_fluid'] = {
  init() {
    this.appendDummyInput().appendField('💧 回调流体对象')
    this.setOutput(true, 'FluidStack')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_cb_simulate'] = {
  init() {
    this.appendDummyInput().appendField('🔍 是否模拟?')
    this.setOutput(true, 'Boolean')
    this.setColour('#E06C75');
  },
}
Blockly.Blocks['kjs_create_heat_no_heat'] = {
  init() {
    this.appendDummyInput().appendField('🔥 无热量(NO_HEAT)')
    this.setOutput(true, 'Number')
    this.setColour('#E06C75');
  },
}

// ═══════════════════════════════════════════════════════════
//  33. Create 配方注册积木（用于 ServerEvents.recipes）
// ═══════════════════════════════════════════════════════════
// 粉碎 — 动态输出槽位
Blockly.Blocks['kjs_create_rc_crushing'] = {
  init() {
    this.outputCount_ = 1;
    this.updateShape_();
    this.setPreviousStatement(true, 'kjs_stmt');
    this.setNextStatement(true, 'kjs_stmt');
    this.setColour('#E06C75');
  },
  updateShape_() {
    while (this.inputList.length > 0) this.removeInput(this.inputList[0].name);
    this.appendDummyInput().appendField('🔨 粉碎');
    this.appendDummyInput()
      .appendField('输入')
      .appendField(new Blockly.FieldTextInput('minecraft:stone'), 'INPUT');
    for (let i = 1; i <= this.outputCount_; i++) {
      this.appendDummyInput()
        .appendField(`─ 输出${i} ─`)
        .appendField(new Blockly.FieldTextInput(''), `OUTPUT${i}_ITEM`)
        .appendField('概率%')
        .appendField(new Blockly.FieldTextInput('75'), `OUTPUT${i}_CHANCE`);
    }
    const btnRow = this.appendDummyInput();
    btnRow.appendField(new ClickableLabel(' ＋ ', () => {
      if (this.outputCount_ < 5) {
        this.outputCount_++;
        this.updateShape_();
      }
    }));
    btnRow.appendField(new ClickableLabel(' － ', () => {
      if (this.outputCount_ > 1) {
        this.outputCount_--;
        this.updateShape_();
      }
    }));
  },
  mutationToDom() {
    const m = document.createElement('mutation');
    m.setAttribute('outputs', String(this.outputCount_ || 1));
    return m;
  },
  domToMutation(xml: Element) {
    this.outputCount_ = parseInt(xml.getAttribute('outputs') || '1', 10);
    if (typeof this.updateShape_ === 'function') this.updateShape_();
  },
}

// 研磨 — 动态输出槽位
Blockly.Blocks['kjs_create_rc_milling'] = {
  init() {
    this.outputCount_ = 1;
    this.updateShape_();
    this.setPreviousStatement(true, 'kjs_stmt');
    this.setNextStatement(true, 'kjs_stmt');
    this.setColour('#E06C75');
  },
  updateShape_() {
    while (this.inputList.length > 0) this.removeInput(this.inputList[0].name);
    this.appendDummyInput().appendField('⚙️ 研磨');
    this.appendDummyInput()
      .appendField('输入')
      .appendField(new Blockly.FieldTextInput('minecraft:stone'), 'INPUT');
    for (let i = 1; i <= this.outputCount_; i++) {
      this.appendDummyInput()
        .appendField(`─ 输出${i} ─`)
        .appendField(new Blockly.FieldTextInput(''), `OUTPUT${i}_ITEM`)
        .appendField('概率%')
        .appendField(new Blockly.FieldTextInput('75'), `OUTPUT${i}_CHANCE`);
    }
    const btnRow = this.appendDummyInput();
    btnRow.appendField(new ClickableLabel(' ＋ ', () => {
      if (this.outputCount_ < 5) {
        this.outputCount_++;
        this.updateShape_();
      }
    }));
    btnRow.appendField(new ClickableLabel(' － ', () => {
      if (this.outputCount_ > 1) {
        this.outputCount_--;
        this.updateShape_();
      }
    }));
  },
  mutationToDom() {
    const m = document.createElement('mutation');
    m.setAttribute('outputs', String(this.outputCount_ || 1));
    return m;
  },
  domToMutation(xml: Element) {
    this.outputCount_ = parseInt(xml.getAttribute('outputs') || '1', 10);
    if (typeof this.updateShape_ === 'function') this.updateShape_();
  },
}

// 切割 — 动态输出槽位
Blockly.Blocks['kjs_create_rc_cutting'] = {
  init() {
    this.outputCount_ = 1;
    this.updateShape_();
    this.setPreviousStatement(true, 'kjs_stmt');
    this.setNextStatement(true, 'kjs_stmt');
    this.setColour('#E06C75');
  },
  updateShape_() {
    while (this.inputList.length > 0) this.removeInput(this.inputList[0].name);
    this.appendDummyInput().appendField('✂️ 切割');
    this.appendDummyInput()
      .appendField('输入')
      .appendField(new Blockly.FieldTextInput('minecraft:log'), 'INPUT');
    for (let i = 1; i <= this.outputCount_; i++) {
      this.appendDummyInput()
        .appendField(`─ 输出${i} ─`)
        .appendField(new Blockly.FieldTextInput(''), `OUTPUT${i}_ITEM`)
        .appendField('概率%')
        .appendField(new Blockly.FieldTextInput('75'), `OUTPUT${i}_CHANCE`);
    }
    const btnRow = this.appendDummyInput();
    btnRow.appendField(new ClickableLabel(' ＋ ', () => {
      if (this.outputCount_ < 5) {
        this.outputCount_++;
        this.updateShape_();
      }
    }));
    btnRow.appendField(new ClickableLabel(' － ', () => {
      if (this.outputCount_ > 1) {
        this.outputCount_--;
        this.updateShape_();
      }
    }));
  },
  mutationToDom() {
    const m = document.createElement('mutation');
    m.setAttribute('outputs', String(this.outputCount_ || 1));
    return m;
  },
  domToMutation(xml: Element) {
    this.outputCount_ = parseInt(xml.getAttribute('outputs') || '1', 10);
    if (typeof this.updateShape_ === 'function') this.updateShape_();
  },
}

// 混合 — 动态输入/输出槽位
Blockly.Blocks['kjs_create_rc_mixing'] = {
  init() {
    this.inputCount_ = 2;
    this.outputCount_ = 1;
    this.updateShape_();
    this.setPreviousStatement(true, 'kjs_stmt');
    this.setNextStatement(true, 'kjs_stmt');
    this.setColour('#E06C75');
  },
  updateShape_() {
    while (this.inputList.length > 0) this.removeInput(this.inputList[0].name);
    this.appendDummyInput().appendField('🧪 混合');
    // 输入槽位
    for (let i = 1; i <= this.inputCount_; i++) {
      this.appendDummyInput()
        .appendField(`输入${i}`)
        .appendField(new Blockly.FieldTextInput(''), `INPUT${i}_ITEM`);
    }
    // 输入加减按钮
    const inBtn = this.appendDummyInput();
    inBtn.appendField(new ClickableLabel('＋输入', () => {
      if (this.inputCount_ < 5) { this.inputCount_++; this.updateShape_(); }
    }));
    inBtn.appendField(new ClickableLabel('－输入', () => {
      if (this.inputCount_ > 1) { this.inputCount_--; this.updateShape_(); }
    }));
    // 输出槽位
    for (let i = 1; i <= this.outputCount_; i++) {
      this.appendDummyInput()
        .appendField(`─ 输出${i} ─`)
        .appendField(new Blockly.FieldTextInput(''), `OUTPUT${i}_ITEM`)
        .appendField('概率%')
        .appendField(new Blockly.FieldTextInput('75'), `OUTPUT${i}_CHANCE`);
    }
    // 输出加减按钮
    const outBtn = this.appendDummyInput();
    outBtn.appendField(new ClickableLabel('＋输出', () => {
      if (this.outputCount_ < 5) { this.outputCount_++; this.updateShape_(); }
    }));
    outBtn.appendField(new ClickableLabel('－输出', () => {
      if (this.outputCount_ > 1) { this.outputCount_--; this.updateShape_(); }
    }));
  },
  mutationToDom() {
    const m = document.createElement('mutation');
    m.setAttribute('inputs', String(this.inputCount_ || 1));
    m.setAttribute('outputs', String(this.outputCount_ || 1));
    return m;
  },
  domToMutation(xml: Element) {
    this.inputCount_ = parseInt(xml.getAttribute('inputs') || '1', 10);
    this.outputCount_ = parseInt(xml.getAttribute('outputs') || '1', 10);
    if (typeof this.updateShape_ === 'function') this.updateShape_();
  },
}

// 压实 — 动态输入/输出槽位
Blockly.Blocks['kjs_create_rc_compacting'] = {
  init() {
    this.inputCount_ = 2;
    this.outputCount_ = 1;
    this.updateShape_();
    this.setPreviousStatement(true, 'kjs_stmt');
    this.setNextStatement(true, 'kjs_stmt');
    this.setColour('#E06C75');
  },
  updateShape_() {
    while (this.inputList.length > 0) this.removeInput(this.inputList[0].name);
    this.appendDummyInput().appendField('📦 压实');
    // 输入槽位
    for (let i = 1; i <= this.inputCount_; i++) {
      this.appendDummyInput()
        .appendField(`输入${i}`)
        .appendField(new Blockly.FieldTextInput(''), `INPUT${i}_ITEM`);
    }
    // 输入加减按钮
    const inBtn = this.appendDummyInput();
    inBtn.appendField(new ClickableLabel('＋输入', () => {
      if (this.inputCount_ < 5) { this.inputCount_++; this.updateShape_(); }
    }));
    inBtn.appendField(new ClickableLabel('－输入', () => {
      if (this.inputCount_ > 1) { this.inputCount_--; this.updateShape_(); }
    }));
    // 输出槽位
    for (let i = 1; i <= this.outputCount_; i++) {
      this.appendDummyInput()
        .appendField(`─ 输出${i} ─`)
        .appendField(new Blockly.FieldTextInput(''), `OUTPUT${i}_ITEM`)
        .appendField('概率%')
        .appendField(new Blockly.FieldTextInput('100'), `OUTPUT${i}_CHANCE`);
    }
    // 输出加减按钮
    const outBtn = this.appendDummyInput();
    outBtn.appendField(new ClickableLabel('＋输出', () => {
      if (this.outputCount_ < 5) { this.outputCount_++; this.updateShape_(); }
    }));
    outBtn.appendField(new ClickableLabel('－输出', () => {
      if (this.outputCount_ > 1) { this.outputCount_--; this.updateShape_(); }
    }));
  },
  mutationToDom() {
    const m = document.createElement('mutation');
    m.setAttribute('inputs', String(this.inputCount_ || 1));
    m.setAttribute('outputs', String(this.outputCount_ || 1));
    return m;
  },
  domToMutation(xml: Element) {
    this.inputCount_ = parseInt(xml.getAttribute('inputs') || '1', 10);
    this.outputCount_ = parseInt(xml.getAttribute('outputs') || '1', 10);
    if (typeof this.updateShape_ === 'function') this.updateShape_();
  },
}

// 压板
Blockly.Blocks['kjs_create_rc_pressing'] = {
  init() {
    this.appendDummyInput().appendField('🔩 压板')
    this.appendDummyInput().appendField('输入').appendField(new Blockly.FieldTextInput('minecraft:iron_ingot'), 'INPUT')
    this.appendDummyInput().appendField('输出').appendField(new Blockly.FieldTextInput('minecraft:iron_block'), 'OUTPUT')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}

// 注液
Blockly.Blocks['kjs_create_rc_filling'] = {
  init() {
    this.appendDummyInput().appendField('🧴 注液')
    this.appendDummyInput().appendField('物品').appendField(new Blockly.FieldTextInput('minecraft:glass_bottle'), 'INPUT')
    this.appendDummyInput().appendField('流体').appendField(new Blockly.FieldTextInput('minecraft:water'), 'FLUID')
    this.appendDummyInput().appendField('输出').appendField(new Blockly.FieldTextInput('minecraft:potion'), 'OUTPUT')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}

// 排液
Blockly.Blocks['kjs_create_rc_emptying'] = {
  init() {
    this.appendDummyInput().appendField('🧴 排液')
    this.appendDummyInput().appendField('输入').appendField(new Blockly.FieldTextInput('minecraft:potion'), 'INPUT')
    this.appendDummyInput().appendField('输出物品').appendField(new Blockly.FieldTextInput('minecraft:glass_bottle'), 'OUTPUT')
    this.appendDummyInput().appendField('输出流体').appendField(new Blockly.FieldTextInput('minecraft:water'), 'FLUID')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}

// 洗涤 — 动态输出槽位
Blockly.Blocks['kjs_create_rc_splashing'] = {
  init() {
    this.outputCount_ = 1;
    this.updateShape_();
    this.setPreviousStatement(true, 'kjs_stmt');
    this.setNextStatement(true, 'kjs_stmt');
    this.setColour('#E06C75');
  },
  updateShape_() {
    while (this.inputList.length > 0) this.removeInput(this.inputList[0].name);
    this.appendDummyInput().appendField('🌊 洗涤');
    this.appendDummyInput()
      .appendField('输入')
      .appendField(new Blockly.FieldTextInput('minecraft:gravel'), 'INPUT');
    for (let i = 1; i <= this.outputCount_; i++) {
      this.appendDummyInput()
        .appendField(`─ 输出${i} ─`)
        .appendField(new Blockly.FieldTextInput(''), `OUTPUT${i}_ITEM`)
        .appendField('概率%')
        .appendField(new Blockly.FieldTextInput('75'), `OUTPUT${i}_CHANCE`);
    }
    const btnRow = this.appendDummyInput();
    btnRow.appendField(new ClickableLabel(' ＋ ', () => {
      if (this.outputCount_ < 5) {
        this.outputCount_++;
        this.updateShape_();
      }
    }));
    btnRow.appendField(new ClickableLabel(' － ', () => {
      if (this.outputCount_ > 1) {
        this.outputCount_--;
        this.updateShape_();
      }
    }));
  },
  mutationToDom() {
    const m = document.createElement('mutation');
    m.setAttribute('outputs', String(this.outputCount_ || 1));
    return m;
  },
  domToMutation(xml: Element) {
    this.outputCount_ = parseInt(xml.getAttribute('outputs') || '1', 10);
    if (typeof this.updateShape_ === 'function') this.updateShape_();
  },
}

// 灵涉 — 动态输出槽位
Blockly.Blocks['kjs_create_rc_haunting'] = {
  init() {
    this.outputCount_ = 1;
    this.updateShape_();
    this.setPreviousStatement(true, 'kjs_stmt');
    this.setNextStatement(true, 'kjs_stmt');
    this.setColour('#E06C75');
  },
  updateShape_() {
    while (this.inputList.length > 0) this.removeInput(this.inputList[0].name);
    this.appendDummyInput().appendField('👻 灵涉');
    this.appendDummyInput()
      .appendField('输入')
      .appendField(new Blockly.FieldTextInput('minecraft:stone'), 'INPUT');
    for (let i = 1; i <= this.outputCount_; i++) {
      this.appendDummyInput()
        .appendField(`─ 输出${i} ─`)
        .appendField(new Blockly.FieldTextInput(''), `OUTPUT${i}_ITEM`)
        .appendField('概率%')
        .appendField(new Blockly.FieldTextInput('75'), `OUTPUT${i}_CHANCE`);
    }
    const btnRow = this.appendDummyInput();
    btnRow.appendField(new ClickableLabel(' ＋ ', () => {
      if (this.outputCount_ < 5) {
        this.outputCount_++;
        this.updateShape_();
      }
    }));
    btnRow.appendField(new ClickableLabel(' － ', () => {
      if (this.outputCount_ > 1) {
        this.outputCount_--;
        this.updateShape_();
      }
    }));
  },
  mutationToDom() {
    const m = document.createElement('mutation');
    m.setAttribute('outputs', String(this.outputCount_ || 1));
    return m;
  },
  domToMutation(xml: Element) {
    this.outputCount_ = parseInt(xml.getAttribute('outputs') || '1', 10);
    if (typeof this.updateShape_ === 'function') this.updateShape_();
  },
}

// 机械手
Blockly.Blocks['kjs_create_rc_deploying'] = {
  init() {
    this.appendDummyInput().appendField('🤖 机械手')
    this.appendDummyInput().appendField('底座').appendField(new Blockly.FieldTextInput('minecraft:stone'), 'INPUT')
    this.appendDummyInput().appendField('手持').appendField(new Blockly.FieldTextInput('minecraft:redstone'), 'HAND')
    this.appendDummyInput().appendField('输出').appendField(new Blockly.FieldTextInput('minecraft:redstone_block'), 'OUTPUT')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}

// 物品应用
Blockly.Blocks['kjs_create_rc_item_app'] = {
  init() {
    this.appendDummyInput().appendField('🔧 物品应用')
    this.appendDummyInput().appendField('底座').appendField(new Blockly.FieldTextInput('minecraft:stone'), 'INPUT')
    this.appendDummyInput().appendField('手持').appendField(new Blockly.FieldTextInput('minecraft:iron_ingot'), 'HAND')
    this.appendDummyInput().appendField('输出').appendField(new Blockly.FieldTextInput('minecraft:iron_block'), 'OUTPUT')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}

// ═══════════════════════════════════════════════════════════
//  34. JS 逻辑控制积木（补充）
// ═══════════════════════════════════════════════════════════

// while 循环
Blockly.Blocks['kjs_while'] = {
  init() {
    this.appendValueInput('COND').setCheck('Boolean').appendField('当')
    this.appendStatementInput('DO').setCheck('kjs_stmt').appendField('时 执行')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}

// do...while 循环
Blockly.Blocks['kjs_do_while'] = {
  init() {
    this.appendStatementInput('DO').setCheck('kjs_stmt').appendField('执行')
    this.appendValueInput('COND').setCheck('Boolean').appendField('当').appendField('时')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}

// for 循环（索引）
Blockly.Blocks['kjs_for'] = {
  init() {
    this.appendValueInput('FROM').setCheck('Number').appendField('从')
    this.appendDummyInput().appendField('到').appendField(new Blockly.FieldTextInput('10'), 'TO_NUM')
    this.appendDummyInput().appendField('步进').appendField(new Blockly.FieldTextInput('1'), 'STEP_NUM')
    this.appendStatementInput('DO').setCheck('kjs_stmt').appendField('执行')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}

// switch/case
Blockly.Blocks['kjs_switch'] = {
  init() {
    this.appendValueInput('VALUE').appendField('判断')
    this.appendStatementInput('CASES').setCheck('kjs_stmt').appendField('分支')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}

// case 分支
Blockly.Blocks['kjs_case'] = {
  init() {
    this.appendValueInput('VALUE').appendField('当值')
    this.appendStatementInput('DO').setCheck('kjs_stmt').appendField('执行')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}

// default 分支
Blockly.Blocks['kjs_default'] = {
  init() {
    this.appendStatementInput('DO').setCheck('kjs_stmt').appendField('默认 执行')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}

// try/catch
Blockly.Blocks['kjs_try'] = {
  init() {
    this.appendStatementInput('TRY').setCheck('kjs_stmt').appendField('尝试')
    this.appendStatementInput('CATCH').setCheck('kjs_stmt').appendField('捕获(变量 e)')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}

// break
Blockly.Blocks['kjs_break'] = {
  init() {
    this.appendDummyInput().appendField('跳出循环')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}

// continue
Blockly.Blocks['kjs_continue'] = {
  init() {
    this.appendDummyInput().appendField('继续下一次')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#98C379');
  },
}

// throw
Blockly.Blocks['kjs_throw'] = {
  init() {
    this.appendValueInput('ERR').appendField('抛出')
    this.setPreviousStatement(true, 'kjs_stmt')
    this.setNextStatement(true, 'kjs_stmt')
    this.setColour('#E06C75');
  },
}
