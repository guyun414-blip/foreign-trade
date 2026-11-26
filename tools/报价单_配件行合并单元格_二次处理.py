import uno,time,subprocess,os,sys
from com.sun.star.beans import PropertyValue
def P(n,v): p=PropertyValue(); p.Name=n; p.Value=v; return p
proc=subprocess.Popen(["soffice","--headless","--norestore","--accept=socket,host=localhost,port=2004;urp;"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for i in range(40):
    try:
        l=uno.getComponentContext(); r=l.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver",l)
        ctx=r.resolve("uno:socket,host=localhost,port=2004;urp;StarOffice.ComponentContext"); break
    except Exception: time.sleep(1)
desk=ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop",ctx)
out=os.path.abspath(sys.argv[1])
doc=desk.loadComponentFromURL("file://"+out+".xls","_blank",0,(P("Hidden",True),))
sh=doc.Sheets.getByIndex(0)
for rng in ("C16:D16","I16:J16"):
    g=sh.getCellRangeByName(rng); g.merge(True); print(rng,g.getIsMerged(), sh.getCellRangeByName(rng.replace("16","15")).getIsMerged())
c=sh.getCellRangeByName("C16"); c.HoriJustify=uno.Enum('com.sun.star.table.CellHoriJustify','CENTER')
print(c.HoriJustify, sh.getCellRangeByName("C15").HoriJustify)
doc.storeToURL("file://"+out+".xls",(P("FilterName","MS Excel 97"),P("Overwrite",True)))
doc.storeToURL("file://"+out+".pdf",(P("FilterName","calc_pdf_Export"),P("Overwrite",True),P("FilterData",uno.Any("[]com.sun.star.beans.PropertyValue",tuple([P("Selection",sh)])))))
doc.close(True); desk.terminate()
