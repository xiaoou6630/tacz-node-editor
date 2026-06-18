import * as Blockly from 'blockly'

export const taczTheme = Blockly.Theme.defineTheme('tacz-kitten', {
  name: 'tacz-kitten',
  base: Blockly.Themes.Classic,
  blockStyles: {
    state_blocks: { colourPrimary: '#FF69B4', colourSecondary: '#FF8EC4', colourTertiary: '#FFB0D8' },
    event_blocks: { colourPrimary: '#87CEEB', colourSecondary: '#A8DAF0', colourTertiary: '#C8E8F5' },
    anim_blocks: { colourPrimary: '#32CD32', colourSecondary: '#5ED85E', colourTertiary: '#8AE48A' },
    check_blocks: { colourPrimary: '#BA55D3', colourSecondary: '#CC77E0', colourTertiary: '#DD99EB' },
    action_blocks: { colourPrimary: '#FF8C00', colourSecondary: '#FFA333', colourTertiary: '#FFBA66' },
    track_blocks: { colourPrimary: '#4A90E2', colourSecondary: '#6BA8E8', colourTertiary: '#8DBFEF' },
    logic_blocks: { colourPrimary: '#FFB347', colourSecondary: '#FFC570', colourTertiary: '#FFD699' },
    mode_blocks: { colourPrimary: '#98FB98', colourSecondary: '#B0FCB0', colourTertiary: '#C8FDC8' },
    math_blocks: { colourPrimary: '#DDA0DD', colourSecondary: '#E6B8E6', colourTertiary: '#EED0EE' },
  },
  componentStyles: {
    workspaceBackgroundColour: '#1E1E2E',
    toolboxBackgroundColour: '#2D2D3F',
    toolboxForegroundColour: '#CDD6F4',
    flyoutBackgroundColour: '#363649',
    flyoutForegroundColour: '#CDD6F4',
    flyoutOpacity: 0.95,
    scrollbarColour: '#45475A',
    scrollbarOpacity: 0.6,
    insertionMarkerColour: '#4D96FF',
    insertionMarkerOpacity: 0.4,
  },
  fontStyle: {
    family: "'PingFang SC', 'Noto Sans SC', sans-serif",
    weight: '600',
    size: 12,
  },
  startHats: true,
})
