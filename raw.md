from openpyxl import load_workbook

file_path = "input.xlsx"

wb = load_workbook(file_path, read_only=True, data_only=True)
ws = wb.active  # 如果不是第一个sheet，后面我再给你写指定sheet的版本

for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
    print(i, row)   # row 是一个 tuple
    if i >= 5:
        break

wb.close()
