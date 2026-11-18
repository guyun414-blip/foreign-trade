---
name: quote
description: 客户给出了尺寸或面积并要价格，或者需求已经确认、在等报价。用报价脚本计算后起草报价消息。例：/quote 铝合金 20x50 透明 2套 加双开门2个
argument-hint: <类型> <宽x长> [数量] [透明] [配件]
---
报价需求：$ARGUMENTS

## 步骤
1. **确定参数**（从客户消息或卡片里取）：
   - 类型：Classic、Wedding、Exhibition、Transparent、A 型 → `铝合金`；预算低的或客户要 steel → `钢铝`；Pagoda 或 3–10 米方形 → `塔篷`；Atrium 中庭款 → 见下方"Atrium"一节
   - 透明 → `--transparent`；N 套 → `--qty N`；配件 → `--addon 名称=数量`（名称用 kb/价格/配件价格.csv 第一列的中文名，例如 双开玻璃门、膨胀螺丝、钢钎地锚80cm）
   - 客户只给了面积或人数：先换算成常见尺寸（圆桌坐席每人 1.5–2 ㎡；长条宴会桌、剧院式排座或站立酒会每人约 1 ㎡；150 人婚宴约 300–400 ㎡），在【回复】里给出 1–2 个尺寸建议，并说明这是估算
   - 客户报的尺寸明显偏大：分两条说。第一条"我尊重你的选择"；第二条从专业角度推荐合适尺寸，并说明能省预算
2. 运行 `node tools/quote.mjs <类型> <宽x长> [选项]`。**不要读 CSV。**
3. 脚本返回 ❌：不报价。【回复】写"I'll confirm the price for this size/style with our factory and get back to you shortly"，【要点】说明需要人工定价的原因。
4. 脚本给出 ⚠ 警告：全部转述到【要点】里。
   - 用户在需求里写了"底价"：加 `--floor`，底价**只写在【要点】里**，【回复】仍然用报价。
5. **贸易术语：默认报 CIF。**
   - 港口按客户 WhatsApp 区号对应的国家选，港口表在 kb/政策/交易条款.md；拿不准客户在哪就先问客户。
   - **运费一律问用户**，在【要点】里写"CIF <港口> 运费待你提供"，不要估算。用户还没给运费时，先起草不含运费的部分，等运费到了再补总价。
   - 内陆国 CIF 只到港口，不说送到首都或家门口。
6. 起草【回复】（语气见 kb/政策/话术规范.md）：
   - 款式、尺寸、数量；主型材；边高/顶高
   - 单价 USD/㎡、篷房小计、海运费、**CIF <港口> 总价**
   - 交期 25–30 个工作日，报价 15 天有效
   - 锁价：付定金锁定篷房价格，材料涨价也不变；海运费会随时变动、不锁定
   - 赠品（见下方）
   - 结尾追问一个问题：使用日期、地面情况，或确认港口
7. 更新卡片：阶段改为"已报价"，"已报价"字段写 `日期 类型 尺寸 单价 合计 贸易术语`，下一步日期 +2 天。
8. 客户要正式报价单或 PDF 报价文件时：先读 kb/政策/报价单检查清单.md，再用 `pi` skill。
9. 客户要图纸：`python3 tools/find_drawing.py <系列> <宽x长>`。✅ 且顶高和本次报价一致 → 在【要点】里给出图片路径，提醒用户手动发送；⚠ 或 ❌ → 问用户。

## Atrium 中庭篷房（不在价格表里）
- 单价：人字顶同跨度报价（`node tools/quote.mjs 铝合金 <宽x长>` 的 CNY 单价）上加价，跨度 10–18 m 加 110 RMB/㎡，20–50 m 加 100 RMB/㎡，÷6.6 换美金。**用户给了具体单价就用用户的**。
- 顶高：人字顶公式 +1.2 m（见 kb/产品/通用规格.md；20 m 跨、边高 4 m → 8.3 m）。
- 体积：面积 × 0.03 × 1.25 CBM。
- 款式描述：黑色铝框架，透明 PVC 墙，中间屋顶抬高，高端吸睛。顶布颜色以用户说的为准（可以是白色顶布）。

## 赠品（本月付定金才送，说法："本月活动福利，方便你的团队安装"）
| 订单金额 | 赠品 |
|---|---|
| 2 万美金以下 | 电动安装工具（1 万多的单也不送灯） |
| 2 万以上 | 电动工具 + 2 架梯子 |
| 3 万以上 | 电动工具 + 梯子或脚手架 + 灯具；**顶高 8 米以上直接送脚手架** |
- 不写订单金额；不让客户挑赠品。
- 报价、催单或用户提醒时才加，不是每条都加；拿不准金额先问用户。

## 示例
> Great choice! Here's your quotation, CIF Durban:
> 1️⃣ A-shape aluminum tent 20m x 30m (600 m²), white PVC
> 2️⃣ Main profile 203x112mm, side height 4m, ridge height 7.1m
> 3️⃣ USD 31.82/m² → tent USD 19,090.91, sea freight USD xxx, total USD xxx (CIF Durban)
> Lead time 25–30 working days, price valid for 15 days. Once you pay the deposit, the tent price is locked, even if material costs rise. Sea freight may change from time to time.
> 🎁 This month's bonus: electric installation tools + 2 ladders to make setup easier for your team.
> May I know your event date? I'll be happy to plan a timeline that works best for you 😊

## 不要做的事
- 不显示底价，不主动让价（`可让价空间` 只写在【要点】里给用户看）
- 不估算运费
- CBM 和重量是粗估值，客户没问就不写进【回复】
