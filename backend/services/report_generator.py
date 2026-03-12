import csv
import os
import json
import requests
import base64
from io import BytesIO
from collections import defaultdict, Counter
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sentiment_trend_analyzer import analyze_sentiment_trend

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

API_KEY = "sk-5e8d2e6ac5aa4340a613d52e8ba57e4d"

def analyze_chart_with_qwen(img_base64, chart_type, video_title):
    """使用通义千问API分析图表"""
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {API_KEY}"
    }
    
    prompt = f"""
    请分析这张关于抖音视频"{video_title}"的{chart_type}图表。
    
    请提供以下分析：
    1. 图表的主要趋势或特征
    2. 数据的分布情况
    3. 可能的原因或影响因素
    4. 有价值的洞察和建议
    
    请用简洁、专业的语言进行分析，控制在200-300字之间。
    """
    
    payload = {
        "model": "qwen-vl-max",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": f"data:image/png;base64,{img_base64}"
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
    }
    
    max_try = 3
    for i in range(max_try):
        try:
            ret = requests.post(url, json=payload, headers=headers, timeout=60)
            if ret.status_code != 200:
                print(f"API调用失败，状态码: {ret.status_code}, 响应: {ret.text}")
                raise Exception(f"http status_code: {ret.status_code}")
            ret_json = ret.json()
            result = ret_json.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", [{}])[0].get("text", "")
            return result
        except Exception as e:
            print(f"尝试 {i+1}/{max_try} 失败: {e}")
            if i < max_try - 1:
                import time
                time.sleep(2)
    
    print("通义千问API分析图表失败，将跳过AI分析")
    return None

def get_csv_data(csv_path):
    """读取CSV文件数据"""
    data = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return []

def analyze_quantity_trend(csv_data, time_dimension='daily'):
    """分析数量趋势"""
    from collections import defaultdict
    
    trend_data = defaultdict(int)
    
    for row in csv_data:
        date_str = row.get('日期', '')
        if not date_str:
            continue
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            if time_dimension == 'daily':
                key = date_obj.strftime('%Y-%m-%d')
            else:
                key = date_obj.strftime('%Y-%m')
            trend_data[key] += 1
        except:
            continue
    
    sorted_data = sorted(trend_data.items(), key=lambda x: x[0])
    
    return {
        'type': time_dimension,
        'data': [{'date': k, 'count': v} for k, v in sorted_data]
    }

def analyze_sentiment(csv_data, model_type='random_forest'):
    """分析情感分布"""
    from sentiment_analyzer import SentimentAnalyzer
    
    analyzer = SentimentAnalyzer(model_type=model_type)
    comments = [row.get('评论', '') for row in csv_data if row.get('评论', '')]
    
    if not comments:
        return {'positive': 0, 'negative': 0, 'neutral': 0}
    
    results = []
    for comment in comments:
        sentiment, confidence = analyzer.predict_sentiment(comment)
        results.append(sentiment)
    
    positive = sum(1 for r in results if r == 'positive')
    negative = sum(1 for r in results if r == 'negative')
    neutral = sum(1 for r in results if r == 'neutral')
    total = len(results)
    
    return {
        'positive': positive,
        'negative': negative,
        'neutral': neutral,
        'total': total,
        'positive_ratio': round(positive / total * 100, 2) if total > 0 else 0,
        'negative_ratio': round(negative / total * 100, 2) if total > 0 else 0,
        'neutral_ratio': round(neutral / total * 100, 2) if total > 0 else 0
    }

def analyze_wordcloud(csv_data, min_count=3):
    """分析词云"""
    from wordcloud_analyzer import extract_keywords, clean_text
    import jieba
    from collections import Counter
    
    comments = [row.get('评论', '') for row in csv_data if row.get('评论', '')]
    
    if not comments:
        return []
    
    all_words = []
    for comment in comments:
        cleaned = clean_text(comment)
        words = jieba.cut(cleaned)
        all_words.extend([w for w in words if len(w) > 1])
    
    word_freq = Counter(all_words)
    
    keywords = [{'word': word, 'count': count} for word, count in word_freq.most_common(100) if count >= min_count]
    
    return keywords

def analyze_region(csv_data, min_count=3):
    """分析地区分布"""
    region_counts = defaultdict(int)
    total_comments = 0
    
    for row in csv_data:
        region = row.get('地区', '')
        if region and region.strip():
            region_counts[region.strip()] += 1
            total_comments += 1
    
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
    
    return regions_data

def generate_trend_chart(trend_data):
    """生成数量趋势图表"""
    dates = [item['date'] for item in trend_data['data']]
    counts = [item['count'] for item in trend_data['data']]
    
    plt.figure(figsize=(12, 6))
    plt.plot(dates, counts, marker='o', linewidth=2, markersize=6, color='#3b82f6')
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('评论数', fontsize=12)
    plt.title('评论数量趋势', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

def generate_sentiment_chart(sentiment_data):
    """生成情感分布图表"""
    labels = ['正面', '负面', '中性']
    sizes = [sentiment_data['positive'], sentiment_data['negative'], sentiment_data['neutral']]
    colors = ['#22c55e', '#ef4444', '#6b7280']
    
    plt.figure(figsize=(10, 8))
    wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                        startangle=90, textprops={'fontsize': 12})
    plt.setp(autotexts, size=12, weight='bold')
    plt.title('情感分布分析', fontsize=14, fontweight='bold')
    plt.axis('equal')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

def generate_sentiment_trend_chart(trend_data, time_dimension='daily'):
    """生成情感趋势图表"""
    if time_dimension == 'daily':
        data = trend_data.get('daily', [])
        title = '每日情感趋势'
        marker = 'o'
    else:
        data = trend_data.get('monthly', [])
        title = '每月情感趋势'
        marker = 's'
    
    if not data:
        return None
    
    dates = [item['date'] for item in data]
    positive = [item['positive'] for item in data]
    negative = [item['negative'] for item in data]
    neutral = [item['neutral'] for item in data]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(dates, positive, label='正面', color='#22c55e', marker=marker, linewidth=2)
    ax.plot(dates, negative, label='负面', color='#ef4444', marker=marker, linewidth=2)
    ax.plot(dates, neutral, label='中性', color='#6b7280', marker=marker, linewidth=2)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('评论数量', fontsize=12)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

def generate_wordcloud_chart(keywords):
    """生成词云图表"""
    from wordcloud import WordCloud
    
    word_freq = {kw['word']: kw['count'] for kw in keywords}
    
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        font_path='C:/Windows/Fonts/msyh.ttc',
        max_words=100,
        relative_scaling=0.5,
        colormap='viridis'
    ).generate_from_frequencies(word_freq)
    
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('评论词云', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

def generate_region_chart(regions):
    """生成地区分布图表"""
    top_regions = regions[:15]
    region_names = [r['region'] for r in top_regions]
    counts = [r['count'] for r in top_regions]
    
    plt.figure(figsize=(12, 8))
    bars = plt.barh(region_names, counts, color='#8b5cf6')
    plt.xlabel('评论数', fontsize=12)
    plt.ylabel('地区', fontsize=12)
    plt.title('地区分布分析', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2,
                f'{width}',
                ha='left', va='center', fontsize=10)
    
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

def generate_report_html(video_title, config, analysis_results, chart_analyses):
    """生成HTML报告"""
    sections = []
    
    if config.get('quantityTrend') and 'quantityTrend' in analysis_results:
        trend = analysis_results['quantityTrend']
        chart_img = trend.get('chart', '')
        chart_analysis = chart_analyses.get('quantityTrend', '')
        
        trend_section = f"""
        <h2>数量趋势分析</h2>
        <p><strong>时间维度：</strong>{trend['type'] == 'daily' and '按天' or '按月'}</p>
        <p><strong>总评论数：</strong>{sum(item['count'] for item in trend['data'])}</p>
        {f'<div style="text-align:center;margin:20px 0;"><img src="data:image/png;base64,{chart_img}" alt="数量趋势图" style="max-width:100%;height:auto;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);"/></div>' if chart_img else ''}
        {f'<div style="background:#f9fafb;padding:20px;border-radius:8px;margin:20px 0;"><h3 style="margin-top:0;color:#374151;">AI分析</h3><p style="color:#6b7280;line-height:1.8;">{chart_analysis}</p></div>' if chart_analysis else ''}
        """
        sections.append(trend_section)
    
    if config.get('sentimentAnalysis') and 'sentimentAnalysis' in analysis_results:
        sentiment = analysis_results['sentimentAnalysis']
        chart_img = sentiment.get('chart', '')
        chart_analysis = chart_analyses.get('sentimentAnalysis', '')
        
        sentiment_section = f"""
        <h2>情感分布分析</h2>
        <p><strong>分析模型：</strong>{config.get('sentimentModel', '随机森林')}</p>
        <p><strong>总评论数：</strong>{sentiment['total']}</p>
        <div style="display:flex;gap:20px;margin-bottom:20px;">
            <div style="flex:1;padding:20px;background:#dcfce7;border-radius:8px;">
                <h3 style="margin:0 0 10px 0;color:#16a34a;">正面评论</h3>
                <p style="font-size:24px;margin:0;color:#16a34a;">{sentiment['positive']}</p>
                <p style="margin:0;color:#16a34a;">{sentiment['positive_ratio']}%</p>
            </div>
            <div style="flex:1;padding:20px;background:#fee2e2;border-radius:8px;">
                <h3 style="margin:0 0 10px 0;color:#dc2626;">负面评论</h3>
                <p style="font-size:24px;margin:0;color:#dc2626;">{sentiment['negative']}</p>
                <p style="margin:0;color:#dc2626;">{sentiment['negative_ratio']}%</p>
            </div>
            <div style="flex:1;padding:20px;background:#e5e7eb;border-radius:8px;">
                <h3 style="margin:0 0 10px 0;color:#6b7280;">中性评论</h3>
                <p style="font-size:24px;margin:0;color:#6b7280;">{sentiment['neutral']}</p>
                <p style="margin:0;color:#6b7280;">{sentiment['neutral_ratio']}%</p>
            </div>
        </div>
        {f'<div style="text-align:center;margin:20px 0;"><img src="data:image/png;base64,{chart_img}" alt="情感分布图" style="max-width:100%;height:auto;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);"/></div>' if chart_img else ''}
        {f'<div style="background:#f9fafb;padding:20px;border-radius:8px;margin:20px 0;"><h3 style="margin-top:0;color:#374151;">AI分析</h3><p style="color:#6b7280;line-height:1.8;">{chart_analysis}</p></div>' if chart_analysis else ''}
        """
        sections.append(sentiment_section)
    
    if config.get('sentimentTrend') and 'sentimentTrend' in analysis_results:
        trend = analysis_results['sentimentTrend']
        chart_img = trend.get('chart', '')
        chart_analysis = chart_analyses.get('sentimentTrend', '')
        
        trend_section = f"""
        <h2>情感趋势分析</h2>
        <p><strong>分析模型：</strong>{config.get('sentimentTrendModel', '随机森林')}</p>
        <p><strong>总评论数：</strong>{trend['total_comments']}</p>
        <div style="display:flex;gap:20px;margin-bottom:20px;">
            <div style="flex:1;padding:20px;background:#dcfce7;border-radius:8px;">
                <h3 style="margin:0 0 10px 0;color:#16a34a;">正面评论</h3>
                <p style="font-size:24px;margin:0;color:#16a34a;">{trend['positive_count']}</p>
                <p style="margin:0;color:#16a34a;">{trend['positive_ratio']}%</p>
            </div>
            <div style="flex:1;padding:20px;background:#fee2e2;border-radius:8px;">
                <h3 style="margin:0 0 10px 0;color:#dc2626;">负面评论</h3>
                <p style="font-size:24px;margin:0;color:#dc2626;">{trend['negative_count']}</p>
                <p style="margin:0;color:#dc2626;">{trend['negative_ratio']}%</p>
            </div>
            <div style="flex:1;padding:20px;background:#e5e7eb;border-radius:8px;">
                <h3 style="margin:0 0 10px 0;color:#6b7280;">中性评论</h3>
                <p style="font-size:24px;margin:0;color:#6b7280;">{trend['neutral_count']}</p>
                <p style="margin:0;color:#6b7280;">{trend['neutral_ratio']}%</p>
            </div>
        </div>
        {f'<div style="text-align:center;margin:20px 0;"><img src="data:image/png;base64,{chart_img}" alt="情感趋势图" style="max-width:100%;height:auto;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);"/></div>' if chart_img else ''}
        {f'<div style="background:#f9fafb;padding:20px;border-radius:8px;margin:20px 0;"><h3 style="margin-top:0;color:#374151;">AI分析</h3><p style="color:#6b7280;line-height:1.8;">{chart_analysis}</p></div>' if chart_analysis else ''}
        """
        sections.append(trend_section)
    
    if config.get('wordCloud') and 'wordCloud' in analysis_results:
        keywords = analysis_results['wordCloud']
        chart_img = keywords.get('chart', '')
        chart_analysis = chart_analyses.get('wordCloud', '')
        
        keyword_section = f"""
        <h2>评论词云分析</h2>
        <p><strong>最少出现次数：</strong>{config.get('minKeywordCount', 3)}</p>
        <p><strong>关键词数量：</strong>{len(keywords.get('data', []))}</p>
        {f'<div style="text-align:center;margin:20px 0;"><img src="data:image/png;base64,{chart_img}" alt="词云图" style="max-width:100%;height:auto;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);"/></div>' if chart_img else ''}
        {f'<div style="background:#f9fafb;padding:20px;border-radius:8px;margin:20px 0;"><h3 style="margin-top:0;color:#374151;">AI分析</h3><p style="color:#6b7280;line-height:1.8;">{chart_analysis}</p></div>' if chart_analysis else ''}
        """
        sections.append(keyword_section)
    
    if config.get('regionDistribution') and 'regionDistribution' in analysis_results:
        regions = analysis_results['regionDistribution']
        chart_img = regions.get('chart', '')
        chart_analysis = chart_analyses.get('regionDistribution', '')
        
        region_section = f"""
        <h2>地区分布分析</h2>
        <p><strong>最少评论数：</strong>{config.get('minRegionCount', 3)}</p>
        <p><strong>覆盖地区数：</strong>{len(regions.get('data', []))}</p>
        {f'<div style="text-align:center;margin:20px 0;"><img src="data:image/png;base64,{chart_img}" alt="地区分布图" style="max-width:100%;height:auto;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);"/></div>' if chart_img else ''}
        {f'<div style="background:#f9fafb;padding:20px;border-radius:8px;margin:20px 0;"><h3 style="margin-top:0;color:#374151;">AI分析</h3><p style="color:#6b7280;line-height:1.8;">{chart_analysis}</p></div>' if chart_analysis else ''}
        """
        sections.append(region_section)
    
    if not sections:
        return None
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>抖音评论分析报告 - {video_title}</title>
        <style>
            body {{
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 20px;
                background-color: #f5f7fa;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #1f2937;
                font-size: 28px;
                margin-bottom: 10px;
                text-align: center;
            }}
            h2 {{
                color: #374151;
                font-size: 22px;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #e5e7eb;
            }}
            h3 {{
                color: #6b7280;
                font-size: 18px;
                margin-bottom: 10px;
            }}
            p {{
                margin-bottom: 10px;
                font-size: 16px;
            }}
            strong {{
                color: #1f2937;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>抖音评论分析报告</h1>
            <p style="text-align:center;color:#6b7280;font-size:18px;">视频标题：{video_title}</p>
            <p style="text-align:center;color:#6b7280;font-size:14px;">生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            {''.join(sections)}
            
            <div class="footer">
                <p>本报告由抖音评论分析系统自动生成</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template

def generate_report(video_id, title, config):
    """生成完整报告"""
    print(f'开始生成报告：视频ID={video_id}, 标题={title}')
    print(f'配置：{config}')
    
    safe_title = title if title else 'video'
    safe_title = ''.join(c for c in safe_title if c.isalnum() or c in (' ', '-', '_')).strip()
    csv_filename = f"{safe_title}.csv" if safe_title else "comments.csv"
    csv_path = os.path.join(os.path.dirname(__file__), 'data', csv_filename)
    
    print(f'CSV文件路径：{csv_path}')
    
    if not os.path.exists(csv_path):
        print(f'CSV文件不存在，尝试模糊匹配...')
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            if csv_files:
                csv_path = os.path.join(data_dir, csv_files[0])
                print(f'使用CSV文件：{csv_path}')
            else:
                return {
                    'success': False,
                    'message': 'data目录下没有CSV文件'
                }
        else:
            return {
                'success': False,
                'message': f'CSV文件不存在: {csv_filename}'
            }
    
    csv_data = get_csv_data(csv_path)
    
    if not csv_data:
        return {
            'success': False,
            'message': 'CSV文件为空或格式错误'
        }
    
    print(f'CSV数据行数：{len(csv_data)}')
    
    analysis_results = {}
    chart_analyses = {}
    
    if config.get('quantityTrend'):
        print('分析数量趋势...')
        trend_data = analyze_quantity_trend(csv_data, config.get('trendTimeDimension', 'daily'))
        print('生成数量趋势图表...')
        chart_img = generate_trend_chart(trend_data)
        trend_data['chart'] = chart_img
        analysis_results['quantityTrend'] = trend_data
        
        print('使用通义千问分析数量趋势图表...')
        analysis = analyze_chart_with_qwen(chart_img, '数量趋势', title)
        chart_analyses['quantityTrend'] = analysis
    
    if config.get('sentimentAnalysis'):
        print('分析情感分布...')
        sentiment_data = analyze_sentiment(csv_data, config.get('sentimentModel', 'random_forest'))
        print('生成情感分布图表...')
        chart_img = generate_sentiment_chart(sentiment_data)
        sentiment_data['chart'] = chart_img
        analysis_results['sentimentAnalysis'] = sentiment_data
        
        print('使用通义千问分析情感分布图表...')
        analysis = analyze_chart_with_qwen(chart_img, '情感分布', title)
        chart_analyses['sentimentAnalysis'] = analysis
    
    if config.get('sentimentTrend'):
        print('分析情感趋势...')
        trend_data = analyze_sentiment_trend(csv_path, config.get('sentimentTrendModel', 'random_forest'))
        if trend_data.get('success'):
            print('生成情感趋势图表...')
            time_dimension = config.get('sentimentTrendTimeDimension', 'daily')
            chart_img = generate_sentiment_trend_chart(trend_data, time_dimension)
            trend_data['chart'] = chart_img
            analysis_results['sentimentTrend'] = trend_data
            
            print('使用通义千问分析情感趋势图表...')
            analysis = analyze_chart_with_qwen(chart_img, '情感趋势', title)
            chart_analyses['sentimentTrend'] = analysis
        else:
            print(f'情感趋势分析失败: {trend_data.get("message")}')
    
    if config.get('wordCloud'):
        print('分析词云...')
        keywords = analyze_wordcloud(csv_data, config.get('minKeywordCount', 3))
        print('生成词云图表...')
        chart_img = generate_wordcloud_chart(keywords)
        wordcloud_data = {'data': keywords, 'chart': chart_img}
        analysis_results['wordCloud'] = wordcloud_data
        
        print('使用通义千问分析词云图表...')
        analysis = analyze_chart_with_qwen(chart_img, '词云分析', title)
        chart_analyses['wordCloud'] = analysis
    
    if config.get('regionDistribution'):
        print('分析地区分布...')
        regions = analyze_region(csv_data, config.get('minRegionCount', 3))
        print('生成地区分布图表...')
        chart_img = generate_region_chart(regions)
        region_data = {'data': regions, 'chart': chart_img}
        analysis_results['regionDistribution'] = region_data
        
        print('使用通义千问分析地区分布图表...')
        analysis = analyze_chart_with_qwen(chart_img, '地区分布', title)
        chart_analyses['regionDistribution'] = analysis
    
    print('生成HTML报告...')
    report_html = generate_report_html(title, config, analysis_results, chart_analyses)
    
    return {
        'success': True,
        'report': report_html,
        'analysis_results': analysis_results
    }
