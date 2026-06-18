/**
 * codegen.js — TACZ (Timeless and Classics Zero) Lua State Machine Code Generator
 *
 * Takes an array of node objects and connection objects (from NodeForge editor),
 * and produces a complete TACZ state machine Lua script.
 *
 * Export:
 *   generateCode(nodes, connections) => string (Lua source)
 *
 * Node object format (from NodeRegistry.createNode):
 *   { id, type, title, config, inputs, outputs, ... }
 *
 * Connection object format:
 *   { id?, fromNodeId, fromPort, toNodeId, toPort }
 *   where fromPort/toPort reference the port's `name` field from the node definition.
 *   For single exec ports the name is '' (empty string).
 *   For condition outputs: '是' / '否'
 *   For IfNode exec outputs: '成立' / '不成立'
 *   For IfNode data input: '条件'
 *   For logic node inputs: 'A', 'B', '输入'
 *   For logic node outputs: '结果'
 *   For track node outputs: 'MAIN', 'BASE', 'BOLT_CAUGHT', 'ADS', 'SPRINT', 'MOVEMENT'
 *   For TrackLineNode outputs: 'STATIC', 'GUN_KICK', 'BLENDING'
 */

'use strict';

// ─── Helpers ──────────────────────────────────────────

/** Find all output connections from a given node + port. */
function findOutputs(nodeId, portName, connections) {
  return connections.filter(c => c.fromNodeId === nodeId && c.fromPort === portName);
}

/** Find the single connection going into a specific node + port. */
function findInput(nodeId, portName, connections) {
  return connections.find(c => c.toNodeId === nodeId && c.toPort === portName);
}

/** Get a node by ID from the nodes array. */
function getNode(nodeId, nodes) {
  return nodes.find(n => n.id === nodeId);
}

/** Safe access to node config values. */
function cfg(node, key, fallback) {
  if (node && node.config && node.config[key] !== undefined) return node.config[key];
  return fallback;
}

/** Escape a Lua string literal (single-quoted). */
function escStr(s) {
  if (typeof s !== 'string') return String(s);
  return s.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
}

/** Format a Lua value for inline use (strings get quoted, booleans as true/false, numbers as-is). */
function luaVal(v) {
  if (typeof v === 'string') return "'" + escStr(v) + "'";
  if (typeof v === 'boolean') return v ? 'true' : 'false';
  if (typeof v === 'number') return String(v);
  return 'nil';
}


// ─── Data-Expression Generation ──────────────────────

/**
 * Generate a Lua expression by walking the data-flow graph backwards from a
 * given node's data output port.  Used to produce condition expressions for
 * IfNode, logic nodes, compare nodes, etc.
 *
 * @param {string} nodeId   Source node ID (the one with the data output)
 * @param {string} portName Output port name on that node
 * @param {Array}  connections
 * @param {Array}  nodes
 * @param {Set}    visited  Avoid circular references
 * @returns {string} Lua expression
 */
function generateDataExpression(nodeId, portName, connections, nodes, visited) {
  const node = getNode(nodeId, nodes);
  if (!node) return 'false';
  const key = nodeId + '::' + portName;
  if (visited.has(key)) return 'false';
  visited.add(key);

  switch (node.type) {
    // ── Condition checks (data output from check-type nodes) ──
    case 'CheckAmmoNode':
      return 'context:hasAmmo()';
    case 'CheckAmmoCountNode': {
      const op = cfg(node, 'operator', '<=');
      const val = cfg(node, 'value', 0);
      return 'context:getAmmoCount() ' + op + ' ' + luaVal(val);
    }
    case 'CheckHeatNode':
      return 'context:isOverHeated()';
    case 'CheckAimingNode': {
      const prog = cfg(node, 'progress', 0.5);
      return 'context:getAimingProgress() >= ' + luaVal(prog);
    }
    case 'CheckGroundNode':
      return 'context:isOnGround()';
    case 'CheckRunningNode':
      return 'context:isRunning()';
    case 'CheckStoppedNode': {
      const trk = cfg(node, 'track', 'MAIN_TRACK');
      return 'context:isAnimationStopped(' + luaVal(trk) + ')';
    }
    case 'CheckShootCooldownNode': {
      const op = cfg(node, 'operator', '>');
      const val = cfg(node, 'value', 0);
      return 'context:getShootCooldown() ' + op + ' ' + luaVal(val);
    }
    case 'CheckTrackIdleNode': {
      const trk = cfg(node, 'track', 'MAIN_TRACK');
      return 'context:isTrackIdle(' + luaVal(trk) + ')';
    }
    case 'CheckTrackHoldingNode': {
      const trk = cfg(node, 'track', 'MOVEMENT_TRACK');
      return 'context:isTrackHolding(' + luaVal(trk) + ')';
    }
    case 'CheckWalkDirectionNode': {
      const dir = cfg(node, 'direction', 'forward');
      return 'context:getWalkDirection() == ' + luaVal(dir);
    }

    // ── Logic operators ──
    case 'AndNode': {
      const aExpr = resolveDataInput(nodeId, 'A', connections, nodes, visited);
      const bExpr = resolveDataInput(nodeId, 'B', connections, nodes, visited);
      return '(' + aExpr + ') and (' + bExpr + ')';
    }
    case 'OrNode': {
      const aExpr = resolveDataInput(nodeId, 'A', connections, nodes, visited);
      const bExpr = resolveDataInput(nodeId, 'B', connections, nodes, visited);
      return '(' + aExpr + ') or (' + bExpr + ')';
    }
    case 'NotNode': {
      const inExpr = resolveDataInput(nodeId, '输入', connections, nodes, visited);
      return 'not (' + inExpr + ')';
    }
    case 'CompareNode': {
      const op = cfg(node, 'operator', '==');
      const aExpr = resolveDataInput(nodeId, 'A', connections, nodes, visited);
      const bExpr = resolveDataInput(nodeId, 'B', connections, nodes, visited);
      return '(' + aExpr + ') ' + op + ' (' + bExpr + ')';
    }

    // ── Math nodes (data output = computed value) ──
    case 'AddNode': {
      const aExpr = resolveDataInput(nodeId, 'A', connections, nodes, visited);
      const bExpr = resolveDataInput(nodeId, 'B', connections, nodes, visited);
      return '(' + aExpr + ') + (' + bExpr + ')';
    }
    case 'SubtractNode': {
      const aExpr = resolveDataInput(nodeId, 'A', connections, nodes, visited);
      const bExpr = resolveDataInput(nodeId, 'B', connections, nodes, visited);
      return '(' + aExpr + ') - (' + bExpr + ')';
    }
    case 'MultiplyNode': {
      const aExpr = resolveDataInput(nodeId, 'A', connections, nodes, visited);
      const bExpr = resolveDataInput(nodeId, 'B', connections, nodes, visited);
      return '(' + aExpr + ') * (' + bExpr + ')';
    }
    case 'DivideNode': {
      const aExpr = resolveDataInput(nodeId, 'A', connections, nodes, visited);
      const bExpr = resolveDataInput(nodeId, 'B', connections, nodes, visited);
      return '(' + aExpr + ') / (' + bExpr + ')';
    }

    // ── Track / TrackLine data outputs (used as literal string values) ──
    case 'TrackNode': {
      // Output port names map to literal track name strings
      const trackMap = {
        'BASE': 'BASE_TRACK',
        'BOLT_CAUGHT': 'BOLT_CAUGHT_TRACK',
        'ADS': 'ADS_TRACK',
        'MAIN': 'MAIN_TRACK',
        'SPRINT': 'SPRINT_TRACK',
        'MOVEMENT': 'MOVEMENT_TRACK',
      };
      return "'" + (trackMap[portName] || portName) + "'";
    }
    case 'TrackLineNode': {
      const lineMap = {
        'STATIC': 'STATIC_TRACK_LINE',
        'GUN_KICK': 'GUN_KICK_TRACK_LINE',
        'BLENDING': 'BLENDING_TRACK_LINE',
      };
      return "'" + (lineMap[portName] || portName) + "'";
    }
    case 'GetTrackNode': {
      const tl = cfg(node, 'track_line', 'STATIC_TRACK_LINE');
      const tr = cfg(node, 'track', 'MAIN_TRACK');
      return "'" + tl + "." + tr + "'";
    }
    case 'OverHeatTrackNode': {
      const heatMap = {
        'OVER_HEAT': "'OVER_HEAT_TRACK'",
        'OVER_HEATING': "'OVER_HEATING_TRACK'",
        'LOOP': "'LOOP_TRACK'",
      };
      return heatMap[portName] || "'OVER_HEAT_TRACK'";
    }
    case 'SlideTrackNode': {
      return "'SLIDE_TRACK'";
    }
    case 'FindIdleTrackNode': {
      const tl = cfg(node, 'track_line', 'GUN_KICK_TRACK_LINE');
      return 'context:findIdleTrack(' + luaVal(tl) + ')';
    }

    // ── Animation mode nodes ──
    case 'LoopModeNode':
      return "'LOOP'";
    case 'PlayOnceStopNode':
      return "'PLAY_ONCE_STOP'";
    case 'PlayOnceHoldNode':
      return "'PLAY_ONCE_HOLD'";

    default:
      return 'true';
  }
}

/**
 * Resolve the expression feeding into a node's data input port by looking up
 * the connection chain.
 */
function resolveDataInput(nodeId, inputPortName, connections, nodes, visited) {
  const conn = findInput(nodeId, inputPortName, connections);
  if (!conn) return 'true';
  return generateDataExpression(conn.fromNodeId, conn.fromPort, connections, nodes, visited);
}


// ─── Exec-Flow Tracing ───────────────────────────────

/**
 * Walk an exec-flow chain starting from a given node's exec output port.
 * Returns an array of "block descriptors":
 *
 *   { type: 'action',  lines: [string] }      – simple action code
 *   { type: 'if',      condition, body, elseBody }  – conditional branch
 *   { type: 'return',  state: string }         – return to a state
 *   { type: 'custom',  lines: [string] }       – raw Lua lines
 *   { type: 'comment', text: string }          – comment
 *
 * The caller flattens these into final Lua code with proper indentation.
 */
function traceExecChain(nodeId, connections, nodes, visited) {
  if (visited.has(nodeId)) return [];
  visited.add(nodeId);

  const node = getNode(nodeId, nodes);
  if (!node) return [];
  const blocks = [];

  // Generate code for the current node
  const nodeBlocks = generateNodeExecBlock(node, connections, nodes, visited);
  blocks.push(...nodeBlocks);

  // Find nodes with '是'/'否' outputs (condition checks) – their branching is
  // handled inside generateNodeExecBlock via recursive calls.
  // For simple nodes with a single '' output, follow the chain.
  const hasBranchOutputs = node.outputs && node.outputs.some(o =>
    (o.name === '是' || o.name === '否' || o.name === '成立' || o.name === '不成立')
  );

  if (!hasBranchOutputs) {
    // Follow single exec output (port name '')
    const nextConns = findOutputs(nodeId, '', connections);
    // Only follow exec-type outputs (not data)
    for (const conn of nextConns) {
      const nextNode = getNode(conn.toNodeId, nodes);
      if (nextNode) {
        const sub = traceExecChain(conn.toNodeId, connections, nodes, visited);
        blocks.push(...sub);
      }
    }
  }

  return blocks;
}

/**
 * Generate the Lua block(s) for a single node.
 * For condition/check nodes, this generates if-else blocks.
 * For simple action nodes, this generates single lines.
 */
function generateNodeExecBlock(node, connections, nodes, visited) {
  const blocks = [];
  const nodeId = node.id;
  const type = node.type;
  const title = node.title || type;

  switch (type) {
    // ── Entry/Update/Exit – these are entry points, their action is what follows ──
    case 'EntryNode':
    case 'UpdateNode':
    case 'ExitNode':
      // These are just markers; actual behavior is in the chain after them
      blocks.push({ type: 'comment', text: '-- [' + title + ']' });
      break;

    // ── Animation control ──
    case 'RunAnimationNode': {
      const anim = cfg(node, 'animation_name', 'idle');
      const track = cfg(node, 'track', 'MAIN_TRACK');
      const blend = cfg(node, 'blend', false);
      const mode = cfg(node, 'mode', 'PLAY_ONCE_STOP');
      const blendTime = cfg(node, 'blend_time', 0.2);
      blocks.push({
        type: 'action',
        lines: ["context:runAnimation('" + escStr(anim) + "', " + luaVal(track) + ', ' + luaVal(blend) + ', ' + luaVal(mode) + ', ' + luaVal(blendTime) + ')']
      });
      break;
    }
    case 'StopAnimationNode': {
      const track = cfg(node, 'track', 'MAIN_TRACK');
      blocks.push({ type: 'action', lines: ['context:stopAnimation(' + luaVal(track) + ')'] });
      break;
    }
    case 'LoopAnimationNode': {
      const anim = cfg(node, 'animation_name', 'idle');
      const track = cfg(node, 'track', 'MOVEMENT_TRACK');
      blocks.push({ type: 'action', lines: ["context:loopAnimation('" + escStr(anim) + "', " + luaVal(track) + ')'] });
      break;
    }
    case 'SetProgressNode': {
      const track = cfg(node, 'track', 'MAIN_TRACK');
      const progress = cfg(node, 'progress', 1.0);
      const isHold = cfg(node, 'is_hold', true);
      blocks.push({ type: 'action', lines: ['context:setAnimationProgress(' + luaVal(track) + ', ' + luaVal(progress) + ', ' + luaVal(isHold) + ')'] });
      break;
    }
    case 'AdjustProgressNode': {
      const track = cfg(node, 'track', 'MAIN_TRACK');
      const delta = cfg(node, 'delta', 0.2);
      const isHold = cfg(node, 'is_hold', false);
      blocks.push({ type: 'action', lines: ['context:adjustAnimationProgress(' + luaVal(track) + ', ' + luaVal(delta) + ', ' + luaVal(isHold) + ')'] });
      break;
    }
    case 'PlayBlendedAnimationNode': {
      const anim = cfg(node, 'animation_name', 'shoot');
      const trackLine = cfg(node, 'track_line', 'GUN_KICK_TRACK_LINE');
      const blend = cfg(node, 'blend', true);
      const mode = cfg(node, 'mode', 'PLAY_ONCE_STOP');
      blocks.push({
        type: 'action',
        lines: ["context:playBlendedAnimation('" + escStr(anim) + "', " + luaVal(trackLine) + ', ' + luaVal(blend) + ', ' + luaVal(mode) + ')']
      });
      break;
    }

    // ── Action nodes ──
    case 'PopShellNode': {
      const idx = cfg(node, 'index', 0);
      blocks.push({ type: 'action', lines: ['context:popShell(' + luaVal(idx) + ')'] });
      break;
    }
    case 'TriggerNode': {
      const evt = cfg(node, 'event_name', 'INPUT_RELOAD');
      blocks.push({ type: 'action', lines: ["context:triggerEvent('" + escStr(evt) + "')"] });
      break;
    }
    case 'CustomLuaNode': {
      const code = cfg(node, 'code', '-- custom code');
      const codeLines = code.split('\n');
      blocks.push({ type: 'custom', lines: codeLines });
      break;
    }
    case 'HideCrosshairNode': {
      const hide = cfg(node, 'hide', true);
      blocks.push({ type: 'action', lines: ['context:hideCrosshair(' + luaVal(hide) + ')'] });
      break;
    }
    case 'AnchorWalkDistNode':
      blocks.push({ type: 'action', lines: ['context:anchorWalkDistance()'] });
      break;
    case 'PlayPutAwayNode': {
      const time = cfg(node, 'put_away_time', 0.5);
      blocks.push({ type: 'action', lines: ['context:playPutAwayAnimation(' + luaVal(time) + ')'] });
      break;
    }
    case 'PlayReloadNode': {
      const rtype = cfg(node, 'reload_type', 'tactical');
      blocks.push({ type: 'action', lines: ["context:playReloadAnimation('" + escStr(rtype) + "')"] });
      break;
    }
    case 'PlayInspectNode':
      blocks.push({ type: 'action', lines: ['context:playInspectAnimation()'] });
      break;
    case 'CycleMeleeNode': {
      const prefix = cfg(node, 'animation_prefix', 'melee_bayonet_');
      const ctr = cfg(node, 'counter_name', 'bayonet_counter');
      const maxC = cfg(node, 'max_count', 3);
      blocks.push({
        type: 'action',
        lines: [
          "context:cycleMeleeAnimation('" + escStr(prefix) + "', '" + escStr(ctr) + "', " + luaVal(maxC) + ')'
        ]
      });
      break;
    }
    case 'TrackHoldNode': {
      const track = cfg(node, 'track', 'MAIN_TRACK');
      blocks.push({ type: 'action', lines: ['context:holdTrack(' + luaVal(track) + ')'] });
      break;
    }

    // ── Condition check nodes (generate if-else) ──
    case 'CheckAmmoNode':
    case 'CheckAmmoCountNode':
    case 'CheckHeatNode':
    case 'CheckAimingNode':
    case 'CheckGroundNode':
    case 'CheckRunningNode':
    case 'CheckStoppedNode':
    case 'CheckShootCooldownNode':
    case 'CheckTrackIdleNode':
    case 'CheckTrackHoldingNode':
    case 'CheckWalkDirectionNode': {
      const condition = generateDataExpression(nodeId, '', connections, nodes, new Set());
      // Trace '是' (true) branch
      const trueConns = findOutputs(nodeId, '是', connections);
      const trueBody = [];
      for (const conn of trueConns) {
        const sub = traceExecChain(conn.toNodeId, connections, nodes, new Set());
        trueBody.push(...sub);
      }
      // Trace '否' (false) branch
      const falseConns = findOutputs(nodeId, '否', connections);
      const falseBody = [];
      for (const conn of falseConns) {
        const sub = traceExecChain(conn.toNodeId, connections, nodes, new Set());
        falseBody.push(...sub);
      }
      blocks.push({
        type: 'if',
        condition: condition,
        body: trueBody,
        elseBody: falseBody
      });
      break;
    }

    // ── IfNode (data-driven branching) ──
    case 'IfNode': {
      // Resolve condition expression from '条件' data input
      const condExpr = resolveDataInput(nodeId, '条件', connections, nodes, new Set());
      // Trace '成立' branch
      const trueConns = findOutputs(nodeId, '成立', connections);
      const trueBody = [];
      for (const conn of trueConns) {
        const sub = traceExecChain(conn.toNodeId, connections, nodes, new Set());
        trueBody.push(...sub);
      }
      // Trace '不成立' branch
      const falseConns = findOutputs(nodeId, '不成立', connections);
      const falseBody = [];
      for (const conn of falseConns) {
        const sub = traceExecChain(conn.toNodeId, connections, nodes, new Set());
        falseBody.push(...sub);
      }
      blocks.push({
        type: 'if',
        condition: condExpr,
        body: trueBody,
        elseBody: falseBody
      });
      break;
    }

    // ── ReturnNode ──
    case 'ReturnNode': {
      const stateName = cfg(node, 'state_name', 'idle');
      blocks.push({ type: 'return', state: stateName });
      break;
    }

    // ── Math / Logic nodes (pure data, no exec effect) ──
    case 'AddNode':
    case 'SubtractNode':
    case 'MultiplyNode':
    case 'DivideNode':
    case 'AndNode':
    case 'OrNode':
    case 'NotNode':
    case 'CompareNode':
      blocks.push({ type: 'comment', text: '-- ' + title + ' (data node, evaluated inline)' });
      break;

    // ── Input event nodes (serve as graph entry points, generate comments) ──
    case 'DrawNode':
    case 'ShootNode':
    case 'ReloadNode':
    case 'InspectNode':
    case 'BoltNode':
    case 'AimNode':
    case 'RunNode':
    case 'WalkNode':
    case 'BayonetMuzzleNode':
    case 'BayonetStockNode':
    case 'BayonetPushNode':
    case 'PutAwayNode':
    case 'IdleInputNode':
    case 'FireSelectNode':
    case 'SprintNode':
    case 'SlideNode':
    case 'BoltCaughtNode':
    case 'BoltNormalNode':
    case 'OverHeatNode':
    case 'CoolingHeatNode':
    case 'InspectRetreatNode':
    case 'AimRetreatNode':
    case 'SpinNode':
      blocks.push({ type: 'comment', text: '-- input event: ' + title });
      break;

    // ── Track system nodes (data-only, handled inline) ──
    case 'TrackNode':
    case 'TrackLineNode':
    case 'GetTrackNode':
    case 'OverHeatTrackNode':
    case 'SlideTrackNode':
    case 'FindIdleTrackNode':
    case 'LoopModeNode':
    case 'PlayOnceStopNode':
    case 'PlayOnceHoldNode':
      break;

    // ── State definition nodes ──
    case 'StateDefineNode':
    case 'TransitionNode':
      break;

    default:
      blocks.push({ type: 'comment', text: '-- TODO: ' + title });
  }

  return blocks;
}


// ─── Block-to-Lua Flattener ──────────────────────────

/**
 * Recursively flatten block descriptors into an array of Lua code lines.
 *
 * @param {Array} blocks
 * @param {number} indent  Current indentation level (in 2-space units)
 * @param {Array} lines    Output array being accumulated
 */
function flattenBlocks(blocks, indent, lines) {
  const pad = '  '.repeat(indent);
  for (const block of blocks) {
    switch (block.type) {
      case 'action':
        for (const line of block.lines) {
          lines.push(pad + line);
        }
        break;
      case 'custom':
        for (const line of block.lines) {
          lines.push(pad + line);
        }
        break;
      case 'comment':
        lines.push(pad + block.text);
        break;
      case 'return':
        lines.push(pad + "return '" + escStr(block.state) + "'");
        break;
      case 'if': {
        lines.push(pad + 'if ' + block.condition + ' then');
        if (block.body && block.body.length > 0) {
          flattenBlocks(block.body, indent + 1, lines);
        } else {
          lines.push(pad + '  -- no actions');
        }
        if (block.elseBody && block.elseBody.length > 0) {
          lines.push(pad + 'else');
          flattenBlocks(block.elseBody, indent + 1, lines);
        }
        lines.push(pad + 'end');
        break;
      }
    }
  }
}


// ─── Graph Analysis ──────────────────────────────────

/**
 * Analyze the node/connection graph and return a structured summary.
 */
function analyzeGraph(nodes, connections) {
  const states = [];          // { name, entryNode, updateNode, exitNode, entryBlocks, updateBlocks, exitBlocks }
  const transitions = [];     // { from_state, to_state, condition, nodeId }
  const trackNodes = [];      // TrackNode instances
  const trackLineNodes = [];  // TrackLineNode instances

  // Group EntryNode / UpdateNode / ExitNode by state_name
  const entryByState = {};
  const updateByState = {};
  const exitByState = {};

  for (const node of nodes) {
    switch (node.type) {
      case 'EntryNode': {
        const sn = cfg(node, 'state_name', 'idle');
        if (!entryByState[sn]) entryByState[sn] = [];
        entryByState[sn].push(node);
        break;
      }
      case 'UpdateNode': {
        const sn = cfg(node, 'state_name', 'idle');
        if (!updateByState[sn]) updateByState[sn] = [];
        updateByState[sn].push(node);
        break;
      }
      case 'ExitNode': {
        const sn = cfg(node, 'state_name', 'idle');
        if (!exitByState[sn]) exitByState[sn] = [];
        exitByState[sn].push(node);
        break;
      }
      case 'TransitionNode':
        transitions.push({
          from_state: cfg(node, 'from_state', 'idle'),
          to_state: cfg(node, 'to_state', 'idle'),
          condition: cfg(node, 'condition', ''),
          nodeId: node.id
        });
        break;
      case 'TrackNode':
        trackNodes.push(node);
        break;
      case 'TrackLineNode':
        trackLineNodes.push(node);
        break;
    }
  }

  // Collect all unique state names
  const allStateNames = new Set();
  for (const node of nodes) {
    if (node.type === 'EntryNode' || node.type === 'UpdateNode' || node.type === 'ExitNode') {
      allStateNames.add(cfg(node, 'state_name', 'idle'));
    }
  }
  // Also add states referenced by TransitionNode
  for (const t of transitions) {
    allStateNames.add(t.from_state);
    allStateNames.add(t.to_state);
  }
  // Also add states from ReturnNode
  for (const node of nodes) {
    if (node.type === 'ReturnNode') {
      allStateNames.add(cfg(node, 'state_name', 'idle'));
    }
  }

  for (const name of allStateNames) {
    states.push({
      name: name,
      entryNodes: entryByState[name] || [],
      updateNodes: updateByState[name] || [],
      exitNodes: exitByState[name] || [],
    });
  }

  return { states, transitions, trackNodes, trackLineNodes };
}


// ─── Code Generation Sections ────────────────────────

function genHeader() {
  const lines = [];
  lines.push('-- TACZ Lua State Machine');
  lines.push('-- Generated by NodeForge Web Editor');
  lines.push('');
  lines.push('---@type TACZStateMachine');
  lines.push('local M = {}');
  lines.push('');
  return lines;
}

function genTrackDefs(analysis) {
  const lines = [];
  lines.push('-- Track definitions');
  lines.push('M.trackLines = {');
  lines.push('    STATIC_TRACK_LINE = {');
  lines.push('        BASE_TRACK = {},');
  lines.push('        BOLT_CAUGHT_TRACK = {},');
  lines.push('        ADS_TRACK = {},');
  lines.push('        MAIN_TRACK = {},');
  lines.push('    },');
  lines.push('    GUN_KICK_TRACK_LINE = {},');
  lines.push('    BLENDING_TRACK_LINE = {},');
  lines.push('}');
  lines.push('');
  return lines;
}

function genStateTable(analysis) {
  const lines = [];
  const stateNames = analysis.states.map(s => s.name);

  lines.push('-- State table');
  lines.push('M.states = {');
  for (const name of stateNames) {
    lines.push('    "' + escStr(name) + '",');
  }
  lines.push('}');
  lines.push('');
  return lines;
}

function genInit() {
  const lines = [];
  lines.push('-- Initialize');
  lines.push('function M:init()');
  lines.push('end');
  lines.push('');
  return lines;
}

function genOnUpdate() {
  const lines = [];
  lines.push('-- Per-frame update');
  lines.push('function M:onUpdate()');
  lines.push('end');
  lines.push('');
  return lines;
}

/**
 * Generate M:onStateEntry(stateName) handling all states.
 */
function genStateEntry(analysis, connections, nodes) {
  const lines = [];
  lines.push('-- State entry logic');
  lines.push('function M:onStateEntry(stateName)');
  lines.push('    if stateName == nil then return end');

  for (const state of analysis.states) {
    if (state.entryNodes.length === 0) continue;

    lines.push('');
    lines.push('    if stateName == ' + luaVal(state.name) + ' then');

    for (const entryNode of state.entryNodes) {
      const blocks = traceExecChain(entryNode.id, connections, nodes, new Set());
      if (blocks.length > 0) {
        flattenBlocks(blocks, 3, lines);
      }
    }

    lines.push('        return');
    lines.push('    end');
  }

  lines.push('end');
  lines.push('');
  return lines;
}

/**
 * Generate M:onStateUpdate(stateName) handling all states.
 */
function genStateUpdate(analysis, connections, nodes) {
  const lines = [];
  lines.push('-- State update logic');
  lines.push('function M:onStateUpdate(stateName)');
  lines.push('    if stateName == nil then return end');

  for (const state of analysis.states) {
    if (state.updateNodes.length === 0) continue;

    lines.push('');
    lines.push('    if stateName == ' + luaVal(state.name) + ' then');

    for (const updateNode of state.updateNodes) {
      const blocks = traceExecChain(updateNode.id, connections, nodes, new Set());
      if (blocks.length > 0) {
        flattenBlocks(blocks, 3, lines);
      }
    }

    lines.push('        return');
    lines.push('    end');
  }

  lines.push('end');
  lines.push('');
  return lines;
}

/**
 * Generate M:onStateExit(stateName) handling all states.
 */
function genStateExit(analysis, connections, nodes) {
  const lines = [];
  lines.push('-- State exit logic');
  lines.push('function M:onStateExit(stateName)');
  lines.push('    if stateName == nil then return end');

  for (const state of analysis.states) {
    if (state.exitNodes.length === 0) continue;

    lines.push('');
    lines.push('    if stateName == ' + luaVal(state.name) + ' then');

    for (const exitNode of state.exitNodes) {
      const blocks = traceExecChain(exitNode.id, connections, nodes, new Set());
      if (blocks.length > 0) {
        flattenBlocks(blocks, 3, lines);
      }
    }

    lines.push('        return');
    lines.push('    end');
  }

  lines.push('end');
  lines.push('');
  return lines;
}

/**
 * Generate M:transition(stateName, input) with all transition rules.
 */
function genTransition(analysis, connections, nodes) {
  const lines = [];
  lines.push('-- Transition logic');
  lines.push('function M:transition(stateName, input)');
  lines.push('    if stateName == nil then return nil end');

  if (analysis.transitions.length === 0) {
    lines.push('    return nil');
    lines.push('end');
    lines.push('');
    return lines;
  }

  // Group transitions by from_state
  const byFromState = {};
  for (const t of analysis.transitions) {
    if (!byFromState[t.from_state]) byFromState[t.from_state] = [];
    byFromState[t.from_state].push(t);
  }

  lines.push('');
  for (const [fromState, trans] of Object.entries(byFromState)) {
    lines.push('    if stateName == ' + luaVal(fromState) + ' then');

    // Find the TransitionNode's exec chain to build the transition body
    for (const t of trans) {
      const transNode = getNode(t.nodeId, nodes);
      if (!transNode) continue;

      // Check if there's a condition data input connected
      const condConn = findInput(t.nodeId, '条件', connections);
      let conditionExpr = null;
      if (condConn) {
        conditionExpr = generateDataExpression(condConn.fromNodeId, condConn.fromPort, connections, nodes, new Set());
      }

      // Check for exec chain after transition node (follow '' output)
      const execBlocks = traceExecChain(t.nodeId, connections, nodes, new Set());

      if (conditionExpr) {
        lines.push('        if ' + conditionExpr + ' then');
        if (execBlocks.length > 0) {
          flattenBlocks(execBlocks, 4, lines);
        } else {
          lines.push("            return '" + escStr(t.to_state) + "'");
        }
        lines.push('        end');
      } else {
        // No condition: always transition
        if (execBlocks.length > 0) {
          lines.push('        -- transition: ' + fromState + ' -> ' + t.to_state);
          flattenBlocks(execBlocks, 3, lines);
        } else {
          lines.push("        return '" + escStr(t.to_state) + "'");
        }
      }
    }

    lines.push('    end');
    lines.push('');
  }

  lines.push('    return nil');
  lines.push('end');
  lines.push('');
  return lines;
}


// ─── Main Export ─────────────────────────────────────

/**
 * Generate complete TACZ Lua state machine code from a node graph.
 *
 * @param {Array}  nodes       Array of node objects (from NodeRegistry.createNode)
 * @param {Array}  connections Array of connection objects { fromNodeId, fromPort, toNodeId, toPort }
 * @returns {string}           Formatted Lua source code
 */
function generateCode(nodes, connections) {
  const analysis = analyzeGraph(nodes, connections);

  const allLines = [
    ...genHeader(),
    ...genTrackDefs(analysis),
    ...genStateTable(analysis),
    ...genInit(),
    ...genOnUpdate(),
    ...genStateEntry(analysis, connections, nodes),
    ...genStateUpdate(analysis, connections, nodes),
    ...genStateExit(analysis, connections, nodes),
    ...genTransition(analysis, connections, nodes),
    'return M',
    '',
  ];

  return allLines.join('\n');
}
