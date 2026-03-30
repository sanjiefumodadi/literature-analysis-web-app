#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI辅助育种优良材料筛选工具

功能：
- 根据设定阈值筛选优良大豆材料
- 生成专业分析报告
- 整合结果到指定文件夹

筛选标准：
- Pod Number > 70
- Seed Weight per Plant > 35
- Hundred Seed Weight > 20
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('breeding_selection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BreedingSelector:
    """育种材料筛选器"""
    
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.base_dir = os.path.join(output_dir, f'breeding_selection_{self.timestamp}')
        
    def create_output_structure(self):
        """创建输出目录结构"""
        logger.info("创建输出目录结构...")
        
        dirs = [
            self.base_dir,
            os.path.join(self.base_dir, 'data'),
            os.path.join(self.base_dir, 'figures'),
            os.path.join(self.base_dir, 'reports')
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
            
            logger.info(f"  数据加载成功，共 {len(data)} 个材料，{len(data.columns)} 个指标")
            return data
        except Exception as e:
            logger.error(f"  数据加载失败: {str(e)}")
            raise
    
    def select_materials(self, data):
        """筛选优良材料"""
        logger.info("开始筛选优良材料...")
        
        # 定义筛选标准
        criteria = {
            'Pod Number per Plant': 70,
            'Seed Weight per Plant': 35,
            'Hundred-Seed Weight': 20
        }
        
        # 筛选符合条件的材料
        selected = data[
            (data['Pod Number per Plant'] > criteria['Pod Number per Plant']) &
            (data['Seed Weight per Plant'] > criteria['Seed Weight per Plant']) &
            (data['Hundred-Seed Weight'] > criteria['Hundred-Seed Weight'])
        ]
        
        logger.info(f"  筛选完成，共 {len(selected)} 个材料符合条件")
        logger.info(f"  符合条件的材料编号: {selected['line_code'].tolist()}")
        
        return selected, criteria
    
    def generate_statistics(self, data, selected, criteria):
        """生成统计分析"""
        logger.info("生成统计分析...")
        
        stats = {
            'total_materials': len(data),
            'selected_materials': len(selected),
            'selection_rate': len(selected) / len(data) * 100,
            'criteria': criteria
        }
        
        # 计算选中材料的统计指标
        if not selected.empty:
            stats['selected_stats'] = selected[[
                'Pod Number per Plant',
                'Seed Weight per Plant',
                'Hundred-Seed Weight'
            ]].describe()
        
        logger.info(f"  总材料数: {stats['total_materials']}")
        logger.info(f"  选中材料数: {stats['selected_materials']}")
        logger.info(f"  选择率: {stats['selection_rate']:.2f}%")
        
        return stats
    
    def generate_visualizations(self, data, selected):
        """生成可视化图表"""
        logger.info("生成可视化图表...")
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.dpi'] = 300
        
        figures = []
        
        # 1. 筛选指标分布箱线图
        plt.figure(figsize=(12, 8))
        metrics = ['Pod Number per Plant', 'Seed Weight per Plant', 'Hundred-Seed Weight']
        for i, metric in enumerate(metrics, 1):
            plt.subplot(3, 1, i)
            sns.boxplot(data=data[metric])
            plt.axhline(y={'Pod Number per Plant': 70, 'Seed Weight per Plant': 35, 'Hundred-Seed Weight': 20}[metric], 
                       color='red', linestyle='--', label='筛选阈值')
            plt.title(f'{metric} 分布')
            plt.legend()
        plt.tight_layout()
        fig_path = os.path.join(self.base_dir, 'figures', 'metrics_distribution.png')
        plt.savefig(fig_path)
        figures.append(fig_path)
        plt.close()
        logger.info(f"  生成图表: {fig_path}")
        
        # 2. 筛选材料散点图
        if not selected.empty:
            plt.figure(figsize=(10, 8))
            sns.scatterplot(
                data=selected,
                x='Pod Number per Plant',
                y='Seed Weight per Plant',
                size='Hundred-Seed Weight',
                hue='Hundred-Seed Weight',
                palette='viridis',
                sizes=(50, 200)
            )
            plt.title('筛选材料三性状关系')
            plt.xlabel('单株荚数')
            plt.ylabel('单株粒重')
            plt.axvline(x=70, color='red', linestyle='--', label='荚数阈值')
            plt.axhline(y=35, color='blue', linestyle='--', label='粒重阈值')
            plt.legend()
            plt.tight_layout()
            fig_path = os.path.join(self.base_dir, 'figures', 'selected_materials_scatter.png')
            plt.savefig(fig_path)
            figures.append(fig_path)
            plt.close()
            logger.info(f"  生成图表: {fig_path}")
        
        return figures
    
    def generate_report(self, data, selected, stats, figures):
        """生成分析报告"""
        logger.info("生成分析报告...")
        
        report_content = f"""# AI辅助育种优良材料筛选报告

## 分析概况

- **分析时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
- **数据来源**: {os.path.basename(self.input_file)}
- **总材料数**: {stats['total_materials']}
- **选中材料数**: {stats['selected_materials']}
- **选择率**: {stats['selection_rate']:.2f}%

## 筛选标准

| 指标 | 阈值 |
|------|------|
| 单株荚数 (Pod Number per Plant) | > {stats['criteria']['Pod Number per Plant']} |
| 单株粒重 (Seed Weight per Plant) | > {stats['criteria']['Seed Weight per Plant']} |
| 百粒重 (Hundred-Seed Weight) | > {stats['criteria']['Hundred-Seed Weight']} |

## 筛选结果

### 符合条件的材料编号

```
{', '.join(selected['line_code'].tolist())}
```

### 选中材料详细信息

{selected[['line_code', 'Pod Number per Plant', 'Seed Weight per Plant', 'Hundred-Seed Weight']].to_markdown(index=False)}

## 统计分析

### 选中材料统计描述

{stats['selected_stats'].to_markdown() if 'selected_stats' in stats else '无符合条件的材料'}

## 可视化分析

### 指标分布

![指标分布](figures/metrics_distribution.png)

### 选中材料三性状关系

{"![选中材料散点图](figures/selected_materials_scatter.png)" if not selected.empty else "无符合条件的材料"}

## 结论与建议

1. **筛选结果**: 本次筛选共获得 {stats['selected_materials']} 个符合条件的优良材料，选择率为 {stats['selection_rate']:.2f}%。

2. **材料特点**: 选中材料在单株荚数、单株粒重和百粒重三个关键产量性状上表现优异。

3. **建议**: 
   - 将选中材料作为亲本用于杂交育种，以聚合优良性状
   - 对选中材料进行进一步的田间验证，确保在不同环境下的表现稳定
   - 结合分子标记技术，加速优良性状的固定和选育进程
   - 可考虑添加其他农艺性状（如抗病性、抗倒伏性等）进行综合评价

## 技术说明

- 分析工具: AI辅助育种筛选工具
- 分析方法: 阈值筛选 + 统计分析 + 可视化
- 数据处理: pandas, numpy
- 可视化: matplotlib, seaborn

---

*本报告由 AI辅助育种筛选工具 自动生成*"""
        
        report_path = os.path.join(self.base_dir, 'reports', 'breeding_selection_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"  生成报告: {report_path}")
        return report_path
    
    def save_results(self, data, selected):
        """保存结果"""
        logger.info("保存结果...")
        
        # 保存原始数据
        raw_data_path = os.path.join(self.base_dir, 'data', 'raw_data.csv')
        data.to_csv(raw_data_path, index=False, encoding='utf-8-sig')
        logger.info(f"  保存原始数据: {raw_data_path}")
        
        # 保存选中材料
        selected_path = os.path.join(self.base_dir, 'data', 'selected_materials.csv')
        selected.to_csv(selected_path, index=False, encoding='utf-8-sig')
        logger.info(f"  保存选中材料: {selected_path}")
        
        # 保存选中材料编号
        codes_path = os.path.join(self.base_dir, 'data', 'selected_codes.txt')
        with open(codes_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(selected['line_code'].tolist()))
        logger.info(f"  保存选中材料编号: {codes_path}")
        
        return raw_data_path, selected_path, codes_path
    
    def run(self):
        """运行筛选流程"""
        try:
            logger.info("AI辅助育种优良材料筛选工具启动")
            
            # 1. 创建输出目录
            self.create_output_structure()
            
            # 2. 加载数据
            data = self.load_data()
            
            # 3. 筛选材料
            selected, criteria = self.select_materials(data)
            
            # 4. 生成统计分析
            stats = self.generate_statistics(data, selected, criteria)
            
            # 5. 生成可视化图表
            figures = self.generate_visualizations(data, selected)
            
            # 6. 生成报告
            report_path = self.generate_report(data, selected, stats, figures)
            
            # 7. 保存结果
            self.save_results(data, selected)
            
            logger.info("筛选流程完成")
            logger.info(f"结果保存至: {self.base_dir}")
            
            return {
                'selected_count': len(selected),
                'selected_codes': selected['line_code'].tolist() if not selected.empty else [],
                'output_dir': self.base_dir,
                'report_path': report_path
            }
            
        except Exception as e:
            logger.error(f"筛选过程中出错: {str(e)}")
            raise

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='AI辅助育种优良材料筛选工具')
    parser.add_argument('--input', '-i', required=True, help='输入数据文件路径')
    parser.add_argument('--output', '-o', default='breeding_selection_results', help='输出文件夹路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出模式')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    selector = BreedingSelector(args.input, args.output)
    result = selector.run()
    
    print("\n" + "="*60)
    print("筛选完成！")
    print(f"符合条件的材料数量: {result['selected_count']}")
    if result['selected_codes']:
        print(f"符合条件的材料编号: {', '.join(result['selected_codes'])}")
    print(f"结果保存至: {result['output_dir']}")
    print(f"报告路径: {result['report_path']}")
    print("="*60)