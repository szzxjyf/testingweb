# Hub Query 字段说明及 Mapping 需求

## 1. 文档目的

Hub Query 作为客户主数据映射表，用于建立不同数据源之间的关联关系。

其核心作用是：

- 统一 Customer ID；
- 补充客户中文名称、英文名称及中文简称；
- 补充组织机构代码和统一社会信用代码；
- 补充 RM 信息；
- 作为其他业务表 Mapping 的基础联合键。

---

## 2. Customer ID 生成规则

Hub Query 中通过 `ZGDCB` 和 `ZGDCS` 生成标准 Customer ID。

| 字段 | 含义 | 处理规则 |
|---|---|---|
| ZGDCB | Customer ID 左侧部分 | 左侧补 `0` 至 3 位 |
| ZGDCS | Customer ID 右侧部分 | 左侧补 `0` 至 6 位 |

生成格式：

> Customer ID = 3 位 ZGDCB + `-` + 6 位 ZGDCS

示例：

| ZGDCB | ZGDCS | Customer ID |
|---:|---:|---|
| 1 | 123 | 001-000123 |
| 12 | 45678 | 012-045678 |
| 123 | 456789 | 123-456789 |

处理要求：

1. 两个字段均按字符处理，避免前导零丢失；
2. ZGDCB 不足 3 位时左侧补零；
3. ZGDCS 不足 6 位时左侧补零；
4. 中间使用短横线连接；
5. 生成后的 Customer ID 作为 Hub Query 与其他数据表 Mapping 的主要关联字段。

---

## 3. 客户名称字段

| 字段 | 含义 |
|---|---|
| ZGC2FN | Customer ID 对应的客户中文全称 |
| ZGCSCN | Customer ID 对应的客户英文名称 |
| ZGC2CN | Customer ID 对应的客户中文简称 |

Mapping 后，其他数据表可通过 Customer ID 取得以上三类客户名称。

---

## 4. 机构识别字段

| 字段 | 含义 | 处理规则 |
|---|---|---|
| ZGIDTY | 组织机构代码前半部分 | 与 ZGIDNO 连接 |
| ZGIDNO | 组织机构代码后半部分 | 与 ZGIDTY 连接 |
| ZUIDNO | 统一社会信用代码 | 直接保留 |

组织机构代码生成规则：

> 组织机构代码 = ZGIDTY + `-` + ZGIDNO

处理要求：

1. 使用短横线连接两个字段；
2. 连接前应保留原始字符及前导零；
3. 如任一字段为空，应保留原始数据并标记 Mapping 状态，不应生成错误代码；
4. 组织机构代码和统一社会信用代码可作为 Customer ID 之外的辅助识别字段。

---

## 5. RM 字段

| 字段 | 含义 |
|---|---|
| ZYRMGR | RM Code |
| YHDS50 | RM Name |

用途：

- 通过 Hub Query 补充客户对应的 RM 信息；
- 支持后续按 RM Name 进行筛选、聚合及客户归属分析；
- RM Code 作为底层识别字段保留。

---

## 6. Mapping 逻辑

### 6.1 主要关联键

Hub Query 的主要关联键为生成后的 Customer ID。

其他业务表中的 Customer ID 应统一为：

> `000-000000`

完成格式统一后，再与 Hub Query 进行匹配。

### 6.2 Mapping 后可补充字段

其他业务表通过 Customer ID 关联 Hub Query 后，可补充：

- 客户中文全称；
- 客户英文名称；
- 客户中文简称；
- 组织机构代码；
- 统一社会信用代码；
- RM Code；
- RM Name。

### 6.3 Mapping 结果要求

建议保留以下 Mapping 状态：

| 状态 | 含义 |
|---|---|
| Matched | Customer ID 成功匹配 |
| Unmatched | Customer ID 未匹配到 Hub Query |
| Duplicate | 同一 Customer ID 在 Hub Query 中存在多条记录 |

处理要求：

1. 不得静默丢弃未匹配记录；
2. 未匹配记录应保留原始 Customer ID；
3. 重复 Customer ID 应单独识别并输出，供数据核查；
4. Mapping 后不得覆盖业务表中的原始字段，应新增标准字段或映射字段。

---

## 7. 数据质量要求

### 7.1 Customer ID

- 必须符合 `000-000000` 格式；
- 左侧固定 3 位；
- 右侧固定 6 位；
- 中间固定使用一个短横线；
- 不得因数值格式转换丢失前导零。

### 7.2 客户名称

- 三类名称字段应分别保留，不应相互覆盖；
- 空值可以保留；
- Mapping 时应保留原始名称及标准名称，便于后续比对。

### 7.3 机构代码

- 组织机构代码按 `ZGIDTY-ZGIDNO` 生成；
- 统一社会信用代码直接使用 `ZUIDNO`；
- 两类代码均作为辅助识别字段，不替代 Customer ID 的主关联作用。

---

## 8. 与后续业务表的关系

Hub Query 作为基础映射表，后续可与以下数据关联：

- TOI 数据；
- Transaction Data；
- Balance 数据；
- Deposit 数据；
- Revenue 数据；
- 客户覆盖及 RM 数据。

整体流程：

> 原始业务表  
> → 标准化 Customer ID  
> → 关联 Hub Query  
> → 补充客户名称、机构代码及 RM 信息  
> → 进入后续分析和聚合
