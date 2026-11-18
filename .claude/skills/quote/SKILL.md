---
name: quote
description: 客户给出了尺寸或面积并要价格，或者需求已经确认、在等报价。用报价脚本计算后起草报价消息。例：/quote 铝合金 20x50 透明 2套 加双开门2个
argument-hint: <类型> <宽x长> [数量] [透明] [配件]
---
报价需求：$ARGUMENTS

## 步骤
1. **确定参数**（从客户消息或卡片里取）：
   - 类型：Classic、Wedding、Exhibition、Transparent、A 型 → `铝合金`；预算低的或客户要 steel → `钢铝`；Pagoda 或 3–10 米方形 → `塔篷`
   - 透明 → `--transparent`；N 套 → `--qty N`；配件 → `--addon 名称=数量`（名称用 kb/价格/配件价格.csv 第一列的中文名，例如 双开玻璃门、膨胀螺丝、钢钎地锚80cm）
   - 客户只给了面积或人数：先换算成常见尺寸（每位宾客约 1–1.2 ㎡，宴会桌席约 1.5 ㎡），在【回复】里给出 1–2 个尺寸建议，并说明这是假设
2. 运行 `node tools/quote.mjs <类型> <宽x长> [选项]`。**不要读 CSV。**
3. 脚本返回 ❌：不报价。【回复】写"I'll confirm the price for this size/style with our factory and get back to you shortly"，【要点】说明需要人工定价的原因。
4. 脚本给出 ⚠ 警告：全部转述到【要点】里。
   - 用户在需求里写了"底价"：加 `--floor`，底价**只写在【要点】里**，【回复】仍然用报价。
5. 起草【回复】：
   - 款式、尺寸、数量；主型材；边高/顶高
   - 单价 USD/㎡ 和总价，**EXW**
   - 交期 25–30 个工作日，报价 15 天有效
   - 结尾追问一个问题：目的港（用于报 CIF）、地面情况（用于配地锚）或使用日期
6. 更新卡片：阶段改为"已报价"，"已报价"字段写 `日期 类型 尺寸 单价 合计 EXW`，下一步日期 +2 天。
7. 客户要正式报价单时，用 `pi` skill。

## 示例
> Here's the quotation for your wedding tent:
> • A-shape aluminum tent 20m x 30m (600 m²), white PVC
> • Main profile 203x112mm, side height 4m, ridge height 7.1m
> • USD 31.82/m² → Total USD 19,090.91 (EXW)
> • Lead time 25–30 working days, price valid for 15 days
> Which port should we ship to? I can quote CIF as well.

## 不要做的事
- 不显示底价，不主动让价（`可让价空间` 只写在【要点】里给用户看）
- 不估算运费：要 CIF 就请用户提供运费
- CBM 和重量是粗估值，客户没问就不写进【回复】
