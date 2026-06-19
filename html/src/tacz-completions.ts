/**
 * TACZ Lua API 自动补全数据
 * 基于 k:\github\TACZ 源码提取
 */

export interface CompletionItem {
  label: string
  type: 'function' | 'constant' | 'keyword' | 'snippet'
  detail: string
  insertText?: string
}

// context 对象方法
export const contextMethods: CompletionItem[] = [
  // ─── 轨道与动画控制 (AnimationStateContext) ───
  { label: 'context:addTrackLine', type: 'function', detail: '() → int  分配新轨道行，返回下标', insertText: 'context:addTrackLine()' },
  { label: 'context:ensureTrackLineSize', type: 'function', detail: '(size: int)  确保轨道行数量', insertText: 'context:ensureTrackLineSize(${1:size})' },
  { label: 'context:getTrackLineSize', type: 'function', detail: '() → int  获取轨道行数量', insertText: 'context:getTrackLineSize()' },
  { label: 'context:assignNewTrack', type: 'function', detail: '(index: int) → int  为轨道行分配新轨道', insertText: 'context:assignNewTrack(${1:index})' },
  { label: 'context:findIdleTrack', type: 'function', detail: '(index: int, interruptHolding: boolean) → int  找空闲轨道', insertText: 'context:findIdleTrack(${1:index}, ${2:true})' },
  { label: 'context:ensureTracksAmount', type: 'function', detail: '(index: int, amount: int)  保证轨道数量', insertText: 'context:ensureTracksAmount(${1:index}, ${2:amount})' },
  { label: 'context:getTrack', type: 'function', detail: '(trackLineIndex: int, trackIndex: int) → int  获取轨道指针', insertText: 'context:getTrack(${1:trackLineIndex}, ${2:trackIndex})' },
  { label: 'context:getAsSingletonTrack', type: 'function', detail: '(index: int) → int  获取单例轨道', insertText: 'context:getAsSingletonTrack(${1:index})' },
  { label: 'context:runAnimation', type: 'function', detail: '(name: string, track: int, blending: boolean, playType: int, transitionTime: float)  播放动画', insertText: 'context:runAnimation("${1:anim}", ${2:track}, ${3:false}, ${4:PLAY_ONCE_STOP}, ${5:0.2})' },
  { label: 'context:stopAnimation', type: 'function', detail: '(track: int)  停止动画', insertText: 'context:stopAnimation(${1:track})' },
  { label: 'context:holdAnimation', type: 'function', detail: '(track: int)  挂起动画（定格最后一帧）', insertText: 'context:holdAnimation(${1:track})' },
  { label: 'context:pauseAnimation', type: 'function', detail: '(track: int)  暂停动画', insertText: 'context:pauseAnimation(${1:track})' },
  { label: 'context:resumeAnimation', type: 'function', detail: '(track: int)  恢复动画', insertText: 'context:resumeAnimation(${1:track})' },
  { label: 'context:setAnimationProgress', type: 'function', detail: '(track: int, progress: float, normalization: boolean)  设置动画进度', insertText: 'context:setAnimationProgress(${1:track}, ${2:0.5}, ${3:false})' },
  { label: 'context:adjustAnimationProgress', type: 'function', detail: '(track: int, progress: float, normalization: boolean)  调整动画进度', insertText: 'context:adjustAnimationProgress(${1:track}, ${2:0.1}, ${3:false})' },
  { label: 'context:isHolding', type: 'function', detail: '(track: int) → boolean  轨道是否挂起', insertText: 'context:isHolding(${1:track})' },
  { label: 'context:isStopped', type: 'function', detail: '(track: int) → boolean  轨道是否停止', insertText: 'context:isStopped(${1:track})' },
  { label: 'context:isPause', type: 'function', detail: '(track: int) → boolean  轨道是否暂停', insertText: 'context:isPause(${1:track})' },
  { label: 'context:hasAnimationPrototype', type: 'function', detail: '(name: string) → boolean  动画是否存在', insertText: 'context:hasAnimationPrototype("${1:anim}")' },
  { label: 'context:trigger', type: 'function', detail: '(input: string)  手动触发状态转移', insertText: 'context:trigger(${1:INPUT_RELOAD})' },
  { label: 'context:shouldHideCrossHair', type: 'function', detail: '() → boolean  是否隐藏准心', insertText: 'context:shouldHideCrossHair()' },
  { label: 'context:setShouldHideCrossHair', type: 'function', detail: '(shouldHide: boolean)  设置隐藏准心', insertText: 'context:setShouldHideCrossHair(${1:true})' },
  // ─── 物品动画 (ItemAnimationStateContext) ───
  { label: 'context:getPutAwayTime', type: 'function', detail: '() → float  收起物品动画时长', insertText: 'context:getPutAwayTime()' },
  { label: 'context:getPartialTicks', type: 'function', detail: '() → float  最后更新的 partialTicks', insertText: 'context:getPartialTicks()' },
  // ─── 枪械专用 (GunAnimationStateContext) ───
  { label: 'context:hasBulletInBarrel', type: 'function', detail: '() → boolean  枪膛中是否有子弹', insertText: 'context:hasBulletInBarrel()' },
  { label: 'context:isOverHeat', type: 'function', detail: '() → boolean  是否过热', insertText: 'context:isOverHeat()' },
  { label: 'context:getHeatProgress', type: 'function', detail: '() → float  过热进度 0~1', insertText: 'context:getHeatProgress()' },
  { label: 'context:getShootInterval', type: 'function', detail: '() → long  射击间隔(ms)', insertText: 'context:getShootInterval()' },
  { label: 'context:getLastShootTimestamp', type: 'function', detail: '() → long  上次射击时间戳(ms)', insertText: 'context:getLastShootTimestamp()' },
  { label: 'context:getCurrentTimestamp', type: 'function', detail: '() → long  当前时间(ms)', insertText: 'context:getCurrentTimestamp()' },
  { label: 'context:adjustClientShootInterval', type: 'function', detail: '(alpha: long)  调整射击间隔(ms)', insertText: 'context:adjustClientShootInterval(${1:0})' },
  { label: 'context:getAmmoCount', type: 'function', detail: '() → int  弹匣备弹数', insertText: 'context:getAmmoCount()' },
  { label: 'context:getMaxAmmoCount', type: 'function', detail: '() → int  弹匣最大备弹数', insertText: 'context:getMaxAmmoCount()' },
  { label: 'context:hasAmmoToConsume', type: 'function', detail: '() → boolean  是否有弹药可消耗', insertText: 'context:hasAmmoToConsume()' },
  { label: 'context:getMagExtentLevel', type: 'function', detail: '() → int  扩容等级 0~3', insertText: 'context:getMagExtentLevel()' },
  { label: 'context:getFireMode', type: 'function', detail: '() → int  开火模式(FireMode ordinal)', insertText: 'context:getFireMode()' },
  { label: 'context:getAimingProgress', type: 'function', detail: '() → float  瞄准进度 0~1', insertText: 'context:getAimingProgress()' },
  { label: 'context:isAiming', type: 'function', detail: '() → boolean  是否正在瞄准', insertText: 'context:isAiming()' },
  { label: 'context:getShootCoolDown', type: 'function', detail: '() → long  射击冷却(ms)', insertText: 'context:getShootCoolDown()' },
  { label: 'context:getReloadStateType', type: 'function', detail: '() → int  换弹状态(ReloadState ordinal)', insertText: 'context:getReloadStateType()' },
  { label: 'context:isInputUp', type: 'function', detail: '() → boolean  按键W', insertText: 'context:isInputUp()' },
  { label: 'context:isInputDown', type: 'function', detail: '() → boolean  按键S', insertText: 'context:isInputDown()' },
  { label: 'context:isInputLeft', type: 'function', detail: '() → boolean  按键A', insertText: 'context:isInputLeft()' },
  { label: 'context:isInputRight', type: 'function', detail: '() → boolean  按键D', insertText: 'context:isInputRight()' },
  { label: 'context:isInputJumping', type: 'function', detail: '() → boolean  按键Space', insertText: 'context:isInputJumping()' },
  { label: 'context:isCrawl', type: 'function', detail: '() → boolean  是否匍匐', insertText: 'context:isCrawl()' },
  { label: 'context:isOnGround', type: 'function', detail: '() → boolean  是否接触地面', insertText: 'context:isOnGround()' },
  { label: 'context:isCrouching', type: 'function', detail: '() → boolean  是否蹲伏', insertText: 'context:isCrouching()' },
  { label: 'context:shouldSlide', type: 'function', detail: '() → boolean  是否斜握', insertText: 'context:shouldSlide()' },
  { label: 'context:anchorWalkDist', type: 'function', detail: '()  在当前行走距离打锚点', insertText: 'context:anchorWalkDist()' },
  { label: 'context:getWalkDist', type: 'function', detail: '() → float  与锚点相对的行走距离', insertText: 'context:getWalkDist()' },
  { label: 'context:popShellFrom', type: 'function', detail: '(index: int)  从指定抛壳窗弹出弹壳', insertText: 'context:popShellFrom(${1:1})' },
  { label: 'context:getStateMachineParams', type: 'function', detail: '() → LuaTable  获取状态机参数表', insertText: 'context:getStateMachineParams()' },
  { label: 'context:getNbtAccessor', type: 'function', detail: '() → LuaNbtAccessor  获取NBT访问器', insertText: 'context:getNbtAccessor()' },
  { label: 'context:getAttachment', type: 'function', detail: '(type: string) → string  获取配件ID', insertText: 'context:getAttachment("${1:stock}")' },
]

// NBT 访问器方法
export const nbtMethods: CompletionItem[] = [
  { label: 'nbt:contains', type: 'function', detail: '(key: string) → boolean', insertText: 'nbt:contains("${1:key}")' },
  { label: 'nbt:getInt', type: 'function', detail: '(key: string) → int', insertText: 'nbt:getInt("${1:key}")' },
  { label: 'nbt:getDouble', type: 'function', detail: '(key: string) → double', insertText: 'nbt:getDouble("${1:key}")' },
  { label: 'nbt:getFloat', type: 'function', detail: '(key: string) → float', insertText: 'nbt:getFloat("${1:key}")' },
  { label: 'nbt:getLong', type: 'function', detail: '(key: string) → long', insertText: 'nbt:getLong("${1:key}")' },
  { label: 'nbt:getString', type: 'function', detail: '(key: string) → string', insertText: 'nbt:getString("${1:key}")' },
  { label: 'nbt:getBoolean', type: 'function', detail: '(key: string) → boolean', insertText: 'nbt:getBoolean("${1:key}")' },
  { label: 'nbt:getCompound', type: 'function', detail: '(key: string) → LuaNbtAccessor', insertText: 'nbt:getCompound("${1:key}")' },
  { label: 'nbt:putInt', type: 'function', detail: '(key: string, value: int)', insertText: 'nbt:putInt("${1:key}", ${2:0})' },
  { label: 'nbt:putDouble', type: 'function', detail: '(key: string, value: double)', insertText: 'nbt:putDouble("${1:key}", ${2:0.0})' },
  { label: 'nbt:putFloat', type: 'function', detail: '(key: string, value: float)', insertText: 'nbt:putFloat("${1:key}", ${2:0.0})' },
  { label: 'nbt:putLong', type: 'function', detail: '(key: string, value: long)', insertText: 'nbt:putLong("${1:key}", ${2:0})' },
  { label: 'nbt:putString', type: 'function', detail: '(key: string, value: string)', insertText: 'nbt:putString("${1:key}", "${2:value}")' },
  { label: 'nbt:putBoolean', type: 'function', detail: '(key: string, value: boolean)', insertText: 'nbt:putBoolean("${1:key}", ${2:true})' },
  { label: 'nbt:putCompound', type: 'function', detail: '(key: string, value: LuaNbtAccessor)', insertText: 'nbt:putCompound("${1:key}", ${2:compound})' },
  { label: 'nbt:newCompoundTag', type: 'function', detail: '() → LuaNbtAccessor  创建新CompoundTag', insertText: 'nbt:newCompoundTag()' },
]

// 常量
export const taczConstants: CompletionItem[] = [
  // 输入常量
  { label: 'INPUT_DRAW', type: 'constant', detail: '"draw"  掏枪', insertText: 'INPUT_DRAW' },
  { label: 'INPUT_SHOOT', type: 'constant', detail: '"shoot"  射击', insertText: 'INPUT_SHOOT' },
  { label: 'INPUT_RELOAD', type: 'constant', detail: '"reload"  换弹', insertText: 'INPUT_RELOAD' },
  { label: 'INPUT_CANCEL_RELOAD', type: 'constant', detail: '"cancel_reload"  取消换弹', insertText: 'INPUT_CANCEL_RELOAD' },
  { label: 'INPUT_INSPECT', type: 'constant', detail: '"inspect"  检视', insertText: 'INPUT_INSPECT' },
  { label: 'INPUT_BOLT', type: 'constant', detail: '"blot"  拉栓', insertText: 'INPUT_BOLT' },
  { label: 'INPUT_PUT_AWAY', type: 'constant', detail: '"put_away"  收枪', insertText: 'INPUT_PUT_AWAY' },
  { label: 'INPUT_WALK', type: 'constant', detail: '"walk"  行走', insertText: 'INPUT_WALK' },
  { label: 'INPUT_RUN', type: 'constant', detail: '"run"  奔跑', insertText: 'INPUT_RUN' },
  { label: 'INPUT_IDLE', type: 'constant', detail: '"idle"  闲置', insertText: 'INPUT_IDLE' },
  { label: 'INPUT_FIRE_SELECT', type: 'constant', detail: '"fire_select"  开火模式切换', insertText: 'INPUT_FIRE_SELECT' },
  { label: 'INPUT_BAYONET_MUZZLE', type: 'constant', detail: '"bayonet_muzzle"  刺刀近战', insertText: 'INPUT_BAYONET_MUZZLE' },
  { label: 'INPUT_BAYONET_STOCK', type: 'constant', detail: '"bayonet_stock"  枪托近战', insertText: 'INPUT_BAYONET_STOCK' },
  { label: 'INPUT_BAYONET_PUSH', type: 'constant', detail: '"bayonet_push"  推击近战', insertText: 'INPUT_BAYONET_PUSH' },
  { label: 'INPUT_BOLT_CAUGHT', type: 'constant', detail: '"bolt_caught"  空挂输入', insertText: 'INPUT_BOLT_CAUGHT' },
  { label: 'INPUT_BOLT_NORMAL', type: 'constant', detail: '"bolt_normal"  不空挂输入', insertText: 'INPUT_BOLT_NORMAL' },
  { label: 'INPUT_OVER_HEAT', type: 'constant', detail: '"over_heat"  过热输入', insertText: 'INPUT_OVER_HEAT' },
  { label: 'INPUT_COOLING_HEAT', type: 'constant', detail: '"cooling_heat"  冷却输入', insertText: 'INPUT_COOLING_HEAT' },
  { label: 'INPUT_INSPECT_RETREAT', type: 'constant', detail: '"inspect_retreat"  退出检视', insertText: 'INPUT_INSPECT_RETREAT' },
  { label: 'INPUT_AIM', type: 'constant', detail: '"aim"  瞄准', insertText: 'INPUT_AIM' },
  { label: 'INPUT_AIM_RETREAT', type: 'constant', detail: '"aim_retreat"  取消瞄准', insertText: 'INPUT_AIM_RETREAT' },
  { label: 'INPUT_SPRINT', type: 'constant', detail: '"sprint"  冲刺', insertText: 'INPUT_SPRINT' },
  { label: 'INPUT_SLIDE', type: 'constant', detail: '"slide"  下蹲', insertText: 'INPUT_SLIDE' },
  // 播放类型
  { label: 'PLAY_ONCE_HOLD', type: 'constant', detail: '0  播放一次保持', insertText: 'PLAY_ONCE_HOLD' },
  { label: 'PLAY_ONCE_STOP', type: 'constant', detail: '1  播放一次停止', insertText: 'PLAY_ONCE_STOP' },
  { label: 'LOOP', type: 'constant', detail: '2  循环播放', insertText: 'LOOP' },
  // 轨道行
  { label: 'STATIC_TRACK_LINE', type: 'constant', detail: '0  主轨道行', insertText: 'STATIC_TRACK_LINE' },
  { label: 'GUN_KICK_TRACK_LINE', type: 'constant', detail: '1  开火轨道行', insertText: 'GUN_KICK_TRACK_LINE' },
  { label: 'BLENDING_TRACK_LINE', type: 'constant', detail: '2  混合轨道行', insertText: 'BLENDING_TRACK_LINE' },
  // 轨道
  { label: 'BASE_TRACK', type: 'constant', detail: '0  基础轨道', insertText: 'BASE_TRACK' },
  { label: 'BOLT_CAUGHT_TRACK', type: 'constant', detail: '1  空挂轨道', insertText: 'BOLT_CAUGHT_TRACK' },
  { label: 'ADS_TRACK', type: 'constant', detail: '3  瞄准轨道', insertText: 'ADS_TRACK' },
  { label: 'MAIN_TRACK', type: 'constant', detail: '4  主轨道', insertText: 'MAIN_TRACK' },
  { label: 'SPRINT_TRACK', type: 'constant', detail: '5  冲刺轨道', insertText: 'SPRINT_TRACK' },
  { label: 'MOVEMENT_TRACK', type: 'constant', detail: '0  移动轨道(混合行)', insertText: 'MOVEMENT_TRACK' },
  { label: 'SLIDE_TRACK', type: 'constant', detail: '1  斜握轨道(混合行)', insertText: 'SLIDE_TRACK' },
  { label: 'OVER_HEAT_TRACK', type: 'constant', detail: '2  过热触发轨道(混合行)', insertText: 'OVER_HEAT_TRACK' },
  { label: 'OVER_HEATING_TRACK', type: 'constant', detail: '3  持续过热轨道(混合行)', insertText: 'OVER_HEATING_TRACK' },
  // 换弹状态
  { label: 'NOT_RELOADING', type: 'constant', detail: '0  未换弹', insertText: 'NOT_RELOADING' },
  { label: 'EMPTY_RELOAD_FEEDING', type: 'constant', detail: '1  空仓换弹-填装', insertText: 'EMPTY_RELOAD_FEEDING' },
  { label: 'EMPTY_RELOAD_FINISHING', type: 'constant', detail: '2  空仓换弹-收尾', insertText: 'EMPTY_RELOAD_FINISHING' },
  { label: 'TACTICAL_RELOAD_FEEDING', type: 'constant', detail: '3  战术换弹-填装', insertText: 'TACTICAL_RELOAD_FEEDING' },
  { label: 'TACTICAL_RELOAD_FINISHING', type: 'constant', detail: '4  战术换弹-收尾', insertText: 'TACTICAL_RELOAD_FINISHING' },
  // 开火模式
  { label: 'AUTO', type: 'constant', detail: '0  全自动', insertText: 'AUTO' },
  { label: 'SEMI', type: 'constant', detail: '1  半自动', insertText: 'SEMI' },
  { label: 'BURST', type: 'constant', detail: '2  多连发', insertText: 'BURST' },
]

// Lua 关键字和基础函数
export const luaKeywords: CompletionItem[] = [
  { label: 'function', type: 'keyword', detail: '定义函数', insertText: 'function ${1:name}(${2:args})\n  ${3:-- body}\nend' },
  { label: 'if', type: 'keyword', detail: '条件判断', insertText: 'if ${1:condition} then\n  ${2:-- body}\nend' },
  { label: 'if-else', type: 'keyword', detail: '条件判断(含else)', insertText: 'if ${1:condition} then\n  ${2:-- body}\nelse\n  ${3:-- else body}\nend' },
  { label: 'for', type: 'keyword', detail: '数值循环', insertText: 'for ${1:i} = ${2:1}, ${3:10} do\n  ${4:-- body}\nend' },
  { label: 'for-in', type: 'keyword', detail: '迭代循环', insertText: 'for ${1:k}, ${2:v} in ${3:pairs(t)} do\n  ${4:-- body}\nend' },
  { label: 'while', type: 'keyword', detail: 'while循环', insertText: 'while ${1:condition} do\n  ${2:-- body}\nend' },
  { label: 'return', type: 'keyword', detail: '返回', insertText: 'return ${1:value}' },
  { label: 'local', type: 'keyword', detail: '局部变量', insertText: 'local ${1:name} = ${2:value}' },
  { label: 'true', type: 'keyword', detail: '布尔真', insertText: 'true' },
  { label: 'false', type: 'keyword', detail: '布尔假', insertText: 'false' },
  { label: 'nil', type: 'keyword', detail: '空值', insertText: 'nil' },
  { label: 'and', type: 'keyword', detail: '逻辑与', insertText: 'and' },
  { label: 'or', type: 'keyword', detail: '逻辑或', insertText: 'or' },
  { label: 'not', type: 'keyword', detail: '逻辑非', insertText: 'not' },
  { label: 'then', type: 'keyword', detail: 'then', insertText: 'then' },
  { label: 'end', type: 'keyword', detail: 'end', insertText: 'end' },
  { label: 'else', type: 'keyword', detail: 'else', insertText: 'else' },
  { label: 'elseif', type: 'keyword', detail: 'elseif', insertText: 'elseif ${1:condition} then' },
  { label: 'repeat', type: 'keyword', detail: 'repeat循环', insertText: 'repeat\n  ${1:-- body}\nuntil ${2:condition}' },
  { label: 'pairs', type: 'function', detail: '(t) 遍历table', insertText: 'pairs(${1:t})' },
  { label: 'ipairs', type: 'function', detail: '(t) 遍历数组', insertText: 'ipairs(${1:t})' },
  { label: 'tostring', type: 'function', detail: '(v) 转字符串', insertText: 'tostring(${1:v})' },
  { label: 'tonumber', type: 'function', detail: '(v) 转数字', insertText: 'tonumber(${1:v})' },
  { label: 'type', type: 'function', detail: '(v) 获取类型', insertText: 'type(${1:v})' },
  { label: 'math.floor', type: 'function', detail: '(n) 向下取整', insertText: 'math.floor(${1:n})' },
  { label: 'math.ceil', type: 'function', detail: '(n) 向上取整', insertText: 'math.ceil(${1:n})' },
  { label: 'math.abs', type: 'function', detail: '(n) 绝对值', insertText: 'math.abs(${1:n})' },
  { label: 'math.min', type: 'function', detail: '(a, b) 最小值', insertText: 'math.min(${1:a}, ${2:b})' },
  { label: 'math.max', type: 'function', detail: '(a, b) 最大值', insertText: 'math.max(${1:a}, ${2:b})' },
  { label: 'math.random', type: 'function', detail: '([a, b]) 随机数', insertText: 'math.random(${1:1}, ${2:10})' },
]

// 状态机模板片段
export const stateSnippets: CompletionItem[] = [
  { label: 'state-entry', type: 'snippet', detail: '状态 entry 函数', insertText: 'entry = function(this, context)\n  ${1:-- body}\nend,' },
  { label: 'state-update', type: 'snippet', detail: '状态 update 函数', insertText: 'update = function(this, context)\n  ${1:-- body}\nend,' },
  { label: 'state-exit', type: 'snippet', detail: '状态 exit 函数', insertText: 'exit = function(this, context)\n  ${1:-- body}\nend,' },
  { label: 'state-transition', type: 'snippet', detail: '状态 transition 函数', insertText: 'transition = function(this, context, input)\n  if input == ${1:INPUT_IDLE} then\n    return ${2:state}\n  end\n  return nil\nend,' },
  { label: 'state-template', type: 'snippet', detail: '完整状态模板', insertText: '{\n  entry = function(this, context)\n  end,\n  update = function(this, context)\n  end,\n  exit = function(this, context)\n  end,\n  transition = function(this, context, input)\n    return nil\n  end,\n}' },
  { label: 'initialize', type: 'snippet', detail: '初始化函数', insertText: 'function M:initialize(context)\n  ${1:-- 分配轨道行和轨道}\nend' },
  { label: 'states', type: 'snippet', detail: 'states 返回函数', insertText: 'function M:states()\n  return {\n    ${1:-- 状态列表}\n  }\nend' },
]

// 合并所有补全项
export const allCompletions: CompletionItem[] = [
  ...contextMethods,
  ...nbtMethods,
  ...taczConstants,
  ...luaKeywords,
  ...stateSnippets,
]
