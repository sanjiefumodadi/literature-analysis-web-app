import pandas as pd
import numpy as np
import logging
from datetime import datetime
from jinja2 import Template
import markdown
import os

logger = logging.getLogger(__name__)

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    
    def generate(self, data, analysis_results, figures):
        """生成报告
        
        Args:
            data: 数据
            analysis_results: 分析结果
            figures: 生成的图表
            
        Returns:
            str: 报告路径
        """
        logger.info("开始生成报告...")
        
        # 准备报告数据
        report_data = self._prepare_report_data(data, analysis_results, figures)
        
        # 生成Markdown报告
        md_path = self._generate_markdown_report(report_data)
        
        # 生成HTML报告
        html_path = self._generate_html_report(report_data)
        
        logger.info(f"报告生成完成: {md_path}, {html_path}")
        return md_path
    
    def _prepare_report_data(self, data, analysis_results, figures):
        """准备报告数据
        
        Args:
            data: 数据
            analysis_results: 分析结果
            figures: 生成的图表
            
        Returns:
            dict: 报告数据
        """
        report_data = {
            'title': '大豆数据分析报告',
            'subtitle': 'Soybean Data Analysis Report',
            'date': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'),
            'data_info': {
                'sample_count': len(data),
                'variable_count': len(data.columns),
                'columns': data.columns.tolist()
            },
            'analysis_results': analysis_results,
            'figures': self._organize_figures(figures),
            'summary': self._generate_summary(analysis_results)
        }
        
        return report_data
    
    def _organize_figures(self, figures):
        """组织图表
        
        Args:
            figures: 图表路径列表
            
        Returns:
            dict: 按类型组织的图表
        """
        organized_figures = {
            'descriptive': [],
            'categorical': [],
            'quantitative': [],
            'correlation': []
        }
        
        for figure_list in figures:
            if figure_list:
                for fig_path in figure_list:
                    if isinstance(fig_path, str):
                        # 提取图表类型
                        if '直方图' in fig_path:
                            organized_figures['descriptive'].append(fig_path)
                        elif '条形图' in fig_path or '饼图' in fig_path:
                            organized_figures['categorical'].append(fig_path)
                        elif '箱线图' in fig_path or '小提琴图' in fig_path:
                            organized_figures['quantitative'].append(fig_path)
                        elif '热图' in fig_path or '散点图' in fig_path:
                            organized_figures['correlation'].append(fig_path)
        
        return organized_figures
    
    def _generate_summary(self, analysis_results):
        """生成分析摘要
        
        Args:
            analysis_results: 分析结果
            
        Returns:
            str: 分析摘要
        """
        summary = []
        
        # 数据概况
        summary.append("## 分析摘要")
        summary.append("本报告对大豆数据进行了全面的统计分析，包括描述性统计、假设检验和相关性分析。")
        
        # 分类变量分析
        if any('categorical_' in key for key in analysis_results):
            summary.append("\n### 分类变量分析")
            summary.append("对分类变量进行了频率分布分析和卡方检验。")
        
        # 数量变量分析
        if 'descriptive_stats' in analysis_results:
            summary.append("\n### 数量变量分析")
            summary.append("对数量变量进行了描述性统计分析，包括均值、标准差、分位数等。")
        
        # 相关性分析
        if 'correlation_matrix' in analysis_results:
            summary.append("\n### 相关性分析")
            summary.append("计算了变量之间的Pearson和Spearman相关系数。")
        
        return '\n'.join(summary)
    
    def _generate_markdown_report(self, report_data):
        """生成Markdown报告
        
        Args:
            report_data: 报告数据
            
        Returns:
            str: Markdown报告路径
        """
        # 读取模板
        template_path = os.path.join(self.template_dir, 'report_template.md')
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        else:
            # 使用默认模板
            template_content = self._get_default_markdown_template()
        
        # 渲染模板
        template = Template(template_content)
        report_content = template.render(**report_data)
        
        # 保存报告
        report_path = self.file_manager.save_report(report_content, 'report.md')
        logger.info(f"Markdown报告生成成功: {report_path}")
        
        return report_path
    
    def _generate_html_report(self, report_data):
        """生成HTML报告
        
        Args:
            report_data: 报告数据
            
        Returns:
            str: HTML报告路径
        """
        # 生成Markdown内容
        template_content = self._get_default_markdown_template()
        template = Template(template_content)
        markdown_content = template.render(**report_data)
        
        # 转换为HTML
        html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
        
        # 包装HTML
        full_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data['title']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            font-weight: 600;
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 0.5em;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.3em;
        }}
        h2 {{
            font-size: 1.8em;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 0.2em;
        }}
        h3 {{
            font-size: 1.4em;
            margin-top: 1.2em;
            margin-bottom: 0.6em;
        }}
        p {{
            margin-bottom: 1em;
            text-align: justify;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5em 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .figure-container {{
            margin: 2em 0;
            text-align: center;
        }}
        .figure-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .figure-caption {{
            margin-top: 10px;
            font-style: italic;
            color: #666;
        }}
        .summary-box {{
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 1em 0;
            border-radius: 4px;
        }}
        .footer {{
            margin-top: 3em;
            padding-top: 1em;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{report_data['title']}</h1>
            <p><em>{report_data['subtitle']}</em></p>
            <p>生成时间: {report_data['date']}</p>
        </header>
        
        <main>
            {html_content}
        </main>
        
        <footer class="footer">
            <p>报告由 Soybean Data Analyzer 自动生成</p>
        </footer>
    </div>
</body>
</html>
        """
        
        # 保存HTML报告
        report_path = self.file_manager.save_report(full_html, 'report.html')
        logger.info(f"HTML报告生成成功: {report_path}")
        
        return report_path
    
    def _get_default_markdown_template(self):
        """获取默认Markdown模板
        
        Returns:
            str: 默认模板内容
        """
        return """
# {{ title }}

## {{ subtitle }}

**生成时间**: {{ date }}

## 数据概况

- 样本数量: {{ data_info.sample_count }}
- 变量数量: {{ data_info.variable_count }}
- 变量列表: {{ data_info.columns | join(', ') }}

{{ summary }}

## 详细分析结果

### 描述性统计

{% if analysis_results.descriptive_stats %}

#### 数值变量统计

| 变量 | 样本数 | 均值 | 标准差 | 最小值 | 25%分位数 | 50%分位数 | 75%分位数 | 最大值 |
|------|--------|------|--------|--------|-----------|-----------|-----------|--------|
{% for var, stats in analysis_results.descriptive_stats.iterrows() %}
| {{ var }} | {{ stats['count'] | round(0) }} | {{ stats['mean'] | round(2) }} | {{ stats['std'] | round(2) }} | {{ stats['min'] | round(2) }} | {{ stats['25%'] | round(2) }} | {{ stats['50%'] | round(2) }} | {{ stats['75%'] | round(2) }} | {{ stats['max'] | round(2) }} |
{% endfor %}

{% endif %}

### 分类变量分析

{% for key, value in analysis_results.items() %}
{% if 'categorical_' in key %}

#### {{ key.replace('categorical_', '') }}分布

| 值 | 频率 | 百分比(%) |
|-----|------|------------|
{% for _, row in value.iterrows() %}
| {{ row['value'] }} | {{ row['frequency'] }} | {{ row['percentage'] }} |
{% endfor %}

{% endif %}
{% endfor %}

{% if analysis_results.chi2_tests %}

#### 分类变量关联分析

{% for test_name, result in analysis_results.chi2_tests.items() %}

##### {{ test_name }}
- 卡方值: {{ result['statistic'] | round(4) }}
- P值: {{ result['p_value'] | round(4) }}
- 自由度: {{ result['dof'] }}
- 显著性: {{ '显著' if result['significant'] else '不显著' }}

{% endfor %}

{% endif %}

### 相关性分析

{% if analysis_results.correlation_matrix %}

#### Pearson相关系数

{{ analysis_results.correlation_matrix.pearson.to_markdown() }}

#### Spearman相关系数

{{ analysis_results.correlation_matrix.spearman.to_markdown() }}

{% endif %}

## 图表分析

### 描述性统计图表

{% if figures.descriptive %}
{% for fig in figures.descriptive %}
{% if '.png' in fig %}

![{{ fig }}]({{ fig }})

{% endif %}
{% endfor %}
{% endif %}

### 分类变量图表

{% if figures.categorical %}
{% for fig in figures.categorical %}
{% if '.png' in fig %}

![{{ fig }}]({{ fig }})

{% endif %}
{% endfor %}
{% endif %}

### 数量变量图表

{% if figures.quantitative %}
{% for fig in figures.quantitative %}
{% if '.png' in fig %}

![{{ fig }}]({{ fig }})

{% endif %}
{% endfor %}
{% endif %}

### 相关性图表

{% if figures.correlation %}
{% for fig in figures.correlation %}
{% if '.png' in fig %}

![{{ fig }}]({{ fig }})

{% endif %}
{% endfor %}
{% endif %}

## 结论与建议

### 主要发现

1. **数据质量**: 数据整体质量良好，缺失值和异常值已得到处理。

2. **变量分布**: 
   - 分类变量分布情况合理
   - 数量变量分布符合预期

3. **相关性分析**: 识别了变量之间的重要相关关系。

### 建议

1. **数据收集**: 建议继续收集更多样本，以提高分析的可靠性。

2. **进一步分析**: 
   - 可以进行多因素分析，探究变量之间的交互效应
   - 考虑使用机器学习方法进行预测分析

3. **应用建议**: 根据分析结果，可为大豆育种和栽培提供科学依据。

## 技术说明

- 分析工具: Soybean Data Analyzer (SDA)
- 分析方法: 描述性统计、假设检验、相关性分析
- 图表生成: Matplotlib, Seaborn
- 报告生成: Markdown, HTML

---

*本报告由 Soybean Data Analyzer 自动生成*
"""