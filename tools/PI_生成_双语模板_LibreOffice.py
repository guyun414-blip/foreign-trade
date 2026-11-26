# PI 生成·双语版（2026-11-24 按用户给的 "PI 20250724" 模板版式：无单价列、描述双语、部件表双语）
# 用法：python3 tools/PI_生成_双语模板_LibreOffice.py job.json → <out>.xlsx + <out>.pdf
# job 字段：out logo sign invoice_no date buyer whatsapp address term
#   items [[标题(蓝色粗体), 英文描述, 第二语言描述, 数量, 金额], ...]
#   remarks [[英文, 第二语言], ...]   components [[英文部件, 第二语言部件, 英文说明, 第二语言说明], ...]
#   qty_text 部件表 Qty 列文字（默认 According to packing list）
# 抬头用 Evelyn 的对外联系方式；银行信息固定为建设银行账户（用户 11-24 确认），不要改。
import json, sys, subprocess, os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.drawing.image import Image as XImg
j = json.load(open(sys.argv[1], encoding='utf-8'))
wb = Workbook(); ws = wb.active; ws.title = 'PI'
FN = 'Times New Roman'; thin = Side(style='thin'); med = Side(style='medium')
GREY = PatternFill('solid', fgColor='D9D9D9')
for col, w in zip('ABCDE', [6, 26, 52, 14, 16]): ws.column_dimensions[col].width = w
def put(rng, v, bold=False, size=11, color=None, h='left', border=False, fill=None, v_='center'):
    a = rng.split(':')[0]
    if ':' in rng: ws.merge_cells(rng)
    c = ws[a]; c.value = v
    c.font = Font(name=FN, bold=bold, size=size, color=color)
    c.alignment = Alignment(horizontal=h, vertical=v_, wrap_text=True)
    cells = [x for row in ws[rng] for x in row] if ':' in rng else [c]
    for x in cells:
        if border: x.border = Border(left=thin, right=thin, top=thin, bottom=thin)
        if fill: x.fill = fill
    return c
def nl(text, chars): return sum(max(1, -(-len(p) // chars)) for p in text.split('\n'))
# 抬头
put('B1:E1', 'SUZHOU GUYUN TENT CO., LTD', bold=True, h='center')
hdr = ['Add: No.1 Chengtai Road South, Taiping Town, Xiangcheng District, Suzhou City, Jiangsu Province, China',
       'Contact Person: Evelyn Wang    TEL/WhatsApp/WeChat: +86 18706208684',
       'E-MAIL: gysales6@guyuntent.com', 'WEBSITE: www.gy-tent.com']
for i, t in enumerate(hdr, 2): put(f'C{i}:E{i}', t)
for i, hg in zip(range(1, 6), [22, 30, 16, 16, 16]): ws.row_dimensions[i].height = hg
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.utils.units import pixels_to_EMU
lg = XImg(j['logo']); lg.width, lg.height = 104, 88
lg.anchor = OneCellAnchor(_from=AnchorMarker(col=0, colOff=pixels_to_EMU(8), row=0, rowOff=pixels_to_EMU(6)), ext=XDRPositiveSize2D(pixels_to_EMU(104), pixels_to_EMU(88)))
ws.add_image(lg)
put('A6:E6', 'PROFORMA INVOICE', bold=True, size=18, h='center'); ws.row_dimensions[6].height = 30
for col in 'ABCDE': ws[f'{col}5'].border = Border(bottom=thin)
put('A7:E7', 'Tax ID: 91320507MA1MMFA46W', h='right')
put('A8:E8', f"Invoice No.:{j['invoice_no']}", h='right'); put('A9:E9', f"Date.:{j['date']}", h='right')
put('A10:E10', j['buyer']); put('A11:E11', f"WhatsApp: {j['whatsapp']}"); put('A12:E12', j['address'])
# 价格表
put('A13:A14', 'No.', bold=True, h='center', border=True, fill=GREY)
put('B13:C14', 'Description', bold=True, h='center', border=True, fill=GREY)
put('D13:E13', j['term'], bold=True, h='center', border=True, fill=GREY)
put('D14', 'Quantity', bold=True, h='center', border=True, fill=GREY)
put('E14', 'Total Price\n(USD)', bold=True, h='center', border=True, fill=GREY); ws.row_dimensions[14].height = 30
r = 15; first = r
blue = InlineFont(rFont=FN, b=True, color='0000FF', sz=11); norm = InlineFont(rFont=FN, sz=11)
for i, (title, en, fr, qty, tot) in enumerate(j['items'], 1):
    put(f'A{r}', i, h='center', border=True)
    c = put(f'B{r}:C{r}', '', border=True)
    parts = [TextBlock(blue, title)]
    if en: parts.append(TextBlock(norm, ', ' + en if not en.startswith('(') else ' ' + en))
    if fr: parts.append(TextBlock(norm, '\n\n' + fr))
    c.value = CellRichText(*parts)
    put(f'D{r}', qty, h='center', border=True)
    put(f'E{r}', tot, h='center', border=True).number_format = '#,##0.00'
    txt = title + ', ' + en + ('\n\n' + fr if fr else '')
    ws.row_dimensions[r].height = 15 * nl(txt, 82) + 10; r += 1
put(f'A{r}', 'Total', bold=True, h='center', border=True)
put(f'B{r}:C{r}', j['term'], h='center', border=True); put(f'D{r}', '', border=True)
put(f'E{r}', f'=SUM(E{first}:E{r-1})', bold=True, h='center', border=True).number_format = '#,##0.00'
ws.row_dimensions[r].height = 22; r += 1
put(f'A{r}:E{r}', 'Remarks / Remarques :', bold=True); r += 1
for en, fr in j['remarks']:
    t = en + ('\n' + fr if fr else ''); put(f'A{r}:E{r}', t); ws.row_dimensions[r].height = 15 * nl(t, 125) + 2; r += 1
# 部件表
put(f'A{r}', 'No.', border=True, fill=GREY); put(f'B{r}', 'Component', border=True, fill=GREY)
put(f'C{r}', 'Details', border=True, fill=GREY); put(f'D{r}:E{r}', 'Qty', border=True, fill=GREY); r += 1
qt = j.get('qty_text', 'According to packing list\nSelon liste de colisage')
for i, (ce, cf, de, df) in enumerate(j['components'], 1):
    put(f'A{r}', i, border=True, v_='top'); put(f'B{r}', ce + '\n' + cf, border=True, v_='top')
    put(f'C{r}', de + '\n' + df, border=True, v_='top'); put(f'D{r}:E{r}', qt, border=True, v_='top')
    ws.row_dimensions[r].height = max(15 * nl(de + '\n' + df, 62) + 4, 15 * nl(ce + '\n' + cf, 24) + 6, 36); r += 1
# 银行（建设银行，固定）
put(f'A{r}:E{r}', "Seller's Bank Information:", bold=True); r += 1
bank = ["Beneficiary name : SUZHOU GUYUN TENT CO.,LTD.",
        "Beneficiary address : No.1200, Feng Yang Road, Wei Tang Town, XiangCheng Zone, Suzhou, Jiangsu, China",
        "Beneficiary bank: China Construction Bank SUZHOU XIANGCHENG SUB-BRANCH",
        "Beneficiary account: 32250199743600005208",
        "Bank address : NO.780, HUAYUAN ROAD, XIANGCHENG DISTRICT, SUZHOU, CHINA",
        "SWIFT Code : PCBCCNBJJSS"]
b0 = r
for t in bank: put(f'A{r}:C{r}', t); ws.row_dimensions[r].height = 16 * nl(t, 95); r += 1
sg = XImg(j['sign']); sg.width, sg.height = 150, 95; ws.add_image(sg, f'D{b0+1}')
ws.row_dimensions[r].height = 20; last = r
for rr in range(1, last + 1):
    for col in 'ABCDE':
        c = ws[f'{col}{rr}']; b = c.border
        c.border = Border(left=med if col == 'A' else b.left, right=med if col == 'E' else b.right,
                          top=med if rr == 1 else b.top, bottom=med if rr == last else b.bottom)
ws.print_area = f'A1:E{last}'; ws.page_setup.paperSize = 9
ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
ws.page_margins.left = ws.page_margins.right = 0.45; ws.page_margins.top = 0.5; ws.page_margins.bottom = 0.4
ws.print_options.horizontalCentered = True
out = j['out']; wb.save(out + '.xlsx')
subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(os.path.abspath(out)), out + '.xlsx'], check=True, capture_output=True)
print('OK', out + '.xlsx', out + '.pdf')
