from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from crawler import main
from wordcloud_analyzer import analyze_keywords
from comments import get_comments_data
from sentiment_analyzer import analyze_sentiment
from trend_analyzer import analyze_comment_trend
from sentiment_trend_analyzer import analyze_sentiment_trend
from region_analyzer import analyze_region_distribution
from report_generator import generate_report
from utils import find_csv_file, validate_csv_file

app = Flask(__name__)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'douyin-crawler'})


@app.route('/api/crawl', methods=['POST'])
def crawl():
    try:
        data = request.get_json()
        
        if not data or 'videoUrl' not in data:
            return jsonify({
                'success': False,
                'message': '视频链接不能为空'
            }), 400
        
        video_url = data['videoUrl']
        
        print(f'收到爬取请求: {video_url}')
        
        result = main(video_url)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f'爬取失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'爬取失败: {str(e)}'
        }), 500


@app.route('/api/wordcloud', methods=['POST'])
def wordcloud():
    try:
        data = request.get_json()
        
        if not data or 'videoId' not in data:
            return jsonify({
                'success': False,
                'message': '视频ID不能为空'
            }), 400
        
        title = data.get('title', '')
        csv_path = find_csv_file(title)
        
        if not csv_path:
            return jsonify({
                'success': False,
                'message': 'data目录下没有CSV文件'
            }), 404
        
        result = analyze_keywords(csv_path)
        
        return jsonify(result)
        
    except Exception as e:
        print(f'词云分析失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'词云分析失败: {str(e)}'
        }), 500


@app.route('/api/comments', methods=['POST'])
def comments():
    result, status_code = get_comments_data(request.get_json())
    return jsonify(result), status_code


@app.route('/api/sentiment', methods=['POST'])
def sentiment():
    try:
        data = request.get_json()
        
        if not data or 'videoId' not in data:
            return jsonify({
                'success': False,
                'message': '视频ID不能为空'
            }), 400
        
        title = data.get('title', '')
        model_type = data.get('model', 'random_forest')
        
        csv_path = find_csv_file(title)
        
        if not csv_path:
            return jsonify({
                'success': False,
                'message': 'data目录下没有CSV文件'
            }), 404
        
        result = analyze_sentiment(csv_path, model_type=model_type)
        
        return jsonify(result)
        
    except Exception as e:
        print(f'情感分析失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'情感分析失败: {str(e)}'
        }), 500


@app.route('/api/trend', methods=['POST'])
def trend():
    try:
        data = request.get_json()
        
        if not data or 'videoId' not in data:
            return jsonify({
                'success': False,
                'message': '视频ID不能为空'
            }), 400
        
        title = data.get('title', '')
        
        csv_path = find_csv_file(title)
        
        if not csv_path:
            return jsonify({
                'success': False,
                'message': 'data目录下没有CSV文件'
            }), 404
        
        result = analyze_comment_trend(csv_path)
        
        return jsonify(result)
        
    except Exception as e:
        print(f'趋势分析失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'趋势分析失败: {str(e)}'
        }), 500


@app.route('/api/sentiment-trend', methods=['POST'])
def sentiment_trend():
    try:
        data = request.get_json()
        
        if not data or 'videoId' not in data:
            return jsonify({
                'success': False,
                'message': '视频ID不能为空'
            }), 400
        
        title = data.get('title', '')
        model_type = data.get('model', 'random_forest')
        
        csv_path = find_csv_file(title)
        
        if not csv_path:
            return jsonify({
                'success': False,
                'message': 'data目录下没有CSV文件'
            }), 404
        
        result = analyze_sentiment_trend(csv_path, model_type=model_type)
        
        return jsonify(result)
        
    except Exception as e:
        print(f'情感趋势分析失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'情感趋势分析失败: {str(e)}'
        }), 500


@app.route('/api/region', methods=['POST'])
def region():
    try:
        data = request.get_json()
        
        if not data or 'videoId' not in data:
            return jsonify({
                'success': False,
                'message': '视频ID不能为空'
            }), 400
        
        title = data.get('title', '')
        min_count = data.get('minCount', 3)
        
        csv_path = find_csv_file(title)
        
        if not csv_path:
            return jsonify({
                'success': False,
                'message': 'data目录下没有CSV文件'
            }), 404
        
        result = analyze_region_distribution(csv_path, min_count)
        
        return jsonify(result)
        
    except Exception as e:
        print(f'地区分析失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'地区分析失败: {str(e)}'
        }), 500


@app.route('/api/generate-report', methods=['POST'])
def generate_report_api():
    """生成分析报告"""
    try:
        data = request.get_json()
        
        print(f'收到的报告请求数据: {data}')
        
        if not data or 'videoId' not in data:
            return jsonify({
                'success': False,
                'message': '视频ID不能为空'
            }), 400
        
        video_id = data['videoId']
        title = data.get('title', '')
        config = data.get('config', {})
        
        print(f'视频ID: {video_id}')
        print(f'视频标题: {title}')
        print(f'报告配置: {config}')
        
        result = generate_report(video_id, title, config)
        
        return jsonify(result)
        
    except Exception as e:
        print(f'生成报告失败: {str(e)}')
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'生成报告失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    print(f'Flask服务启动在 http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=True)