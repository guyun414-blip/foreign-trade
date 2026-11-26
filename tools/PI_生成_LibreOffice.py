# PI 生成（2026-11-22 按用户给的模板 原始资料/PI模板/PI Sulaiman 2x 20x40m EXW 2026.11.19 (deposit 35000).pdf 复刻）
# 用法：python3 tools/PI_生成_LibreOffice.py job.json  → 输出 <out>.xlsx 和 <out>.pdf（需要 LibreOffice）
# job.json 字段：
#   out 输出路径(不含扩展名)；logo / sign 图片（原始资料/PI模板/logo.png、sign.png）
#   invoice_no(GYZP+日期+序号，如 GYZP2026112201)  date(2026/11/22)  buyer  whatsapp  address
#   term  价格列头和 Total 行，如 "EXW" / "CIF Lagos (Apapa)"
#   items  [[描述, 数量文字, 单价文字, 小计数字], ...]  单价可为 ""（如运费行）
#   discount 可选（正数，显示为负）
#   remarks [..]（付款：定金金额 + 尾款金额；交期；包装+CBM+毛重；HS Code）
#   components [[部件, 说明], ...]（Qty 列统一 According to packing list）
# 银行信息固定为模板上的建设银行账户，脚本里写死，不要改。
import json, sys, subprocess, os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.drawing.image import Image as XImg

j = json.load(open(sys.argv[1], encoding='utf-8'))
wb = Workbook(); ws = wb.active; ws.title = 'PI'
FN = 'Times New Roman'
thin = Side(style='thin'); med = Side(style='medium')
# 列：A No | B 部件 | C 描述余下 | D 数量 | E 单价 | F 小计 ；价格表描述 = B:C，部件表说明 = C:E
for col, w in zip('ABCDEF', [6, 24, 46, 11, 14, 15]): ws.column_dimensions[col].width = w

def put(rng, v, bold=False, size=10, color=None, h='left', wrap=True, border=False, indent=0):
    a = rng.split(':')[0]
    if ':' in rng: ws.merge_cells(rng)
    c = ws[a]; c.value = v
    c.font = Font(name=FN, bold=bold, size=size, color=color)
    c.alignment = Alignment(horizontal=h, vertical='center', wrap_text=wrap, indent=indent)
    if border:
        for row in ws[rng] if ':' in rng else ((c,),):
            for x in row: x.border = Border(left=thin, right=thin, top=thin, bottom=thin)
    return c

def lines(text, chars):  # 估算行数
    return max(1, -(-len(text) // chars))

# 抬头
put('B1:F1', 'SUZHOU GUYUN TENT CO., LTD', bold=True, h='center')
hdr = ['Add: No.1 Chengtai Road South, Taiping Town, Xiangcheng District, Suzhou City, Jiangsu Province, China',
       'Contact Person: Evelyn Wang    TEL/WhatsApp/WeChat: +86 18706208684',
       'E-MAIL: gysales6@guyuntent.com', 'WEBSITE: https://www.gy-tent.com/']
for i, t in enumerate(hdr, 2): put(f'C{i}:F{i}', t)
for i, hgt in zip(range(1, 6), [20, 26, 16, 14, 16]): ws.row_dimensions[i].height = hgt
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.utils.units import pixels_to_EMU
lg = XImg(j['logo']); lg.width, lg.height = 104, 88
lg.anchor = OneCellAnchor(_from=AnchorMarker(col=0, colOff=pixels_to_EMU(6), row=0, rowOff=pixels_to_EMU(5)), ext=XDRPositiveSize2D(pixels_to_EMU(104), pixels_to_EMU(88)))
ws.add_image(lg)
put('A6:F6', 'PROFORMA INVOICE', bold=True, size=18, h='center'); ws.row_dimensions[6].height = 30
put('A7:F7', 'Tax ID: 91320507MA1MMFA46W', h='right')
put('A8:F8', f"Invoice No.:{j['invoice_no']}", h='right')
put('A9:F9', f"Date.:{j['date']}", h='right')
put('A10:F10', f"Buyer: {j['buyer']}"); put('A11:F11', f"WhatsApp: {j['whatsapp']}"); put('A12:F12', f"Add: {j['address']}")
for i in range(7, 13): ws.row_dimensions[i].height = 14
for col in 'ABCDEF': ws[f'{col}5'].border = Border(bottom=thin)

# 价格表
put('A13:A14', 'No.', bold=True, h='center', border=True)
put('B13:C14', 'Description', bold=True, h='center', border=True)
put('D13:F13', j['term'], bold=True, h='center', border=True)
for c, t in zip('DEF', ['Quantity', 'Unit Price (USD)', 'Total Price (USD)']): put(f'{c}14', t, bold=True, h='center', border=True)
ws.row_dimensions[14].height = 28
r = 15; first = r
for i, (desc, qty, unit, tot) in enumerate(j['items'], 1):
    put(f'A{r}', i, h='center', border=True)
    put(f'B{r}:C{r}', desc, bold=True, color='0000FF', border=True)
    put(f'D{r}', qty, h='center', border=True); put(f'E{r}', unit, h='center', border=True)
    put(f'F{r}', tot, h='center', border=True).number_format = '#,##0.00'
    ws.row_dimensions[r].height = 14 * lines(desc, 80) + 18
    r += 1
if j.get('discount'):
    put(f'A{r}', '', border=True); put(f'B{r}:C{r}', 'Discount', h='center', border=True)
    put(f'D{r}', '', border=True); put(f'E{r}', '', border=True)
    put(f'F{r}', -j['discount'], h='center', border=True).number_format = '#,##0.00'; r += 1
put(f'A{r}', 'Total', bold=True, h='center', border=True)
put(f'B{r}:C{r}', j['term'], h='center', border=True)
put(f'D{r}', '', border=True); put(f'E{r}', '', border=True)
put(f'F{r}', f'=SUM(F{first}:F{r-1})', bold=True, h='center', border=True).number_format = '#,##0.00'
r += 1
put(f'A{r}:F{r}', 'Remarks:', bold=True); r += 1
for t in j['remarks']:
    put(f'A{r}:F{r}', t); ws.row_dimensions[r].height = 14 * lines(t, 140); r += 1

# 部件表
put(f'A{r}', 'No.', border=True); put(f'B{r}', 'Component', border=True)
put(f'C{r}:E{r}', 'Details', border=True); put(f'F{r}', 'Qty', border=True); r += 1
for i, (comp, det) in enumerate(j['components'], 1):
    put(f'A{r}', i, border=True); put(f'B{r}', comp, border=True)
    put(f'C{r}:E{r}', det, border=True); put(f'F{r}', 'According to packing list', border=True)
    ws.row_dimensions[r].height = max(28, 14 * lines(det, 85) + 8); r += 1

# 银行（固定，不要改）
put(f'A{r}:F{r}', "Seller's Bank Information:", bold=True); r += 1
bank = ["Beneficiary name : SUZHOU GUYUN TENT CO.,LTD.",
        "Beneficiary address : No.1200, Feng Yang Road, Wei Tang Town, XiangCheng Zone, Suzhou, Jiangsu, China",
        "Beneficiary bank: China Construction Bank SUZHOU XIANGCHENG SUB-BRANCH",
        "Beneficiary account: 32250199743600005208",
        "Bank address : NO.780, HUAYUAN ROAD, XIANGCHENG DISTRICT, SUZHOU, CHINA",
        "SWIFT Code : PCBCCNBJJSS"]
b0 = r
for t in bank:
    put(f'A{r}:D{r}', t); ws.row_dimensions[r].height = 14; r += 1
sg = XImg(j['sign']); sg.width, sg.height = 150, 95; ws.add_image(sg, f'E{b0+1}')
ws.row_dimensions[r].height = 20; last = r

# 外框（双线效果用 medium）
for rr in range(1, last + 1):
    for col in 'ABCDEF':
        c = ws[f'{col}{rr}']; b = c.border
        c.border = Border(left=med if col == 'A' else b.left, right=med if col == 'F' else b.right,
                          top=med if rr == 1 else b.top, bottom=med if rr == last else b.bottom)
ws.print_area = f'A1:F{last}'
ws.page_setup.paperSize = 9
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1
ws.page_margins.left = ws.page_margins.right = 0.45; ws.page_margins.top = 0.5; ws.page_margins.bottom = 0.4
ws.print_options.horizontalCentered = True
out = j['out']; wb.save(out + '.xlsx')
subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(os.path.abspath(out)), out + '.xlsx'], check=True, capture_output=True)
print('OK', out + '.xlsx', out + '.pdf')
