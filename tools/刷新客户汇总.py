# 从 客户/*.md 卡片重新同步客户汇总表（2026-11-19 整理）
# 用法：python3 tools/刷新客户汇总.py
# 做的事：以卡片为准更新"全部客户"每一行（阶段、下一步日期、下一步、用途、尺寸、目的港、已报价、最近联系、最近记录、沉默原因），
#        卡片有但表里没有的客户追加到末尾，重建"紧急待办"表，另存为 客户汇总_分类版_<今天>.xlsx 并删除旧版。
# 运行前请在 Excel 里关掉汇总表。
# ⭐ 重点关注：卡片阶段里带"重点关注"（如 已报价（⭐重点关注））→ 分类为 ⭐ 重点关注；"全部客户"行顺序保持不变，所以置顶的客户会一直在第 2 行。
import openpyxl, re, datetime, os
from copy import copy
from pathlib import Path
D=Path(__file__).resolve().parent.parent/'客户'
today=datetime.date.today()
files=sorted(D.glob('客户汇总_分类版_*.xlsx'))
src=files[-1]
wb=openpyxl.load_workbook(src); ws=wb['全部客户']

def parse(p):
    t=p.read_text(encoding='utf-8').split('\n')
    c={'recs':[]}
    h=t[0].lstrip('# ').split(' | ')
    c['name']=h[0].strip(); c['country']=h[1].strip() if len(h)>1 else ''
    c['wa']=h[2].replace('WhatsApp','').strip() if len(h)>2 else ''
    for l in t:
        if l.startswith('阶段：'): c['stage']=l[3:].strip()
        elif l.startswith('已报价：'): c['quoted']=l[4:].strip()
        elif l.startswith('沉默原因：'): c['reason']=l[5:].strip()
        elif l.startswith('来源：'):
            m=re.match(r'来源：(.*?)\s*首次联系：(\S*)',l)
            if m: c['src'],c['first']=m.group(1).strip(),m.group(2)
        elif l.startswith('下一步：'):
            m=re.match(r'下一步：(\d{4}-\d{2}-\d{2})?\s*(.*)',l); c['next'],c['todo']=m.group(1),m.group(2).strip()
        elif l.startswith('需求：'):
            for k,key in (('用途','use'),('尺寸','size'),('目的港','port')):
                m=re.search(k+r' ([^|]*)',l); c[key]=m.group(1).strip() if m else ''
        elif l.startswith('- ') and re.match(r'- \d{1,2}-\d',l): c['recs'].append(l[2:].strip())
    return c

def d(s):
    try: return datetime.datetime.fromisoformat(s)
    except Exception: return None

def lastdate(recs):
    for r in reversed(recs):
        m=re.match(r'(\d{1,2})-(\d{1,2})',r)
        if m:
            try: return datetime.datetime(2026,int(m.group(1)),int(m.group(2)))
            except ValueError: pass
    return None

cards={p.name:p for p in D.glob('*.md') if p.name not in ('客户列表.md','_模板.md')}
seen=set(); last=1
for r in range(2,ws.max_row+1):
    f=ws.cell(r,18).value
    if not f: continue
    last=r
    if f not in cards: continue
    seen.add(f); c=parse(cards[f])
    if c.get('stage'): ws.cell(r,5).value=c['stage']
    if c.get('next') and d(c['next']): ws.cell(r,6).value=d(c['next'])
    if c.get('todo') is not None: ws.cell(r,8).value=c.get('todo')
    for col,key in ((9,'use'),(10,'size'),(11,'port'),(12,'quoted')):
        if c.get(key): ws.cell(r,col).value=c[key]
    if c.get('country') and c['country']!='？': ws.cell(r,3).value=c['country']
    ld=lastdate(c['recs'])
    if ld: ws.cell(r,15).value=ld
    if c['recs']: ws.cell(r,16).value='\n'.join(c['recs'][-3:])
    if c.get('reason'): ws.cell(r,19).value=c['reason']
added=0
for f,p in sorted(cards.items()):
    if f in seen: continue
    c=parse(p); r=last+1; last=r; added+=1
    for col in range(1,20): ws.cell(r,col)._style=copy(ws.cell(2,col)._style)
    ws.cell(r,1).value=f'=IF(ISNUMBER(SEARCH("重点关注",E{r})),"⭐ 重点关注",IF(E{r}="流失","⚫ 流失/非客户",IF(ISNUMBER(SEARCH("⚠",H{r})),"🔴 紧急待办",IF(E{r}="待付款","🟠 待付款",IF(F{r}="","⚪ 稍后/低频",IF(F{r}<=TODAY(),"🟡 今天该跟进",IF(F{r}-TODAY()<=3,"🟢 3天内跟进","⚪ 稍后/低频")))))))'
    vals={2:c['name'],3:c.get('country',''),4:'英语',5:c.get('stage',''),6:d(c.get('next') or ''),7:f'=IF(F{r}="","",F{r}-TODAY())',8:c.get('todo',''),9:c.get('use',''),10:c.get('size',''),11:c.get('port',''),12:c.get('quoted',''),13:c.get('src',''),14:d(c.get('first') or ''),15:lastdate(c['recs']),16:'\n'.join(c['recs'][-3:]),17:c.get('wa',''),18:f,19:c.get('reason','')}
    for col,v in vals.items(): ws.cell(r,col).value=v
# 看板统计范围
for row in wb['看板'].iter_rows():
    for cell in row:
        if isinstance(cell.value,str): cell.value=re.sub(r'\$A\$2:\$A\$\d+|\$E\$2:\$E\$\d+|\$D\$2:\$D\$\d+',lambda m:m.group(0).rsplit('$',1)[0]+'$2000',cell.value)
# 重建紧急待办
uw=wb['紧急待办']
for r in range(4,uw.max_row+1):
    for col in range(1,8): uw.cell(r,col).value=None
items=[]
for r in range(2,last+1):
    nm=ws.cell(r,2).value
    if not nm: continue
    todo=str(ws.cell(r,8).value or ''); st=ws.cell(r,5).value
    if st in ('流失','成交'): continue
    if '重点关注' in str(st): cat='⭐ 重点关注'
    elif '⚠' in todo: cat='🔴 紧急待办'
    elif st=='待付款': cat='🟠 待付款'
    else: continue
    items.append((cat,nm,ws.cell(r,3).value,ws.cell(r,4).value,todo,ws.cell(r,12).value,ws.cell(r,17).value))
items.sort(key=lambda x:({'⭐ 重点关注':0,'🔴 紧急待办':1}.get(x[0],2),str(x[1])))
for i,it in enumerate(items):
    for col,v in enumerate(it,1):
        uw.cell(4+i,col).value=v
        if 4+i>4: uw.cell(4+i,col)._style=copy(uw.cell(4,col)._style)
uw.cell(1,1).value=f'紧急待办 + 待付款（{len(items)} 个，生成于 {today.isoformat()}；处理完后改客户卡片"下一步"，再运行 tools/刷新客户汇总.py）'
out=D/f'客户汇总_分类版_{today.isoformat()}.xlsx'
wb.save(out)
for f in files:
    if f!=out: f.unlink()
print('saved',out.name,'| 新增',added,'| 紧急待办+待付款',len(items))
