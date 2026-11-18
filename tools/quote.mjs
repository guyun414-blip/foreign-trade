#!/usr/bin/env node
// 篷房报价计算器：读取 kb/价格/*.csv，输出一份很短的报价草稿，供 Claude 回复客户时使用。
// 用法：
//   node tools/quote.mjs 铝合金 20x50
//   node tools/quote.mjs 铝合金 10x30 --qty 2 --transparent --addon 玻璃墙=60 --addon 双开玻璃门=2
//   node tools/quote.mjs 塔篷 6x6 --qty 4
//   node tools/quote.mjs 钢铝 12x24 --floor      # 显示底价（仅内部，绝不发给客户）
//   node tools/quote.mjs --spans                 # 列出各类型可报跨度
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const P = (...p) => path.join(ROOT, 'kb', '价格', ...p);

function readCsv(file) {
  const text = fs.readFileSync(file, 'utf8').replace(/^﻿+/, ''); // Excel 存的 CSV 带 BOM
  const [head, ...lines] = text.split(/\r?\n/).filter((l) => l.trim());
  const keys = head.split(',');
  return lines.map((l) => {
    const cells = l.split(',');
    return Object.fromEntries(keys.map((k, i) => [k, (cells[i] ?? '').trim()]));
  });
}

const cfg = JSON.parse(fs.readFileSync(P('参数.json'), 'utf8'));
const RATE = cfg['汇率_CNY_per_USD'];
const rows = readCsv(P('篷房价格表.csv'));
const addons = readCsv(P('配件价格.csv'));

const TYPE_ALIAS = {
  铝合金: '铝合金', 铝: '铝合金', alu: '铝合金', aluminum: '铝合金', aluminium: '铝合金', a: '铝合金',
  classic: '铝合金', wedding: '铝合金', exhibition: '铝合金', transparent: '铝合金', 'a-shape': '铝合金',
  钢铝: '钢铝', steel: '钢铝',
  塔篷: '塔篷', 塔: '塔篷', pagoda: '塔篷',
};

// ---- 参数解析 ----
const argv = process.argv.slice(2);
const opts = { qty: 1, transparent: false, floor: false, addons: [] };
const pos = [];
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--qty') opts.qty = Number(argv[++i]);
  else if (a === '--transparent' || a === '--clear') opts.transparent = true;
  else if (a === '--floor') opts.floor = true;
  else if (a === '--addon') opts.addons.push(argv[++i]);
  else if (a === '--spans') opts.spans = true;
  else if (a === '--json') opts.json = true;
  else pos.push(a);
}

const usd = (cny) => cny / RATE;
const f2 = (n) => n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const out = [];
const warn = [];

if (opts.spans) {
  for (const t of ['铝合金', '钢铝', '塔篷']) {
    const spans = [...new Set(rows.filter((r) => r['类型'] === t).map((r) => Number(r['跨度m'])))];
    const alias = cfg['跨度同价规则'][t];
    const extra = alias ? Object.entries(alias).map(([a, b]) => `${a}(同${b})`) : [];
    console.log(`${t}: ${spans.join(', ')}${extra.length ? ' | ' + extra.join(', ') : ''}`);
  }
  process.exit(0);
}

const type = TYPE_ALIAS[(pos[0] || '').toLowerCase()];
const m = (pos[1] || '').match(/^(\d+(?:\.\d+)?)\s*[x*×X]\s*(\d+(?:\.\d+)?)$/);
if (!type || !m) {
  console.log('用法: node tools/quote.mjs <铝合金|钢铝|塔篷> <宽x长> [--qty N] [--transparent] [--addon 名称=数量] [--floor] | --spans');
  process.exit(1);
}
const W = Number(m[1]);
const L = Number(m[2]);
const lookupSpan = cfg['跨度同价规则'][type]?.[String(W)] ?? W;
if (lookupSpan !== W) warn.push(`${W}米跨按${lookupSpan}米跨价格计（价格表规则）`);

const pool = rows.filter((r) => r['类型'] === type && Number(r['跨度m']) === lookupSpan);
if (!pool.length) {
  console.log(`❌ 价格表没有【${type} ${W}米跨】→ 需人工报价。可用 --spans 查看可报跨度。`);
  process.exit(2);
}

// ---- 匹配价格行 ----
let row = pool.find((r) => Number(r['长度m']) === L);
let matchNote = '精确匹配';
if (!row) {
  if (type === '塔篷') {
    console.log(`❌ 塔篷没有 ${W}x${L} 标准尺寸 → 需人工报价。`);
    process.exit(2);
  }
  const perM2 = pool.filter((r) => r['计价单位'] === '㎡').sort((a, b) => a['长度m'] - b['长度m']);
  const lower = perM2.filter((r) => Number(r['长度m']) <= L);
  if (lower.length) {
    row = lower[lower.length - 1];
    matchNote = `表中无${L}米长，按较短档 ${lookupSpan}x${row['长度m']} 计（单价偏高，较稳妥）`;
    if (row === perM2[perM2.length - 1] && L > Number(row['长度m'])) matchNote = `超出表中最长档，按 ${lookupSpan}x${row['长度m']} 计`;
  } else {
    row = perM2[0];
    matchNote = `短于表中最短档，按 ${lookupSpan}x${row['长度m']} 计 —— 短篷房通常更贵，建议人工确认`;
    warn.push('长度短于价格表最短档');
  }
}

const unit = row['计价单位'];
let quoteCny = Number(row['报价CNY']);
const floorCny = row['底价CNY'] ? Number(row['底价CNY']) : null;
if (!quoteCny) {
  console.log(`❌ ${type} ${W}x${L} 没有对外报价 → 需人工定价。`);
  process.exit(2);
}
let transAdd = 0;
if (opts.transparent) {
  transAdd = cfg['透明加价_CNY_per_m2'];
  if (unit === '㎡') quoteCny += transAdd;
  else warn.push('套价产品的透明加价未自动计算，需人工确认');
}

const area = W * L;
const eave = Number(row['边高m']) || (W >= 15 ? 4 : 3);
// 跨度借用别的跨度价格时，表里的顶高不适用，改用公式
const tableRidge = lookupSpan === W ? Number(row['顶高m']) : 0;
const ridge = tableRidge || +(W * 0.5 * (W >= 15 ? 0.31 : 0.36) + eave).toFixed(2);
const ridgeSrc = tableRidge ? '价格表' : '公式';
const bay = lookupSpan === 10 ? 3 : 5; // 10米跨常规3米开间，其余按模板常规5米

let subtotalUsd;
out.push(`【报价草稿·内部】${type === '塔篷' ? '塔篷' : type + '篷房'} ${W}x${L}m × ${opts.qty}  （${matchNote}）`);
out.push(`主型材 ${row['主型材'] || '未注明'} | 边高 ${eave}m | 顶高 ${ridge}m(${ridgeSrc}) | 开间 ${bay}m(常规)`);
if (unit === '㎡') {
  const unitUsd = usd(quoteCny);
  subtotalUsd = unitUsd * area * opts.qty;
  out.push(`单价 ${quoteCny} CNY/㎡${transAdd ? `(含透明+${transAdd})` : ''} → $${f2(unitUsd)}/㎡  (汇率 ${RATE})`);
  out.push(`面积 ${area}㎡ × ${opts.qty} = ${area * opts.qty}㎡ → 小计 $${f2(subtotalUsd)}`);
} else {
  subtotalUsd = usd(quoteCny) * opts.qty;
  out.push(`单价 ${quoteCny} CNY/套 → $${f2(usd(quoteCny))}/set × ${opts.qty} → 小计 $${f2(subtotalUsd)}`);
}

// ---- 配件 ----
let addonUsd = 0;
const addonLines = [];
for (const a of opts.addons) {
  const [name, q] = a.split('=');
  const qty = Number(q || 1);
  const item = addons.find((x) => x['配件'].startsWith(name));
  if (!item) { warn.push(`配件「${name}」不在配件价格表 → 人工报价`); continue; }
  const pUsd = item['报价USD'] ? Number(item['报价USD']) : item['报价CNY'] ? usd(Number(item['报价CNY'])) : null;
  if (pUsd == null) { warn.push(`配件「${item['配件']}」没有对外报价（${item['备注']}）→ 人工定价`); continue; }
  addonUsd += pUsd * qty;
  addonLines.push({ name: item['配件'], nameEn: item['英文名'] || item['配件'], spec: item['规格'] || '', unit: item['计价单位'], qty, unitUsd: +pUsd.toFixed(2) });
  out.push(`+ ${item['配件']} ${qty}${item['计价单位']} × $${f2(pUsd)} = $${f2(pUsd * qty)}`);
}
if (addonUsd) out.push(`合计 $${f2(subtotalUsd + addonUsd)}`);

// ---- 估算重量体积 ----
const totalArea = area * opts.qty;
out.push(`估算 重量≈${(totalArea / 100 * cfg['重量估算_吨_per_100m2']).toFixed(2)}t  体积≈${(totalArea / 100 * cfg['体积估算_CBM_per_100m2']).toFixed(1)}CBM（粗估，发前确认）`);

if (row['备注']) warn.push(`价格表备注：${row['备注']}`);
const disc = cfg['数量优惠_仅内部参考'][type];
if (disc) out.push(`可让价空间(内部)：${disc}`);
if (opts.floor) {
  out.push(`🔒 底价：${floorCny ?? '无'}${floorCny ? ` CNY/${unit} → $${f2(usd(floorCny))}` : ''}  —— 仅供你本人参考，禁止写进给客户的消息`);
}
if (warn.length) out.push('⚠ ' + warn.join('；'));

if (opts.json) {
  // 供 tools/pi.ps1 等程序调用；不含底价（除非 --floor）
  const res = {
    type, width: W, length: L, qty: opts.qty, unit, transparent: opts.transparent,
    unitCny: quoteCny, rate: RATE, unitUsd: +usd(quoteCny).toFixed(2),
    area, subtotalUsd: +subtotalUsd.toFixed(2), addons: addonLines, totalUsd: +(subtotalUsd + addonUsd).toFixed(2),
    profile: row['主型材'], eave, ridge, bay,
    weightT: +(totalArea / 100 * cfg['重量估算_吨_per_100m2']).toFixed(2),
    cbm: +(totalArea / 100 * cfg['体积估算_CBM_per_100m2']).toFixed(1),
    match: matchNote, warnings: warn,
  };
  if (opts.floor) res.floorCny = floorCny;
  console.log(JSON.stringify(res));
} else {
  console.log(out.join('\n'));
}
