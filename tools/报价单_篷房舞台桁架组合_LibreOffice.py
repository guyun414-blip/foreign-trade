# 篷房 + 舞台桁架 组合报价单生成脚本（Cowork 云端 LibreOffice）
# 2026-11-19 P.S. Hlatjwako 单，结果与同事核算版（原始资料/报价模板/7.篷房+舞台桁架组合报价_同事核算版.xls）逐格一致。
# 用法：
#  1. 先用 报价单_批量生成_LibreOffice.py 生成一份同尺寸、同港口的 Classic 篷房报价单，复制成 /tmp/q/thobeka.xls（底板）
#  2. 原始资料/产品照片/舞台桁架配件/*  stage 到 /tmp/q/img/；设计师图片拼成 /tmp/q/drawings.jpg（2x2 拼图，3000x2000）
#  3. 改下面的硬编码：客户信息、TRUSS、STAGE、FREIGHT、CBM/KG/PORT、A9 追加文字、各标题
#  4. python3 本脚本 → /tmp/q/out/ 生成 xls + pdf；渲染每页检查
# 计价方法见 kb/价格/舞台桁架报价方法.md；单价一律用 舞台桁架价格表.xls 的"报价"列 ÷6.6
import uno,time,subprocess,os
from com.sun.star.beans import PropertyValue
from com.sun.star.awt import Point, Size
from PIL import Image as PImage
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

R=6.6
CI='/tmp/q/img/'   # = 原始资料/产品照片/舞台桁架配件/ 里的配件图，stage 到这里
TRUSS=[ # name, picture, description, qty, unit-format, unit RMB formula
 ("Aluminum alloy spigot truss", CI+"spigot_truss.jpg",
  "Aluminum Alloy 6061-T6, 290*290mm\nMain 50*3mm, vice 25*2mm, brace 20*2mm\nPillars (1m+2m) x4; beams 8m (3+3+2m) x2, 6m (3+3m) x2\n3m: 8pcs  2m: 6pcs  1m: 4pcs",
  40,"m","=(3*8*210+2*6*220+1*4*260)/40/6.6"),
 ("Sleeve block", CI+"sleeve_block.jpg",
  "Aluminum alloy material\nTruss lift system\nConnecting beams to pillars", 4,"pcs","=600/6.6"),
 ("Top section", CI+"top_section.png",
  "Aluminum alloy material\nTruss lift system", 4,"pcs","=400/6.6"),
 ("Manual hoist", CI+"manual_hoist.jpg",
  "Truss lift system\n(2T / 6M)", 4,"pcs","=450/6.6"),
 ("Belt", CI+"belt.jpg",
  "Truss lift system\nUsed for tying beam\n(2T / 3M)", 4,"pcs","=60/6.6"),
 ("Base", CI+"base.png",
  "Galvanized iron stabilizing base\nwith adjustable feet\nfor pillar truss", 4,"pcs","=400/6.6"),
 ("Outrigger", CI+"outrigger.png",
  "Aluminum Alloy 6061-T6\nMain tube: 50*3mm, 5ft / 1.5m\nBracing the pillar (4 per pillar)", 16,"pcs","=160/6.6"),
 ("Spigot hinge", CI+"spigot_hinge.jpg",
  "Aluminum material\nConnecting outriggers to the pillar", 16,"pcs","=60/6.6"),
 ("Conical connector", CI+"conical_connector.jpg",
  "Aluminum spigot + steel pin + R-clip\nUsed to link trusses\n(20% spare included)", 144,"sets","=16/6.6"),
]
STAGE=[
 ("Stage panels", CI+"stage_panel.jpg",
  "Aluminum frame, 18mm double-sided laminated anti-slip plywood\nPanel color: Black\nEach panel: 1.22x1.22m [4x4ft]\n15pcs = 6.1x3.66m (22.3 m²)", 15,"pcs","=210/6.6"),
 ("Stage brace", CI+"stage_brace.png",
  "Aluminum alloy 6061-T6\nRound tube: 50*3mm\nBrace tube: 25*2mm\nLength: 1170mm  Height: 250mm", 38,"pcs","=105/6.6"),
 ("Pillar and built-in tube", CI+"stage_pillar.png",
  "Aluminum alloy 6061-T6\nPillar round tube: 50*3mm\nBuilt-in tube: 43*3mm\nHeight adjustable: 0.4-0.8m (set at 0.8m)", 24,"pcs","=35/6.6"),
 ("Adjustable base", CI+"adjustable_base.png",
  "Galvanized iron material\nScrew jack for leveling", 24,"pcs","=12/6.6"),
 ("Aluminum alloy stair", CI+"stair.png",
  "18mm anti-slip panel, black\nWidth: 1220mm  Depth: 300mm\n3-step stair (for 0.8m stage)", 1,"set","=600/6.6"),
]
FREIGHT="=7650+700+100"

doc=desk.loadComponentFromURL("file:///tmp/q/thobeka.xls","_blank",0,(P("Hidden",True),))
sh=doc.Sheets.getByIndex(0); c=lambda a: sh.getCellRangeByName(a)
rows=sh.Rows; cols=sh.Columns
c("A2").String="Buyer: P.S. Hlatjwako"; c("A3").String="Contact: P.S. Hlatjwako"
c("A4").String="M.P./WhatsApp: "; c("A5").String="Add: "
c("F7").String="Quotation No: GY20261119-PSH"; c("H7").String="Date: 2026/11/19"
c("A6").String="QUOTATION"
c("A9").String=c("A9").String+"\n\nStage & Truss (installed inside the tent):\nTruss frame: 8 x 6 x 3 m (L x W x H), 290*290mm aluminum spigot truss with lift system\nStage: 6.1 x 3.66 m (5 x 3 panels of 1.22 x 1.22 m), height 0.8 m, black anti-slip panels"
rows.getByIndex(8).Height=rows.getByIndex(8).Height+2300
c("B15").String="Classic White A-Shape Tent"

# record the sketch shape (anchored at row index 22) before inserting rows
dp=sh.DrawPage
def anchor_row(s):
    try: return s.Anchor.CellAddress.Row
    except Exception: return None
y0=sum(rows.getByIndex(i).Height for i in range(22) if rows.getByIndex(i).IsVisible); y1=y0+rows.getByIndex(22).Height
sketch=[dp.getByIndex(i) for i in range(dp.Count) if dp.getByIndex(i).Size.Width>20000]
print("sketch shapes",len(sketch),y0,y1,[(dp.getByIndex(i).Position.Y,dp.getByIndex(i).Size.Width,dp.getByIndex(i).Size.Height,dp.getByIndex(i).ShapeType) for i in range(dp.Count)])

NI=(3+len(TRUSS))+(3+len(STAGE))
rows.insertByIndex(15,NI)
def copyrow(src,dst):
    sh.copyRange(sh.getCellByPosition(0,dst).CellAddress, sh.getCellRangeByPosition(0,src,9,src).RangeAddress)
    rows.getByIndex(dst).Height=rows.getByIndex(src).Height
nf=doc.NumberFormats; loc=uno.createUnoStruct("com.sun.star.lang.Locale"); loc.Language="en"; loc.Country="US"
def F(s):
    k=nf.queryKey(s,loc,False)
    return k if k!=-1 else nf.addNew(s,loc)
money=F('[$$-409]#,##0.00')
SUMROW=15+NI   # original "Sum:" row index after insertion
def remerge(r,spans):
    rr=sh.getCellRangeByPosition(0,r,9,r); rr.merge(False)
    for a,b in spans: sh.getCellRangeByPosition(a,r,b,r).merge(True)
pics=[]
def section(start,title,items):
    r=start
    copyrow(12,r); sh.getCellByPosition(0,r).String=title; r+=1           # yellow label (like SALES PRICE)
    copyrow(13,r); remerge(r,[(2,3),(4,5),(8,9)])
    for col,t in [(0,"NO."),(1,"COMPONENT"),(2,"PICTURE"),(4,"DESCRIPTION"),(6,"QTY"),(7,"UNIT PRICE"),(8,"Sub-total (USD)")]:
        sh.getCellByPosition(col,r).String=t
    r+=1; first=r
    for k,(name,pic,desc,qty,unit,price) in enumerate(items):
        copyrow(14,r); remerge(r,[(2,3),(4,5),(8,9)])
        rows.getByIndex(r).Height=2300 if k else 3210
        for col in range(10): sh.getCellByPosition(col,r).String=""
        sh.getCellByPosition(0,r).Value=k+1
        sh.getCellByPosition(1,r).String=name; sh.getCellByPosition(1,r).IsTextWrapped=True
        d=sh.getCellByPosition(4,r); d.String=desc; d.IsTextWrapped=True; d.CharHeight=8.5
        q=sh.getCellByPosition(6,r); q.Value=qty; q.NumberFormat=F('0" %s"'%unit)
        u=sh.getCellByPosition(7,r); u.Formula=price; u.NumberFormat=money
        s=sh.getCellByPosition(8,r); s.Formula=f"=G{r+1}*H{r+1}"; s.NumberFormat=money
        pics.append((r,pic)); r+=1
    copyrow(SUMROW,r); sh.getCellByPosition(0,r).String=title.split(" (")[0]+" Sum:"
    sh.getCellByPosition(8,r).Formula=f"=SUM(I{first+1}:I{r})"; sh.getCellByPosition(8,r).NumberFormat=money
    return r
t_sum=section(15,"Truss Series (8 x 6 x 3 m truss frame with lift system)",TRUSS)
s_sum=section(t_sum+1,"Stage Series (6.1 x 3.66 m, height range 0.4-0.8 m)",STAGE)
assert s_sum+1==SUMROW, (s_sum,SUMROW)
S=SUMROW
CBM,KG,PORT="18.3","3385","CIF Durban"
rows.removeByIndex(S+1,3)          # drop Trade Terms / CBM / WEIGHT rows (colleague format)
c(f"A{S+1}").String=f"({CBM}CBM {KG}KG for reference) Subtotal (Tent + Truss + Stage):"
c(f"I{S+1}").Formula=f"=I15+I{t_sum+1}+I{s_sum+1}"
c(f"A{S+2}").String="Shipping cost :"; c(f"I{S+2}").Formula=FREIGHT
c(f"A{S+3}").String=f"Grand Total ({PORT}):"; c(f"A{S+3}").CharColor=0xFF0000
c(f"I{S+3}").Formula=f"=I{S+1}+I{S+2}"
for a in [f"I{S+1}",f"I{S+2}",f"I{S+3}"]: c(a).NumberFormat=money
c(f"A{S+4}").String="Design Drawings: 15x20m Tent with 8x6x3m Truss & Stage"
sk=S+4
rows.getByIndex(sk).Height=17200
def red_part(cell):   # size text inside "(...)" in red, like the colleague's version
    t=cell.String; i=t.find("(")
    if i<0: return
    cur=cell.createTextCursor(); cur.gotoStart(False); cur.goRight(i+1,False); cur.goRight(len(t)-i-2,True); cur.CharColor=0xFF0000
red_part(sh.getCellByPosition(0,15)); red_part(sh.getCellByPosition(0,t_sum+1))
def bold_last_line(cell):
    t=cell.String; i=t.rfind("\n")+1
    cur=cell.createTextCursor(); cur.gotoStart(False); cur.goRight(i,False); cur.gotoEnd(True); cur.CharWeight=150
bold_last_line(sh.getCellByPosition(4,s_sum-1))
def ypos(r): return sum(rows.getByIndex(i).Height for i in range(r) if rows.getByIndex(i).IsVisible)
def xpos(cn): return sum(cols.getByIndex(i).Width for i in range(cn))
def place(path,r,c0,c1,pad=150,rowh=None):
    im=PImage.open(path); iw,ih=im.size
    if im.mode not in ("RGB","L"):
        bg=PImage.new("RGB",im.size,"white"); bg.paste(im,mask=im.convert("RGBA").split()[3]); im=bg
        path=path.rsplit(".",1)[0]+"_w.png"; im.save(path)
    W=xpos(c1+1)-xpos(c0)-2*pad; H=(rowh or rows.getByIndex(r).Height)-2*pad
    s=min(W/iw,H/ih); w,h=int(iw*s),int(ih*s)
    g=doc.createInstance("com.sun.star.drawing.GraphicObjectShape"); dp.add(g)
    try: g.Anchor=sh.getCellByPosition(c0,r)
    except Exception: pass
    g.Graphic=G(path); g.Size=Size(w,h)
    g.Position=Point(xpos(c0)+pad+(W-w)//2, ypos(r)+pad+(H-h)//2)
olds=[dp.getByIndex(i) for i in range(dp.Count) if dp.getByIndex(i).Size.Width>20000]
for s_ in olds: dp.remove(s_)
print('removed',len(olds),dp.Count)
for r,p in pics: place(p,r,2,3,pad=120)
place("/tmp/q/drawings.jpg",sk,0,9,pad=200)

# remarks
for i in range(sk+1,sk+40):
    cell=sh.getCellByPosition(0,i); t=cell.String
    if t.startswith("HS Code"): cell.String="HS Code: Tent 9406900090; Aluminum stage & truss 7616999000"
    if t.startswith("1. Incoterms"): cell.String=f"1. Incoterms: {PORT} via FCL"
    if t.startswith("4. Delivery Time"): cell.String="4. Delivery Time: 25-30 working days from the date of receipt of the deposit (tent, truss and stage shipped together)."
# page breaks
p2=t_sum+1; p3=sk+1
for r_ in range(200): rows.getByIndex(r_).IsStartOfNewPage=False
rows.getByIndex(p2).IsStartOfNewPage=True; rows.getByIndex(p3).IsStartOfNewPage=True
doc.calculateAll()
cur=sh.createCursor(); cur.gotoEndOfUsedArea(False); last=cur.RangeAddress.EndRow
pa=uno.createUnoStruct("com.sun.star.table.CellRangeAddress"); pa.Sheet=0; pa.StartColumn=0; pa.StartRow=0; pa.EndColumn=9; pa.EndRow=last
sh.setPrintAreas((pa,))
ps=doc.StyleFamilies.getByName("PageStyles").getByName(sh.PageStyle)
ps.LeftMargin=800; ps.RightMargin=800; ps.TopMargin=1000; ps.BottomMargin=1000; ps.CenterHorizontally=True
ps.HeaderIsOn=False; ps.FooterIsOn=False
tw=xpos(10); aw=ps.Width-1600; ah=ps.Height-2000-300
hs=[sum(rows.getByIndex(r_).Height for r_ in range(a,b) if rows.getByIndex(r_).IsVisible) for a,b in [(0,p2),(p2,p3),(p3,last+1)]]
sc=min([aw/tw]+[ah/h for h in hs])
ps.ScaleToPagesX=0; ps.ScaleToPagesY=0; ps.ScaleToPages=0; ps.PageScale=int(sc*100)
print("scale",int(sc*100),[round(ah/h,2) for h in hs], round(aw/tw,2))
for a in ["I15",f"I{t_sum+1}",f"I{s_sum+1}",f"I{S+1}",f"I{S+5}",f"I{S+6}"]: print(a, round(c(a).Value,2))
os.makedirs('/tmp/q/out',exist_ok=True)
out="/tmp/q/out/Quotation_PSHlatjwako_ClassicWhite_15x20_Truss_Stage_CIF_Durban_2026-11-19"
doc.storeToURL("file://"+out+".xls",(P("FilterName","MS Excel 97"),))
doc.storeToURL("file://"+out+".pdf",(P("FilterName","calc_pdf_Export"),P("FilterData",uno.Any("[]com.sun.star.beans.PropertyValue",tuple([P("Selection",sh)])))))
doc.close(True)
try: desk.terminate()
except: pass
