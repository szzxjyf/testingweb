import pandas as pd

# 1. 定义需要检查的列和关键词
cols_to_check = ['DFAC2N', 'PO@BNM', 'PO@PNM']
keywords = '总司|分司'  # 这样写可以同时涵盖 总公司/总司/分公司/分司

# 2. 条件一：三列中任意一列包含关键词
mask_keywords = df[cols_to_check].apply(lambda x: x.str.contains(keywords, na=False)).any(axis=1)

# 3. 条件二：'DFAC2N' 和 'PO@BNM' 的前4个字符相同
# 注意：这里会自动处理，如果长度不足4位则对比全部字符
mask_same_prefix = df['DFAC2N'].str[:4] == df['PO@BNM'].str[:4]

# 4. 组合两个条件 (使用 & 表示“且”)
result_df = df[mask_keywords & mask_same_prefix]
