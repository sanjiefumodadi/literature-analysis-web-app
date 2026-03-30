#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Soybean Data Analyzer (SDA)
大豆数据命令行分析工具

功能：
- 自动数据读取与预处理
- 智能统计分析
- 专业图表生成
- 自动报告生成
- 结果整理到结构化文件夹

用法：
python sda.py --input <data_file> --output <output_dir> [options]
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sda.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.reader import DataReader
from data.cleaner import DataCleaner
from data.preprocessor import DataPreprocessor
from analysis.descriptive import DescriptiveAnalyzer
from analysis.inferential import InferentialAnalyzer
from analysis.effect_size import EffectSizeCalculator
from visualization.plotter import PlotGenerator
from reporting.generator import ReportGenerator
from utils.file_manager import FileManager

class SoybeanDataAnalyzer:
    """大豆数据分析器"""
    
    def __init__(self, input_file, output_dir, analysis_type='comprehensive', verbose=False):
        self.input_file = input_file
        self.output_dir = output_dir
        self.analysis_type = analysis_type
        self.verbose = verbose
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 初始化模块
        self.file_manager = FileManager(output_dir, self.timestamp)
        self.reader = DataReader()
        self.cleaner = DataCleaner()
        self.preprocessor = DataPreprocessor()
        self.descriptive = DescriptiveAnalyzer()
        self.inferential = InferentialAnalyzer()
        self.effect_size = EffectSizeCalculator()
        self.plotter = PlotGenerator(self.file_manager)
        self.report = ReportGenerator(self.file_manager)
    
    def run(self):
        """运行分析流程"""
        try:
            logger.info("=" * 80)
            logger.info("Soybean Data Analyzer (SDA) 启动")
            logger.info(f"分析类型: {self.analysis_type}")
            logger.info(f"输入文件: {self.input_file}")
            logger.info(f"输出目录: {self.output_dir}")
            logger.info("=" * 80)
            
            # 1. 创建输出目录结构
            self.file_manager.create_output_structure()
            
            # 2. 数据读取
            logger.info("【步骤1】数据读取")
            data = self.reader.read_file(self.input_file)
            logger.info(f"✓ 读取成功，共{len(data)}个样本，{len(data.columns)}个变量")
            
            # 3. 数据清洗
            logger.info("【步骤2】数据清洗")
            cleaned_data = self.cleaner.clean(data)
            logger.info(f"✓ 清洗完成，剩余{len(cleaned_data)}个有效样本")
            
            # 4. 数据预处理
            logger.info("【步骤3】数据预处理")
            processed_data = self.preprocessor.preprocess(cleaned_data)
            logger.info("✓ 预处理完成")
            
            # 5. 统计分析
            logger.info("【步骤4】统计分析")
            analysis_results = {}
            
            if self.analysis_type in ['comprehensive', 'categorical']:
                logger.info("  - 分类性状分析")
                categorical_results = self.analyze_categorical(processed_data)
                analysis_results.update(categorical_results)
            
            if self.analysis_type in ['comprehensive', 'quantitative']:
                logger.info("  - 数量性状分析")
                quantitative_results = self.analyze_quantitative(processed_data)
                analysis_results.update(quantitative_results)
            
            if self.analysis_type in ['comprehensive', 'correlation']:
                logger.info("  - 相关性分析")
                correlation_results = self.analyze_correlation(processed_data)
                analysis_results.update(correlation_results)
            
            # 6. 生成图表
            logger.info("【步骤5】图表生成")
            figures = self.plotter.generate_all(processed_data, analysis_results)
            logger.info(f"✓ 生成{len(figures)}个图表")
            
            # 7. 生成报告
            logger.info("【步骤6】报告生成")
            report_path = self.report.generate(processed_data, analysis_results, figures)
            logger.info(f"✓ 报告生成成功: {report_path}")
            
            # 8. 保存数据
            logger.info("【步骤7】数据保存")
            self.file_manager.save_data(data, 'raw_data.csv')
            self.file_manager.save_data(processed_data, 'processed_data.csv')
            logger.info("✓ 数据保存完成")
            
            logger.info("=" * 80)
            logger.info("分析完成！")
            logger.info(f"所有结果已保存至: {self.output_dir}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"分析过程中出错: {str(e)}")
            raise
    
    def analyze_categorical(self, data):
        """分类性状分析"""
        results = {}
        
        # 识别分类变量
        categorical_vars = self.preprocessor.get_categorical_variables(data)
        if categorical_vars:
            logger.info(f"  识别到{len(categorical_vars)}个分类变量")
            
            # 描述性统计
            for var in categorical_vars:
                freq_table = self.descriptive.frequency_table(data[var])
                results[f'categorical_{var}'] = freq_table
            
            # 卡方检验
            if len(categorical_vars) >= 2:
                chi2_results = self.inferential.chi_square_test(data, categorical_vars)
                results['chi2_tests'] = chi2_results
        
        return results
    
    def analyze_quantitative(self, data):
        """数量性状分析"""
        results = {}
        
        # 识别数量变量
        quantitative_vars = self.preprocessor.get_quantitative_variables(data)
        if quantitative_vars:
            logger.info(f"  识别到{len(quantitative_vars)}个数量变量")
            
            # 描述性统计
            desc_stats = self.descriptive.descriptive_statistics(data[quantitative_vars])
            results['descriptive_stats'] = desc_stats
        
        return results
    
    def analyze_correlation(self, data):
        """相关性分析"""
        results = {}
        
        # 识别数量变量
        quantitative_vars = self.preprocessor.get_quantitative_variables(data)
        if len(quantitative_vars) >= 2:
            logger.info(f"  对{len(quantitative_vars)}个数量变量进行相关性分析")
            
            # 计算相关矩阵
            corr_matrix = self.descriptive.correlation_matrix(data[quantitative_vars])
            results['correlation_matrix'] = corr_matrix
        
        return results

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Soybean Data Analyzer (SDA) - 大豆数据命令行分析工具',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='输入数据文件路径（支持TXT、CSV、Excel格式）'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='analysis_results',
        help='输出文件夹路径（默认: analysis_results）'
    )
    
    parser.add_argument(
        '--analysis', '-a',
        choices=['comprehensive', 'categorical', 'quantitative', 'correlation'],
        default='comprehensive',
        help='分析类型（默认: comprehensive）'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出模式'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='SDA v1.0.0'
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        logger.error(f"输入文件不存在: {args.input}")
        sys.exit(1)
    
    # 运行分析
    analyzer = SoybeanDataAnalyzer(
        input_file=args.input,
        output_dir=args.output,
        analysis_type=args.analysis,
        verbose=args.verbose
    )
    
    analyzer.run()

if __name__ == '__main__':
    main()