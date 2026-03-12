import csv
import os
from flask import jsonify
from sentiment_analyzer import SentimentAnalyzer


def get_comments_data(data):
    """
    获取CSV文件中的评论数据
    """
    try:
        if not data or 'videoId' not in data:
            return {
                'success': False,
                'message': '视频ID不能为空'
            }, 400
        
        video_id = data['videoId']
        sentiment_filter = data.get('sentiment', 'all')
        model_type = data.get('model', 'random_forest')
        title = data.get('title', '')
        
        safe_title = title if title else 'video'
        safe_title = ''.join(c for c in safe_title if c.isalnum() or c in (' ', '-', '_')).strip()
        csv_filename = f"{safe_title}.csv" if safe_title else "comments.csv"
        csv_path = os.path.join(os.path.dirname(__file__), 'data', csv_filename)
        
        print(f'收到评论数据请求: {csv_path}, 情感过滤: {sentiment_filter}, 模型: {model_type}')
        
        if not os.path.exists(csv_path):
            print(f'CSV文件不存在，尝试模糊匹配...')
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            if os.path.exists(data_dir):
                csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
                print(f'data目录下的CSV文件: {csv_files}')
                
                if csv_files:
                    csv_path = os.path.join(data_dir, csv_files[0])
                    print(f'使用CSV文件: {csv_path}')
                else:
                    return {
                        'success': False,
                        'message': 'data目录下没有CSV文件'
                    }, 404
            else:
                return {
                    'success': False,
                    'message': f'CSV文件不存在: {csv_filename}'
                }, 404
        
        comments_data = []
        try:
            analyzer = SentimentAnalyzer(model_type=model_type)
            analyzer.train_model(csv_path)
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    comment_text = row.get('评论', '')
                    if not comment_text or not comment_text.strip():
                        continue
                    
                    sentiment, _ = analyzer.predict_sentiment(comment_text)
                    
                    if sentiment_filter != 'all' and sentiment != sentiment_filter:
                        continue
                    
                    comments_data.append({
                        'id': len(comments_data) + 1,
                        'video_title': row.get('视频标题', ''),
                        'video_tags': row.get('视频标签', ''),
                        'author_name': row.get('作者名称', ''),
                        'user_name': row.get('昵称', ''),
                        'region': row.get('地区', ''),
                        'created_at': row.get('日期', ''),
                        'content': comment_text,
                        'sentiment': sentiment
                    })
        except Exception as e:
            print(f'读取CSV文件失败: {e}')
            return {
                'success': False,
                'message': f'读取CSV文件失败: {str(e)}'
            }, 500
        
        return {
            'success': True,
            'comments': comments_data,
            'total': len(comments_data)
        }, 200
        
    except Exception as e:
        print(f'获取评论数据失败: {e}')
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': f'获取评论数据失败: {str(e)}'
        }, 500
