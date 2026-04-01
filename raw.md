from openpyxl import load_workbook
import csv

file_path = r"C:\Users\...\your_file.xlsx"
output_file = r"C:\Users\...\sheet0_output.csv"

wb = load_workbook(file_path, read_only=True, data_only=True)
ws = wb["sheet0"]   # 👈 只处理 sheet0

with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)

    rows = ws.iter_rows(values_only=True)

    # 表头
    header = next(rows)
    writer.writerow(header)

    for i, row in enumerate(rows, start=1):
        writer.writerow(row)

        if i % 10000 == 0:
            print(f"{i} rows processed")

wb.close()
print("done")
