---
name: pi
description: 客户确认下单或要求正式报价单/形式发票（PI / proforma invoice）时，用 tools/pi.ps1 从现有模板生成 Excel 格式的 PI。
argument-hint: <系列> <宽x长> [客户名] [国家] [贸易术语] [运费]
---
需求：$ARGUMENTS

**开始前先读 kb/政策/报价单检查清单.md，交付前逐条核对。**

## 步骤
1. 从参数、客户卡片或聊天中收集以下信息：
   - 系列：Classic、Wedding、Atrium、Transparent、Curved、Exhibition（款式选不准时问用户）
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
- 发文件前提醒用户核对：文件名里的尺寸和贸易条款（EXW/CIF、尺寸是否对应客户）、赠品档位、保修期（2–3 年）。
- 在 Cowork 云端没法运行 pi.ps1（需要 Windows + Excel）：改用 `tools/报价单_参考脚本_LibreOffice.py` 的做法。
- 中庭款新版图纸立柱每 5 m 一根（20 m 跨每榀 5 根），旧版"三视图"每榀 4 根，以新版为准。
