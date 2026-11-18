# 报价单生成参考脚本（LibreOffice 版，2026-11-18 Mahlogonolo Atrium 20x30 CIF Durban 用过）
# 用途：在 Cowork 云端（没有 Windows/Excel，pi.ps1 跑不了）时，用 LibreOffice 改 原始资料/报价模板 里的 .xls 并导出 PDF。
# 用法：先把模板复制到 /tmp/q/atrium.xls，修改下方客户、尺寸、单价、运费、图片路径等硬编码值，再 python3 本脚本。
# 已处理的坑：联系方式换新版、质保 2-3 years、顶布颜色、CBM 只写数字+CBM、运费/总价两位小数、页宽缩到 1 页宽、
#   Material Guarantee 前强制分页、产品图和 3D 图按尺寸替换、工厂照片对齐不重叠。
# 规范见 kb/政策/报价单检查清单.md

import uno, time, subprocess, sys, re
from com.sun.star.beans import PropertyValue
def P(n,v): p=PropertyValue(); p.Name=n; p.Value=v; return p
proc=subprocess.Popen(["soffice","--headless","--norestore","--accept=socket,host=localhost,port=2002;urp;"])
ctx=None
for i in range(30):
    try:
        local=uno.getComponentContext()
        res=local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver",local)
        ctx=res.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"); break
    except Exception: time.sleep(1)
desk=ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop",ctx)
src="file:///tmp/q/atrium.xls"
doc=desk.loadComponentFromURL(src,"_blank",0,(P("Hidden",True),))
sh=doc.Sheets.getByIndex(0)
def c(a): return sh.getCellRangeByName(a)
W,L=20,30; area=W*L; unit=45.45; rate=6.6
cbm=round(area*0.03*1.25,2)
ship=7650+700+100
c("A2").String="Buyer: Mahlogonolo Phahlamohlaka"
c("A3").String="Contact: Mahlogonolo Phahlamohlaka"
c("A4").String="M.P./WhatsApp: +27 74 085 1983"
c("A5").String="Add: South Africa"
c("A6").String="QUOTATION"
c("F7").String="Quotation No: GY202611181"
c("H7").String="Date: 2026/11/18"
c("F2").String="Supplier: SUZHOU GUYUN TENT CO., LTD"
c("F3").String="Contact Person: Evelyn,  Email: gysales6@guyuntent.com"
c("F4").String="WhatsApp/WeChat: +008618706208684"
c("F5").String="Add: No.1 Chengtai Road South, Taiping Town, Xiangcheng District, Suzhou City, Jiangsu Province, China"
c("A9").String=c("A9").String.replace("150*108*3mm","203*112mm").replace("Top cover:  950G/m² double-coated Transparent PVC","Top cover:  950G/m² double-coated white PVC").replace("Warranty: 5 years","Warranty: 2-3 years")
c("B12").String="20x30m"; c("D12").Value=20; c("E12").Value=30
c("F12").Value=4; c("G12").Value=8.3; c("H12").Value=5; c("I12").String="203*112mm"
c("B15").String="Aluminum Atrium Tent"; c("C15").String="20x30m"; c("F15").Value=1; c("E15").String="White/Clear PVC\nBlack frame"
c("G15").Formula="=20*30"; c("H15").Value=unit; c("I15").Formula="=H15*G15*F15"
c("I16").Formula="=I15"
c("I17").String="CIF Durban"
c("I18").String=f"{cbm} CBM"
c("I19").String=f"{round(area*8/1000,1)} ton"
c("I20").Value=ship
c("A21").String="Total Amount:"; c("I21").Formula="=I16+I20"
c("A24").String=c("A24").String.replace("150*108*3mm","203*112mm")
c("A37").String="1. Incoterms: CIF Durban"
c("A39").String="3. The valid period of the offer: 15 Days from 2026/11/18"
for a in ["H15","I15","I16","I20","I21"]: pass
doc.calculateAll()
from com.sun.star.awt import Point, Size
gp=ctx.ServiceManager.createInstanceWithContext("com.sun.star.graphic.GraphicProvider",ctx)
def G(path): return gp.queryGraphic((P("URL","file://"+path),))
dp=sh.DrawPage
shp=[dp.getByIndex(i) for i in range(dp.Count)]
def find(x,y):
    for q in shp:
        if abs(q.Position.X-x)<50 and abs(q.Position.Y-y)<50: return q
prod=find(16501,6403); sk=find(6098,28046); i6=find(26,54268); i7=find(19810,54187); i8=find(19852,58967)
# 1 product photo
prod.Graphic=G("/tmp/q/p3_crop.jpg")
# 2 3D sketch: enlarge row 23
rows=sh.Rows; rows.getByIndex(22).Height=16200; rows.getByIndex(26).IsStartOfNewPage=True
sk.Graphic=G("/mnt/user-data/uploads/9cb8f909-image.png")
y23=sum(rows.getByIndex(r).Height for r in range(22) if rows.getByIndex(r).IsVisible)
sk.Size=Size(23200,15950); sk.Position=Point(6100,y23+120)
# 3 factory photos row 35
y35=sum(rows.getByIndex(r).Height for r in range(34) if rows.getByIndex(r).IsVisible)
H=rows.getByIndex(34).Height
def fit_crop(q,W,Hh):
    g=q.Graphic; sz=g.getPropertyValue("Size100thMM")
    gw,gh=sz.Width,sz.Height
    if gw<=0 or gh<=0:
        px=g.getPropertyValue("SizePixel"); gw,gh=px.Width*26,px.Height*26
    cr=uno.createUnoStruct("com.sun.star.text.GraphicCrop")
    if gw/gh>W/Hh:
        d=int((gw-gh*W/Hh)/2); cr.Left=d; cr.Right=d
    else:
        d=int((gh-gw*Hh/W)/2); cr.Top=d; cr.Bottom=d
    q.GraphicCrop=cr; q.Size=Size(W,Hh)
gap=60
leftW=19811-gap; rightX=19811+gap; rightW=29353-rightX-gap; half=(H-3*gap)//2
fit_crop(i6,leftW-gap,H-2*gap); i6.Position=Point(gap,y35+gap)
fit_crop(i7,rightW,half); i7.Position=Point(rightX,y35+gap)
fit_crop(i8,rightW,half); i8.Position=Point(rightX,y35+2*gap+half)
doc.calculateAll()
ps=doc.StyleFamilies.getByName("PageStyles").getByName(sh.PageStyle)
ps.ScaleToPagesX=1; ps.ScaleToPagesY=0
nf=doc.NumberFormats; loc=uno.createUnoStruct("com.sun.star.lang.Locale"); loc.Language="en"; loc.Country="US"
k=nf.queryKey('[$$-409]#,##0.00',loc,False)
if k==-1: k=nf.addNew('[$$-409]#,##0.00',loc)
for a in ["I20","I21"]: c(a).NumberFormat=k
print("unit",c("H15").Value,"sub",c("I15").Value,"ship",c("I20").Value,"total",c("I21").Value,"cbm",cbm)
out="/tmp/q/out/Quotation_Mahlogonolo_Atrium_20x30_CIF_Durban_2026-11-18"
import os; os.makedirs("/tmp/q/out",exist_ok=True)
doc.storeToURL("file://"+out+".xls",(P("FilterName","MS Excel 97"),))
# pdf only first sheet
doc.storeToURL("file://"+out+".pdf",(P("FilterName","calc_pdf_Export"),P("FilterData",uno.Any("[]com.sun.star.beans.PropertyValue",tuple([P("Selection",sh)]))) ))
doc.close(True); 
try: desk.terminate()
except Exception: pass
