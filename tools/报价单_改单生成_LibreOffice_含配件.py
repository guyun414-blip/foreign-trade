# 报价单改单生成（2026-11-20 会话整理）：在已调好版式的底稿上改客户、尺寸、价格、图片，导出 xls + pdf（2 页）
# 用法：python3 tools/报价单_改单生成_LibreOffice.py jobs.json   （在任意工作目录运行，输出到当前目录，再拷到 输出/报价/）
# jobs.json 每项：
#   base   底稿：原始资料/报价模板/8.经典白底稿（改单脚本用）.xls（经典白/体育篷）或 9.工业篷底稿（改单脚本用）.xls（工业篷）
#   buyer wa country no   客户名、WhatsApp、国家、报价单号
#   w l eave ridge prof   跨度、长度、边高、顶高（体育篷固定 10.5）、主型材
#   name rmb              产品名、人民币单价（脚本 ÷6.6）
#   photo                 可选，替换产品实景图（体育篷用 原始资料/产品照片/体育篷房_足球场实景.jpg）
#   sketch                3D 建构图路径（必填；图库没有就先用 tools/画结构图_人字顶截面平面图.py 画）
#   cif freight incoterm  可选，CIF 时填：如 "CIF Durban"、"=8600+700+200+30"、"1. Incoterms: CIF Durban, South Africa"；不填就是 EXW
#   qty                   可选，套数（默认 1）；CBM、重量按 面积×套数 算
#   date                  可选，报价日期 "2026/11/23"（默认今天）
#   out                   输出文件名（不带扩展名）
# 体积重量脚本按 面积×0.03 CBM、面积×8 kg 现算（中庭不要用这个脚本）。
import sys, datetime
TODAY=datetime.date.today().strftime("%Y/%m/%d")
import uno,time,subprocess,os,json,re
from com.sun.star.beans import PropertyValue
from com.sun.star.awt import Point, Size
from PIL import Image as PImage
def P(n,v): p=PropertyValue(); p.Name=n; p.Value=v; return p
proc=subprocess.Popen(["soffice","--headless","--norestore","--accept=socket,host=localhost,port=2003;urp;"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for i in range(40):
    try:
        l=uno.getComponentContext(); r=l.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver",l)
        ctx=r.resolve("uno:socket,host=localhost,port=2003;urp;StarOffice.ComponentContext"); break
    except Exception: time.sleep(1)
desk=ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop",ctx)
gp=ctx.ServiceManager.createInstanceWithContext("com.sun.star.graphic.GraphicProvider",ctx)
H=os.path.abspath("."); cnt=[0]
def putimg(q,path,crop):
    W,Hh=q.Size.Width,q.Size.Height; pos=q.Position
    im=PImage.open(path).convert("RGB"); gw,gh=im.size
    if crop:
        if gw/gh>W/Hh: nw=int(gh*W/Hh); x=(gw-nw)//2; im=im.crop((x,0,x+nw,gh))
        else: nh=int(gw*Hh/W); y=(gh-nh)//2; im=im.crop((0,y,gw,y+nh))
    else:
        if gw/gh>W/Hh: nh=int(gw*Hh/W); bg=PImage.new("RGB",(gw,nh),"white"); bg.paste(im,(0,(nh-gh)//2)); im=bg
        else: nw=int(gh*W/Hh); bg=PImage.new("RGB",(nw,gh),"white"); bg.paste(im,((nw-gw)//2,0)); im=bg
    if im.width>1600: im=im.resize((1600,int(im.height*1600/im.width)))
    cnt[0]+=1; f=f"{H}/tmp_{cnt[0]}.jpg"; im.save(f,quality=88)
    q.Graphic=gp.queryGraphic((P("URL","file://"+f),)); q.Size=Size(W,Hh); q.Position=pos
for j in json.load(open(sys.argv[1])):
    doc=desk.loadComponentFromURL("file://"+os.path.abspath(j["base"]),"_blank",0,(P("Hidden",True),))
    sh=doc.Sheets.getByIndex(0); c=lambda a: sh.getCellRangeByName(a); rows=sh.Rows; dp=sh.DrawPage
    W_,L_=j["w"],j["l"]
    c("A2").String="Buyer: "+j["buyer"]; c("A3").String="Contact: "+j["buyer"]; c("A4").String="M.P./WhatsApp: "+j["wa"]; c("A5").String="Add: "+j["country"]
    c("F7").String="Quotation No: "+j["no"]; c("H7").String="Date: "+j.get("date",TODAY)
    c("B12").String=f"{W_}x{L_}m"; c("D12").Value=W_; c("E12").Value=L_
    for a,v in (("F12",j["eave"]),("G12",j["ridge"])): c(a).String=f"{v}m"
    c("H12").String="5m"; c("I12").String=j["prof"]
    c("B15").String=j["name"]; c("C15").String=f"{W_}x{L_}m"; c("E15").String="White PVC"; c("F15").Value=j.get("qty",1)
    c("G15").Formula=f"={W_}*{L_}"; c("H15").Formula=f"={j['rmb']}/6.6"
    area=W_*L_; c("I17").String="EXW"; Q=j.get("qty",1); c("I18").String=f"{area*Q*0.03:g} CBM"; c("I19").String=f"{area*Q*8:,} kg"
    if j.get("cif"):
        c("I17").String=j["cif"]; c("I20").Formula=j["freight"]; c("I21").Formula="=I16+I20"
        nf=doc.NumberFormats; loc=uno.createUnoStruct("com.sun.star.lang.Locale"); loc.Language="en"; loc.Country="US"
        k=nf.queryKey('[$$-409]#,##0.00',loc,False); k=k if k!=-1 else nf.addNew('[$$-409]#,##0.00',loc)
        c("I20").NumberFormat=k; c("I21").NumberFormat=k
    else:
        c("I20").String="Not included (EXW)"; c("I21").Formula="=I16"
    for r in range(60):
        for col in range(10):
            x=sh.getCellByPosition(col,r)
            if x.Type.value!='TEXT': continue
            s=x.String; s2=re.sub(r"Clear span \d+m",f"Clear span {W_}m",s)
            for old in ("252*112*4mm","203*112mm","350*120*5mm","68*121mm","150*108*3mm"):
                if r>7 and r!=11 and old in s2: s2=s2.replace(old,j["prof"])
            if s2.startswith("1. Incoterms"): s2=j.get("incoterm","1. Incoterms: EXW (CIF price to follow)")
            if s2.startswith("3. The valid period"): s2="3. The valid period of the offer: 15 Days from "+j.get("date",TODAY)
            if s2!=s: x.String=s2
    shp=[dp.getByIndex(i) for i in range(dp.Count)]
    sk=max(shp,key=lambda q:q.Size.Height*q.Size.Width if q.Position.Y>20000 and q.Position.Y<40000 else 0)
    ph=max(shp,key=lambda q:q.Size.Width if q.Position.Y<15000 else 0)
    if j.get("photo"): putimg(ph,j["photo"],True)
    if j.get("sketch"): putimg(sk,j["sketch"],False)
    else:
        rr=[r for r in range(40) if sh.getCellByPosition(0,r).String.startswith("3D Dimension")][0]+1
        dp.remove(sk); rows.getByIndex(rr).Height=900
        sh.getCellByPosition(0,rr).String="3D drawing for this exact size: available on request"
    ex=j.get('extras') or []
    if ex:
        nx=len(ex); rows.insertByIndex(15,nx); src=sh.getCellRangeByPosition(0,14,9,14).RangeAddress
        for k,e in enumerate(ex):
            r=15+k; sh.copyRange(sh.getCellByPosition(0,r).CellAddress,src); rows.getByIndex(r).Height=rows.getByIndex(14).Height
            name,size,color,qty,area,unit=e
            sh.getCellByPosition(0,r).Value=k+2; sh.getCellByPosition(1,r).String=name; sh.getCellByPosition(2,r).String=size
            sh.getCellByPosition(4,r).String=color; sh.getCellByPosition(5,r).Value=qty
            sh.getCellByPosition(6,r).Formula=str(area); sh.getCellByPosition(7,r).Formula=unit; sh.getCellByPosition(8,r).Formula=f"=H{r+1}*G{r+1}*F{r+1}"
            for a,b in ((2,3),(8,9)):
                sh.getCellByPosition(b,r).setString('')
                nb=uno.createUnoStruct('com.sun.star.table.BorderLine2')
                ca=sh.getCellByPosition(a,r); cb=sh.getCellByPosition(b,r)
                ca.RightBorder=nb; cb.LeftBorder=nb; ca.HoriJustify=uno.Enum('com.sun.star.table.CellHoriJustify','CENTER')
                cb.RightBorder=sh.getCellByPosition(b,14).RightBorder
            for cc in range(10): sh.getCellByPosition(cc,r).HoriJustify=sh.getCellByPosition(cc,14).HoriJustify
        sh.getCellByPosition(8,15+nx).Formula=f"=SUM(I15:I{15+nx})"
    doc.calculateAll()
    p2=[r for r in range(80) if sh.getCellByPosition(0,r).String.startswith("Tent Material")][0]
    for r in range(200): rows.getByIndex(r).IsStartOfNewPage=False
    rows.getByIndex(p2).IsStartOfNewPage=True
    cur=sh.createCursor(); cur.gotoEndOfUsedArea(False); lastrow=cur.RangeAddress.EndRow
    pa=uno.createUnoStruct("com.sun.star.table.CellRangeAddress"); pa.Sheet=0; pa.StartColumn=0; pa.StartRow=0; pa.EndColumn=9; pa.EndRow=lastrow
    sh.setPrintAreas((pa,))
    ps=doc.StyleFamilies.getByName("PageStyles").getByName(sh.PageStyle)
    tw=sum(sh.Columns.getByIndex(k).Width for k in range(10))
    aw=ps.Width-ps.LeftMargin-ps.RightMargin; ah=ps.Height-ps.TopMargin-ps.BottomMargin-300
    h1=sum(rows.getByIndex(r).Height for r in range(p2) if rows.getByIndex(r).IsVisible)
    h2=sum(rows.getByIndex(r).Height for r in range(p2,lastrow+1) if rows.getByIndex(r).IsVisible)
    sc=min(aw/tw, ah/h1, ah/h2); ps.ScaleToPagesX=0; ps.ScaleToPagesY=0; ps.ScaleToPages=0; ps.PageScale=int(sc*100)
    left=[(chr(65+cc)+str(r+1),sh.getCellByPosition(cc,r).String[:50]) for r in range(60) for cc in range(10) if re.search(r"Anna|Lady|Senegal|Nigeria|Dakar|Lagos|25x50|20x35",sh.getCellByPosition(cc,r).String) and j["w"]!=25]
    print(j["out"], {a:c(a).String for a in ("I12","G12","H15","I15","B16","I16","I17","I18","I19","I20","I21","I22")}, 'scale',int(sc*100), 'LEFT',left)
    out=H+"/"+j["out"]
    doc.storeToURL("file://"+out+".xls",(P("FilterName","MS Excel 97"),))
    doc.storeToURL("file://"+out+".pdf",(P("FilterName","calc_pdf_Export"),P("FilterData",uno.Any("[]com.sun.star.beans.PropertyValue",tuple([P("Selection",sh)])))))
    doc.close(True)
desk.terminate()
