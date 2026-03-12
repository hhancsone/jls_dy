import csv
import re
from collections import Counter
import jieba
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os


def load_csv_data(csv_path):
    """加载CSV文件数据"""
    comments = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                comment = row.get('评论', '')
                if comment:
                    comments.append(comment)
    except Exception as e:
        print(f'加载CSV文件失败: {e}')
    return comments


def clean_text(text):
    """清理文本，去除特殊字符和表情"""
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_keywords(comments, top_n=100):
    """提取关键词"""
    all_words = []
    
    for comment in comments:
        cleaned = clean_text(comment)
        words = jieba.cut(cleaned)
        all_words.extend([w for w in words if len(w) > 1])
    
    word_freq = Counter(all_words)
    return word_freq.most_common(top_n)


def generate_wordcloud(word_freq, width=800, height=400, background_color='white'):
    """生成词云图"""
    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color=background_color,
        font_path='C:/Windows/Fonts/simhei.ttf',
        max_words=100,
        relative_scaling=0.5,
        colormap='viridis'
    ).generate_from_frequencies(dict(word_freq))
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64


def analyze_keywords(csv_path):
    """分析关键词并生成词云"""
    comments = load_csv_data(csv_path)
    
    if not comments:
        return {
            'success': False,
            'message': '未找到评论数据'
        }
    
    keywords = extract_keywords(comments, top_n=100)
    wordcloud_image = generate_wordcloud(keywords)
    
    return {
        'success': True,
        'keywords': [{'word': word, 'count': count} for word, count in keywords[:50]],
        'wordcloud': wordcloud_image,
        'total_comments': len(comments)
    }


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        result = analyze_keywords(csv_path)
        if result['success']:
            print(f'成功分析 {result["total_comments"]} 条评论')
            print(f'提取了 {len(result["keywords"])} 个关键词')
        else:
            print(result['message'])