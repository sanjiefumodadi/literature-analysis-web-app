#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Soybean Data Analyzer (SDA) 测试脚本

功能：
- 测试SDA的核心功能
- 验证数据处理、分析、可视化和报告生成
- 确保工具的稳定性和可靠性
"""

import os
import sys
import unittest
import tempfile
import shutil
from sda import SoybeanDataAnalyzer

class TestSDA(unittest.TestCase):
    """SDA测试类"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试数据
        self.test_data = os.path.join(self.temp_dir, 'test_data.txt')
        self._create_test_data()
        
    def tearDown(self):
        """清理测试环境"""
        # 删除临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_test_data(self):
        """创建测试数据"""
        test_content = """
Plant Hight,Effective Branch Number,Main Stem Node Number,Height of Lowest Pod,Hundred-Seed Weight,Seed Number,Seed Weight per Plant,Pod Number per Plant,Growth Habit,Leaf Shape,Flower Color
65.2,3.5,18,10.5,18.2,120,25.5,45,1,1,1
72.1,2.8,20,12.3,19.5,135,28.7,52,2,2,1
68.5,3.2,19,11.2,17.8,125,26.3,48,1,2,2
75.3,2.5,21,13.1,20.1,140,30.2,55,2,2,1
62.8,3.8,17,9.8,16.9,115,24.1,42,1,1,2
70.4,2.9,20,12.0,18.9,130,27.5,50,2,2,1
66.7,3.3,18,10.8,17.5,122,25.8,46,1,1,2
73.8,2.6,21,12.7,19.8,138,29.5,54,2,2,1
64.1,3.6,17,10.0,17.2,118,24.5,43,1,1,2
71.2,2.7,20,12.5,19.2,132,28.0,51,2,2,1
""".strip()
        
        with open(self.test_data, 'w', encoding='utf-8') as f:
            f.write(test_content)
    
    def test_data_reader(self):
        """测试数据读取功能"""
        from data.reader import DataReader
        
        reader = DataReader()
        data = reader.read_file(self.test_data)
        
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 10)
        self.assertEqual(len(data.columns), 11)
        print("✓ 数据读取测试通过")
    
    def test_data_cleaner(self):
        """测试数据清洗功能"""
        from data.reader import DataReader
        from data.cleaner import DataCleaner
        
        reader = DataReader()
        cleaner = DataCleaner()
        
        data = reader.read_file(self.test_data)
        cleaned_data = cleaner.clean(data)
        
        self.assertIsNotNone(cleaned_data)
        self.assertEqual(len(cleaned_data), 10)
        print("✓ 数据清洗测试通过")
    
    def test_descriptive_analysis(self):
        """测试描述性统计分析"""
        from data.reader import DataReader
        from data.cleaner import DataCleaner
        from analysis.descriptive import DescriptiveAnalyzer
        
        reader = DataReader()
        cleaner = DataCleaner()
        descriptive = DescriptiveAnalyzer()
        
        data = reader.read_file(self.test_data)
        cleaned_data = cleaner.clean(data)
        
        # 测试描述性统计
        numeric_cols = ['Plant Hight', 'Effective Branch Number']
        stats = descriptive.descriptive_statistics(cleaned_data[numeric_cols])
        
        self.assertIsNotNone(stats)
        self.assertEqual(len(stats), 2)
        print("✓ 描述性统计测试通过")
    
    def test_correlation_analysis(self):
        """测试相关性分析"""
        from data.reader import DataReader
        from data.cleaner import DataCleaner
        from analysis.descriptive import DescriptiveAnalyzer
        
        reader = DataReader()
        cleaner = DataCleaner()
        descriptive = DescriptiveAnalyzer()
        
        data = reader.read_file(self.test_data)
        cleaned_data = cleaner.clean(data)
        
        # 测试相关性分析
        numeric_cols = ['Plant Hight', 'Effective Branch Number', 'Main Stem Node Number']
        corr_matrix = descriptive.correlation_matrix(cleaned_data[numeric_cols])
        
        self.assertIsNotNone(corr_matrix)
        self.assertIn('pearson', corr_matrix)
        self.assertIn('spearman', corr_matrix)
        print("✓ 相关性分析测试通过")
    
    def test_inferential_analysis(self):
        """测试推断统计分析"""
        from data.reader import DataReader
        from data.cleaner import DataCleaner
        from analysis.inferential import InferentialAnalyzer
        
        reader = DataReader()
        cleaner = DataCleaner()
        inferential = InferentialAnalyzer()
        
        data = reader.read_file(self.test_data)
        cleaned_data = cleaner.clean(data)
        
        # 测试正态性检验
        normality = inferential.normality_test(cleaned_data[['Plant Hight']])
        self.assertIsNotNone(normality)
        
        # 测试方差齐性检验
        homogeneity = inferential.homogeneity_test(cleaned_data, 'Growth Habit')
        self.assertIsNotNone(homogeneity)
        
        print("✓ 推断统计测试通过")
    
    def test_full_analysis(self):
        """测试完整分析流程"""
        output_dir = os.path.join(self.temp_dir, 'test_output')
        
        analyzer = SoybeanDataAnalyzer(
            input_file=self.test_data,
            output_dir=output_dir,
            analysis_type='comprehensive',
            verbose=True
        )
        
        # 运行分析
        analyzer.run()
        
        # 检查输出目录
        self.assertTrue(os.path.exists(output_dir))
        
        # 检查是否生成了报告
        analysis_dirs = os.listdir(output_dir)
        self.assertTrue(len(analysis_dirs) > 0)
        
        print("✓ 完整分析流程测试通过")
    
    def test_command_line_interface(self):
        """测试命令行接口"""
        import subprocess
        
        output_dir = os.path.join(self.temp_dir, 'cli_test')
        
        # 测试命令行运行
        cmd = [
            sys.executable,
            'sda.py',
            '--input', self.test_data,
            '--output', output_dir,
            '--analysis', 'comprehensive'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 检查命令是否成功执行
        self.assertEqual(result.returncode, 0)
        print("✓ 命令行接口测试通过")

if __name__ == '__main__':
    print("开始测试 Soybean Data Analyzer...")
    print("=" * 60)
    
    # 运行测试
    unittest.main(verbosity=2)
    
    print("=" * 60)
    print("测试完成！")