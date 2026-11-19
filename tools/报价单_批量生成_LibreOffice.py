import uno,time,subprocess,os,json
from com.sun.star.beans import PropertyValue
from com.sun.star.awt import Point, Size
def P(n,v): p=PropertyValue(); p.Name=n; p.Value=v; return p
proc=subprocess.Popen(["soffice","--headless","--norestore","--accept=socket,host=localhost,port=2002;urp;"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for i in range(40):
    try:
        l=uno.getComponentContext(); r=l.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver",l)
        ctx=r.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"); break
    except Exception: time.sleep(1)
desk=ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop",ctx)
gp=ctx.ServiceManager.createInstanceWithContext("com.sun.star.graphic.GraphicProvider",ctx)
def G(path): return gp.queryGraphic((P("URL","file://"+path),))
import itertools
from PIL import Image as PImage
_cnt=itertools.count()
def fit_crop(q,W,Hh):
    # 不用 GraphicCrop（Excel/WPS 打开 xls 时裁切过的图会丢失）：先导出图片，用 PIL 裁成目标比例再放回
    tmp=f"/tmp/q/tmpimg_{next(_cnt)}.png"
    gp.storeGraphic(q.Graphic,(P("URL","file://"+tmp),P("MimeType","image/png")))
    im=PImage.open(tmp).convert("RGB"); gw,gh=im.size
    if gw/gh>W/Hh:
        nw=int(gh*W/Hh); x=(gw-nw)//2; im=im.crop((x,0,x+nw,gh))
    else:
        nh=int(gw*Hh/W); y=(gh-nh)//2; im=im.crop((0,y,gw,y+nh))
    if im.width>1600: im=im.resize((1600,int(im.height*1600/im.width)))
    out=tmp.replace(".png",".jpg"); im.save(out,quality=88)
    q.Graphic=G(out); q.Size=Size(W,Hh)
jobs=json.load(open('/tmp/q/jobs.json'))
os.makedirs('/tmp/q/out',exist_ok=True)
for j in jobs:
    doc=desk.loadComponentFromURL("file:///tmp/q/"+j['tpl'],"_blank",0,(P("Hidden",True),))
    sh=doc.Sheets.getByIndex(0); c=lambda a: sh.getCellRangeByName(a)
    c("A2").String="Buyer: "+j['buyer']; c("A3").String="Contact: "+j['buyer']
    c("A4").String="M.P./WhatsApp: "+j['wa']; c("A5").String="Add: "+j['country']
    c("A6").String="QUOTATION"; c("F7").String="Quotation No: "+j['no']; c("H7").String="Date: 2026/11/18"
    c("F2").String="Supplier: SUZHOU GUYUN TENT CO., LTD"
    c("F3").String="Contact Person: Evelyn,  Email: gysales6@guyuntent.com"
    c("F4").String="WhatsApp/WeChat: +008618706208684"
    c("F5").String="Add: No.1 Chengtai Road South, Taiping Town, Xiangcheng District, Suzhou City, Jiangsu Province, China"
    s=c("A9").String
    for a,b in j['a9']: s=s.replace(a,b)
    c("A9").String=s
    for k,v in j['cells'].items():
        if isinstance(v,str) and v.startswith('='): c(k).Formula=v
        elif isinstance(v,str): c(k).String=v
        else: c(k).Value=v
    for k,(a,b) in j.get('repl',{}).items(): c(k).String=c(k).String.replace(a,b)
    ex=j.get('extras') or []
    nx=len(ex)
    if nx:
        rows0=sh.Rows
        rows0.insertByIndex(15,nx)
        src=sh.getCellRangeByPosition(0,14,9,14).RangeAddress
        for k,e in enumerate(ex):
            r=15+k
            sh.copyRange(sh.getCellByPosition(0,r).CellAddress,src)
            rows0.getByIndex(r).Height=rows0.getByIndex(14).Height
            name,size,color,qty,area,unit=e[:6]
            sh.getCellByPosition(0,r).Value=k+2
            sh.getCellByPosition(1,r).String=name; sh.getCellByPosition(2,r).String=size
            sh.getCellByPosition(4,r).String=color; sh.getCellByPosition(5,r).Value=qty
            sh.getCellByPosition(7,r).Formula=unit
            if len(e)>6 and e[6]=='pcs':
                sh.getCellByPosition(6,r).String=str(area); sh.getCellByPosition(8,r).Formula=f"=H{r+1}*F{r+1}"
                sh.getCellByPosition(7,r).NumberFormat=sh.getCellByPosition(8,r).NumberFormat
            else:
                sh.getCellByPosition(6,r).Formula=str(area); sh.getCellByPosition(8,r).Formula=f"=H{r+1}*G{r+1}*F{r+1}"
        sc_=sh.getCellByPosition(8,15+nx); sc_.Formula=f"=SUM(I15:I{15+nx})"
    nf=doc.NumberFormats; loc=uno.createUnoStruct("com.sun.star.lang.Locale"); loc.Language="en"; loc.Country="US"
    fk=nf.queryKey('[$$-409]#,##0.00',loc,False)
    if fk==-1: fk=nf.addNew('[$$-409]#,##0.00',loc)
    for a in j['money']: c(a).NumberFormat=fk
    dp=sh.DrawPage; shp=[dp.getByIndex(i) for i in range(dp.Count)]
    rows=sh.Rows
    for idx,path in j.get('img',{}).items():
        q=shp[int(idx)]; W,H=q.Size.Width,q.Size.Height; pos=q.Position
        q.Graphic=G(path); fit_crop(q,W,H); q.Position=pos
    if j.get('sketch'):
        idx,path,row=j['sketch']; row+=nx; q=shp[idx]
        rows.getByIndex(row).Height=16200
        y=sum(rows.getByIndex(r).Height for r in range(row) if rows.getByIndex(r).IsVisible)
        q.Graphic=G(path); fit_crop(q,23200,15950); q.Position=Point(6100,y+120)
    if j.get('nosketch') is not None:
        idx,row=j['nosketch']; row+=nx
        dp.remove(shp[idx]); rows.getByIndex(row).Height=900
        sh.getCellByPosition(1,row).String="3D drawing for this exact size: available on request"
    if j.get('factory'):
        a,b,cc,row=j['factory']; row+=nx; y=sum(rows.getByIndex(r).Height for r in range(row) if rows.getByIndex(r).IsVisible); H=rows.getByIndex(row).Height
        gap=60; leftW=19811-gap; rightX=19811+gap; rightW=29353-rightX-gap; half=(H-3*gap)//2
        fit_crop(shp[a],leftW-gap,H-2*gap); shp[a].Position=Point(gap,y+gap)
        fit_crop(shp[b],rightW,half); shp[b].Position=Point(rightX,y+gap)
        fit_crop(shp[cc],rightW,half); shp[cc].Position=Point(rightX,y+2*gap+half)
    if j.get('addsketch'):
        path,ri=j['addsketch']; ri+=nx
        rows.insertByIndex(ri,2)
        src=sh.getCellRangeByPosition(0,ri+2,9,ri+2).RangeAddress
        sh.copyRange(sh.getCellByPosition(0,ri).CellAddress,src)
        sh.getCellByPosition(0,ri).String="3D Dimension Sketch"
        rows.getByIndex(ri).Height=rows.getByIndex(ri+2).Height
        ir=ri+1; rows.getByIndex(ir).Height=16400
        rng=sh.getCellRangeByPosition(0,ir,9,ir); rng.merge(True); rng.CellBackColor=0xFFFFFF
        bl=uno.createUnoStruct("com.sun.star.table.BorderLine2"); bl.OuterLineWidth=18
        for side in ("TopBorder","BottomBorder","LeftBorder","RightBorder"): rng.setPropertyValue(side,bl)
        g=doc.createInstance("com.sun.star.drawing.GraphicObjectShape")
        dp.add(g); g.Graphic=G(path)
        y=sum(rows.getByIndex(r).Height for r in range(ir) if rows.getByIndex(r).IsVisible)
        tw=sum(sh.Columns.getByIndex(c).Width for c in range(10))
        fit_crop(g,24000,16000); g.Position=Point((tw-24000)//2,y+200)
        j['brk']+=2
    p2=(j.get('p2') or {'curved.xls':21,'atrium.xls':23,'classic.xls':23 if j.get('addsketch') else 21}[j['tpl']])+nx
    for r in range(rows.Count if rows.Count<200 else 200): rows.getByIndex(r).IsStartOfNewPage=False
    rows.getByIndex(p2).IsStartOfNewPage=True
    doc.calculateAll()
    # 打印区域只取 A:J，避免右侧空列/超出的图片把表格缩小
    cur=sh.createCursor(); cur.gotoEndOfUsedArea(False); lastrow=cur.RangeAddress.EndRow
    pa=uno.createUnoStruct("com.sun.star.table.CellRangeAddress"); pa.Sheet=0; pa.StartColumn=0; pa.StartRow=0; pa.EndColumn=9; pa.EndRow=lastrow
    sh.setPrintAreas((pa,))
    ps=doc.StyleFamilies.getByName("PageStyles").getByName(sh.PageStyle)
    ps.LeftMargin=800; ps.RightMargin=800; ps.TopMargin=1000; ps.BottomMargin=1000; ps.CenterHorizontally=True
    ps.HeaderIsOn=False; ps.FooterIsOn=False
    # 手动算缩放：宽度铺满，同时第 1 页（到建构图为止）和第 2 页各自放得下
    tw=sum(sh.Columns.getByIndex(c).Width for c in range(10))
    aw=ps.Width-ps.LeftMargin-ps.RightMargin; ah=ps.Height-ps.TopMargin-ps.BottomMargin-300
    h1=sum(rows.getByIndex(r).Height for r in range(p2) if rows.getByIndex(r).IsVisible)
    h2=sum(rows.getByIndex(r).Height for r in range(p2,lastrow+1) if rows.getByIndex(r).IsVisible)
    sc=min(aw/tw, ah/h1, ah/h2)
    ps.ScaleToPagesX=0; ps.ScaleToPagesY=0; ps.ScaleToPages=0; ps.PageScale=int(sc*100)
    print('scale',int(sc*100),'w',round(aw/tw,2),'p1',round(ah/h1,2),'p2',round(ah/h2,2))
    print(j['out'],[ (a,round(c(a).Value,2)) for a in j['money']])
    out="/tmp/q/out/"+j['out']
    doc.storeToURL("file://"+out+".xls",(P("FilterName","MS Excel 97"),))
    doc.storeToURL("file://"+out+".pdf",(P("FilterName","calc_pdf_Export"),P("FilterData",uno.Any("[]com.sun.star.beans.PropertyValue",tuple([P("Selection",sh)])))))
    doc.close(True)
try: desk.terminate()
except: pass
