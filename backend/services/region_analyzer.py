import csv
import os
from collections import defaultdict, Counter


def analyze_region_distribution(csv_path, min_count=3):
    """分析评论地区分布"""
    print(f'开始分析地区分布: {csv_path}')
    print(f'最少评论数: {min_count}')
    
    region_counts = defaultdict(int)
    total_comments = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                region = row.get('地区', '')
                if region and region.strip():
                    region_counts[region.strip()] += 1
                    total_comments += 1
        
        if total_comments == 0:
            return {
                'success': False,
                'message': '没有找到地区数据'
            }
        
        sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
        
        regions_data = []
        for region, count in sorted_regions:
            if count >= min_count:
                ratio = (count / total_comments) * 100
                regions_data.append({
                    'region': region,
                    'count': count,
                    'ratio': round(ratio, 2)
                })
        
        top_region = sorted_regions[0][0] if sorted_regions else '无'
        
        print(f'分析完成，共 {total_comments} 条评论，覆盖 {len(sorted_regions)} 个地区，显示 {len(regions_data)} 个地区')
        print(f'最活跃地区: {top_region}')
        
        return {
            'success': True,
            'total_comments': total_comments,
            'total_regions': len(regions_data),
            'top_region': top_region,
            'regions': regions_data
        }
        
    except Exception as e:
        print(f'分析失败: {e}')
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': f'分析失败: {str(e)}'
        }
