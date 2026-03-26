import pandas as pd

# 假设你的 dataframe 叫 df
cols_to_check = ['DFAC2N', 'PO@BNM', 'PO@PNM']

# 定义关键词，用 | (或) 符号连接
# '总公司|总司|分司|分公司'
keywords = '总公司|总司|分司|分公司'

# 核心过滤逻辑
# 1. 选中指定的列
# 2. 对每一行应用 contains 检查
# 3. .any(axis=1) 表示只要其中一列命中即为 True
mask = df[cols_to_check].apply(lambda x: x.str.contains(keywords, na=False)).any(axis=1)

# 获取结果
result_df = df[mask]
