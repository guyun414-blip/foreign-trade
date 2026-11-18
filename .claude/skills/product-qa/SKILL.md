---
name: product-qa
description: 客户咨询产品本身：材料、抗风、雪载、寿命、型材、边高顶高、地面固定、款式区别、定制、配件（墙体、门、地板、内饰）、舞台桁架、安装。
---
# 产品咨询

1. 先看 CLAUDE.md 的速查，能回答就不读文件。
2. 否则按 CLAUDE.md 的路由表**只读一个文件**；kb/政策/FAQ.md 里有现成答案的，优先用它。
3. 回答时：
   - 先直接回答问题，1–3 句话，用文件里的英文表述。
   - 状态为 C（冲突）的参数：给出 PI 上的数值，同时在【要点】里写"⚠ 资料冲突：xx，请确认"。
   - 知识库里没有的（如 logo 工艺、安装服务、桁架承重）：回复"Let me check with our engineer and get back to you"，并在【要点】里写明缺什么，同时把它加进 kb/待核实.md 的"待补充的知识"一节。
   - 结尾顺势推进到报价：如果还不知道尺寸，就问尺寸。
4. 客户问"有没有图片、视频、图纸"：在【回复】里答应发送，在【要点】里提醒用户从 `原始资料/画册/` 或自己的素材库里找出来手动发。
5. 更新卡片：把客户关心的点写进"记录"（例如"关心抗风，海边使用"）。

## 示例
> Q: Can it stand strong wind?
> A: Yes, the frame is 6061-T6 aluminum with galvanized steel connectors, rated for wind up to 100 km/h. Will the tent be used near the coast or in an open area? Then I can suggest the right profile size.
>
> 【要点】抗风值资料冲突（PI 写 100–120，画册写 80–100），这里保守写了 100，请确认。
