/**
 * 编辑器模式状态管理
 * - tacz: TACZ Lua 状态机编辑模式（默认）
 * - kjs:  TaCZJS / KubeJS JavaScript 编辑模式
 */

import { ref } from 'vue'

export type EditorMode = 'tacz' | 'kjs'
export type KJSTab = 'server' | 'client' | 'startup'

/** 当前编辑器模式 */
export const currentMode = ref<EditorMode>('tacz')

/** KJS 模式下当前激活的标签 */
export const activeKJSTab = ref<KJSTab>('server')

/** 每个 KJS 标签独立的工作区 XML 存储 */
export const kjsWorkspaceXMLs = ref<Record<KJSTab, string>>({
  server: '',
  client: '',
  startup: '',
})

/** 切换到 KJS 模式 */
export function switchToKJSMode() {
  currentMode.value = 'kjs'
  activeKJSTab.value = 'server'
}

/** 切换回 TACZ 模式 */
export function switchToTACZMode() {
  currentMode.value = 'tacz'
}
