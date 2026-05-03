"""
客户交易数据统计分析模块
========================
基于 CUST（客户号）和 DFAC2N（公司名）对交易数据进行多维度统计分析。

使用方法 (Jupyter Notebook):
    from cust_analysis import *

    # 一键运行全部分析
    run_full_analysis(data)

    # 或单独调用某个分析函数
    counts = cust_value_counts(data)
    pareto_analysis(data)
    frequency_distribution(data)
    summary_stats(data)
    company_cross_analysis(data)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


# ============================================
# 全局设置
# ============================================

def _setup_plot_style():
    """设置 matplotlib 中文字体和全局样式。"""
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei', 'PingFang SC']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 120


# ============================================
# 1. 基础 value_counts 分析
# ============================================

def cust_value_counts(data, col='CUST', top_n=20, show=True):
    """
    对指定列做 value_counts 分析，打印摘要并返回结果。

    Parameters
    ----------
    data : pd.DataFrame
        原始数据表。
    col : str
        要统计的列名，默认 'CUST'。
    top_n : int
        展示前 N 名，默认 20。
    show : bool
        是否打印输出，默认 True。

    Returns
    -------
    pd.Series
        value_counts 结果（降序排列）。
    """
    counts = data[col].value_counts()

    if show:
        print(f"📊 [{col}] 基础统计")
        print(f"{'=' * 50}")
        print(f"  记录总数:       {len(data)}")
        print(f"  唯一值数量:     {data[col].nunique()}")
        print(f"  平均频次:       {counts.mean():.2f}")
        print(f"  中位数频次:     {counts.median():.1f}")
        print(f"\n🏆 Top {top_n} 排名:")
        print(f"{'-' * 50}")
        print(counts.head(top_n).to_string())
        print(f"\n📈 频次分布统计 (describe):")
        print(f"{'-' * 50}")
        print(counts.describe())

    return counts


# ============================================
# 2. 帕累托 (Pareto) 分析
# ============================================

def pareto_analysis(data, col='CUST', top_n=20, figsize=(16, 6)):
    """
    客户集中度与帕累托分析，包含 Top N 柱状图和帕累托曲线。

    Parameters
    ----------
    data : pd.DataFrame
        原始数据表。
    col : str
        要统计的列名，默认 'CUST'。
    top_n : int
        左图展示前 N 名，默认 20。
    figsize : tuple
        图表大小。

    Returns
    -------
    dict
        包含 pareto_80_pct（贡献 80% 交易量的客户占比）等关键指标。
    """
    _setup_plot_style()
    counts = data[col].value_counts()

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # --- 左图：Top N 柱状图 ---
    top = counts.head(top_n)
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top)))
    axes[0].barh(range(len(top)), top.values, color=colors)
    axes[0].set_yticks(range(len(top)))
    axes[0].set_yticklabels(top.index, fontsize=9)
    axes[0].invert_yaxis()
    axes[0].set_xlabel('交易笔数')
    axes[0].set_title(f'Top {top_n} 客户交易笔数', fontsize=14, fontweight='bold')
    for i, v in enumerate(top.values):
        axes[0].text(v + 0.5, i, str(v), va='center', fontsize=9)

    # --- 右图：帕累托曲线 ---
    cumulative_pct = counts.cumsum() / counts.sum() * 100
    customer_pct = np.arange(1, len(cumulative_pct) + 1) / len(cumulative_pct) * 100

    axes[1].plot(customer_pct, cumulative_pct.values, color='#2196F3', linewidth=2)
    axes[1].fill_between(customer_pct, cumulative_pct.values, alpha=0.15, color='#2196F3')
    axes[1].axhline(y=80, color='red', linestyle='--', alpha=0.7, label='80% 交易量')
    axes[1].set_xlabel('客户占比 (%)')
    axes[1].set_ylabel('累计交易笔数占比 (%)')
    axes[1].set_title('客户帕累托曲线 (Pareto)', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    # 标注 80% 分位点
    idx_80 = np.searchsorted(cumulative_pct.values, 80)
    pct_80 = customer_pct[idx_80] if idx_80 < len(customer_pct) else 100
    axes[1].axvline(x=pct_80, color='red', linestyle='--', alpha=0.7)
    axes[1].annotate(
        f'{pct_80:.1f}% 的客户\n贡献 80% 交易',
        xy=(pct_80, 80), fontsize=10, color='red',
        xytext=(min(pct_80 + 10, 85), 60),
        arrowprops=dict(arrowstyle='->', color='red')
    )

    plt.tight_layout()
    plt.show()

    print(f"\n📊 帕累托分析结论: {pct_80:.1f}% 的客户贡献了 80% 的交易笔数")

    return {'pareto_80_pct': round(pct_80, 2)}


# ============================================
# 3. 交易频次分布分析
# ============================================

def frequency_distribution(data, col='CUST',
                           bins=None, labels=None,
                           hist_bins=50, figsize=(16, 6)):
    """
    客户交易频次分布：直方图 + 分箱统计。

    Parameters
    ----------
    data : pd.DataFrame
        原始数据表。
    col : str
        要统计的列名，默认 'CUST'。
    bins : list or None
        自定义分箱边界。默认 [0,1,2,5,10,20,50,100,inf]。
    labels : list or None
        自定义分箱标签，需与 bins 数量匹配 (len(bins)-1)。
    hist_bins : int
        直方图 bin 数量，默认 50。
    figsize : tuple
        图表大小。

    Returns
    -------
    pd.Series
        各分箱区间的客户数量。
    """
    _setup_plot_style()
    counts = data[col].value_counts()

    if bins is None:
        bins = [0, 1, 2, 5, 10, 20, 50, 100, float('inf')]
    if labels is None:
        labels = ['1次', '2次', '3-5次', '6-10次', '11-20次', '21-50次', '51-100次', '100次+']

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # --- 左图：频次直方图 ---
    axes[0].hist(counts.values, bins=hist_bins, color='#4CAF50', edgecolor='white', alpha=0.85)
    axes[0].set_xlabel('交易笔数')
    axes[0].set_ylabel('客户数量')
    axes[0].set_title('客户交易频次分布 (直方图)', fontsize=14, fontweight='bold')
    axes[0].axvline(counts.mean(), color='red', linestyle='--',
                    label=f'均值: {counts.mean():.1f}')
    axes[0].axvline(counts.median(), color='orange', linestyle='--',
                    label=f'中位数: {counts.median():.1f}')
    axes[0].legend()

    # --- 右图：分箱统计 ---
    cust_bins = pd.cut(counts, bins=bins, labels=labels, right=True)
    bin_counts = cust_bins.value_counts().reindex(labels)

    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(labels)))
    bars = axes[1].bar(labels, bin_counts.values, color=colors, edgecolor='white')
    axes[1].set_xlabel('交易频次区间')
    axes[1].set_ylabel('客户数量')
    axes[1].set_title('客户交易频次分箱统计', fontsize=14, fontweight='bold')
    axes[1].tick_params(axis='x', rotation=45)

    for bar, val in zip(bars, bin_counts.values):
        if val > 0:
            axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                         str(val), ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.show()

    return bin_counts


# ============================================
# 4. 关键统计指标汇总
# ============================================

def _calc_gini(values):
    """计算基尼系数。"""
    sorted_vals = np.sort(values)
    n = len(sorted_vals)
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * sorted_vals) / (n * np.sum(sorted_vals)) - (n + 1) / n)


def summary_stats(data, col='CUST', show=True):
    """
    生成关键统计指标汇总表。

    Parameters
    ----------
    data : pd.DataFrame
        原始数据表。
    col : str
        要统计的列名，默认 'CUST'。
    show : bool
        是否打印输出，默认 True。

    Returns
    -------
    pd.DataFrame
        统计指标汇总表。
    """
    counts = data[col].value_counts()
    gini = _calc_gini(counts.values)
    top10_pct = counts.head(int(len(counts) * 0.1)).sum() / counts.sum() * 100

    summary = pd.DataFrame({
        '指标': [
            '记录总数',
            '唯一客户数',
            '平均交易笔数/客户',
            '中位数交易笔数/客户',
            '标准差',
            '最大交易笔数',
            '最大交易笔数客户',
            '偏度 (Skewness)',
            '峰度 (Kurtosis)',
            '变异系数 (CV)',
            '基尼系数 (Gini)',
            '前10%客户交易占比',
        ],
        '值': [
            f"{len(data)}",
            f"{data[col].nunique()}",
            f"{counts.mean():.2f}",
            f"{counts.median():.1f}",
            f"{counts.std():.2f}",
            f"{counts.max()}",
            f"{counts.idxmax()}",
            f"{stats.skew(counts.values):.2f}",
            f"{stats.kurtosis(counts.values):.2f}",
            f"{(counts.std() / counts.mean() * 100):.1f}%",
            f"{gini:.4f}",
            f"{top10_pct:.1f}%",
        ]
    })

    if show:
        print(f"📋 [{col}] 统计指标汇总")
        print("=" * 50)
        print(summary.to_string(index=False))

    return summary


# ============================================
# 5. DFAC2N 公司维度交叉分析
# ============================================

def company_cross_analysis(data, cust_col='CUST', company_col='DFAC2N',
                           max_chart_rows=30, figsize=(14, None)):
    """
    CUST × DFAC2N 交叉分析：统计各公司的交易笔数、客户数及人均交易数。

    Parameters
    ----------
    data : pd.DataFrame
        原始数据表。
    cust_col : str
        客户列名，默认 'CUST'。
    company_col : str
        公司列名，默认 'DFAC2N'。
    max_chart_rows : int
        当公司数量不超过此值时绘制图表，默认 30。
    figsize : tuple
        图表大小，高度会根据行数自动计算。

    Returns
    -------
    pd.DataFrame
        各公司统计结果。
    """
    _setup_plot_style()

    company_stats = data.groupby(company_col).agg(
        交易笔数=(cust_col, 'count'),
        唯一客户数=(cust_col, 'nunique'),
    ).assign(
        平均每客户交易数=lambda df: (df['交易笔数'] / df['唯一客户数']).round(2)
    ).sort_values('交易笔数', ascending=False)

    print(f"📊 各公司 ({company_col}) 客户交易统计:")
    print("=" * 60)
    print(company_stats.to_string())

    # 可视化
    if len(company_stats) <= max_chart_rows:
        fig_h = max(6, len(company_stats) * 0.45)
        fig, ax = plt.subplots(figsize=(figsize[0], fig_h))

        y_pos = range(len(company_stats))
        ax.barh(y_pos, company_stats['交易笔数'], color='#2196F3', alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(company_stats.index, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('交易笔数')
        ax.set_title(f'各公司 ({company_col}) 交易笔数分布', fontsize=14, fontweight='bold')

        for i, v in enumerate(company_stats['交易笔数']):
            ax.text(v + 0.5, i, str(v), va='center', fontsize=9)

        plt.tight_layout()
        plt.show()

    return company_stats


# ============================================
# 一键运行全部分析
# ============================================

def run_full_analysis(data, cust_col='CUST', company_col='DFAC2N', top_n=20):
    """
    一键运行全部分析流程。

    Parameters
    ----------
    data : pd.DataFrame
        原始数据表。
    cust_col : str
        客户列名，默认 'CUST'。
    company_col : str
        公司列名，默认 'DFAC2N'。
    top_n : int
        Top N 展示数量，默认 20。

    Returns
    -------
    dict
        包含各分析结果的字典:
        - 'value_counts': pd.Series
        - 'pareto': dict
        - 'freq_bins': pd.Series
        - 'summary': pd.DataFrame
        - 'company_stats': pd.DataFrame
    """
    print("🚀 开始全量分析...\n")

    print("\n" + "=" * 60)
    print("  第 1 部分: 基础 value_counts 分析")
    print("=" * 60)
    vc = cust_value_counts(data, col=cust_col, top_n=top_n)

    print("\n\n" + "=" * 60)
    print("  第 2 部分: 帕累托 (Pareto) 分析")
    print("=" * 60)
    pareto = pareto_analysis(data, col=cust_col, top_n=top_n)

    print("\n\n" + "=" * 60)
    print("  第 3 部分: 交易频次分布分析")
    print("=" * 60)
    freq = frequency_distribution(data, col=cust_col)

    print("\n\n" + "=" * 60)
    print("  第 4 部分: 关键统计指标汇总")
    print("=" * 60)
    summary = summary_stats(data, col=cust_col)

    print("\n\n" + "=" * 60)
    print("  第 5 部分: 公司维度交叉分析")
    print("=" * 60)
    company = company_cross_analysis(data, cust_col=cust_col, company_col=company_col)

    print("\n\n✅ 全量分析完成!")

    return {
        'value_counts': vc,
        'pareto': pareto,
        'freq_bins': freq,
        'summary': summary,
        'company_stats': company,
    }
