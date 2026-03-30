import os
import logging
import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)

class FileManager:
    """文件管理器"""
    
    def __init__(self, output_dir, timestamp):
        self.output_dir = output_dir
        self.timestamp = timestamp
        self.base_dir = os.path.join(output_dir, f'analysis_{timestamp}')
    
    def create_output_structure(self):
        """创建输出目录结构"""
        logger.info("创建输出目录结构...")
        
        # 定义目录结构
        dirs = [
            self.base_dir,
            os.path.join(self.base_dir, 'data'),
            os.path.join(self.base_dir, 'figures'),
            os.path.join(self.base_dir, 'figures', 'png'),
            os.path.join(self.base_dir, 'figures', 'pdf'),
            os.path.join(self.base_dir, 'figures', 'tiff'),
            os.path.join(self.base_dir, 'tables'),
            os.path.join(self.base_dir, 'reports'),
            os.path.join(self.base_dir, 'logs')
        ]
        
        # 创建目录
        for dir_path in dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"  创建目录: {dir_path}")
            else:
                logger.info(f"  目录已存在: {dir_path}")
        
        logger.info("输出目录结构创建完成")
    
    def save_data(self, data, filename):
        """保存数据文件
        
        Args:
            data: 数据
            filename: 文件名
            
        Returns:
            str: 保存路径
        """
        try:
            data_path = os.path.join(self.base_dir, 'data', filename)
            
            if isinstance(data, pd.DataFrame):
                data.to_csv(data_path, index=False, encoding='utf-8-sig')
            else:
                # 其他数据类型
                with open(data_path, 'w', encoding='utf-8') as f:
                    f.write(str(data))
            
            logger.info(f"  数据保存成功: {data_path}")
            return data_path
        except Exception as e:
            logger.error(f"  数据保存失败: {str(e)}")
            return None
    
    def save_figure(self, fig, filename, format='png'):
        """保存图表
        
        Args:
            fig: 图表对象
            filename: 文件名
            format: 格式 (png, pdf, tiff)
            
        Returns:
            str: 保存路径
        """
        try:
            # 确定保存目录
            if format == 'png':
                fig_dir = os.path.join(self.base_dir, 'figures', 'png')
            elif format == 'pdf':
                fig_dir = os.path.join(self.base_dir, 'figures', 'pdf')
            elif format == 'tiff':
                fig_dir = os.path.join(self.base_dir, 'figures', 'tiff')
            else:
                logger.error(f"  不支持的格式: {format}")
                return None
            
            # 构建文件路径
            file_path = os.path.join(fig_dir, f'{filename}.{format}')
            
            # 保存图表
            fig.savefig(file_path, dpi=600, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            
            logger.info(f"  图表保存成功: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"  图表保存失败: {str(e)}")
            return None
    
    def save_report(self, content, filename):
        """保存报告
        
        Args:
            content: 报告内容
            filename: 文件名
            
        Returns:
            str: 保存路径
        """
        try:
            report_path = os.path.join(self.base_dir, 'reports', filename)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"  报告保存成功: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"  报告保存失败: {str(e)}")
            return None
    
    def save_table(self, data, filename):
        """保存表格
        
        Args:
            data: 表格数据
            filename: 文件名
            
        Returns:
            str: 保存路径
        """
        try:
            table_path = os.path.join(self.base_dir, 'tables', filename)
            
            if isinstance(data, pd.DataFrame):
                data.to_csv(table_path, index=False, encoding='utf-8-sig')
            else:
                # 其他数据类型
                with open(table_path, 'w', encoding='utf-8') as f:
                    f.write(str(data))
            
            logger.info(f"  表格保存成功: {table_path}")
            return table_path
        except Exception as e:
            logger.error(f"  表格保存失败: {str(e)}")
            return None
    
    def get_output_directory(self):
        """获取输出目录
        
        Returns:
            str: 输出目录路径
        """
        return self.base_dir
    
    def get_directory_structure(self):
        """获取目录结构
        
        Returns:
            dict: 目录结构
        """
        structure = {
            'base': self.base_dir,
            'data': os.path.join(self.base_dir, 'data'),
            'figures': {
                'png': os.path.join(self.base_dir, 'figures', 'png'),
                'pdf': os.path.join(self.base_dir, 'figures', 'pdf'),
                'tiff': os.path.join(self.base_dir, 'figures', 'tiff')
            },
            'tables': os.path.join(self.base_dir, 'tables'),
            'reports': os.path.join(self.base_dir, 'reports'),
            'logs': os.path.join(self.base_dir, 'logs')
        }
        return structure
    
    def list_files(self, directory=None):
        """列出目录中的文件
        
        Args:
            directory: 目录路径
            
        Returns:
            list: 文件列表
        """
        if directory is None:
            directory = self.base_dir
        
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        
        return files
    
    def get_file_count(self):
        """获取文件数量
        
        Returns:
            dict: 文件数量统计
        """
        structure = self.get_directory_structure()
        counts = {}
        
        for key, path in structure.items():
            if isinstance(path, dict):
                sub_counts = {}
                for sub_key, sub_path in path.items():
                    if os.path.exists(sub_path):
                        sub_counts[sub_key] = len(os.listdir(sub_path))
                counts[key] = sub_counts
            else:
                if os.path.exists(path):
                    counts[key] = len(os.listdir(path))
        
        return counts
    
    def clean_output(self):
        """清理输出目录
        
        Returns:
            bool: 是否清理成功
        """
        try:
            import shutil
            
            if os.path.exists(self.base_dir):
                shutil.rmtree(self.base_dir)
                logger.info(f"  清理输出目录: {self.base_dir}")
            
            return True
        except Exception as e:
            logger.error(f"  清理输出目录失败: {str(e)}")
            return False