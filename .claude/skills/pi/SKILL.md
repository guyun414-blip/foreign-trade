---
name: pi
description: 客户确认下单或要求正式报价单/形式发票（PI / proforma invoice）时，用 tools/pi.ps1 从现有模板生成 Excel 格式的 PI。
argument-hint: <系列> <宽x长> [客户名] [国家] [贸易术语] [运费]
---
需求：$ARGUMENTS

**开始前先读 kb/政策/报价单检查清单.md，交付前逐条核对。**

## 步骤
1. 从参数、客户卡片或聊天中收集以下信息：
   - 系列：Classic、Wedding、Atrium、Transparent、Curved、Exhibition（款式选不准时问用户）。**中庭客户没有特殊说明默认 WT 款（白顶透明墙黑框），模板 `3.1WT  Atrium tent 模板.xlsx`**
   - 尺寸、数量、颜色（可选）
   - 客户名、WhatsApp、国家或地址
   - 贸易术语：默认 CIF，港口按客户 WhatsApp 国家选（kb/政策/交易条款.md）。运费一律由用户提供，**不要自己估**
   - 配件：`-Addon "双开玻璃门=2"`
   缺少客户名：先问用户，不要自己编。
2. 运行：
   ```
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/pi.ps1 -Series Classic -Size 20x50 -Qty 1 -Buyer "名字" -WhatsApp "+xx" -Country "国家" -Incoterm "EXW"
   ```
   - Atrium 和 Curved 不在价格表里：必须由用户给出单价，加 `-UnitUsd 34.85`
   - 用户已经同意让价：加 `-UnitUsd <让价后的美元单价>`，不要走脚本价格
   - CIF：`-Incoterm "CIF Mombasa" -Shipping 1500`
   - 用户知道准确的体积和重量：`-Cbm 18 -Weight 4800kg`
3. 把脚本输出的 ⚠ 警告全部转述到【要点】里，并提醒用户：
   - 用 Excel 打开文件核对一遍，然后**手动**通过 WhatsApp 发给客户（文件在 `输出/PI/`）
   - 银行信息是模板原有的，**不要改**
4. 【回复】示例："Please find the PI attached. Kindly check the details, and once confirmed you can arrange the 30% deposit. Production starts right after we receive it."
5. 更新卡片：阶段改为"待付款"，记录 PI 文件名和金额。

## ⭐ PI 标准模板（2026-11-22 用户指定，优先用这个）
- 模板：`原始资料/PI模板/PI Sulaiman 2x 20x40m EXW 2026.11.19 (deposit 35000).pdf`。**PI 是单独的一页式发票，不要拿报价单改抬头当 PI**（11-22 Steven 第一版就是这样做错的）。
- 生成：`python3 tools/PI_生成_LibreOffice.py job.json`（需要 LibreOffice；Cowork 云端可用），字段说明见脚本头部；logo/签章图在 `原始资料/PI模板/logo.png、sign.png`。示例 job：`输出/PI/job_Steven_2026-11-22.json`。
- 版式：抬头（logo + 公司、地址、Evelyn Wang、邮箱、网站）→ PROFORMA INVOICE → 右侧 Tax ID: 91320507MA1MMFA46W / Invoice No. / Date → 左侧 Buyer、WhatsApp、Add → 价格表（No. | Description 蓝色粗体 | 贸易术语列头下 Quantity / Unit Price / Total Price）→ 可选 Discount 行 → Total 行 → Remarks 4 条 → 部件表（Component / Details / Qty=According to packing list）→ 银行信息（建设银行，固定）+ 签章。
- Invoice No.：`GYZP + yyyymmdd + 两位序号`（如 GYZP2026112201），发前请用户确认编号。
- 描述写法：款式, (size: 宽m*长m*边高m), Covering area, Ridge height, Bay distance, 主型材, Aluminum alloy 6061-T6, Color/PVC 克重, "Specification according to quotation."。CIF 单加一行 "Sea freight to <港口> port"（1 Lot）。
- Remarks 1 写定金和尾款的具体金额："USD x as deposit, balance (USD y) before shipment."；3 写包装 + CBM + 毛重；4 写 HS Code。
- 个人客户抬头只写姓名，不加公司/昵称。

## 尺寸图（报价单/PI 里的 3D Dimension Sketch）
每做一份报价单或 PI 都要换成本单尺寸的图，模板自带的图不能用。
1. 查图：`python3 tools/find_drawing.py <系列> <宽x长> [--eave 边高]`（系列直接用 Classic/Wedding/Atrium/Transparent/Exhibition 等）。电脑上没有 python 时，直接在 `Tent 建构图/_索引.csv` 里按"款式,宽,长"查，规则相同
2. 按结果处理：
   - **✅ 且图上边高、顶高和本单规格表一致** → 直接替换，在【要点】里写用了哪张图
   - **⚠**（顶高和公式不一致、边高不同、索引里没有数字）→ 先自己打开图核对：图上数字和本单规格一致就替换并在【要点】说明；不一致就**问用户**用这张、改规格，还是另出图
   - **❌ 没有这个尺寸或款式**（如 Curved 弧形）→ **问用户**：提供图 / 用相近尺寸的图 / 这次不放 3D 图。不要拿别的尺寸凑
3. 替换方法：
   - Cowork 云端（`tools/报价单_参考脚本_LibreOffice.py` 的做法）：模板第 23 行那张图换成新图，宽度保持 23200（1/100 mm），按图片宽高比加大第 23 行行高，图片不变形、不出格
   - Windows `pi.ps1`：脚本不会换图，在【要点】里写明要换的图片路径，提醒用户在 Excel 里手动替换
4. 用户发来新图或确认了可疑图：放进 `Tent 建构图/` 对应文件夹并按 `_说明.md` 命名，更新 `_索引.csv`

## 脚本失败时
脚本出错会自动删除半成品，不会留下错误的文件。报错内容原样告诉用户。最常见的原因：价格表里没有这个尺寸（需要加 `-UnitUsd`），或者 Excel 正在占用模板文件。

## 其他规则（来自以往做法）
- 抬头用 kb/公司信息.md 的对外联系方式；PI 需要盖公司章。
- 定金取整数，零头放进尾款。
- 中庭款图纸：每榀 4 根柱、中间抬高；开间超过 8 个只标总长。人字顶按坡度画。
- 发文件前提醒用户核对：文件名里的尺寸和贸易条款（EXW/CIF、尺寸是否对应客户）、保修期（2–3 年）。
- 在 Cowork 云端没法运行 pi.ps1（需要 Windows + Excel）：改用 `tools/报价单_批量生成_LibreOffice.py`（见下节）。
- 中庭款新版图纸立柱每 5 m 一根（20 m 跨每榀 5 根），旧版"三视图"每榀 4 根，以新版为准。

## Cowork 云端批量生成报价单（2026-11-19 整理，`tools/报价单_批量生成_LibreOffice.py`）
1. 把要用的模板（`原始资料/报价模板/1.Classic / 3.1WT Atrium（中庭默认，复制成 wt.xlsx）/ 5.Curved`）、建构图、产品照片 stage 到云端 `/tmp/q/`，写 `/tmp/q/jobs.json`，一个 job 一份报价单：
   - `tpl` 模板；`out` 文件名；`buyer` `wa` `country` `no`
   - `a9`：产品描述里要替换的文字（顶布/围布颜色、主型材、Warranty 5 years → 2-3 years）
   - `cells`：规格表和价格表单元格（Classic/Atrium：B12 尺寸、D12/E12 宽长、F12 边高、G12 顶高、H12 开间、I12 型材、H15 单价公式如 `=200/6.6`、I17 贸易术语、I18 CBM、I19 重量、I20 运费、I21 总价；Curved 列位置不同：I17 CBM、I18 重量、I19 运费、I20 总价，没有贸易术语行，写在 A19 标签和 A35 条款里）
   - `img`：产品照片替换；`sketch`：Atrium/Curved 模板自带图位置换成本尺寸建构图；`addsketch`：Classic 模板没有图位，插两行放建构图；`nosketch`：没有对应尺寸的图时删掉模板旧图并写"available on request"
   - `extras`：配件行（玻璃墙、玻璃门、地板等），插在篷房行下面，Sum 自动改成 SUM 公式；按件计价的加第 7 项 `"pcs"`
   - `money`：需要显示两位小数的运费、总价单元格（有 extras 时地址顺延）
2. 版式（用户 11-19 定）：**2 页**。第 1 页：抬头 → 产品描述 → 规格 → 价格 → 总价 → **建构图**；第 2 页：材料配件 → 材料保障 → 固定方式 → 条款和银行信息。打印区域只设 A:J，缩放比例按宽度和两页高度自动算，表格铺满页宽。
3. 图片不用 GraphicCrop（Excel/WPS 打开 xls 会丢图），脚本先用 PIL 裁好再放。
4. 多港口：每个港口单独一份（如 `_CIF_Durban_` 和 `_CIF_WalvisBay_`）；多款式也各一份。
5. 生成后把每份 PDF 渲染成图看一遍（建构图在第 1 页、没有被切开的表格），再 SendUserFile 给用户并 commit 到 `输出/报价/`；同一客户的旧版本删掉，避免发错。

### 3.1WT Atrium 模板（wt.xlsx）的参数
- 图片序号：产品照片 `img {"8": ...}`（用 `原始资料/产品照片/Atrium_白顶透明墙_湖边实景.jpg`）；建构图 `sketch [9, 图, 22]`；工厂照片 `factory [5,6,7,34]`。
- 这份模板原本是埃及客户的**定制单**（客户要透明顶），只当版式参考。默认款式一律是 **白色 PVC 顶、四周透明墙、黑框**：A9 里 "Top cover: … Transparent  PVC"（两个空格）替换成 White PVC，"Side Wall: … White PVC" 替换成 Transparent PVC。只有客户自己要求透明顶等定制时才按客户说的改。
- E15 写 "White roof / Clear walls\nBlack frame"；单元格位置和 3.Atrium 模板一样（A37 条款、A39 有效期）；I21 要自己写 `=I16+I20`。

## 改单脚本（2026-11-20）
`python3 tools/报价单_改单生成_LibreOffice.py jobs.json`：在 `原始资料/报价模板/8.经典白底稿 / 9.工业篷底稿` 上改客户、尺寸、单价、实景图、3D 图、EXW/CIF，一次出多份 xls+pdf，参数见脚本头部。没有 3D 图先用 `tools/画结构图_人字顶截面平面图.py` 画。

## 人民币报价单（2026-11-20 Gwembere）
在已发的 USD 报价单上改：单价写 RMB（如 210）、小计/Sum/运费/总价格式 "RMB #,##0.00"、表头 "Sub-total (RMB)"；运费人民币 = USD 部分 × 6.6 + 人民币杂费；地锚 USD3/4.5 改 RMB 19.8/29.7；银行信息不动，但提醒用户确认人民币收款账户。
