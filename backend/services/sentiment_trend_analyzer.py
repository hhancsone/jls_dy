import csv
import os
from collections import defaultdict
from datetime import datetime
from sentiment_analyzer import SentimentAnalyzer


def analyze_sentiment_trend(csv_path, model_type='random_forest'):
    """分析情感趋势（按天/月统计正面、负面、中性评论的数量）"""
    print(f'开始分析情感趋势: {csv_path}, 模型: {model_type}')
    
    analyzer = SentimentAnalyzer(model_type=model_type)
    analyzer.train_model(csv_path)
    
    daily_sentiment = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
    monthly_sentiment = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
    
    total_comments = 0
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                comment = row.get('评论', '')
                date_str = row.get('日期', '')
                
                if not comment or not comment.strip():
                    continue
                
                sentiment, _ = analyzer.predict_sentiment(comment)
                
                total_comments += 1
                
                if sentiment == 'positive':
                    positive_count += 1
                elif sentiment == 'negative':
                    negative_count += 1
                else:
                    neutral_count += 1
                
                if date_str:
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        
                        day_key = date_obj.strftime('%Y-%m-%d')
                        month_key = date_obj.strftime('%Y-%m')
                        
                        daily_sentiment[day_key][sentiment] += 1
                        monthly_sentiment[month_key][sentiment] += 1
                    except Exception as e:
                        print(f'日期解析失败: {date_str}, 错误: {e}')
                        continue
        
        daily_data = sorted(daily_sentiment.items(), key=lambda x: x[0])
        monthly_data = sorted(monthly_sentiment.items(), key=lambda x: x[0])
        
        print(f'分析完成，共统计 {len(daily_data)} 天，{len(monthly_data)} 个月的数据')
        
        return {
            'success': True,
            'daily': [{'date': date, **counts} for date, counts in daily_data],
            'monthly': [{'date': date, **counts} for date, counts in monthly_data],
            'total_comments': total_comments,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_ratio': round(positive_count / total_comments * 100, 2) if total_comments > 0 else 0,
            'negative_ratio': round(negative_count / total_comments * 100, 2) if total_comments > 0 else 0,
            'neutral_ratio': round(neutral_count / total_comments * 100, 2) if total_comments > 0 else 0
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
        result = analyze_sentiment_trend(csv_path)
        if result['success']:
            print(f'总评论数: {result["total_comments"]}')
            print(f'正面评论: {result["positive_count"]} ({result["positive_ratio"]}%)')
            print(f'负面评论: {result["negative_count"]} ({result["negative_ratio"]}%)')
            print(f'中性评论: {result["neutral_count"]} ({result["neutral_ratio"]}%)')