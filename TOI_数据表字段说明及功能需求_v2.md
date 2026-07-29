# TOI 数据表字段说明及功能需求

## 1. 文档目的

用于明确 TOI 数据表的字段含义、计算关系、数据清洗规则，以及后续筛选、聚合和展示要求。

---

## 2. 数据模块

TOI 数据表主要包括：

1. Customer Information
2. CS Coverage
3. Balance
4. Deposits
5. NII
6. NFI Details
7. Total NFI
8. Core Revenue / TOI
9. Transaction Volumes & Values
10. Digital Indicators
11. Others

除本需求中明确提出调整的字段外，其他字段暂时保留，不删除。

---

## 3. Customer Information & CS Coverage

### 3.1 字段说明

| 字段 | 含义 | 处理要求 |
|---|---|---|
| GB / Customer ID | 客户唯一编号 | 删除现有固定前缀，仅保留实际 Customer ID |
| Customer Name | 客户英文名称 | 一个 Customer Group 可对应多个 Customer Name |
| Customer Group | 客户所属集团 | 允许为空 |
| RM Code | 客户经理代码 | 底层保留，后续不作为主要展示或聚合字段 |
| RM Name | 客户经理姓名 | 支持筛选及聚合 |
| Sector | 客户所属业务板块 | 包括 GNB、GC、BB、ICG 等 |
| Team | RM 所属团队 | 支持筛选及聚合 |
| CS Coverage / CS Covered | 是否有 CS Coverage | `0` 代表无，`1` 代表有 |
| Country CSM | 国家客户服务经理 | 支持筛选及聚合 |
| Local CSM | 本地客户服务经理 | 支持筛选及聚合 |
| Team Leader of Local CSM | Local CSM 的团队主管 | 支持筛选及聚合 |

### 3.2 Customer ID 清洗规则

- 删除 Customer ID 开头的固定前缀；
- 不修改前缀之后的实际编号；
- 清洗后的 Customer ID 作为后续展示、匹配及 Mapping 使用的标准值。

---

## 4. Balance

所有字段均分别提供 2025 年和 2026 年数据。

| 字段 | 含义 |
|---|---|
| LCY Balance | 本币余额 |
| FCY Balance | 外币余额 |
| Total Balance | 总余额 |

业务关系：

- LCY Balance 对应 LCY NII；
- FCY Balance 对应 FCY NII；
- Total Balance 对应总体 NII。

---

## 5. Deposits

所有字段均分别提供 2025 年和 2026 年数据。

| 字段 | 含义 |
|---|---|
| TMD | 定期存款 |
| CASA | 活期及储蓄存款 |

---

## 6. NII

所有字段均分别提供 2025 年和 2026 年数据。

| 字段 | 含义 |
|---|---|
| LCY NII | 本币净利息收入 |
| FCY NII | 外币净利息收入 |
| NII | 总体净利息收入 |

规则：

- 字段名称中未注明 LCY 或 FCY 时，NII 代表总体 NII；
- 总体 NII 原则上由 LCY NII 与 FCY NII 汇总形成。

---

## 7. NFI Details

NFI Details 分为两类。

### 7.1 Transaction Fees

| 字段 | 含义 |
|---|---|
| LCY Collection | 本币收款手续费收入 |
| LCY Payment | 本币付款手续费收入 |
| IRTT | 外币收款手续费收入 |
| ORTT | 外币付款手续费收入 |

所有字段均分别提供 2025 年和 2026 年数据。

### 7.2 Account & Service Fees

保留当前表内全部明细字段，包括：

- Acc Srv
- HEX
- Paper COS
- RMS
- Online Banking Service Fee
- EL
- GLS
- Advising

所有字段均分别提供 2025 年和 2026 年数据。

---

## 8. Total NFI

计算关系：

> Total NFI = Transaction Fees + Account & Service Fees

对应字段：

- 2025 NFI
- 2026 NFI

IT 需确保 Total NFI 与各项 NFI Details 的汇总结果一致。

---

## 9. Core Revenue / TOI

计算关系：

> Core Revenue / TOI = NII + NFI

对应字段：

- 2025 Core Revenue / TOI
- 2026 Core Revenue / TOI

---

## 10. Transaction Volumes & Values

交易类型包括：

- IRTT
- ORTT
- LCY Collection
- LCY Payment

每类交易均需要区分：

| 指标 | 含义 |
|---|---|
| Count / Cnt | 交易笔数 |
| Amount / Amt | 交易金额 |

所有指标均分别提供 2025 年和 2026 年数据。

---

## 11. Digital Indicators

数字化指标用于标识客户是否开通对应功能。

| 字段 | 含义 |
|---|---|
| Online Banking Indicator | 是否开通网银 |
| E-Tax | 是否开通 E-Tax |
| E-Port | 是否开通 E-Port |
| ECDS | 是否开通 ECDS |
| LIS | 是否开通 LIS |

统一口径：

- `0`：未开通
- `1`：已开通

---

## 12. 筛选及聚合需求

### 12.1 支持的筛选维度

系统应支持以下字段的单独筛选及多条件交叉筛选：

- Customer Group
- Customer Name
- RM Name
- Sector
- Team
- CS Coverage
- Country CSM
- Local CSM
- Team Leader of Local CSM

要求：

- 同一字段支持多选；
- 不同字段之间支持组合筛选；
- 不同字段之间原则上采用 AND 逻辑；
- 同一字段选择多个值时采用 OR 逻辑。

### 12.2 Customer Group 展示逻辑

选择某个 Customer Group 后，系统应：

1. 展示该集团下全部 Customer Name；
2. 汇总该集团下所有客户数据；
3. 支持集团汇总与单个客户下钻；
4. 保留 Customer Group 为空的客户，并支持筛选。

### 12.3 数值字段聚合

以下字段按筛选结果进行加总：

- Balance
- Deposits
- NII
- NFI
- Core Revenue / TOI
- Transaction Count
- Transaction Amount

### 12.4 Digital Indicators 聚合

Digital Indicators 可用于统计：

- 已开通客户数量；
- 未开通客户数量；
- 产品开通率。

计算示例：

> 开通率 = 指标值为 1 的客户数量 ÷ 当前筛选范围内客户总数

---

## 13. 年度数据要求

2025 年和 2026 年数据需要支持：

- 分年度查看；
- 两年度并列对比；
- 按所选维度汇总；
- 展示年度变化值。

年度变化值计算：

> 年度变化值 = 2026 数据 - 2025 数据

如后续增加增长率：

> 增长率 =（2026 数据 - 2025 数据）÷ 2025 数据

当 2025 年数值为 0 或为空时，增长率显示为 `N/A`。

---

## 14. 数据保留要求

1. 除 Customer ID 固定前缀清洗外，现阶段不删除其他原始字段；
2. RM Code 可不在前端展示，但底层继续保留；
3. Others 部分的 OD、FX、LPLR、Adjusted Core Revenue 等字段暂时保留；
4. 暂未使用的字段可以隐藏，但不得从底层数据中删除；
5. 字段调整后应同步更新字段说明和计算逻辑。
