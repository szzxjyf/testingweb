from openpyxl import load_workbook

# read_only=True 是关键，它不会把整个文件加载进内存
wb = load_workbook("your_file.xlsx", read_only=True)
sheet = wb.worksheets[0] # 获取第一个 sheet

for row in sheet.iter_rows(values_only=True):
    # 在这里逐行处理数据，例如存入数据库或进行计算
    print(row)
