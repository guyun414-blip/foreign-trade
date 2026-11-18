---
name: pi
description: 客户确认下单或要求正式报价单/形式发票（PI / proforma invoice）时，用 tools/pi.ps1 从现有模板生成 Excel 格式的 PI。
argument-hint: <系列> <宽x长> [客户名] [国家] [贸易术语] [运费]
---
需求：$ARGUMENTS

## 步骤
1. 从参数、客户卡片或聊天中收集以下信息：
   - 系列：Classic、Wedding、Atrium、Transparent、Curved、Exhibition（款式选不准时问用户）
   - 尺寸、数量、颜色（可选）
   - 客户名、WhatsApp、国家或地址
   - 贸易术语：默认 EXW。CIF/FOB 需要用户提供运费，**不要自己估**
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

## 脚本失败时
脚本出错会自动删除半成品，不会留下错误的文件。报错内容原样告诉用户。最常见的原因：价格表里没有这个尺寸（需要加 `-UnitUsd`），或者 Excel 正在占用模板文件。
