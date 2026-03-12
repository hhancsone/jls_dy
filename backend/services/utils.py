import os
import sys

def find_csv_file(title, data_dir=None):
    """
    查找CSV文件，支持模糊匹配
    
    Args:
        title: 视频标题
        data_dir: 数据目录路径，默认为当前目录下的data文件夹
    
    Returns:
        CSV文件完整路径，如果找不到返回None
    """
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    safe_title = title if title else 'video'
    safe_title = ''.join(c for c in safe_title if c.isalnum() or c in (' ', '-', '_')).strip()
    csv_filename = f"{safe_title}.csv" if safe_title else "comments.csv"
    csv_path = os.path.join(data_dir, csv_filename)
    
    if os.path.exists(csv_path):
        return csv_path
    
    if not os.path.exists(data_dir):
        return None
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if csv_files:
        return os.path.join(data_dir, csv_files[0])
    
    return None


def validate_csv_file(csv_path):
    """
    验证CSV文件是否存在
    
    Args:
        csv_path: CSV文件路径
    
    Returns:
        (bool, str): (是否有效, 错误信息)
    """
    if not csv_path:
        return False, 'CSV文件路径为空'
    
    if not os.path.exists(csv_path):
        return False, f'CSV文件不存在: {csv_path}'
    
    return True, ''
