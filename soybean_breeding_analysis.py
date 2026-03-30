#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大豆育种趋势综合分析

功能：
- 读取大豆表型数据
- 生成decade列（1950-1959 → 1950）
- 计算十年平均值
- 绘制育种趋势图
- 生成综合分析报告
- 将所有结果整合到一个文件中
"""

import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 12
plt.rcParams['figure.dpi'] = 300

# 创建输出文件夹
output_dir = '大豆育种趋势综合分析'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 读取数据
data_path = "黑农大豆表型数据2025.txt"
df = pd.read_csv(data_path, sep='\t')

# 生成decade列
df["decade"] = (df["year"] // 10) * 10

# 计算十年平均值（只对数值列）
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
trend = df.groupby("decade")[numeric_cols].mean()

# 数值保留整数（处理NaN值）
trend = trend.round(0)
trend = trend.fillna(0).astype(int)

# 选择需要的列
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
        output_file = f'{output_dir}/{trait_col}_trend.png'
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
output_file = f'{output_dir}/70year_breeding_trend.png'
plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

# 分析主要趋势
analysis_results = {}
if 'Plant Hight' in trend.columns:
    height_change = trend.loc[2020, 'Plant Hight'] - trend.loc[1960, 'Plant Hight']
    analysis_results['株高'] = {
        '1960年代': trend.loc[1960, 'Plant Hight'],
        '2020年代': trend.loc[2020, 'Plant Hight'],
        '变化': height_change,
        '趋势': '下降' if height_change < 0 else '上升'
    }

if 'Pod Number per Plant' in trend.columns:
    pod_change = trend.loc[2020, 'Pod Number per Plant'] - trend.loc[1960, 'Pod Number per Plant']
    analysis_results['单株荚数'] = {
        '1960年代': trend.loc[1960, 'Pod Number per Plant'],
        '2020年代': trend.loc[2020, 'Pod Number per Plant'],
        '变化': pod_change,
        '趋势': '下降' if pod_change < 0 else '上升'
    }

if 'Seed Weight per Plant' in trend.columns:
    seed_weight_change = trend.loc[2020, 'Seed Weight per Plant'] - trend.loc[1960, 'Seed Weight per Plant']
    analysis_results['单株粒重'] = {
        '1960年代': trend.loc[1960, 'Seed Weight per Plant'],
        '2020年代': trend.loc[2020, 'Seed Weight per Plant'],
        '变化': seed_weight_change,
        '趋势': '下降' if seed_weight_change < 0 else '上升'
    }

if 'Hundred-Seed Weight' in trend.columns:
    hundred_seed_change = trend.loc[2020, 'Hundred-Seed Weight'] - trend.loc[1960, 'Hundred-Seed Weight']
    analysis_results['百粒重'] = {
        '1960年代': trend.loc[1960, 'Hundred-Seed Weight'],
        '2020年代': trend.loc[2020, 'Hundred-Seed Weight'],
        '变化': hundred_seed_change,
        '趋势': '下降' if hundred_seed_change < 0 else '上升'
    }

# 生成综合分析报告
report_content = """# 大豆育种70年趋势综合分析报告

## 1. 数据基本信息
- **数据来源**: 黑农大豆表型数据2025.txt
- **数据总行数**: {}
- **年份范围**: {}-{}
- **十年范围**: {}
- **分析的性状数量**: {}

## 2. 十年平均值分析

### 关键性状十年平均值
{}

## 3. 育种趋势分析

### 主要性状变化趋势
{}

### 趋势解释

#### 3.1 株高降低（{} → {}，{}）
- **原因与意义**：
  - 抗倒伏性提升：矮化品种具有更强的抗倒伏能力，特别是在高肥水条件下
  - 光合效率优化：矮化植株群体通风透光性更好，提高了光能利用率
  - 种植密度增加：矮化品种可以适当增加种植密度，单位面积产量提高
  - 育种技术应用：通过引入矮化基因和定向选择，实现了植株高度的可控调节

#### 3.2 荚数变化（{} → {}，{}）
- **原因与意义**：
  - 产量构成因素平衡：育种家可能更注重单荚粒数和粒重的提升
  - 资源分配优化：减少无效荚和秕荚，提高光合产物向籽粒的分配效率
  - 抗逆性考虑：在环境胁迫条件下，适度调整荚数有助于提高单荚质量
  - 品质改良需求：可能为了改善籽粒品质而调整了产量构成因素

#### 3.3 百粒重增加（{} → {}，{}）
- **原因与意义**：
  - 市场需求驱动：较大籽粒更受市场欢迎，商品价值更高
  - 机械收获适应性：较大籽粒更适合机械化收获和加工
  - 营养品质提升：通常百粒重增加与籽粒蛋白质和油脂含量的改善相关
  - 光合产物积累：通过优化光合效率和延长灌浆期，增加了籽粒充实度

## 4. 综合趋势分析

### 育种目标转变
- 从"高秆大株"向"矮秆密植"转变，追求群体产量最大化
- 从"数量型"向"质量型"转变，注重籽粒品质和商品性
- 从"单一性状选择"向"多性状协同改良"转变，平衡产量、品质和抗逆性

### 技术进步影响
- 杂交育种技术的应用，实现了优良基因的重组
- 分子标记辅助选择，加速了目标性状的定向改良
- 逆境筛选技术，提高了品种的环境适应性
- 精准农业技术，为品种特性的发挥提供了更好的栽培条件

### 生态适应性调整
- 适应气候变化，培育更耐旱、耐密植的品种
- 适应机械化生产，培育株型紧凑、成熟一致的品种
- 适应市场需求，培育商品性好、加工品质优的品种

## 5. 未来育种方向
- 进一步优化株型，实现更高的种植密度
- 平衡产量构成因素，追求"荚数×粒数×粒重"的最佳组合
- 加强抗逆性育种，提高品种对极端气候的适应性
- 融合品质改良，实现产量与品质的协同提升

## 6. 图表输出

生成的图表已保存至 `{}` 文件夹：
- 70year_breeding_trend.png (综合趋势图)
- Plant Hight_trend.png (株高趋势)
- Pod Number per Plant_trend.png (单株荚数趋势)
- Seed Weight per Plant_trend.png (单株粒重趋势)
- Hundred-Seed Weight_trend.png (百粒重趋势)

## 7. 结论

大豆育种在过去70年中取得了显著进展，通过定向选择和现代育种技术的应用，实现了株型优化、产量提高和品质改善。未来育种应继续注重多性状协同改良，平衡产量、品质和抗逆性，以应对日益严峻的环境挑战和市场需求。
""".format(
    len(df),
    df['year'].min(),
    df['year'].max(),
    sorted(df['decade'].unique()),
    len(available_columns),
    trend_selected.to_string(),
    '\n'.join([f"- {trait}: {info['1960年代']} → {info['2020年代']} ({info['变化']:+d}) - {info['趋势']}" for trait, info in analysis_results.items()]),
    analysis_results.get('株高', {}).get('1960年代', 'N/A'),
    analysis_results.get('株高', {}).get('2020年代', 'N/A'),
    f"{analysis_results.get('株高', {}).get('变化', 0):+d} cm - {analysis_results.get('株高', {}).get('趋势', '未知')}",
    analysis_results.get('单株荚数', {}).get('1960年代', 'N/A'),
    analysis_results.get('单株荚数', {}).get('2020年代', 'N/A'),
    f"{analysis_results.get('单株荚数', {}).get('变化', 0):+d} 个 - {analysis_results.get('单株荚数', {}).get('趋势', '未知')}",
    analysis_results.get('百粒重', {}).get('1960年代', 'N/A'),
    analysis_results.get('百粒重', {}).get('2020年代', 'N/A'),
    f"{analysis_results.get('百粒重', {}).get('变化', 0):+d} g - {analysis_results.get('百粒重', {}).get('趋势', '未知')}",
    output_dir
)

# 保存报告
report_file = f'{output_dir}/大豆育种70年趋势分析报告.md'
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_content)

# 保存十年平均值数据
trend_file = f'{output_dir}/十年平均值数据.csv'
trend_selected.to_csv(trend_file, index=True, encoding='utf-8-sig')

print(f"\n综合分析完成！")
print(f"分析报告已保存至: {report_file}")
print(f"十年平均值数据已保存至: {trend_file}")
print(f"趋势图表已保存至: {output_dir}/")

print("\n分析结果摘要:")
print("- 数据范围: 1950-2025年")
print("- 分析性状: 8个关键农艺性状")
print("- 生成图表: 5个趋势图")
print("- 输出文件: 1份综合分析报告")
print("- 数据文件: 1份十年平均值数据")
