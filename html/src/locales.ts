import { ref } from 'vue'

export const i18n = ref({ lang: 'zh' })

export function t(key: string): string {
  const dict = i18n.value.lang === 'zh' ? zh : en
  return (dict as any)[key] || key
}

export function _b(zhText: string, enText: string): string {
  return i18n.value.lang === 'en' ? enText : zhText
}

export function setLang(lang: string) {
  i18n.value.lang = lang
  localStorage.setItem('bt_lang', lang)
  window.location.reload()
}

// 初始化语言
const saved = localStorage.getItem('bt_lang')
if (saved === 'en' || saved === 'zh') i18n.value.lang = saved

const zh: Record<string, string> = {
  appName: 'NodeForge — TACZ 状态机编辑器',
  projectName: '项目名称',
  luaCode: '生成的 Lua 代码',
  copy: '复制',
  download: '下载',
  ok: '确定',
  file: '文件',
  newProject: '新建项目',
  exportLua: '导出 Lua 文件',
  settings: '设置',
  language: '语言',
  help: '帮助手册',
  about: '关于',
  aboutDesc: '专为 TACZ (Timeless and Classics Zero) 设计的积木编程编辑器',
  aboutStack: '基于 Blockly · Vue 3 · CodeMirror 6 构建',
  aboutAuthor: '作者: xiaoou6630',
  aboutFile: '项目文件后缀: .taczp (TACZ Project)',
}

const en: Record<string, string> = {
  appName: 'NodeForge — TACZ State Machine Editor',
  projectName: 'Project Name',
  luaCode: 'Generated Lua Code',
  copy: 'Copy',
  download: 'Download',
  ok: 'OK',
  file: 'File',
  newProject: 'New Project',
  exportLua: 'Export Lua File',
  settings: 'Settings',
  language: 'Language',
  help: 'Help Manual',
  about: 'About',
  aboutDesc: 'Block programming editor for TACZ (Timeless and Classics Zero)',
  aboutStack: 'Built with Blockly · Vue 3 · CodeMirror 6',
  aboutAuthor: 'Author: xiaoou6630',
  aboutFile: 'Project file extension: .taczp (TACZ Project)',
}
