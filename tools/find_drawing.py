# 按款式和尺寸查尺寸图：python3 tools/find_drawing.py <系列或款式> <宽x长> [--eave 4]
# 例：python3 tools/find_drawing.py Atrium 20x30
# 输出：✅ 唯一匹配 / ⚠ 有匹配但需要人工确认 / ❌ 没有，需要问用户
import csv, sys, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, 'Tent 建构图', '_索引.csv')
SERIES = {'classic':'A-Frame','wedding':'A-Frame','transparent':'A-Frame','exhibition':'A-Frame','a-frame':'A-Frame',
          'a-shape':'A-Frame','铝合金':'A-Frame','人字顶':'A-Frame','atrium':'Atrium','中庭':'Atrium',
          'dome':'Dome','球形':'Dome','polygon':'Polygon','多边形':'Polygon','pagoda':'Pagoda','塔篷':'Pagoda'}
a = sys.argv[1:]
if len(a) < 2: sys.exit(__doc__ or '用法：find_drawing.py <款式> <宽x长> [--eave N]')
style = SERIES.get(a[0].lower())
m = re.match(r'(\d+(?:\.\d+)?)\s*[xX*×]\s*(\d+(?:\.\d+)?)', a[1])
eave = a[a.index('--eave')+1] if '--eave' in a else None
if not style: sys.exit(f'❌ 款式「{a[0]}」没有对应的尺寸图分类（如 Curved 弧形），请问用户要用哪张图')
W, L = float(m.group(1)), float(m.group(2))
rows = list(csv.DictReader(open(IDX, encoding='utf-8-sig')))
hit = [r for r in rows if r['款式']==style and float(r['宽m'])==W and float(r['长m'])==L]
want = float(eave) if eave else (3.0 if W < 15 else 4.0)   # 默认边高：kb/产品/通用规格.md
eave_note = ''
same = [r for r in hit if not r['边高m'] or float(r['边高m']) == want]
if hit and not same:
    eave_note = f"没有边高 {want:g} m 的图，只有边高 " + '/'.join(sorted({r['边高m'] for r in hit})) + ' m'
    if eave: hit = []
else:
    hit = same
if not hit:
    same_w = sorted({int(float(r['长m'])) for r in rows if r['款式']==style and float(r['宽m'])==W})
    sys.exit(f'❌ 没有 {style} {W:g}x{L:g}m 的尺寸图，需要问用户。同跨度已有长度：{same_w or "无"}')
hit.sort(key=lambda r: (r['版式']!='截面平面图', '⚠' in r['顶高公式核对'], '结构简图' in r['文件']))
best = hit[0]
warn = []
if '⚠' in best['顶高公式核对']: warn.append('图上顶高和公式不一致：'+best['顶高公式核对'])
if not best['顶高m']: warn.append('索引里没有这张图的边高顶高（旧版三视图或标题缺失），要人工核对图上数字')
if eave_note: warn.append(eave_note)
if len(hit) > 1: warn.append('同尺寸还有：' + '；'.join(r['文件'] for r in hit[1:]))
flag = '⚠' if ('⚠' in best['顶高公式核对'] or eave_note or not best['顶高m']) else '✅'
print(f"{flag} {os.path.join('Tent 建构图', best['文件'])}  边高 {best['边高m'] or '?'} m / 顶高 {best['顶高m'] or '?'} m")
for w in warn: print('   - ' + w)
