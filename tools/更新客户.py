# 批量更新客户卡片 + 客户列表.md + 客户汇总表（2026-11-19 会话整理）
# 用法：python3 tools/更新客户.py updates.json
# updates.json 是一个列表，每项：
#   key   客户在汇总表"客户"列/客户列表里的唯一片段（如 "Thobeka"、"+243 814 444 612"）
#   card  卡片文件名（客户/ 下）
#   stage 阶段；next 下一步日期 YYYY-MM-DD；todo 下一步（带 ⚠ 会进"紧急待办"）；rec 记录一行（≤20 字，带日期）
#   可选：quoted 已报价字段；country 国家；port 目的港；reason 沉默原因（写进卡片和汇总表"沉默原因"列）
# 注意：汇总表要先在 Excel 里关掉再运行。
import openpyxl, re, datetime, sys, json, shutil
from pathlib import Path
D=Path(__file__).resolve().parent.parent/'客户'
ups=json.load(open(sys.argv[1]))
today=datetime.date.today().isoformat()
# cards + list
lst=(D/'客户列表.md').read_text(encoding='utf-8').split('\n')
for u in ups:
    c=D/u['card']; t=c.read_text(encoding='utf-8').split('\n')
    for i,l in enumerate(t):
        if l.startswith('阶段：'): t[i]='阶段：'+u['stage']
        if l.startswith('已报价：') and u.get('quoted'): t[i]='已报价：'+u['quoted']
        if l.startswith('下一步：'): t[i]='下一步：'+u['next']+' '+u['todo']
        if i==0 and u.get('country'): parts=l.split(' | '); parts[1]=u['country']; t[i]=' | '.join(parts)
        if l.startswith('需求：') and u.get('port'): t[i]=re.sub(r'目的港 [^|]*',f"目的港 {u['port']} ",l)
    if u.get('reason'):
        t=[l for l in t if not l.startswith('沉默原因：')]
        i=[k for k,l in enumerate(t) if l.startswith('下一步：')][0]; t.insert(i+1,'沉默原因：'+u['reason'])
    while t and t[-1]=='': t.pop()
    t.append('- '+u['rec']); c.write_text('\n'.join(t)+'\n',encoding='utf-8')
    for i,l in enumerate(lst):
        if l.startswith('| ') and u['key'] in l.split('|')[1]:
            p=l.split('|'); p[3]=f" {u['stage']} "; p[4]=f" {today} "; p[5]=f" {u['next']} "; p[6]=f" {u['todo']} "
            if u.get('country'): p[2]=f" {u['country']} "
            lst[i]='|'.join(p)
(D/'客户列表.md').write_text('\n'.join(lst),encoding='utf-8')
# xlsx
f=sorted(D.glob('客户汇总_分类版_*.xlsx'))[-1]
wb=openpyxl.load_workbook(f); ws=wb['全部客户']; uw=wb['紧急待办']
for u in ups:
    hit=0
    for r in range(2,ws.max_row+1):
        if u['key'] in str(ws.cell(r,2).value):
            hit+=1
            ws.cell(r,5).value=u['stage']; ws.cell(r,6).value=datetime.datetime.fromisoformat(u['next']); ws.cell(r,8).value=u['todo']
            ws.cell(r,15).value=datetime.datetime.fromisoformat(today)
            ws.cell(r,16).value=(str(ws.cell(r,16).value or '')+'\n'+u['rec']).strip()
            if u.get('country'): ws.cell(r,3).value=u['country']
            if u.get('port'): ws.cell(r,11).value=u['port']
            if u.get('reason'): ws.cell(r,19).value=u['reason']
            if u.get('quoted'): ws.cell(r,12).value=u['quoted']
    for r in range(4,uw.max_row+1):
        if u['key'] in str(uw.cell(r,2).value):
            uw.cell(r,1).value='✅ 已处理 11-18'; uw.cell(r,5).value=u['todo']+'（下次 '+u['next'][5:]+'）'
    print(u['key'],'rows',hit)
wb.save(f)
