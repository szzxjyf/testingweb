# Transaction Data 逻辑需求说明

## 1. 目的

以 `CUST` 为客户主键，对付款交易进行客户信息补充、同名划转识别、收款人脱敏、交易附言分类、收款银行及收款人分析，并形成客户月度交易快照。

---

## 2. 主要字段

| 字段 | 含义 |
|---|---|
| `PO@CDT` | 付款日期，8 位数字，格式为 `YYYYMMDD` |
| `PO@CTM` | 付款时间，6 位数字，格式为 `HHMMSS` |
| `CUST` | Customer ID，格式为 `000-000000` |
| `DFAC2N` | 原始交易数据中的客户中文名称 |
| `PO@BNM` | 收款人名称 |
| `NAR` | 交易附言 |
| `BENE_BANK` | 原始收款银行名称 |
| `PO@RCL` | 收款银行 CNAPS Code |
| `PO@PCY` | 付款币种；人民币付款为 `CNY` |
| `AMT` | 付款金额 |

---

## 3. Customer ID 关联

通过 `CUST` 与 Hub Query 中的 Customer ID 关联，取得：

| Hub Query 字段 | 含义 |
|---|---|
| `ZGC2FN` | 客户中文全称 |
| `ZGCSCN` | 客户英文名称 |
| `ZGC2CN` | 客户中文简称 |

Hub Query 的 Customer ID 生成规则：

- `ZGDCB` 左侧补零至 3 位；
- `ZGDCS` 左侧补零至 6 位；
- 中间以短横线连接；
- 格式为 `000-000000`。

---

## 4. 同名划转识别

### 4.1 名称匹配

将 `PO@BNM` 与以下名称逐一匹配：

- `ZGC2FN`
- `ZGCSCN`
- `ZGC2CN`
- `DFAC2N`

任意一个名称匹配成功，即认定为同名划转。

### 4.2 交易附言补充判断

如果名称未匹配，但 `NAR` 中包含明确的同名划转描述，也认定为同名划转，例如：

- 同名划转
- 同名转账
- 同名账户划转
- 同户名划转
- 本人账户划转
- same name transfer
- same-name transfer
- transfer between same-name accounts
- own account transfer

建议生成字段：

- `Same_Name_Transfer_Ind`：`1` 为同名划转，`0` 为非同名划转。

---

## 5. 收款人识别及脱敏

当 `PO@BNM` 的字符数小于或等于 4 时：

- 识别为个人收款人；
- 仅保留第一个字符；
- 其余字符以 `*` 隐藏。

示例：

| 原始名称 | 展示名称 |
|---|---|
| 张三 | 张* |
| 王小明 | 王** |
| 欧阳娜娜 | 欧*** |

汇总和排序应使用原始名称，脱敏仅用于展示，避免不同收款人因脱敏结果相同而被合并。

---

## 6. 客户月度交易汇总

以 `CUST` 和月份为维度，统计：

- 当月付款笔数；
- 当月付款总金额；
- 同名划转笔数及金额；
- 集团内划转笔数及金额；
- 非工作时间付款笔数及金额。

---

## 7. 收款银行分析

### 7.1 银行识别规则

从 `PO@RCL` 提取前三位。

特殊代码：

`313、314、320、323、402、600、904、906、910`

处理规则：

1. 前三位属于特殊代码：直接使用原始 `BENE_BANK` 名称进行汇总；
2. 前三位不属于特殊代码：按前三位汇总，并映射为对应的标准银行名称。

### 7.2 汇总及 Top 5

以 `CUST` 和归类后的银行为维度，统计：

- 付款笔数；
- 付款总金额。

排序规则：

1. 付款笔数从高到低；
2. 笔数相同时，付款金额从高到低；
3. 每个客户保留前五家银行。

输出内容：

- Top 1–5 Bank
- 对应付款笔数
- 对应付款金额

完整的客户—银行汇总结果需要保留，供后续分析使用。

---

## 8. 收款人分析

以 `CUST` 和原始 `PO@BNM` 为维度，统计：

- 付款笔数；
- 付款总金额。

排序规则：

1. 付款笔数从高到低；
2. 笔数相同时，付款金额从高到低；
3. 每个客户保留前五个收款人。

展示时，对符合个人识别规则的收款人名称进行脱敏。

---

## 9. 交易附言分类

关键词采用包含匹配，使用最小有效关键词，避免重复配置。

| 分类 | 中文关键词 | 英文关键词 | 说明 |
|---|---|---|---|
| 工资 | 工资、薪资、薪金、薪酬、奖金、津贴、补贴、加班费、佣金、遣散费、离职补偿 | salary、payroll、wage、remuneration、bonus、allowance、overtime、commission、severance | 命中任一关键词，归类为“工资” |
| 报销 | 报销、费用返还、垫付返还、代垫返还 | reimbursement、expense claim、expense refund、expense repayment、out-of-pocket | 命中任一关键词，归类为“报销” |
| E-Tax | 税、税款、缴税、纳税、税务、增值税、消费税、所得税、资源税、城建税、房产税、土地使用税、土地增值税、耕地占用税、契税、车辆购置税、车船税、印花税、烟叶税、环保税、教育费附加 | tax、taxation、VAT、CIT、IIT、excise tax、income tax、property tax、stamp duty、tax payment | 不包括海关、关税和进口环节税款 |
| E-Port | 海关、关税、报关、进口税、出口税、进口增值税、进口消费税、船舶吨税、行邮税、电子口岸、单一窗口 | customs、customs duty、tariff、import duty、export duty、import VAT、customs clearance、e-port、single window | 同时命中 E-Tax 时，优先归类为 E-Port |
| 货币基金 | 货币基金、基金申购、基金认购、现金管理基金、同业划转 | money market fund、MMF、money fund、fund subscription、fund purchase、interbank transfer | 仅出现“同业划转”时，需结合收款银行或其他基金类信息判断 |
| 集团内划转 | 集团间转款、集团间划转、集团内转款、集团内划转、母公司、子公司、兄弟公司、关联公司、关联方、内部往来、资金归集 | intercompany transfer、intragroup transfer、group transfer、parent company、subsidiary、sister company、affiliate、related party、cash pooling | 不以同名划转为前提 |
| 其他 | 未命中以上关键词 | 未命中以上关键词 | 暂不分类 |

分类优先级：

`E-Port → E-Tax → 集团内划转 → 货币基金 → 工资 → 报销 → 其他`

---

## 10. 标签叠加逻辑

### 10.1 基础标签

建议保留：

- `Same_Name_Transfer_Ind`
- `Intragroup_Transfer_Ind`
- `Narrative_Category`
- `Off_Hours_Payment_Ind`
- `Matched_Keyword`

### 10.2 组合规则

除“集团内划转”外，工资、报销、E-Tax、E-Port 和货币基金等分类，只有在同时满足同名划转条件时，才生成相应的整合标签，例如：

- 同名工资
- 同名报销
- 同名 E-Tax
- 同名 E-Port
- 同名货币基金

集团内划转不以同名划转为前提，可以独立打标。

同一笔交易可以同时具有多个标签，各标签之间不互相覆盖。

---

## 11. 非工作时间付款

根据 `PO@CTM` 判断：

- 早于 `08:00:00`；
- 晚于 `18:00:00`。

满足任一条件，即标记为非工作时间付款。

现阶段建议设置：

- `Off_Hours_Payment_Ind`
- 客户当月非工作时间付款笔数
- 客户当月非工作时间付款金额
- “存在非工作时间付款”标签

“非工作时间付款较多”的具体门槛后续再确定。

---

## 12. 最终客户快照

每个 Customer ID 的月度快照至少应包括：

- 当月付款笔数及总金额；
- Top 5 收款银行及对应笔数、金额；
- Top 5 收款人及对应笔数、金额；
- 同名划转笔数及金额；
- 集团内划转笔数及金额；
- 交易附言分类及组合标签；
- 非工作时间付款笔数、金额及标签。
