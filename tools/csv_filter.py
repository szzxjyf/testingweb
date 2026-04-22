"""
通用 CSV 批量筛选工具 — 从文件夹中读取多个 CSV，按任意列条件筛选。

Jupyter Notebook 用法:
────────────────────
from csv_filter import filter_csvs, save_result

# 1) 按任意一列筛选
result = filter_csvs("./data", filters={"CUST": ["ABC123", "DEF456"]})

# 2) 按任意多列组合筛选 (AND 关系)
result = filter_csvs("./data", filters={
    "CUST": ["ABC123", "DEF456"],
    "DEPT": ["Finance"],
    "STATUS": ["Active", "Pending"],
})

# 3) 不筛选，只合并所有文件
result = filter_csvs("./data")

# 4) 保存结果
save_result(result, "output.csv")
"""

import os
import glob
import pandas as pd
from datetime import datetime


# ── 自动编码读取 ──────────────────────────────────────────────
def read_csv_auto_encoding(file_path):
    """尝试多种编码读取 CSV 文件，返回 (DataFrame, encoding)"""
    for enc in ["utf-8-sig", "utf-8", "gb18030", "gbk"]:
        try:
            return pd.read_csv(file_path, encoding=enc, low_memory=False), enc
        except Exception:
            continue
    raise ValueError(f"无法解码 CSV 文件: {file_path}")


# ── 按条件筛选单个 DataFrame ─────────────────────────────────
def apply_filters(df, filters):
    """
    对 DataFrame 应用筛选条件。

    Parameters
    ----------
    df : pd.DataFrame
    filters : dict
        键为列名，值为该列需要匹配的值列表。
        多列之间是 AND 关系（同时满足）。
        例: {"COL_A": ["val1", "val2"], "COL_B": ["val3"]}

    Returns
    -------
    pd.DataFrame  筛选后的子集
    """
    if not filters:
        return df

    mask = pd.Series(True, index=df.index)

    for col, values in filters.items():
        if col not in df.columns:
            print(f"  ⚠️  列 '{col}' 不存在，跳过该条件 (现有列: {list(df.columns[:10])}...)")
            continue
        values_str = set(str(v).strip() for v in values)
        col_series = df[col].astype(str).str.strip()
        mask = mask & col_series.isin(values_str)

    return df[mask]


# ── 批量处理 ──────────────────────────────────────────────────
def filter_csvs(folder_path, filters=None, add_source=True):
    """
    遍历文件夹内所有 CSV 文件，按 filters 筛选后合并返回。

    Parameters
    ----------
    folder_path : str
        CSV 文件所在文件夹路径
    filters : dict, optional
        筛选条件。键=列名，值=匹配值列表。
        多列之间 AND 关系。为 None 时不做筛选，返回所有数据。
        例: {"COL_A": ["val1"], "COL_B": ["val2", "val3"]}
    add_source : bool
        是否添加 _source_file 列标记数据来源文件

    Returns
    -------
    pd.DataFrame  合并后的结果
    """
    csv_files = sorted(glob.glob(os.path.join(folder_path, "*.csv")))

    if not csv_files:
        print(f"⚠️  '{folder_path}' 中没有找到 CSV 文件")
        return pd.DataFrame()

    print(f"📂 找到 {len(csv_files)} 个 CSV 文件")
    if filters:
        for col, vals in filters.items():
            print(f"   筛选 {col}: {vals}")
    else:
        print("   无筛选条件，合并所有数据")
    print()

    all_results = []
    total_rows = 0
    matched_rows = 0

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        print(f"── {file_name}")

        try:
            df, enc = read_csv_auto_encoding(file_path)
            print(f"   编码: {enc} | {len(df)} 行 × {len(df.columns)} 列")
        except ValueError as e:
            print(f"   ❌ 跳过: {e}")
            continue

        total_rows += len(df)

        matched = apply_filters(df, filters)
        matched_count = len(matched)
        matched_rows += matched_count
        print(f"   ✅ 匹配: {matched_count} 行\n")

        if matched_count > 0:
            matched = matched.copy()
            if add_source:
                matched["_source_file"] = file_name
            all_results.append(matched)

    result = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()

    print("=" * 50)
    print(f"汇总: {len(csv_files)} 个文件 | 共 {total_rows} 行 | 匹配 {matched_rows} 行")

    return result


# ── 保存结果 ──────────────────────────────────────────────────
def save_result(df, output_path=None, encoding="utf-8-sig"):
    """
    保存 DataFrame 为 CSV 文件。

    Parameters
    ----------
    df : pd.DataFrame
    output_path : str, optional
        输出路径。不传则自动生成带时间戳的文件名。
    encoding : str
        输出编码，默认 utf-8-sig（Excel 友好）
    """
    if df.empty:
        print("没有数据，未生成文件。")
        return

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"filtered_output_{timestamp}.csv"

    df.to_csv(output_path, index=False, encoding=encoding)
    print(f"✅ 已保存: {output_path} ({len(df)} 行)")
