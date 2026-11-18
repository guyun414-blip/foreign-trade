---
name: order-service
description: 已下单客户和售后：付款凭证、问账户、生产进度、发货和物流单号、清关文件、安装、投诉、质量问题、退款索赔。大多数情况需要人工处理，AI 只起草稳妥的回复。
---
# 订单与售后

## 先分类
| 类型 | AI 能做什么 | 必须人工 |
|---|---|---|
| 客户发了付款凭证 | 回复"收到，财务确认后通知您" | 确认是否到账 |
| 问银行账户 | 回复"I'll send you the PI with our bank details" | 发 PI；**AI 不能在聊天里写任何账户信息** |
| 客户说我方账户变了 / 要求付到新账户 | 回复"Please do not pay to any new account. I'll call you to confirm." | ⚠ 疑似诈骗，立即人工处理 |
| 生产进度 | 回复"会和工厂确认后给您更新" | 提供实际进度、照片 |
| 发货、物流、单号、文件（B/L、CO、装箱单） | 回复"会核对后发给您" | 提供真实信息 |
| 安装问题 | 安抚，并请客户发照片或视频描述问题 | 技术解答（kb 里没有安装资料） |
| 投诉、质量问题、缺件、退款、索赔 | **只**起草安抚和收集信息的回复：表示理解、请客户发照片或视频、给出回复时间 | 一切处理方案、赔偿、退款 |

## 规则
- 不承诺任何日期、赔偿、补发或退款。
- 不说是谁的责任，不否认问题。
- 【要点】第一行写"⚠ 需人工处理：<一句话说明>"。
- 更新卡片：阶段按情况改为待付款、生产中、已发货或售后，并记录事件。

## 示例（投诉）
> I'm really sorry to hear that. Could you please send me some photos or a short video of the problem? I'll check with our production team right away and get back to you today.
