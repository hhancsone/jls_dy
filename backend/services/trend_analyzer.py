import csv
import os
from collections import defaultdict
from datetime import datetime


def analyze_comment_trend(csv_path):
    """分析评论数量趋势（按天/月统计）"""
    print(f'开始分析评论趋势: {csv_path}')
    
    daily_counts = defaultdict(int)
    monthly_counts = defaultdict(int)
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = row.get('日期', '')
                if not date_str:
                    continue
                
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    
                    day_key = date_obj.strftime('%Y-%m-%d')
                    month_key = date_obj.strftime('%Y-%m')
                    
                    daily_counts[day_key] += 1
                    monthly_counts[month_key] += 1
                except Exception as e:
                    print(f'日期解析失败: {date_str}, 错误: {e}')
                    continue
        
        daily_data = sorted(daily_counts.items(), key=lambda x: x[0])
        monthly_data = sorted(monthly_counts.items(), key=lambda x: x[0])
        
        print(f'分析完成，共统计 {len(daily_data)} 天，{len(monthly_data)} 个月的数据')
        
        return {
            'success': True,
            'daily': [{'date': date, 'count': count} for date, count in daily_data],
            'monthly': [{'date': date, 'count': count} for date, count in monthly_data],
            'total_days': len(daily_data),
            'total_months': len(monthly_data),
            'total_comments': sum(daily_counts.values())
        }
        
    except Exception as e:
        print(f'分析失败: {e}')
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': f'分析失败: {str(e)}'
        }


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        result = analyze_comment_trend(csv_path)
        if result['success']:
            print(f'总评论数: {result["total_comments"]}')
            print(f'统计天数: {result["total_days"]}')
            print(f'统计月数: {result["total_months"]}')
