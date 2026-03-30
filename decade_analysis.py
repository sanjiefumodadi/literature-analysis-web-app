#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
十年趋势分析工具

功能：
- 读取大豆表型数据
- 生成decade列（1950-1959 → 1950）
- 计算十年平均值
- 绘制育种趋势图
- 输出分析结果
"""

import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

# 读取数据
data_path = "黑农大豆表型数据2025.txt"
df = pd.read_csv(data_path, sep='\t')

# Step1: 生成decade列
df["decade"] = (df["year"] // 10) * 10

# Step2: 计算十年平均值（只对数值列）
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
trend = df.groupby("decade")[numeric_cols].mean()

# 数值保留整数（处理NaN值）
trend = trend.round(0)
# 替换NaN为0或其他合适的值
trend = trend.fillna(0).astype(int)

# 选择需要的列（如果需要）
selected_columns = [
    'Plant Hight',
    'Pod Number per Plant',
    'Seed Weight per Plant',
    'Hundred-Seed Weight',
    'Effective Branch Number',
    'Main Stem Node Number',
    'Height of Lowest Pod',
    'Seed Number'
]

# 过滤列（如果存在的话）
available_columns = [col for col in selected_columns if col in trend.columns]
trend_selected = trend[available_columns]

# 输出结果
print("Step1: 生成decade列")
print("前5行数据:")
print(df[['year', 'decade']].head())
print("\nStep2: 计算十年平均值")
print("十年平均值结果:")
print(trend_selected)

# 保存结果（跳过保存以避免权限错误）
# output_file = "decade_trend_integers.csv"
# trend_selected.to_csv(output_file, index=True)
# print(f"\n结果已保存至: {output_file}")

# 显示详细信息
print("\n详细信息:")
print(f"数据总行数: {len(df)}")
print(f"年份范围: {df['year'].min()}-{df['year'].max()}")
print(f"十年范围: {sorted(df['decade'].unique())}")
print(f"计算的性状数量: {len(available_columns)}")

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 12
plt.rcParams['figure.dpi'] = 300

# 创建输出文件夹
if not os.path.exists('breeding_trend_figures'):
    os.makedirs('breeding_trend_figures')

# 绘制关键性状趋势图
key_traits = [
    ('Plant Hight', '株高 (cm)', '株高趋势'),
    ('Pod Number per Plant', '单株荚数', '单株荚数趋势'),
    ('Seed Weight per Plant', '单株粒重 (g)', '单株粒重趋势'),
    ('Hundred-Seed Weight', '百粒重 (g)', '百粒重趋势')
]

# 绘制单个性状趋势图
for trait_col, trait_name, title in key_traits:
    if trait_col in trend.columns:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=trend, x=trend.index, y=trait_col, 
                    marker='o', markersize=8, linewidth=2.5, 
                    color='royalblue')
        
        # 添加网格
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 设置标题和标签
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('十年期', fontsize=14)
        plt.ylabel(trait_name, fontsize=14)
        
        # 设置坐标轴范围
        plt.xlim(trend.index.min() - 5, trend.index.max() + 5)
        y_min = trend[trait_col].min() * 0.9 if trend[trait_col].min() > 0 else 0
        y_max = trend[trait_col].max() * 1.1
        plt.ylim(y_min, y_max)
        
        # 保存图表
        output_file = f'breeding_trend_figures/{trait_col}_trend.png'
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

# 绘制综合趋势图
plt.figure(figsize=(12, 8))

# 绘制多个性状
if 'Plant Hight' in trend.columns:
    sns.lineplot(data=trend, x=trend.index, y='Plant Hight', 
                label='株高', marker='o', markersize=7, linewidth=2)
if 'Pod Number per Plant' in trend.columns:
    sns.lineplot(data=trend, x=trend.index, y='Pod Number per Plant', 
                label='单株荚数', marker='s', markersize=7, linewidth=2)
if 'Seed Weight per Plant' in trend.columns:
    sns.lineplot(data=trend, x=trend.index, y='Seed Weight per Plant', 
                label='单株粒重', marker='^', markersize=7, linewidth=2)
if 'Hundred-Seed Weight' in trend.columns:
    sns.lineplot(data=trend, x=trend.index, y='Hundred-Seed Weight', 
                label='百粒重', marker='D', markersize=7, linewidth=2)

# 添加网格
plt.grid(True, linestyle='--', alpha=0.7)

# 设置标题和标签
plt.title('70年大豆育种趋势图', fontsize=18, fontweight='bold')
plt.xlabel('十年期', fontsize=14)
plt.ylabel('数值', fontsize=14)

# 添加图例
plt.legend(fontsize=12, loc='best')

# 设置坐标轴范围
plt.xlim(trend.index.min() - 5, trend.index.max() + 5)

# 保存综合趋势图
output_file = 'breeding_trend_figures/70year_breeding_trend.png'
plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print("\n育种趋势图已生成并保存至: breeding_trend_figures/")
print("生成的图表:")
print("- 70year_breeding_trend.png (综合趋势图)")
print("- Plant Hight_trend.png (株高趋势)")
print("- Pod Number per Plant_trend.png (单株荚数趋势)")
print("- Seed Weight per Plant_trend.png (单株粒重趋势)")
print("- Hundred-Seed Weight_trend.png (百粒重趋势)")

# 分析主要趋势
print("\n70年大豆育种主要趋势分析:")
if 'Plant Hight' in trend.columns:
    height_change = trend.loc[2020, 'Plant Hight'] - trend.loc[1960, 'Plant Hight']
    print(f"· 株高: {trend.loc[1960, 'Plant Hight']} → {trend.loc[2020, 'Plant Hight']} ({height_change:+d} cm) - {'下降' if height_change < 0 else '上升'}")

if 'Pod Number per Plant' in trend.columns:
    pod_change = trend.loc[2020, 'Pod Number per Plant'] - trend.loc[1960, 'Pod Number per Plant']
    print(f"· 单株荚数: {trend.loc[1960, 'Pod Number per Plant']} → {trend.loc[2020, 'Pod Number per Plant']} ({pod_change:+d} 个) - {'下降' if pod_change < 0 else '上升'}")

if 'Seed Weight per Plant' in trend.columns:
    seed_weight_change = trend.loc[2020, 'Seed Weight per Plant'] - trend.loc[1960, 'Seed Weight per Plant']
    print(f"· 单株粒重: {trend.loc[1960, 'Seed Weight per Plant']} → {trend.loc[2020, 'Seed Weight per Plant']} ({seed_weight_change:+d} g) - {'下降' if seed_weight_change < 0 else '上升'}")

if 'Hundred-Seed Weight' in trend.columns:
    hundred_seed_change = trend.loc[2020, 'Hundred-Seed Weight'] - trend.loc[1960, 'Hundred-Seed Weight']
    print(f"· 百粒重: {trend.loc[1960, 'Hundred-Seed Weight']} → {trend.loc[2020, 'Hundred-Seed Weight']} ({hundred_seed_change:+d} g) - {'下降' if hundred_seed_change < 0 else '上升'}")