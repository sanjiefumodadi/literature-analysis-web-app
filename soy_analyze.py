#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Soybean Analyzer Tool
大豆分析工具

功能：
- 自动数据读取与预处理
- 生成相关性热图
- 自动生成分析报告

用法：
python soy_analyze.py --file soy.txt
"""

import os
import sys
import argparse
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SoyAnalyzer:
    """大豆分析器"""
    
    def __init__(self, input_file):
        self.input_file = input_file
    
    def run(self):
        """运行分析流程"""
        try:
            logger.info("=" * 60)
            logger.info("Soybean Analyzer 启动")
            logger.info(f"输入文件: {self.input_file}")
            logger.info("=" * 60)
            
            # 1. 数据读取
            logger.info("【步骤1】数据读取")
            data = self._read_file()
            logger.info(f"✓ 读取成功，共{len(data)}个样本，{len(data.columns)}个变量")
            
            # 2. 数据清洗
            logger.info("【步骤2】数据清洗")
            cleaned_data = self._clean_data(data)
            logger.info(f"✓ 清洗完成，剩余{len(cleaned_data)}个有效样本")
            
            # 3. 识别数值变量
            logger.info("【步骤3】识别变量")
            numeric_columns = self._get_numeric_columns(cleaned_data)
            if not numeric_columns:
                logger.error("未识别到数值变量，无法生成热图")
                return
            logger.info(f"识别到{len(numeric_columns)}个数值变量: {numeric_columns}")
            
            # 4. 分析
            logger.info("【步骤4】数据分析")
            analysis_results = self._analyze_data(cleaned_data, numeric_columns)
            
            # 5. 生成热图
            logger.info("【步骤5】生成热图")
            self._generate_heatmap(cleaned_data, numeric_columns)
            logger.info("✓ 热图生成成功: heatmap.png")
            
            # 6. 生成报告
            logger.info("【步骤6】生成报告")
            self._generate_report(cleaned_data, numeric_columns, analysis_results)
            logger.info("✓ 报告生成成功: report.txt")
            
            logger.info("=" * 60)
            logger.info("分析完成！")
            logger.info("结果文件:")
            logger.info("  - heatmap.png (相关性热图)")
            logger.info("  - report.txt (分析报告)")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"分析过程中出错: {str(e)}")
            raise
    
    def _read_file(self):
        """读取文件"""
        if self.input_file.endswith('.txt'):
            return pd.read_csv(self.input_file, sep=',', encoding='utf-8')
        elif self.input_file.endswith('.csv'):
            return pd.read_csv(self.input_file, encoding='utf-8')
        elif self.input_file.endswith('.xlsx'):
            return pd.read_excel(self.input_file)
        else:
            raise ValueError("不支持的文件格式")
    
    def _clean_data(self, data):
        """清洗数据"""
        # 去除空值
        return data.dropna()
    
    def _get_numeric_columns(self, data):
        """获取数值列"""
        return data.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    def _analyze_data(self, data, numeric_columns):
        """分析数据"""
        results = {}
        
        # 描述性统计
        results['descriptive'] = data[numeric_columns].describe()
        
        # 相关性分析
        results['correlation'] = data[numeric_columns].corr()
        
        return results
    
    def _generate_heatmap(self, data, numeric_columns):
        """生成热图"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        # 计算相关系数
        corr_matrix = data[numeric_columns].corr()
        
        # 创建热图
        plt.figure(figsize=(12, 10))
        
        # 生成掩码
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        # 绘制热图
        sns.heatmap(
            corr_matrix, 
            mask=mask, 
            annot=True, 
            fmt='.2f', 
            cmap='coolwarm',
            vmin=-1, 
            vmax=1,
            square=True,
            linewidths=0.5,
            cbar_kws={'label': '相关系数'}
        )
        
        plt.title('大豆性状相关性热图', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # 保存热图
        plt.savefig('heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_report(self, data, numeric_columns, analysis_results):
        """生成报告"""
        report_content = []
        report_content.append("# 大豆数据分析报告")
        report_content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append("")
        
        # 数据基本信息
        report_content.append("## 1. 数据基本信息")
        report_content.append(f"- 样本数量: {len(data)}")
        report_content.append(f"- 变量数量: {len(data.columns)}")
        report_content.append(f"- 变量名称: {', '.join(data.columns.tolist())}")
        report_content.append(f"- 数值变量: {', '.join(numeric_columns)}")
        report_content.append("")
        
        # 描述性统计
        report_content.append("## 2. 描述性统计")
        desc_stats = analysis_results['descriptive']
        for col in numeric_columns:
            report_content.append(f"{col}:")
            report_content.append(f"  均值: {desc_stats.loc['mean', col]:.2f}")
            report_content.append(f"  标准差: {desc_stats.loc['std', col]:.2f}")
            report_content.append(f"  最小值: {desc_stats.loc['min', col]:.2f}")
            report_content.append(f"  最大值: {desc_stats.loc['max', col]:.2f}")
            report_content.append(f"  中位数: {desc_stats.loc['50%', col]:.2f}")
            report_content.append("")
        report_content.append("")
        
        # 相关性分析
        report_content.append("## 3. 相关性分析")
        report_content.append("相关系数矩阵:")
        corr_matrix = analysis_results['correlation']
        report_content.append(corr_matrix.to_string())
        report_content.append("")
        
        # 生成热图信息
        report_content.append("## 4. 可视化结果")
        report_content.append("- 已生成相关性热图: heatmap.png")
        report_content.append("  热图展示了各性状之间的相关关系，颜色越红表示正相关越强，越蓝表示负相关越强")
        
        # 保存报告
        with open('report.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Soybean Analyzer - 大豆分析工具',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '--file',
        required=True,
        help='输入数据文件路径（支持TXT、CSV、Excel格式）'
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.file):
        logger.error(f"输入文件不存在: {args.file}")
        sys.exit(1)
    
    # 运行分析
    analyzer = SoyAnalyzer(input_file=args.file)
    analyzer.run()

if __name__ == '__main__':
    main()
