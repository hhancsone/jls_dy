import csv
import os
import re
import jieba
import numpy as np
from collections import Counter
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import pickle


class SentimentAnalyzer:
    def __init__(self, model_type='random_forest'):
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        self.model_type = model_type
        self.model = self._create_model(model_type)
        self.is_trained = False
        
        self.positive_words = [
            '好', '棒', '赞', '喜欢', '爱', '优秀', '厉害', '强', '牛', '支持', '推荐',
            '有用', '感谢', '开心', '快乐', '幸福', '满意', '完美', '精彩', '漂亮',
            '不错', '给力', '给力', '给力', '太棒了', '太好了', '非常棒', '非常好',
            'good', 'great', 'excellent', 'love', 'like', 'awesome', 'amazing'
        ]
        
        self.negative_words = [
            '差', '烂', '垃圾', '讨厌', '恶心', '失望', '糟糕', '不好', '太差', '差劲',
            '无语', '坑', '骗', '假', '水', '无聊', '浪费时间', '后悔', '生气',
            '愤怒', '悲伤', '难过', '痛苦', '糟糕', '恶心', '讨厌', '失望',
            'bad', 'terrible', 'hate', 'disappointed', 'awful', 'worst'
        ]
    
    def _create_model(self, model_type):
        """根据模型类型创建模型"""
        if model_type == 'random_forest':
            return RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_type == 'naive_bayes':
            return MultinomialNB(alpha=1.0)
        elif model_type == 'logistic_regression':
            return LogisticRegression(max_iter=1000, random_state=42)
        elif model_type == 'svm':
            return SVC(kernel='linear', probability=True, random_state=42)
        elif model_type == 'gradient_boosting':
            return GradientBoostingClassifier(n_estimators=100, random_state=42)
        else:
            return RandomForestClassifier(n_estimators=100, random_state=42)
    
    def load_csv_data(self, csv_path):
        """加载CSV文件数据"""
        comments = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    comment = row.get('评论', '')
                    if comment and comment.strip():
                        comments.append(comment)
        except Exception as e:
            print(f'加载CSV文件失败: {e}')
        return comments
    
    def preprocess_text(self, text):
        """文本预处理"""
        if not text:
            return ''
        
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def rule_based_sentiment(self, text):
        """基于规则的情感分析"""
        if not text:
            return 'neutral'
        
        positive_count = sum(1 for word in self.positive_words if word in text)
        negative_count = sum(1 for word in self.negative_words if word in text)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def train_model(self, csv_path):
        """训练模型"""
        model_name_map = {
            'random_forest': '随机森林',
            'naive_bayes': '朴素贝叶斯',
            'logistic_regression': '逻辑回归',
            'svm': '支持向量机',
            'gradient_boosting': '梯度提升'
        }
        model_name = model_name_map.get(self.model_type, '随机森林')
        print(f'开始训练{model_name}模型...')
        
        comments = self.load_csv_data(csv_path)
        if len(comments) < 10:
            print('数据量不足，使用规则方法')
            return False
        
        processed_texts = [self.preprocess_text(text) for text in comments]
        labels = [self.rule_based_sentiment(text) for text in comments]
        
        if len(set(labels)) < 2:
            print('标签种类不足，使用规则方法')
            return False
        
        X_train, X_test, y_train, y_test = train_test_split(
            processed_texts, labels, test_size=0.2, random_state=42
        )
        
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        self.model.fit(X_train_tfidf, y_train)
        
        accuracy = self.model.score(X_test_tfidf, y_test)
        print(f'{model_name}模型训练完成，准确率: {accuracy:.2%}')
        
        self.is_trained = True
        return True
    
    def predict_sentiment(self, text):
        """预测单条评论的情感"""
        if not text:
            return 'neutral', 0.5
        
        processed_text = self.preprocess_text(text)
        
        if self.is_trained:
            text_tfidf = self.vectorizer.transform([processed_text])
            prediction = self.model.predict(text_tfidf)[0]
            probabilities = self.model.predict_proba(text_tfidf)[0]
            
            classes = self.model.classes_
            label_map = {label: idx for idx, label in enumerate(classes)}
            idx = label_map.get(prediction, 0)
            confidence = probabilities[idx]
            
            return prediction, confidence
        else:
            return self.rule_based_sentiment(text), 0.5
    
    def analyze_comments(self, csv_path):
        """分析CSV文件中的所有评论"""
        print(f'开始分析CSV文件: {csv_path}')
        print(f'文件是否存在: {os.path.exists(csv_path)}')
        
        comments_data = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                print(f'CSV列名: {reader.fieldnames}')
                
                row_count = 0
                for row in reader:
                    row_count += 1
                    comment = row.get('评论', '')
                    if not comment or not comment.strip():
                        continue
                    
                    sentiment, confidence = self.predict_sentiment(comment)
                    
                    comments_data.append({
                        'video_title': row.get('视频标题', ''),
                        'video_tags': row.get('视频标签', ''),
                        'author_name': row.get('作者名称', ''),
                        'nickname': row.get('昵称', ''),
                        'region': row.get('地区', ''),
                        'date': row.get('日期', ''),
                        'comment': comment,
                        'sentiment': sentiment,
                        'confidence': round(confidence, 3)
                    })
                
                print(f'总共读取了 {row_count} 行数据')
        except Exception as e:
            print(f'分析评论失败: {e}')
            import traceback
            traceback.print_exc()
            return []
        
        print(f'分析完成，共处理 {len(comments_data)} 条评论')
        return comments_data
    
    def get_sentiment_stats(self, comments_data):
        """获取情感统计信息"""
        if not comments_data:
            return {
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'positive_ratio': 0,
                'negative_ratio': 0,
                'neutral_ratio': 0
            }
        
        total = len(comments_data)
        positive = sum(1 for c in comments_data if c['sentiment'] == 'positive')
        negative = sum(1 for c in comments_data if c['sentiment'] == 'negative')
        neutral = sum(1 for c in comments_data if c['sentiment'] == 'neutral')
        
        return {
            'total': total,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_ratio': round(positive / total * 100, 2) if total > 0 else 0,
            'negative_ratio': round(negative / total * 100, 2) if total > 0 else 0,
            'neutral_ratio': round(neutral / total * 100, 2) if total > 0 else 0
        }


def analyze_sentiment(csv_path, model_type='random_forest'):
    """分析CSV文件的情感分布"""
    print(f'=== 情感分析开始 ===')
    print(f'CSV路径: {csv_path}')
    print(f'模型类型: {model_type}')
    
    analyzer = SentimentAnalyzer(model_type=model_type)
    
    analyzer.train_model(csv_path)
    comments_data = analyzer.analyze_comments(csv_path)
    stats = analyzer.get_sentiment_stats(comments_data)
    
    print(f'=== 分析结果 ===')
    print(f'总评论数: {stats["total"]}')
    print(f'正面评论: {stats["positive"]} ({stats["positive_ratio"]}%)')
    print(f'负面评论: {stats["negative"]} ({stats["negative_ratio"]}%)')
    print(f'中性评论: {stats["neutral"]} ({stats["neutral_ratio"]}%)')
    print(f'==================')
    
    return {
        'success': True,
        'comments': comments_data,
        'stats': stats,
        'model_type': model_type
    }


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        result = analyze_sentiment(csv_path)
        if result['success']:
            stats = result['stats']
            print(f'分析完成:')
            print(f'总评论数: {stats["total"]}')
            print(f'正面评论: {stats["positive"]} ({stats["positive_ratio"]}%)')
            print(f'负面评论: {stats["negative"]} ({stats["negative_ratio"]}%)')
            print(f'中性评论: {stats["neutral"]} ({stats["neutral_ratio"]}%)')
