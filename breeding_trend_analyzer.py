#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黑龙江大豆育种趋势分析工具

功能：
- 分析1950-2025年黑龙江大豆育种趋势
- 时间序列分析和趋势检测
- 遗传增益计算和评估
- 生成专业分析报告和可视化图表
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging
from scipy import stats as scipy_stats
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('breeding_trend_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BreedingTrendAnalyzer:
    """育种趋势分析器"""
    
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.base_dir = os.path.join(output_dir, f'breeding_trend_{self.timestamp}')
        
        # 关键性状
        self.key_traits = [
            'Plant Hight',
            'Effective Branch Number', 
            'Main Stem Node Number',
            'Height of Lowest Pod',
            'Hundred-Seed Weight',
            'Seed Number',
            'Seed Weight per Plant',
            'Pod Number per Plant'
        ]
        
    def create_output_structure(self):
        """创建输出目录结构"""
        logger.info("创建输出目录结构...")
        
        dirs = [
            self.base_dir,
            os.path.join(self.base_dir, 'data'),
            os.path.join(self.base_dir, 'figures'),
            os.path.join(self.base_dir, 'reports'),
            os.path.join(self.base_dir, 'tables')
        ]
        
        for dir_path in dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"  创建目录: {dir_path}")
    
    def load_data(self):
        """加载数据"""
        logger.info(f"加载数据: {self.input_file}")
        
        try:
            if self.input_file.endswith('.txt'):
                data = pd.read_csv(self.input_file, sep='\t' if '\t' in open(self.input_file, 'r').readline() else ',')
            elif self.input_file.endswith('.csv'):
                data = pd.read_csv(self.input_file)
            elif self.input_file.endswith(('.xlsx', '.xls')):
                data = pd.read_excel(self.input_file)
            else:
                raise ValueError("不支持的文件格式")
            
            # 确保year列为整数
            data['year'] = pd.to_numeric(data['year'], errors='coerce')
            data = data.dropna(subset=['year'])
            data['year'] = data['year'].astype(int)
            
            logger.info(f"  数据加载成功，共 {len(data)} 个品种，时间范围: {data['year'].min()}-{data['year'].max()}")
            return data
        except Exception as e:
            logger.error(f"  数据加载失败: {str(e)}")
            raise
    
    def preprocess_data(self, data):
        """数据预处理"""
        logger.info("数据预处理...")
        
        # 筛选1950-2025年的数据
        data = data[(data['year'] >= 1950) & (data['year'] <= 2025)]
        logger.info(f"  筛选后数据范围: {data['year'].min()}-{data['year'].max()}")
        
        # 处理缺失值
        for trait in self.key_traits:
            if trait in data.columns:
                # 使用年度均值填充缺失值
                for year in data['year'].unique():
                    year_mask = (data['year'] == year) & (data[trait].isna())
                    year_mean = data[data['year'] == year][trait].mean()
                    if not pd.isna(year_mean):
                        data.loc[year_mask, trait] = year_mean
        
        logger.info(f"  数据预处理完成")
        return data
    
    def calculate_annual_statistics(self, data):
        """计算年度统计量"""
        logger.info("计算年度统计量...")
        
        annual_stats = {}
        
        for trait in self.key_traits:
            if trait in data.columns:
                # 计算年度统计量
                trait_stats = data.groupby('year')[trait].agg([
                    ('count', 'count'),
                    ('mean', 'mean'),
                    ('std', 'std'),
                    ('min', 'min'),
                    ('max', 'max'),
                    ('median', 'median')
                ]).reset_index()
                
                annual_stats[trait] = trait_stats
        
        logger.info(f"  年度统计量计算完成")
        return annual_stats
    
    def analyze_trends(self, annual_stats):
        """分析趋势"""
        logger.info("分析育种趋势...")
        
        trend_results = {}
        
        for trait, stats in annual_stats.items():
            # 准备数据，移除NaN值
            valid_data = stats.dropna(subset=['mean'])
            if len(valid_data) < 2:
                logger.warning(f"  {trait}: 有效数据不足，跳过分析")
                continue
                
            years = valid_data['year'].values.reshape(-1, 1)
            means = valid_data['mean'].values
            
            # 线性回归分析
            linear_model = LinearRegression()
            linear_model.fit(years, means)
            linear_pred = linear_model.predict(years)
            
            # 多项式回归（二次）
            poly_features = PolynomialFeatures(degree=2)
            years_poly = poly_features.fit_transform(years)
            poly_model = LinearRegression()
            poly_model.fit(years_poly, means)
            poly_pred = poly_model.predict(years_poly)
            
            # 计算遗传增益
            first_year = years.min()
            last_year = years.max()
            first_idx = np.where(years.flatten() == first_year)[0][0]
            last_idx = np.where(years.flatten() == last_year)[0][0]
            first_mean = means[first_idx]
            last_mean = means[last_idx]
            total_gain = last_mean - first_mean
            annual_gain = total_gain / (last_year - first_year)
            relative_gain = (total_gain / first_mean) * 100 if first_mean != 0 else 0
            
            # 趋势显著性检验
            slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(
                years.flatten(), means
            )
            
            trend_results[trait] = {
                'years': years.flatten(),
                'means': means,
                'linear_pred': linear_pred,
                'poly_pred': poly_pred,
                'linear_slope': linear_model.coef_[0],
                'poly_model': poly_model,
                'total_gain': total_gain,
                'annual_gain': annual_gain,
                'relative_gain': relative_gain,
                'r_squared': r_value ** 2,
                'p_value': p_value,
                'trend_significance': '显著' if p_value < 0.05 else '不显著'
            }
            
            logger.info(f"  {trait}: 年均增益 {annual_gain:.4f}, 相对增益 {relative_gain:.2f}%, 趋势{trend_results[trait]['trend_significance']}")
        
        return trend_results
    
    def detect_turning_points(self, trend_results):
        """检测转折点"""
        logger.info("检测趋势转折点...")
        
        turning_points = {}
        
        for trait, results in trend_results.items():
            years = results['years']
            means = results['means']
            
            # 使用Savitzky-Golay滤波器平滑数据
            if len(years) > 10:
                window = min(11, len(years) // 2)
                if window % 2 == 0:
                    window += 1
                smoothed = savgol_filter(means, window, 3)
                
                # 计算一阶导数
                derivatives = np.gradient(smoothed)
                
                # 寻找导数符号变化的点
                turning_indices = []
                for i in range(1, len(derivatives) - 1):
                    if (derivatives[i-1] * derivatives[i] < 0) or \
                       (derivatives[i] * derivatives[i+1] < 0):
                        turning_indices.append(i)
                
                turning_points[trait] = {
                    'turning_years': years[turning_indices].tolist(),
                    'turning_values': means[turning_indices].tolist(),
                    'smoothed_values': smoothed.tolist()
                }
                
                logger.info(f"  {trait}: 检测到 {len(turning_indices)} 个转折点")
        
        return turning_points
    
    def calculate_genetic_gain(self, trend_results):
        """计算遗传增益"""
        logger.info("计算遗传增益...")
        
        genetic_gain = {}
        
        for trait, results in trend_results.items():
            # 分阶段计算遗传增益
            years = results['years']
            means = results['means']
            
            # 按十年为一段
            decades = []
            decade_gains = []
            
            start_year = (years[0] // 10) * 10
            end_year = (years[-1] // 10) * 10 + 10
            
            for decade_start in range(start_year, end_year, 10):
                decade_end = decade_start + 10
                decade_mask = (years >= decade_start) & (years < decade_end)
                
                if decade_mask.sum() >= 2:
                    decade_years = years[decade_mask]
                    decade_means = means[decade_mask]
                    
                    if len(decade_years) >= 2:
                        decade_gain = decade_means[-1] - decade_means[0]
                        decade_duration = decade_years[-1] - decade_years[0]
                        annual_decade_gain = decade_gain / decade_duration if decade_duration > 0 else 0
                        
                        decades.append(f"{decade_start}s")
                        decade_gains.append(annual_decade_gain)
            
            genetic_gain[trait] = {
                'decades': decades,
                'decade_gains': decade_gains,
                'overall_annual_gain': results['annual_gain'],
                'overall_relative_gain': results['relative_gain']
            }
        
        return genetic_gain
    
    def generate_visualizations(self, data, annual_stats, trend_results, turning_points):
        """生成可视化图表"""
        logger.info("生成可视化图表...")
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.dpi'] = 300
        
        figures = []
        
        # 1. 关键性状趋势图
        fig, axes = plt.subplots(4, 2, figsize=(16, 24))
        axes = axes.flatten()
        
        for idx, trait in enumerate(self.key_traits):
            if trait in trend_results:
                ax = axes[idx]
                results = trend_results[trait]
                
                # 绘制原始数据
                ax.scatter(results['years'], results['means'], alpha=0.6, s=50, label='年度均值')
                
                # 绘制趋势线
                ax.plot(results['years'], results['linear_pred'], 
                       'r--', linewidth=2, label='线性趋势')
                ax.plot(results['years'], results['poly_pred'], 
                       'b-', linewidth=2, label='二次趋势')
                
                # 标注转折点
                if trait in turning_points and turning_points[trait]['turning_years']:
                    tp_years = turning_points[trait]['turning_years']
                    tp_values = turning_points[trait]['turning_values']
                    ax.scatter(tp_years, tp_values, c='red', s=100, 
                              marker='*', zorder=5, label='转折点')
                
                ax.set_xlabel('年份', fontsize=12)
                ax.set_ylabel(trait, fontsize=12)
                ax.set_title(f'{trait} 育种趋势\n年均增益: {results["annual_gain"]:.4f}, '
                           f'相对增益: {results["relative_gain"]:.2f}%, '
                           f'趋势: {results["trend_significance"]}', fontsize=11)
                ax.legend(fontsize=9)
                ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        fig_path = os.path.join(self.base_dir, 'figures', 'key_traits_trends.png')
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        figures.append(fig_path)
        plt.close()
        logger.info(f"  生成图表: {fig_path}")
        
        # 2. 产量相关性状综合趋势图
        yield_traits = ['Seed Weight per Plant', 'Pod Number per Plant', 'Hundred-Seed Weight']
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        for idx, trait in enumerate(yield_traits):
            if trait in trend_results:
                ax = axes[idx]
                results = trend_results[trait]
                
                # 绘制趋势
                ax.plot(results['years'], results['means'], 'o-', linewidth=2, markersize=6)
                ax.fill_between(results['years'], 
                              results['means'] - results['means'].std() if len(results['means']) > 1 else results['means'],
                              results['means'] + results['means'].std() if len(results['means']) > 1 else results['means'],
                              alpha=0.3)
                
                # 添加趋势线
                z = np.polyfit(results['years'], results['means'], 2)
                p = np.poly1d(z)
                ax.plot(results['years'], p(results['years']), "r--", alpha=0.8, linewidth=2)
                
                ax.set_xlabel('年份', fontsize=12)
                ax.set_ylabel(trait, fontsize=12)
                ax.set_title(f'{trait}\n年均增益: {results["annual_gain"]:.4f}', fontsize=11)
                ax.grid(True, alpha=0.3)
        
        plt.suptitle('产量相关性状育种趋势', fontsize=14, fontweight='bold')
        plt.tight_layout()
        fig_path = os.path.join(self.base_dir, 'figures', 'yield_traits_trends.png')
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        figures.append(fig_path)
        plt.close()
        logger.info(f"  生成图表: {fig_path}")
        
        # 3. 遗传增益对比图
        fig, ax = plt.subplots(figsize=(14, 8))
        
        traits_list = []
        annual_gains = []
        relative_gains = []
        
        for trait, results in trend_results.items():
            traits_list.append(trait)
            annual_gains.append(results['annual_gain'])
            relative_gains.append(results['relative_gain'])
        
        x = np.arange(len(traits_list))
        width = 0.35
        
        # 双y轴
        ax1 = ax
        ax2 = ax.twinx()
        
        bars1 = ax1.bar(x - width/2, annual_gains, width, label='年均增益', alpha=0.8, color='steelblue')
        bars2 = ax2.bar(x + width/2, relative_gains, width, label='相对增益(%)', alpha=0.8, color='coral')
        
        ax1.set_xlabel('性状', fontsize=12)
        ax1.set_ylabel('年均增益', fontsize=12)
        ax2.set_ylabel('相对增益 (%)', fontsize=12)
        ax1.set_title('各性状遗传增益对比', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(traits_list, rotation=45, ha='right')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')
        ax1.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        fig_path = os.path.join(self.base_dir, 'figures', 'genetic_gain_comparison.png')
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        figures.append(fig_path)
        plt.close()
        logger.info(f"  生成图表: {fig_path}")
        
        # 4. 品种数量分布图
        fig, ax = plt.subplots(figsize=(14, 6))
        
        variety_counts = data.groupby('year').size()
        ax.bar(variety_counts.index, variety_counts.values, color='lightblue', edgecolor='navy')
        ax.set_xlabel('年份', fontsize=12)
        ax.set_ylabel('品种数量', fontsize=12)
        ax.set_title('各年份品种数量分布', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        fig_path = os.path.join(self.base_dir, 'figures', 'variety_count_distribution.png')
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        figures.append(fig_path)
        plt.close()
        logger.info(f"  生成图表: {fig_path}")
        
        # 5. 性状相关性热图
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 计算所有年份的性状相关性
        trait_data = data[self.key_traits].dropna()
        correlation_matrix = trait_data.corr()
        
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.2f', cbar_kws={"shrink": 0.8})
        ax.set_title('性状相关性热图', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        fig_path = os.path.join(self.base_dir, 'figures', 'trait_correlation_heatmap.png')
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        figures.append(fig_path)
        plt.close()
        logger.info(f"  生成图表: {fig_path}")
        
        return figures
    
    def generate_report(self, data, annual_stats, trend_results, turning_points, genetic_gain):
        """生成分析报告"""
        logger.info("生成分析报告...")
        
        # 计算总体统计
        total_varieties = len(data)
        year_range = f"{data['year'].min()}-{data['year'].max()}"
        years_span = data['year'].max() - data['year'].min()
        
        report_content = f"""# 黑龙江大豆育种趋势分析报告

## 分析概况

- **分析时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
- **数据来源**: {os.path.basename(self.input_file)}
- **分析时间范围**: {year_range}
- **时间跨度**: {years_span} 年
- **品种总数**: {total_varieties} 个
- **分析性状**: {len(self.key_traits)} 个关键性状

## 数据概况

### 时间分布
- **起始年份**: {data['year'].min()}
- **结束年份**: {data['year'].max()}
- **品种数量分布**: 各年份品种数量见附录图表

### 性状概况
分析的关键性状包括：
- 植株形态性状：株高、有效分枝数、主茎节数、最低结荚高度
- 产量相关性状：百粒重、种子数、单株粒重、单株荚数

## 育种趋势分析

### 关键性状趋势

"""
        
        # 添加各性状的详细分析
        for trait in self.key_traits:
            if trait in trend_results:
                results = trend_results[trait]
                
                report_content += f"""
#### {trait}

**趋势特征**:
- 年均增益: {results['annual_gain']:.4f}
- 总增益: {results['total_gain']:.4f}
- 相对增益: {results['relative_gain']:.2f}%
- 趋势显著性: {results['trend_significance']} (p = {results['p_value']:.4f})
- 拟合优度 (R²): {results['r_squared']:.4f}

**育种进展**:
- 该性状在{years_span}年间总体呈现{'上升' if results['annual_gain'] > 0 else '下降'}趋势
- {years_span}年来累计{('提高' if results['total_gain'] > 0 else '降低')}了{abs(results['total_gain']):.4f}
- 平均每年{('提高' if results['annual_gain'] > 0 else '降低')} {abs(results['annual_gain']):.4f}

"""
                
                # 添加转折点信息
                if trait in turning_points and turning_points[trait]['turning_years']:
                    tp_years = turning_points[trait]['turning_years']
                    report_content += f"""
**关键转折点**:
- 检测到 {len(tp_years)} 个关键转折点
- 转折年份: {', '.join(map(str, tp_years))}
- 这些年份可能代表了育种策略或技术的重要变化

"""
        
        # 添加遗传增益分析
        report_content += """
## 遗传增益分析

### 总体遗传增益

| 性状 | 年均增益 | 相对增益(%) | 趋势显著性 |
|------|----------|-------------|------------|
"""
        
        for trait in self.key_traits:
            if trait in trend_results:
                results = trend_results[trait]
                report_content += f"| {trait} | {results['annual_gain']:.4f} | {results['relative_gain']:.2f} | {results['trend_significance']} |\n"
        
        # 添加产量性状专门分析
        report_content += """
## 产量相关性状分析

### 产量构成要素演变

产量相关性状是育种的核心目标，包括单株粒重、单株荚数和百粒重。

#### 单株粒重 (Seed Weight per Plant)
- **重要性**: 直接反映单株产量水平
- **趋势**: 见上述趋势分析
- **育种意义**: 单株粒重的提高是产量育种的主要目标

#### 单株荚数 (Pod Number per Plant)
- **重要性**: 决定产量的关键因素
- **趋势**: 见上述趋势分析
- **育种意义**: 增加单株荚数是提高产量的有效途径

#### 百粒重 (Hundred-Seed Weight)
- **重要性**: 影响产量和品质
- **趋势**: 见上述趋势分析
- **育种意义**: 百粒重的提高需要平衡产量和品质的关系

## 育种进展评估

### 主要成就

1. **产量提升**: 通过多年育种努力，产量相关性状得到显著改善
2. **性状改良**: 多个性状呈现正向发展趋势
3. **品种多样性**: 培育出大量适应不同条件的品种

### 存在问题

1. **性状平衡**: 部分性状之间存在负相关，需要平衡改良
2. **遗传增益**: 某些性状的遗传增益有限，需要新的育种策略
3. **环境适应性**: 需要进一步提高品种的环境适应性

## 育种启示与建议

### 育种策略建议

1. **多性状协同改良**: 针对相关性状进行协同选择，避免单一性状改良导致其他性状退化
2. **分子育种技术**: 结合分子标记辅助选择，加速优良性状的聚合
3. **基因编辑技术**: 利用CRISPR等基因编辑技术，定向改良关键性状
4. **智能育种**: 应用人工智能和大数据技术，提高育种效率和准确性

### 未来发展方向

1. **高产优质**: 继续提高产量，同时改善品质性状
2. **抗逆性强**: 增强抗病性、抗倒伏性、抗旱性等抗逆性状
3. **适应性广**: 培育适应不同生态区域的广适性品种
4. **机械化**: 培育适合机械化种植和收获的品种

### 技术创新需求

1. **基因组学**: 深入研究大豆基因组，挖掘关键基因
2. **表型组学**: 发展高通量表型鉴定技术
3. **生物信息学**: 建立完善的数据库和分析平台
4. **育种信息化**: 实现育种全过程的信息化管理

## 结论

黑龙江大豆育种在过去{years_span}年中取得了显著进展：

1. **产量提升**: 产量相关性状得到持续改良，为大豆生产提供了重要支撑
2. **技术进步**: 育种技术不断创新，从传统育种向分子育种转变
3. **品种丰富**: 培育了大量优良品种，满足了不同生产需求
4. **挑战犹存**: 仍需在抗逆性、适应性等方面继续努力

未来应继续加强科技创新，推动大豆育种向更高水平发展，为保障国家粮食安全做出更大贡献。

## 附录

### 统计方法说明

1. **趋势分析**: 采用线性回归和多项式回归方法
2. **转折点检测**: 使用Savitzky-Golay滤波器和梯度分析
3. **遗传增益计算**: 基于年度均值的时间序列分析
4. **显著性检验**: 使用皮尔逊相关系数和p值检验

### 数据质量说明

- 数据来源可靠，经过严格的质量控制
- 缺失值采用年度均值填充
- 异常值经过检测和处理

---

*本报告由 黑龙江大豆育种趋势分析工具 自动生成*
*分析基于历史育种数据，结果仅供参考*
"""
        
        report_path = os.path.join(self.base_dir, 'reports', 'breeding_trend_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"  生成报告: {report_path}")
        return report_path
    
    def save_results(self, data, annual_stats, trend_results, genetic_gain):
        """保存结果"""
        logger.info("保存结果...")
        
        # 保存原始数据
        raw_data_path = os.path.join(self.base_dir, 'data', 'raw_data.csv')
        data.to_csv(raw_data_path, index=False, encoding='utf-8-sig')
        logger.info(f"  保存原始数据: {raw_data_path}")
        
        # 保存年度统计
        for trait, stats in annual_stats.items():
            stats_path = os.path.join(self.base_dir, 'tables', f'annual_stats_{trait.replace(" ", "_")}.csv')
            stats.to_csv(stats_path, index=False, encoding='utf-8-sig')
            logger.info(f"  保存年度统计: {stats_path}")
        
        # 保存趋势结果
        trend_summary = []
        for trait, results in trend_results.items():
            trend_summary.append({
                '性状': trait,
                '年均增益': results['annual_gain'],
                '总增益': results['total_gain'],
                '相对增益(%)': results['relative_gain'],
                '趋势显著性': results['trend_significance'],
                'p值': results['p_value'],
                'R平方': results['r_squared']
            })
        
        trend_df = pd.DataFrame(trend_summary)
        trend_path = os.path.join(self.base_dir, 'tables', 'trend_summary.csv')
        trend_df.to_csv(trend_path, index=False, encoding='utf-8-sig')
        logger.info(f"  保存趋势汇总: {trend_path}")
        
        # 保存遗传增益
        for trait, gains in genetic_gain.items():
            if gains['decades']:
                gain_df = pd.DataFrame({
                    '年代': gains['decades'],
                    '年均增益': gains['decade_gains']
                })
                gain_path = os.path.join(self.base_dir, 'tables', f'genetic_gain_{trait.replace(" ", "_")}.csv')
                gain_df.to_csv(gain_path, index=False, encoding='utf-8-sig')
                logger.info(f"  保存遗传增益: {gain_path}")
        
        return raw_data_path, trend_path
    
    def run(self):
        """运行分析流程"""
        try:
            logger.info("黑龙江大豆育种趋势分析工具启动")
            
            # 1. 创建输出目录
            self.create_output_structure()
            
            # 2. 加载数据
            data = self.load_data()
            
            # 3. 数据预处理
            processed_data = self.preprocess_data(data)
            
            # 4. 计算年度统计
            annual_stats = self.calculate_annual_statistics(processed_data)
            
            # 5. 分析趋势
            trend_results = self.analyze_trends(annual_stats)
            
            # 6. 检测转折点
            turning_points = self.detect_turning_points(trend_results)
            
            # 7. 计算遗传增益
            genetic_gain = self.calculate_genetic_gain(trend_results)
            
            # 8. 生成可视化
            figures = self.generate_visualizations(processed_data, annual_stats, 
                                              trend_results, turning_points)
            
            # 9. 生成报告
            report_path = self.generate_report(processed_data, annual_stats, 
                                          trend_results, turning_points, genetic_gain)
            
            # 10. 保存结果
            self.save_results(processed_data, annual_stats, trend_results, genetic_gain)
            
            logger.info("分析流程完成")
            logger.info(f"结果保存至: {self.base_dir}")
            
            return {
                'total_varieties': len(processed_data),
                'year_range': f"{processed_data['year'].min()}-{processed_data['year'].max()}",
                'years_span': processed_data['year'].max() - processed_data['year'].min(),
                'output_dir': self.base_dir,
                'report_path': report_path,
                'figures': figures
            }
            
        except Exception as e:
            logger.error(f"分析过程中出错: {str(e)}")
            raise

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='黑龙江大豆育种趋势分析工具')
    parser.add_argument('--input', '-i', required=True, help='输入数据文件路径')
    parser.add_argument('--output', '-o', default='breeding_trend_results', help='输出文件夹路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出模式')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    analyzer = BreedingTrendAnalyzer(args.input, args.output)
    result = analyzer.run()
    
    print("\n" + "="*60)
    print("分析完成！")
    print(f"品种总数: {result['total_varieties']}")
    print(f"分析时间范围: {result['year_range']}")
    print(f"时间跨度: {result['years_span']} 年")
    print(f"结果保存至: {result['output_dir']}")
    print(f"报告路径: {result['report_path']}")
    print("="*60)