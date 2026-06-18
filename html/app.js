/**
 * NodeForge - TACZ Lua State Machine Node Editor
 * Main application logic for the web-based node editor.
 *
 * Handles all interactive operations:
 *   - Node rendering, dragging, selection, deletion
 *   - Connection drawing with bezier curves
 *   - Toolbox drag-and-drop node creation
 *   - Zoom and pan
 *   - Node configuration modal
 *   - Right-click context menu
 *   - Code generation / copy / download
 */

(function () {
  'use strict';

  // ============================================================
  //  Constants & State
  // ============================================================

  const SVG_NS = 'http://www.w3.org/2000/svg';
  const NODE_W = 160;
  const NODE_H = 60;
  const HEADER_H = 28;
  const PORT_R = 5;

  let nodeIdCounter = 0;
  const nodes = new Map();         // id -> node object
  const connections = [];          // { id, fromNodeId, fromPortName, toNodeId, toPortName }
  let selectedNodeId = null;
  let connectState = null;         // { fromNodeId, fromPortName } while dragging
  let dragNodeId = null;
  let clipboardNode = null;        // for copy/paste
  let editingNode = null;
  let contextMenuNodeId = null;

  // Zoom & Pan state
  let viewTransform = { x: 0, y: 0, scale: 1 };
  let isPanning = false;
  let panStart = { x: 0, y: 0 };

  // ============================================================
  //  DOM References
  // ============================================================

  const $ = (id) => document.getElementById(id);
  const canvasSvg = $('canvasSvg');
  const nodesLayer = $('nodesLayer');
  const connectionsLayer = $('connectionsLayer');
  const dragLine = $('dragLine');
  const codeOutput = $('codeOutput');
  const nodeModal = $('nodeModal');
  const modalTitle = $('modalTitle');
  const modalBody = $('modalBody');
  const modalCloseBtn = $('modalCloseBtn');
  const modalCancelBtn = $('modalCancelBtn');
  const modalConfirmBtn = $('modalConfirmBtn');
  const contextMenu = $('contextMenu');
  const toolboxScroll = $('toolboxScroll');
  const projectNameInput = $('projectName');
  const canvasContainer = $('canvasContainer');
  const zoomInfo = document.querySelector('.canvas-zoom-info');

  // ============================================================
  //  Grid Background Pattern
  // ============================================================

  function addGridPattern() {
    const defs = canvasSvg.querySelector('defs');
    if (!defs) return;

    // Check if pattern already exists
    if (defs.querySelector('#gridPattern')) return;

    const pattern = document.createElementNS(SVG_NS, 'pattern');
    pattern.id = 'gridPattern';
    pattern.setAttribute('width', '20');
    pattern.setAttribute('height', '20');
    pattern.setAttribute('patternUnits', 'userSpaceOnUse');

    const path = document.createElementNS(SVG_NS, 'path');
    path.setAttribute('d', 'M 20 0 L 0 0 0 20');
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', '#2a2a3a');
    path.setAttribute('stroke-width', '0.5');
    path.setAttribute('opacity', '0.5');

    pattern.appendChild(path);
    defs.appendChild(pattern);
  }

  // ============================================================
  //  Transform Helpers
  // ============================================================

  function applyTransform() {
    const t = viewTransform;
    canvasSvg.style.transformOrigin = '0 0';
    canvasSvg.style.transform = `translate(${t.x}px, ${t.y}px) scale(${t.scale})`;
    if (zoomInfo) {
      zoomInfo.innerHTML = `<i class="fa-solid fa-magnifying-glass"></i> ${Math.round(t.scale * 100)}%`;
    }
  }

  function screenToSvg(clientX, clientY) {
    const rect = canvasSvg.getBoundingClientRect();
    const t = viewTransform;
    return {
      x: (clientX - rect.left - t.x) / t.scale,
      y: (clientY - rect.top - t.y) / t.scale
    };
  }

  // ============================================================
  //  Build Toolbox from NodeRegistry
  // ============================================================

  function buildToolbox() {
    toolboxScroll.innerHTML = '';

    // Use NodeRegistry if available (ES modules from nodes.js)
    let categories = [];
    try {
      if (typeof NodeRegistry !== 'undefined') {
        const catNames = NodeRegistry.getCategories();
        categories = catNames.map((name) => ({
          name,
          nodes: NodeRegistry.getNodesByCategory(name)
        }));
      }
    } catch (_) { /* fallback below */ }

    // Fallback: build from CATEGORIES defined in HTML
    if (categories.length === 0 && typeof CATEGORIES !== 'undefined') {
      categories = CATEGORIES.map((cat) => ({
        name: cat.name,
        icon: cat.icon,
        nodes: cat.nodes.map((n) => ({
          id: n.type,
          title: n.label,
          color: '#888',
          category: cat.name
        }))
      }));
    }

    // If still empty, try to extract from inline data
    if (categories.length === 0) {
      // Check window for any defined categories
      return;
    }

    categories.forEach((cat, idx) => {
      const item = document.createElement('div');
      item.className = 'category-item';

      const header = document.createElement('div');
      header.className = 'category-header';
      header.innerHTML = `
        <i class="fa-solid fa-chevron-down"></i>
        <span class="cat-icon"><i class="fa-regular fa-folder"></i></span>
        ${cat.name}
      `;

      const body = document.createElement('div');
      body.className = 'category-body';

      cat.nodes.forEach((n) => {
        const btn = document.createElement('div');
        btn.className = 'node-btn';
        btn.draggable = true;
        btn.dataset.nodeType = n.id || n.type;
        btn.innerHTML = `
          <span class="port-indicator exec"></span>
          <i class="fa-regular fa-square" style="font-size:11px;width:14px;text-align:center;"></i>
          ${n.title || n.label}
        `;
        btn.addEventListener('dragstart', onToolboxDragStart);
        body.appendChild(btn);
      });

      // Accordion toggle
      header.addEventListener('click', () => {
        header.classList.toggle('collapsed');
        body.classList.toggle('collapsed');
      });

      item.appendChild(header);
      item.appendChild(body);
      toolboxScroll.appendChild(item);
    });
  }

  // ============================================================
  //  Node Rendering
  // ============================================================

  function getNodeDefinition(type) {
    try {
      if (typeof NodeRegistry !== 'undefined') {
        return NodeRegistry.getDefinition(type);
      }
    } catch (_) { /* ignore */ }

    // Fallback: check NODE_FIELDS or CATEGORIES from HTML
    if (typeof NODE_FIELDS !== 'undefined' && NODE_FIELDS[type]) {
      const info = NODE_FIELDS[type];
      return {
        id: type,
        title: info.label,
        color: getCategoryColor(type),
        inputs: [{ name: '', type: 'exec', dataType: 'exec' }],
        outputs: [{ name: '', type: 'exec', dataType: 'exec' }],
        defaultConfig: info.props || {}
      };
    }
    return null;
  }

  function getCategoryColor(type) {
    const colorMap = {
      start_state: '#FF69B4', normal_state: '#FF69B4', end_state: '#FF69B4', state_group: '#FF69B4',
      key_event: '#87CEEB', mouse_event: '#87CEEB', custom_event: '#87CEEB', time_event: '#87CEEB',
      play_anim: '#32CD32', stop_anim: '#32CD32', switch_anim: '#32CD32', set_anim_param: '#32CD32',
      condition: '#BA55D3', state_check: '#BA55D3', var_check: '#BA55D3', null_check: '#BA55D3',
      set_var: '#FF8C00', call_func: '#FF8C00', send_msg: '#FF8C00', log_output: '#FF8C00',
      create_track: '#4A90E2', remove_track: '#4A90E2', track_xform: '#4A90E2',
      sequence: '#FFB347', loop: '#FFB347', parallel: '#FFB347', delay: '#FFB347',
      blend_mode: '#98FB98', overlay_mode: '#98FB98', transition: '#98FB98',
      math_op: '#DDA0DD', compare_op: '#DDA0DD', logic_op: '#DDA0DD', string_op: '#DDA0DD'
    };
    return colorMap[type] || '#888';
  }

  function getNodeBodyText(node) {
    const config = node.config || {};
    const keys = Object.keys(config);
    if (keys.length === 0) return '';
    const firstKey = keys[0];
    const val = config[firstKey];
    return firstKey + ': ' + (typeof val === 'object' ? JSON.stringify(val) : String(val));
  }

  function getPortsForNode(node) {
    const def = getNodeDefinition(node.type);
    if (!def) {
      // Fallback to generic ports
      return {
        inputs: [{ name: 'execIn', type: 'exec', dataType: 'exec' }],
        outputs: [{ name: 'execOut', type: 'exec', dataType: 'exec' }]
      };
    }

    // Map inputs: assign position info
    const inputs = (def.inputs || []).map((p, i) => ({
      ...p,
      portName: p.name || ('in_' + i),
      dir: 'in'
    }));

    const outputs = (def.outputs || []).map((p, i) => ({
      ...p,
      portName: p.name || ('out_' + i),
      dir: 'out'
    }));

    return { inputs, outputs };
  }

  function computePortPositions(node, inputs, outputs) {
    const positions = [];

    // Input ports on the left side
    const totalIn = inputs.length;
    if (totalIn > 0) {
      // Space them vertically in the node body
      const spacing = (NODE_H - HEADER_H) / (totalIn + 1);
      inputs.forEach((p, i) => {
        positions.push({
          ...p,
          cx: 0,
          cy: HEADER_H + spacing * (i + 1)
        });
      });
    }

    // Output ports on the right side
    const totalOut = outputs.length;
    if (totalOut > 0) {
      const spacing = (NODE_H - HEADER_H) / (totalOut + 1);
      outputs.forEach((p, i) => {
        positions.push({
          ...p,
          cx: NODE_W,
          cy: HEADER_H + spacing * (i + 1)
        });
      });
    }

    return positions;
  }

  function createNodeEl(node) {
    const g = document.createElementNS(SVG_NS, 'g');
    g.classList.add('node-group');
    g.dataset.nodeId = node.id;

    // === Background ===
    const bg = document.createElementNS(SVG_NS, 'rect');
    bg.classList.add('node-bg');
    bg.setAttribute('width', NODE_W);
    bg.setAttribute('height', NODE_H);
    bg.setAttribute('rx', '12');
    bg.setAttribute('ry', '12');
    bg.setAttribute('filter', 'url(#nodeShadow)');
    g.appendChild(bg);

    // === Header background ===
    const color = node.color || getCategoryColor(node.type) || '#888';
    const hbg = document.createElementNS(SVG_NS, 'rect');
    hbg.classList.add('node-header-bg');
    hbg.setAttribute('width', NODE_W);
    hbg.setAttribute('height', HEADER_H);
    hbg.setAttribute('rx', '12');
    hbg.setAttribute('ry', '12');
    hbg.setAttribute('fill', color);
    g.appendChild(hbg);

    // === Header title text ===
    const ht = document.createElementNS(SVG_NS, 'text');
    ht.classList.add('node-header-text');
    ht.setAttribute('x', NODE_W / 2);
    ht.setAttribute('y', HEADER_H / 2 + 1);
    ht.setAttribute('text-anchor', 'middle');
    ht.setAttribute('dominant-baseline', 'central');
    ht.textContent = node.title || node.type;
    g.appendChild(ht);

    // === Body text (first config value) ===
    const bt = document.createElementNS(SVG_NS, 'text');
    bt.classList.add('node-body-text');
    bt.setAttribute('x', NODE_W / 2);
    bt.setAttribute('y', HEADER_H + (NODE_H - HEADER_H) / 2);
    bt.setAttribute('text-anchor', 'middle');
    bt.setAttribute('dominant-baseline', 'central');
    bt.textContent = getNodeBodyText(node);
    g.appendChild(bt);

    // === Ports ===
    const { inputs, outputs } = getPortsForNode(node);
    const portPositions = computePortPositions(node, inputs, outputs);

    // Group by direction for storage
    const inputPorts = [];
    const outputPorts = [];

    portPositions.forEach((p) => {
      const portGroup = document.createElementNS(SVG_NS, 'g');
      portGroup.classList.add('port-group');
      portGroup.dataset.portName = p.portName;
      portGroup.dataset.portDir = p.dir;
      portGroup.dataset.portType = p.type;

      const circle = document.createElementNS(SVG_NS, 'circle');
      circle.classList.add('port-dot');
      circle.classList.add(p.type || 'exec');
      circle.setAttribute('cx', p.cx);
      circle.setAttribute('cy', p.cy);
      circle.setAttribute('r', PORT_R);

      // Color: pink for exec, gray for data
      const fillColor = (p.type === 'exec' || !p.type) ? '#FF69B4' : '#999';
      circle.setAttribute('fill', fillColor);
      circle.setAttribute('stroke', '#1e1e2e');
      circle.setAttribute('stroke-width', '1.5');

      portGroup.appendChild(circle);

      // Port label (if name exists)
      if (p.name) {
        const label = document.createElementNS(SVG_NS, 'text');
        label.classList.add('port-label');
        const isInput = p.dir === 'in';
        label.setAttribute('x', isInput ? p.cx + 10 : p.cx - 10);
        label.setAttribute('y', p.cy + 1);
        label.setAttribute('text-anchor', isInput ? 'start' : 'end');
        label.setAttribute('dominant-baseline', 'central');
        label.setAttribute('font-size', '9');
        label.setAttribute('fill', '#aaa');
        label.textContent = p.name;
        portGroup.appendChild(label);
      }

      g.appendChild(portGroup);

      // Store port reference
      const portRef = {
        el: portGroup,
        circleEl: circle,
        cx: p.cx,
        cy: p.cy,
        portName: p.portName,
        dir: p.dir,
        type: p.type
      };

      if (p.dir === 'in') {
        inputPorts.push(portRef);
      } else {
        outputPorts.push(portRef);
      }
    });

    // Store ports on node object
    node._ports = { inputs: inputPorts, outputs: outputPorts };
    node._allPorts = [...inputPorts, ...outputPorts];

    // === Events ===
    g.addEventListener('mousedown', onNodeMouseDown);
    g.addEventListener('dblclick', () => openNodeModal(node));
    g.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      e.stopPropagation();
      showContextMenu(e.clientX, e.clientY, node);
    });

    // Port events
    node._allPorts.forEach((p) => {
      p.circleEl.addEventListener('mousedown', (e) => onPortMouseDown(e, node, p));
      p.circleEl.addEventListener('mouseup', (e) => onPortMouseUp(e, node, p));
    });

    return g;
  }

  // ============================================================
  //  Node CRUD
  // ============================================================

  function addNode(type, x, y) {
    const def = getNodeDefinition(type);
    if (!def) return null;

    const id = ++nodeIdCounter;
    const node = {
      id: id,
      type: type,
      title: def.title || type,
      color: def.color || getCategoryColor(type),
      category: def.category || '',
      description: def.description || '',
      x: Math.max(0, x),
      y: Math.max(0, y),
      config: def.defaultConfig ? JSON.parse(JSON.stringify(def.defaultConfig)) : {},
      el: null,
      _ports: { inputs: [], outputs: [] },
      _allPorts: []
    };

    const el = createNodeEl(node);
    el.setAttribute('transform', `translate(${node.x},${node.y})`);
    nodesLayer.appendChild(el);
    node.el = el;
    nodes.set(id, node);

    selectNode(id);
    updateCode();
    return node;
  }

  function removeNode(id) {
    const node = nodes.get(id);
    if (!node) return;

    // Remove all connections involving this node
    for (let i = connections.length - 1; i >= 0; i--) {
      const c = connections[i];
      if (c.fromNodeId === id || c.toNodeId === id) {
        removeConnectionLine(c.id);
        connections.splice(i, 1);
      }
    }

    node.el.remove();
    nodes.delete(id);

    if (selectedNodeId === id) selectedNodeId = null;
    updateCode();
  }

  function duplicateNode(id) {
    const src = nodes.get(id);
    if (!src) return;

    const copy = addNode(src.type, src.x + 30, src.y + 30);
    if (copy) {
      copy.config = JSON.parse(JSON.stringify(src.config));
      copy.title = src.title;
      updateNodeVisual(copy);
      updateCode();
    }
  }

  function updateNodeVisual(node) {
    if (!node.el) return;
    const headerText = node.el.querySelector('.node-header-text');
    const bodyText = node.el.querySelector('.node-body-text');
    if (headerText) headerText.textContent = node.title || node.type;
    if (bodyText) bodyText.textContent = getNodeBodyText(node);
  }

  // ============================================================
  //  Node Drag
  // ============================================================

  function onNodeMouseDown(e) {
    if (e.button !== 0) return;
    const g = e.currentTarget;
    const nodeId = parseInt(g.dataset.nodeId, 10);
    const node = nodes.get(nodeId);
    if (!node) return;

    selectNode(nodeId);

    // Ignore if clicking on a port circle
    if (e.target.closest('.port-dot')) return;

    const startX = e.clientX;
    const startY = e.clientY;
    const origX = node.x;
    const origY = node.y;
    dragNodeId = nodeId;

    const onMove = (ev) => {
      const t = viewTransform;
      const dx = (ev.clientX - startX) / t.scale;
      const dy = (ev.clientY - startY) / t.scale;
      node.x = Math.max(0, origX + dx);
      node.y = Math.max(0, origY + dy);
      node.el.setAttribute('transform', `translate(${node.x},${node.y})`);
      updateConnectionsForNode(nodeId);
    };

    const onUp = () => {
      dragNodeId = null;
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    };

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }

  // ============================================================
  //  Connections
  // ============================================================

  function addConnection(fromNodeId, fromPortName, toNodeId, toPortName) {
    // Prevent self-connections
    if (fromNodeId === toNodeId) return;

    // Avoid duplicates
    const dup = connections.some(
      (c) => c.fromNodeId === fromNodeId && c.fromPortName === fromPortName &&
             c.toNodeId === toNodeId && c.toPortName === toPortName
    );
    if (dup) return;

    const conn = {
      id: 'conn-' + Date.now() + '-' + Math.random().toString(36).slice(2, 6),
      fromNodeId,
      fromPortName,
      toNodeId,
      toPortName,
      el: null
    };

    connections.push(conn);
    const path = createConnectionPath(conn);
    if (path) {
      conn.el = path;
      connectionsLayer.appendChild(path);
    }
    updateCode();
  }

  function createConnectionPath(conn) {
    const fromNode = nodes.get(conn.fromNodeId);
    const toNode = nodes.get(conn.toNodeId);
    if (!fromNode || !toNode) return null;

    const fromPort = findPortByName(fromNode, conn.fromPortName);
    const toPort = findPortByName(toNode, conn.toPortName);
    if (!fromPort || !toPort) return null;

    const x1 = fromNode.x + fromPort.cx;
    const y1 = fromNode.y + fromPort.cy;
    const x2 = toNode.x + toPort.cx;
    const y2 = toNode.y + toPort.cy;

    const dx = Math.abs(x2 - x1) * 0.5;
    const d = `M${x1},${y1} C${x1 + dx},${y1} ${x2 - dx},${y2} ${x2},${y2}`;

    const path = document.createElementNS(SVG_NS, 'path');
    path.classList.add('connection-line');
    path.setAttribute('d', d);
    path.dataset.connId = conn.id;

    path.addEventListener('click', (e) => {
      e.stopPropagation();
      removeConnection(conn.id);
    });

    return path;
  }

  function findPortByName(node, portName) {
    if (!node._allPorts) return null;
    return node._allPorts.find((p) => p.portName === portName);
  }

  function removeConnection(connId) {
    for (let i = connections.length - 1; i >= 0; i--) {
      if (connections[i].id === connId) {
        removeConnectionLine(connId);
        connections.splice(i, 1);
        break;
      }
    }
    updateCode();
  }

  function removeConnectionLine(connId) {
    const el = connectionsLayer.querySelector(`[data-conn-id="${connId}"]`);
    if (el) el.remove();
  }

  function updateConnectionsForNode(nodeId) {
    connections.forEach((c) => {
      if (c.fromNodeId === nodeId || c.toNodeId === nodeId) {
        const pathEl = c.el;
        if (!pathEl) return;

        const fromNode = nodes.get(c.fromNodeId);
        const toNode = nodes.get(c.toNodeId);
        if (!fromNode || !toNode) return;

        const fromPort = findPortByName(fromNode, c.fromPortName);
        const toPort = findPortByName(toNode, c.toPortName);
        if (!fromPort || !toPort) return;

        const x1 = fromNode.x + fromPort.cx;
        const y1 = fromNode.y + fromPort.cy;
        const x2 = toNode.x + toPort.cx;
        const y2 = toNode.y + toPort.cy;

        const dx = Math.abs(x2 - x1) * 0.5;
        pathEl.setAttribute('d', `M${x1},${y1} C${x1 + dx},${y1} ${x2 - dx},${y2} ${x2},${y2}`);
      }
    });
  }

  function rebuildAllConnections() {
    connectionsLayer.querySelectorAll('.connection-line:not(#dragLine)').forEach((el) => el.remove());
    connections.forEach((conn) => {
      const path = createConnectionPath(conn);
      if (path) {
        conn.el = path;
        connectionsLayer.appendChild(path);
      }
    });
  }

  // ============================================================
  //  Port Connection Dragging
  // ============================================================

  function onPortMouseDown(e, node, port) {
    e.stopPropagation();
    e.preventDefault();

    if (port.dir !== 'out') return;

    connectState = {
      fromNodeId: node.id,
      fromPortName: port.portName
    };

    dragLine.style.display = 'block';
    updateTempDragLine(e.clientX, e.clientY);
  }

  function onPortMouseUp(e, node, port) {
    if (!connectState) return;
    e.stopPropagation();
    e.preventDefault();

    if (port.dir !== 'in') {
      cancelConnect();
      return;
    }

    addConnection(connectState.fromNodeId, connectState.fromPortName, node.id, port.portName);
    cancelConnect();
  }

  function updateTempDragLine(cx, cy) {
    const fromNode = nodes.get(connectState.fromNodeId);
    if (!fromNode) return;

    const fromPort = findPortByName(fromNode, connectState.fromPortName);
    if (!fromPort) return;

    const x1 = fromNode.x + fromPort.cx;
    const y1 = fromNode.y + fromPort.cy;
    const svgPos = screenToSvg(cx, cy);
    const x2 = svgPos.x;
    const y2 = svgPos.y;

    const dx = Math.abs(x2 - x1) * 0.5;
    const d = `M${x1},${y1} C${x1 + dx},${y1} ${x2 - dx},${y2} ${x2},${y2}`;
    dragLine.setAttribute('d', d);
  }

  function cancelConnect() {
    connectState = null;
    dragLine.style.display = 'none';
    dragLine.setAttribute('d', '');
  }

  // ============================================================
  //  Toolbox Drag & Drop
  // ============================================================

  function onToolboxDragStart(e) {
    const btn = e.target.closest('.node-btn');
    if (!btn) return;
    e.dataTransfer.setData('text/plain', btn.dataset.nodeType);
    e.dataTransfer.effectAllowed = 'copy';
  }

  // Canvas drop handler
  canvasSvg.addEventListener('dragover', (e) => e.preventDefault());
  canvasSvg.addEventListener('drop', (e) => {
    e.preventDefault();
    const type = e.dataTransfer.getData('text/plain');
    if (!type) return;

    const svgPos = screenToSvg(e.clientX, e.clientY);
    addNode(type, svgPos.x - NODE_W / 2, svgPos.y - NODE_H / 2);
  });

  // ============================================================
  //  Selection & Keyboard
  // ============================================================

  function selectNode(id) {
    document.querySelectorAll('.node-group.selected').forEach((el) => el.classList.remove('selected'));
    selectedNodeId = id;
    if (id) {
      const node = nodes.get(id);
      if (node && node.el) node.el.classList.add('selected');
    }
  }

  // Canvas click to deselect
  canvasSvg.addEventListener('click', (e) => {
    if (e.target === canvasSvg || e.target.tagName === 'svg') {
      selectNode(null);
      contextMenu.classList.remove('active');
    }
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    // Delete / Backspace to remove selected node
    if ((e.key === 'Delete' || e.key === 'Backspace') && !e.target.closest('input,textarea,select')) {
      if (selectedNodeId) {
        removeNode(selectedNodeId);
      }
    }

    // Escape to close modals/menus
    if (e.key === 'Escape') {
      if (nodeModal.classList.contains('active')) closeModal();
      contextMenu.classList.remove('active');
      if (connectState) cancelConnect();
    }
  });

  // ============================================================
  //  Context Menu
  // ============================================================

  // Canvas right-click: show canvas menu
  canvasSvg.addEventListener('contextmenu', (e) => {
    // Only show canvas menu if clicking on empty space (not on a node)
    if (!e.target.closest('.node-group')) {
      e.preventDefault();
      showCanvasContextMenu(e.clientX, e.clientY);
    }
  });

  function showContextMenu(x, y, node) {
    contextMenuNodeId = node.id;
    // Show node-specific items
    contextMenu.querySelectorAll('[data-action]').forEach((item) => {
      item.style.display = '';
    });
    // Hide canvas-specific items if any exist (they don't in current HTML)
    contextMenu.style.left = x + 'px';
    contextMenu.style.top = y + 'px';
    contextMenu.classList.add('active');
  }

  function showCanvasContextMenu(x, y) {
    contextMenuNodeId = null;
    // For canvas, show Paste if clipboad has data, and Clear All
    const pasteItem = contextMenu.querySelector('[data-action="paste"]');
    if (pasteItem) pasteItem.style.display = clipboardNode ? '' : 'none';
    const clearItem = contextMenu.querySelector('[data-action="clearall"]');
    if (clearItem) clearItem.style.display = '';
    // Hide node-specific items
    contextMenu.querySelectorAll('[data-action="edit"],[data-action="duplicate"],[data-action="delete"]').forEach((item) => {
      item.style.display = 'none';
    });
    contextMenu.style.left = x + 'px';
    contextMenu.style.top = y + 'px';
    contextMenu.classList.add('active');
  }

  // Close context menu on document click
  document.addEventListener('click', (e) => {
    if (!contextMenu.contains(e.target)) {
      contextMenu.classList.remove('active');
    }
  });

  // Context menu action handler
  contextMenu.addEventListener('click', (e) => {
    const item = e.target.closest('.context-menu-item');
    if (!item) return;

    const action = item.dataset.action;
    contextMenu.classList.remove('active');

    switch (action) {
      case 'edit':
        if (contextMenuNodeId) {
          const node = nodes.get(contextMenuNodeId);
          if (node) openNodeModal(node);
        }
        break;

      case 'duplicate':
        if (contextMenuNodeId) duplicateNode(contextMenuNodeId);
        break;

      case 'delete':
        if (contextMenuNodeId) removeNode(contextMenuNodeId);
        break;

      case 'paste':
        if (clipboardNode) {
          const newNode = addNode(clipboardNode.type, clipboardNode.x + 30, clipboardNode.y + 30);
          if (newNode) {
            newNode.config = JSON.parse(JSON.stringify(clipboardNode.config));
            newNode.title = clipboardNode.title;
            updateNodeVisual(newNode);
            updateCode();
          }
        }
        break;

      case 'clearall':
        if (confirm('确定要清空所有节点和连接吗？')) {
          clearAll();
        }
        break;
    }
  });

  function clearAll() {
    // Remove all nodes (connections are cleaned up in removeNode)
    const ids = Array.from(nodes.keys());
    ids.forEach((id) => removeNode(id));
    connections.length = 0;
    connectionsLayer.innerHTML = '';
    selectedNodeId = null;
    updateCode();
  }

  // ============================================================
  //  Node Config Modal
  // ============================================================

  function openNodeModal(node) {
    editingNode = node;
    modalTitle.textContent = '配置 - ' + (node.title || node.type);
    modalBody.innerHTML = '';

    // Label field first
    const labelGroup = document.createElement('div');
    labelGroup.className = 'form-group';
    const labelLabel = document.createElement('label');
    labelLabel.textContent = '显示名称';
    labelGroup.appendChild(labelLabel);
    const labelInput = document.createElement('input');
    labelInput.type = 'text';
    labelInput.dataset.key = '_label';
    labelInput.value = node.title || '';
    labelGroup.appendChild(labelInput);
    modalBody.appendChild(labelGroup);

    // Config fields
    const config = node.config || {};
    Object.keys(config).forEach((key) => {
      const val = config[key];
      const group = document.createElement('div');
      group.className = 'form-group';

      const label = document.createElement('label');
      label.textContent = key;
      group.appendChild(label);

      let input;
      if (typeof val === 'boolean') {
        const sel = document.createElement('select');
        sel.dataset.key = key;
        sel.innerHTML = '<option value="true">是</option><option value="false">否</option>';
        sel.value = val ? 'true' : 'false';
        input = sel;
      } else if (typeof val === 'number') {
        input = document.createElement('input');
        input.type = 'number';
        input.step = 'any';
        input.dataset.key = key;
        input.value = val;
      } else if (Array.isArray(val)) {
        input = document.createElement('input');
        input.type = 'text';
        input.dataset.key = key;
        input.value = JSON.stringify(val);
        input.placeholder = 'JSON 数组';
      } else {
        input = document.createElement('input');
        input.type = 'text';
        input.dataset.key = key;
        input.value = val;
      }

      group.appendChild(input);
      modalBody.appendChild(group);
    });

    nodeModal.classList.add('active');
  }

  function closeModal() {
    nodeModal.classList.remove('active');
    editingNode = null;
  }

  function saveModal() {
    if (!editingNode) return;

    const inputs = modalBody.querySelectorAll('[data-key]');
    inputs.forEach((inp) => {
      const key = inp.dataset.key;

      if (key === '_label') {
        editingNode.title = inp.value;
        return;
      }

      const currentVal = editingNode.config[key];
      if (typeof currentVal === 'boolean') {
        editingNode.config[key] = inp.value === 'true';
      } else if (typeof currentVal === 'number') {
        editingNode.config[key] = parseFloat(inp.value) || 0;
      } else if (Array.isArray(currentVal)) {
        try {
          editingNode.config[key] = JSON.parse(inp.value);
        } catch {
          editingNode.config[key] = [];
        }
      } else {
        editingNode.config[key] = inp.value;
      }
    });

    updateNodeVisual(editingNode);
    updateCode();
    closeModal();
  }

  // Modal event listeners
  modalCloseBtn.addEventListener('click', closeModal);
  modalCancelBtn.addEventListener('click', closeModal);
  modalConfirmBtn.addEventListener('click', saveModal);
  nodeModal.addEventListener('click', (e) => {
    if (e.target === nodeModal) closeModal();
  });

  // ============================================================
  //  Zoom & Pan
  // ============================================================

  // Mouse wheel zoom
  canvasContainer.addEventListener('wheel', (e) => {
    e.preventDefault();
    const rect = canvasSvg.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.min(3, Math.max(0.2, viewTransform.scale * delta));

    // Zoom towards mouse position
    viewTransform.x = mx - (mx - viewTransform.x) * (newScale / viewTransform.scale);
    viewTransform.y = my - (my - viewTransform.y) * (newScale / viewTransform.scale);
    viewTransform.scale = newScale;

    applyTransform();
  }, { passive: false });

  // Pan: mousedown on empty canvas area
  canvasSvg.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    // Only start pan if clicking on empty SVG space (not on a node)
    if (e.target.closest('.node-group') || e.target.closest('.port-dot') || e.target.closest('.connection-line')) {
      return;
    }

    isPanning = true;
    panStart.x = e.clientX - viewTransform.x;
    panStart.y = e.clientY - viewTransform.y;
  });

  document.addEventListener('mousemove', (e) => {
    if (isPanning) {
      viewTransform.x = e.clientX - panStart.x;
      viewTransform.y = e.clientY - panStart.y;
      applyTransform();
    }

    // Update temporary connection drag line
    if (connectState) {
      updateTempDragLine(e.clientX, e.clientY);
    }
  });

  document.addEventListener('mouseup', () => {
    if (isPanning) {
      isPanning = false;
    }
    if (connectState) {
      cancelConnect();
    }
  });

  // ============================================================
  //  Code Generation
  // ============================================================

  function updateCode() {
    // Try external codegen module first
    try {
      if (typeof generateCode === 'function') {
        const code = generateCode(nodes, connections);
        displayCode(code);
        return;
      }
    } catch (_) { /* fallback to built-in */ }

    // Built-in code generation
    const lines = generateLua();
    displayCode(lines);
  }

  function displayCode(lines) {
    codeOutput.innerHTML = '';

    if (!lines || lines.length === 0) {
      codeOutput.innerHTML = `
        <div class="code-empty-state">
          <i class="fa-regular fa-file-code"></i>
          <p>将节点拖入画布并连接，<br>Lua 代码将自动生成于此</p>
        </div>
      `;
      return;
    }

    const pre = document.createElement('pre');
    pre.style.margin = '0';
    pre.style.whiteSpace = 'pre-wrap';
    pre.style.fontFamily = 'var(--font-mono)';
    pre.style.fontSize = '12px';
    pre.style.lineHeight = '1.7';

    // Build full text with syntax highlighting
    const fullText = lines.join('\n');
    const highlighted = fullText
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/(--.*)/g, '<span class="comment">$1</span>')
      .replace(/\b(function|if|then|else|elseif|end|return|for|while|do|local|nil|true|false|and|or|not|repeat|until|break)\b/g, '<span class="keyword">$1</span>')
      .replace(/"([^"]*)"/g, '<span class="string">"$1"</span>')
      .replace(/'([^']*)'/g, '<span class="string">\'$1\'</span>')
      .replace(/\b(\d+\.?\d*)\b/g, '<span class="number">$1</span>');

    pre.innerHTML = highlighted;
    codeOutput.appendChild(pre);
  }

  function generateLua() {
    const sortedNodes = topologicalSort();
    if (sortedNodes.length === 0) return [];

    const lines = [];
    lines.push('-- ============================================');
    lines.push('-- Generated by NodeForge - TACZ Lua Editor');
    lines.push('-- Project: ' + (projectNameInput.value || 'Untitled'));
    lines.push('-- ============================================');
    lines.push('');

    sortedNodes.forEach((id) => {
      const node = nodes.get(id);
      if (!node) return;

      const title = node.title || node.type;
      const config = node.config || {};
      const type = node.type;

      lines.push('-- [' + node.id + '] ' + title);

      switch (type) {
        case 'start_state':
        case 'EntryNode':
          lines.push('function state_' + node.id + '_entry()');
          lines.push('  -- Initial state: ' + (config.state_name || 'entry'));
          lines.push('  return "' + (config.state_name || 'entry') + '"');
          lines.push('end');
          break;

        case 'normal_state':
        case 'UpdateNode':
          lines.push('function state_' + node.id + '()');
          lines.push('  -- State: ' + (config.name || config.state_name || 'idle'));
          if (config.on_enter) lines.push('  ' + config.on_enter);
          if (config.condition) lines.push('  if ' + config.condition + ' then');
          lines.push('  -- ... behavior ...');
          if (config.condition) lines.push('  end');
          if (config.on_exit) lines.push('  ' + config.on_exit);
          lines.push('end');
          break;

        case 'end_state':
        case 'ExitNode':
          lines.push('function state_' + node.id + '_exit()');
          lines.push('  -- Exit state: ' + (config.state_name || 'exit'));
          lines.push('  return nil');
          lines.push('end');
          break;

        case 'TransitionNode':
          lines.push('-- Transition: ' + (config.from_state || '') + ' -> ' + (config.to_state || ''));
          if (config.condition) {
            lines.push('if ' + config.condition + ' then');
            lines.push('  return "' + (config.to_state || 'idle') + '"');
            lines.push('end');
          } else {
            lines.push('return "' + (config.to_state || 'idle') + '"');
          }
          break;

        case 'play_anim':
        case 'RunAnimationNode':
          lines.push('anim_play("' + (config.animation_name || config.anim_name || '') + '", {');
          lines.push('  track = ' + (config.track || 'MAIN_TRACK') + ',');
          lines.push('  blend = ' + (config.blend_time || config.blend || 0.2) + ',');
          lines.push('  mode = "' + (config.mode || 'PLAY_ONCE_STOP') + '"');
          lines.push('})');
          break;

        case 'stop_anim':
        case 'StopAnimationNode':
          lines.push('anim_stop(' + (config.track || 'MAIN_TRACK') + ')');
          break;

        case 'LoopAnimationNode':
          lines.push('anim_loop("' + (config.animation_name || '') + '", ' + (config.track || 'MOVEMENT_TRACK') + ')');
          break;

        case 'set_var':
        case 'SetVarNode':
          lines.push(config.var_name + ' = ' + JSON.stringify(config.value));
          break;

        case 'condition':
        case 'condition_branch':
        case 'IfNode':
          lines.push('if ' + (config.expression || 'true') + ' then');
          lines.push('  -- condition met');
          lines.push('else');
          lines.push('  -- condition not met');
          lines.push('end');
          break;

        case 'CheckAmmoNode':
          lines.push('if has_ammo() then');
          lines.push('  -- has ammo');
          lines.push('else');
          lines.push('  -- no ammo');
          lines.push('end');
          break;

        case 'CheckAmmoCountNode':
          lines.push('if ammo_count() ' + (config.operator || '<=') + ' ' + (config.value || 0) + ' then');
          lines.push('  -- condition met');
          lines.push('else');
          lines.push('  -- condition not met');
          lines.push('end');
          break;

        case 'CheckHeatNode':
          lines.push('if is_over_heated() then');
          lines.push('  -- over heated');
          lines.push('else');
          lines.push('  -- not over heated');
          lines.push('end');
          break;

        case 'CheckAimingNode':
          lines.push('if get_aim_progress() >= ' + (config.progress || 0.5) + ' then');
          lines.push('  -- aiming complete');
          lines.push('else');
          lines.push('  -- still aiming');
          lines.push('end');
          break;

        case 'CheckGroundNode':
          lines.push('if is_on_ground() then');
          lines.push('  -- on ground');
          lines.push('else');
          lines.push('  -- in air');
          lines.push('end');
          break;

        case 'CheckStoppedNode':
          lines.push('if is_anim_stopped(' + (config.track || 'MAIN_TRACK') + ') then');
          lines.push('  -- anim stopped');
          lines.push('else');
          lines.push('  -- anim playing');
          lines.push('end');
          break;

        case 'ReturnNode':
          lines.push('return "' + (config.state_name || 'idle') + '"');
          break;

        case 'loop':
        case 'LoopNode':
          lines.push('for i = 1, ' + (config.count || 1) + ' do');
          lines.push('  -- loop body');
          lines.push('end');
          break;

        case 'delay':
        case 'DelayNode':
          lines.push('wait_ms(' + (config.delay_ms || 500) + ')');
          break;

        case 'log_output':
        case 'LogOutputNode':
          lines.push('print("[' + (config.level || 'info') + '] ' + (config.message || '') + '")');
          break;

        case 'key_event':
          lines.push('-- Key event: ' + (config.key || 'space') + ' (' + (config.action || 'press') + ')');
          break;

        case 'mouse_event':
          lines.push('-- Mouse event: ' + (config.button || 'left') + ' (' + (config.action || 'click') + ')');
          break;

        case 'custom_event':
          lines.push('-- Custom event: ' + (config.event_name || 'my_event'));
          break;

        case 'time_event':
          lines.push('-- Time event: every ' + (config.delay_ms || 1000) + 'ms' + (config.repeat ? ' (repeat)' : ''));
          break;

        case 'call_func':
        case 'CallFuncNode':
          lines.push(config.func_name + '(' + (Array.isArray(config.args) ? config.args.join(', ') : '') + ')');
          break;

        case 'send_msg':
          lines.push('send_message("' + (config.channel || '') + '", ' + JSON.stringify(config.data) + ')');
          break;

        case 'CustomLuaNode':
          lines.push(config.code || '-- custom code');
          break;

        case 'HideCrosshairNode':
          lines.push('set_crosshair_visible(' + (config.hide !== false ? 'false' : 'true') + ')');
          break;

        case 'PlayReloadNode':
          lines.push('play_reload("' + (config.reload_type || 'tactical') + '")');
          break;

        case 'AndNode':
          lines.push('-- A and B');
          break;

        case 'OrNode':
          lines.push('-- A or B');
          break;

        case 'NotNode':
          lines.push('-- not A');
          break;

        case 'CompareNode':
          lines.push('-- A ' + (config.operator || '==') + ' B');
          break;

        case 'math_op':
        case 'MathOpNode':
          lines.push('-- ' + (config.a || 0) + ' ' + (config.op || '+') + ' ' + (config.b || 0));
          break;

        case 'compare_op':
          lines.push('-- ' + (config.a || 0) + ' ' + (config.op || '>') + ' ' + (config.b || 0));
          break;

        case 'logic_op':
          lines.push('-- ' + (config.a !== false ? 'true' : 'false') + ' ' + (config.op || 'AND') + ' ' + (config.b !== false ? 'true' : 'false'));
          break;

        case 'string_op':
          if (config.op === 'concat') {
            lines.push('-- ' + JSON.stringify(config.a || '') + ' .. ' + JSON.stringify(config.b || ''));
          } else {
            lines.push('-- string operation: ' + (config.op || 'concat'));
          }
          break;

        default:
          lines.push('-- TODO: implement logic for ' + type);
      }

      lines.push('');
    });

    return lines;
  }

  function topologicalSort() {
    const adj = {};
    const inDeg = {};

    nodes.forEach((_, id) => {
      adj[id] = [];
      inDeg[id] = 0;
    });

    connections.forEach((c) => {
      if (adj[c.fromNodeId]) {
        adj[c.fromNodeId].push(c.toNodeId);
        if (inDeg[c.toNodeId] !== undefined) inDeg[c.toNodeId]++;
      }
    });

    const queue = [];
    nodes.forEach((_, id) => {
      if (inDeg[id] === 0) queue.push(id);
    });

    const result = [];
    while (queue.length > 0) {
      const u = queue.shift();
      result.push(u);
      (adj[u] || []).forEach((v) => {
        inDeg[v]--;
        if (inDeg[v] === 0) queue.push(v);
      });
    }

    return result;
  }

  // ============================================================
  //  Code Panel Buttons
  // ============================================================

  // Copy button
  $('copyCodeBtn').addEventListener('click', () => {
    const text = codeOutput.textContent || '';
    navigator.clipboard.writeText(text).catch((err) => {
      console.warn('Copy failed:', err);
    });
  });

  // Export / Download button
  $('exportCodeBtn').addEventListener('click', () => {
    const text = codeOutput.textContent || '';
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = (projectNameInput.value || 'state_machine') + '.lua';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });

  // Refresh button
  $('refreshCodeBtn').addEventListener('click', updateCode);

  // ============================================================
  //  Window Resize
  // ============================================================

  window.addEventListener('resize', () => {
    // No-op for now; connections are recalculated on node move
  });

  // ============================================================
  //  Initialization
  // ============================================================

  function init() {
    addGridPattern();

    // Try to load from codegen.js if available
    // The codegen.js module should expose a global `generateCode` function
    // or we use the built-in generator

    buildToolbox();
    applyTransform();

    // Add example nodes
    const n1 = addNode('start_state', 50, 150);
    if (n1) {
      n1.title = '初始状态';
      n1.config.name = 'entry';
      updateNodeVisual(n1);
    }

    const n2 = addNode('normal_state', 300, 150);
    if (n2) {
      n2.title = '空闲状态';
      n2.config.name = 'idle';
      updateNodeVisual(n2);
    }

    const n3 = addNode('normal_state', 300, 310);
    if (n3) {
      n3.title = '运行状态';
      n3.config.name = 'running';
      updateNodeVisual(n3);
    }

    // Wire connections
    if (n1 && n2) {
      const n1Out = n1._ports.outputs[0];
      const n2In = n2._ports.inputs[0];
      if (n1Out && n2In) addConnection(n1.id, n1Out.portName, n2.id, n2In.portName);
    }

    if (n2 && n3) {
      const n2Out = n2._ports.outputs[0];
      const n3In = n3._ports.inputs[0];
      if (n2Out && n3In) addConnection(n2.id, n2Out.portName, n3.id, n3In.portName);
    }

    selectNode(null);
    updateCode();
  }

  // Wait for DOM and modules to load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
