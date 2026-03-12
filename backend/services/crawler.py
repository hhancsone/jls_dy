from DrissionPage import ChromiumPage
from datetime import datetime
import csv
import sys
import json
import time
import re
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def extract_video_info(page):
    """提取视频标题和以#开头的标签"""
    try:
        title_ele = page.ele('tag:h1', timeout=5)
        title = title_ele.text.strip() if title_ele else '未知标题'

        tag_pattern = re.compile(r'#\S+')
        tags = tag_pattern.findall(title)
        pure_title = tag_pattern.sub('', title).strip() or title

        return pure_title, tags
    except Exception as e:
        print(f"提取视频信息失败：{e}")
        return '未知标题', []


def extract_author_info(page):
    """
    提取作者信息
    """
    author_info = {
        '作者名称': '未知'
    }

    try:
        author_ele = page.ele('xpath://div[@class="q5XQ42ql" and @data-click-from="title"]', timeout=3)
        if author_ele:
            author_name = author_ele.text.strip()
            if author_name:
                author_info['作者名称'] = author_name
    except Exception as e:
        print(f"提取作者信息失败：{e}")

    return author_info


def main(video_url):
    comments_data = []
    
    dp = ChromiumPage()
    success_page_count = 0
    video_title = '未知标题'
    video_tags = []
    author_info = {'作者名称': '未知'}
    csv_filename = 'comments.csv'
    
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    try:
        print(f'开始爬取，视频URL: {video_url}')
        print('开始监听评论数据包...')
        dp.listen.start('comment/list/')
        dp.get(video_url)
        print('页面已访问，等待8秒...')
        time.sleep(8)

        video_title, video_tags = extract_video_info(dp)
        author_info = extract_author_info(dp)
        print(f"\n=== 开始爬取 ===")
        print(f"视频标题：{video_title}")
        print(f"视频标签：{','.join(video_tags) if video_tags else '无'}")
        print(f"作者名称：{author_info['作者名称']}")
        print(f"================\n")
        
        safe_title = ''.join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
        csv_filename = f"{safe_title}.csv" if safe_title else "comments.csv"
        csv_path = os.path.join(data_dir, csv_filename)
        print(f"CSV文件名：{csv_filename}")
        print(f"CSV保存路径：{csv_path}")

        with open(csv_path, mode='w', encoding='UTF-8', newline='') as f:
            csv_writer = csv.DictWriter(f, fieldnames=['视频标题', '视频标签', '作者名称', '昵称', '地区', '日期', '评论'])
            csv_writer.writeheader()

            page_num = 1
            has_next_page = True

            while has_next_page:
                print(f'正在采集第 {page_num} 页的数据内容')

                resp = dp.listen.wait(timeout=15)
                if not resp:
                    print(f"第 {page_num} 页等待数据包超时，尝试滚动加载...")
                    dp.scroll.to_bottom()
                    time.sleep(2)
                    resp = dp.listen.wait(timeout=5)
                    if not resp:
                        print(f"第 {page_num} 页仍无数据包，终止爬取")
                        break

                try:
                    json_data = resp.response.body
                    comments = json_data.get('comments', [])
                    
                    print(f'第 {page_num} 页获取到 {len(comments)} 条评论')
                    
                    if not comments:
                        print(f"第 {page_num} 页无评论数据，终止爬取")
                        break

                    for index in comments:
                        try:
                            create_time = index.get('create_time', 0)
                            if create_time == 0:
                                date = '未知时间'
                            else:
                                date = str(datetime.fromtimestamp(create_time))
                            
                            region = index.get('ip_label', '')
                            if not region:
                                ip_client_info = index.get('client_info', {})
                                region = ip_client_info.get('province', '未知')
                        except KeyError as e:
                            print(f"处理单个评论数据出现异常，异常信息：{e}，跳过该评论")
                            continue

                        dit = {
                            '视频标题': video_title,
                            '视频标签': ','.join(video_tags),
                            '作者名称': author_info['作者名称'],
                            '昵称': index.get('user', {}).get('nickname', '未知'),
                            '地区': region,
                            '日期': date,
                            '评论': index.get('text', ''),
                        }

                        try:
                            csv_writer.writerow(dit)
                            comments_data.append(dit)
                            print(json.dumps(dit, ensure_ascii=False))
                        except Exception as e:
                            print(f"写入CSV文件出现异常，异常信息：{e}，跳过该数据")

                    success_page_count += 1

                    next_page = dp.ele('css:.Rcc71LyU', timeout=3)
                    if not next_page:
                        print("未找到下一页元素，终止爬取")
                        break

                    try:
                        print('找到下一页按钮，正在滚动和点击...')
                        dp.scroll.to_see(next_page)
                        time.sleep(1)
                        next_page.click()
                        page_num += 1
                        time.sleep(3)
                        print('下一页已点击，等待数据加载...')
                    except Exception as e:
                        print(f"滚动/点击下一页按钮失败，异常信息：{e}，终止爬取")
                        break

                except Exception as e:
                    print(f"第 {page_num} 页数据处理出现异常，异常信息：{e}，终止爬取")
                    break

            print(f"\n=== 爬取结束 ===")
            print(f"共采集了 {success_page_count} 页评论数据")
            print(f"总共爬取了 {len(comments_data)} 条评论")
            print(f"数据已保存到：{csv_filename}")
            
            print(f"\n=== 视频信息 ===")
            video_info = {
                'title': video_title,
                'author_name': author_info['作者名称'],
                'tags': ','.join(video_tags),
                'comment_count': len(comments_data)
            }
            print(json.dumps(video_info, ensure_ascii=False))
            print(f"================\n")
            
            result = {
                'title': video_title,
                'author_name': author_info['作者名称'],
                'tags': ','.join(video_tags),
                'comment_count': len(comments_data),
                'comments': comments_data
            }
            
            print(f"\n=== 函数返回 ===")
            print(json.dumps(result, ensure_ascii=False))
            print(f"================\n")
            
            return result
            
    except Exception as e:
        print(f"爬取过程中出现致命异常：{e}")
        import traceback
        traceback.print_exc()
    finally:
        print('正在关闭浏览器...')
        dp.quit()
        print("浏览器已关闭")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
        result = main(video_url)
        print(f'成功爬取 {len(result["comments"])} 条评论')
    else:
        video_url = input('请输入抖音视频链接: ')
        if video_url:
            result = main(video_url)
            print(f'成功爬取 {len(result["comments"])} 条评论')
