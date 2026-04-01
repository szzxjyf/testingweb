import pandas as pd

file_path = "your_file.xlsx"

# 读取整个工作簿里的所有 sheet，返回 dict：{sheet_name: DataFrame}
all_sheets = pd.read_excel(file_path, sheet_name=None)

# 合并所有 sheet
merged_df = pd.concat(all_sheets.values(), ignore_index=True)

# 如果想保留来源 sheet 名
# merged_df = pd.concat(
#     [df.assign(source_sheet=sheet_name) for sheet_name, df in all_sheets.items()],
#     ignore_index=True
# )

# 导出
merged_df.to_excel("merged_output.xlsx", index=False)
# 或者导出成 csv，更轻一些
# merged_df.to_csv("merged_output.csv", index=False, encoding="utf-8-sig")
