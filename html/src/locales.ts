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
  appName: 'TACZ Lua 编辑器',
  projectName: '项目名称',
  luaCode: '生成的 Lua 代码',
  copy: '复制',
  download: '下载',
  ok: '确定',
  file: '文件',
  newProject: '新建项目',
  exportLua: '导出 Lua 文件',
  exportProject: '导出项目 (.tlbw)',
  importProject: '导入项目 (.tlbw)',
  settings: '设置',
  language: '语言',
  help: '帮助手册',
  about: '关于',
  aboutDesc: '专为 TACZ (Timeless and Classics Zero) 设计的积木编程编辑器',
  aboutStack: '基于 Blockly · Vue 3 · CodeMirror 6 构建',
  aboutAuthor: '作者: xiaoou6630',
  aboutGitHub: 'GitHub: xiaoou6630/tacz-node-editor',
  aboutFile: '项目文件后缀: .tlbw (TACZ Blockly Workspace)',
  envCheck: '环境检测',
  envTitle: '环境检测',
  envDesc: '检测您的浏览器是否支持编辑器的全部功能',
  envSupport: '支持',
  envPartial: '部分支持',
  envNot: '不支持',
  envStorage: '本地存储',
  envIndexedDB: '索引数据库',
  envFileAPI: '文件读写 API',
  envClipboard: '剪贴板 API',
  envWorker: 'Web Worker',
  envHTTP: 'HTTP 请求',
  envWebSocket: 'WebSocket',
  envScreen: '屏幕分辨率',
  envTouch: '触摸支持',
  envSW: 'Service Worker',
  envDOMParser: 'XML 解析',
  confirmNew: '确定要新建吗？未保存的项目将丢失。',
  importFailed: '导入失败，文件格式不正确。',
}

const en: Record<string, string> = {
  appName: 'TACZ Lua Editor',
  projectName: 'Project Name',
  luaCode: 'Generated Lua Code',
  copy: 'Copy',
  download: 'Download',
  ok: 'OK',
  file: 'File',
  newProject: 'New Project',
  exportLua: 'Export Lua File',
  exportProject: 'Export Project (.tlbw)',
  importProject: 'Import Project (.tlbw)',
  settings: 'Settings',
  language: 'Language',
  help: 'Help Manual',
  about: 'About',
  aboutDesc: 'Block programming editor for TACZ (Timeless and Classics Zero)',
  aboutStack: 'Built with Blockly · Vue 3 · CodeMirror 6',
  aboutAuthor: 'Author: xiaoou6630',
  aboutGitHub: 'GitHub: xiaoou6630/tacz-node-editor',
  aboutFile: 'Project file extension: .tlbw (TACZ Blockly Workspace)',
  envCheck: 'Environment Check',
  envTitle: 'Environment Check',
  envDesc: 'Check if your browser supports all editor features',
  envSupport: 'Supported',
  envPartial: 'Partial',
  envNot: 'Not Supported',
  envStorage: 'Local Storage',
  envIndexedDB: 'IndexedDB',
  envFileAPI: 'File API',
  envClipboard: 'Clipboard API',
  envWorker: 'Web Worker',
  envHTTP: 'HTTP (fetch/XHR)',
  envWebSocket: 'WebSocket',
  envScreen: 'Screen Resolution',
  envTouch: 'Touch Support',
  envSW: 'Service Worker (Offline)',
  envDOMParser: 'XML Parsing',
  confirmNew: 'Create new project? Unsaved changes will be lost.',
  importFailed: 'Import failed. Invalid file format.',
}
