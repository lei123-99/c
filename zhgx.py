import time
import os
import requests
import re
import threading
import eventlet

headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

urls = [
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJzaGFueGki"
]

results = []

for url in urls:
    try:
        response = requests.get(url, headers=headers, timeout=15)
        page_content = response.text
        # 查找所有符合指定格式的网址
        pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 设置匹配的格式，如http://8.8.8.8:8888
        urls_all = re.findall(pattern, page_content)
        urls = set(urls_all)  # 去重得到唯一的URL列表
        # 遍历网址列表，获取JSON文件并解析
        for url in urls:
            try:
                # 发送GET请求获取JSON文件，设置超时时间为0.5秒
                json_url = f'{url}/ZHGXTV/Public/json/live_interface.txt'
                response = requests.get(json_url, timeout=0.5)
                json_data = response.content.decode('utf-8')
                try:
                    # 按行分割数据
                    lines = json_data.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line:
                            name, channel_url = line.split(',',1)
                            urls = channel_url.split('/', 3)
                            url_data = json_url.split('/', 3)
                            if len(urls) >= 4:
                                urld = (f"{urls[0]}//{url_data[2]}/{urls[3]}")
                            else:
                                urld = (f"{urls[0]}//{url_data[2]}")

                            if name and urld:
                                # 删除特定文字
                                name = name.replace("cctv", "CCTV")
                                name = name.replace("中央", "CCTV")
                                name = name.replace("央视", "")
                                name = name.replace("高清", "")
                                name = name.replace("HD", "")
                                name = name.replace("标清", "")
                                name = name.replace("频道", "")
                                name = name.replace("-", "")
                                name = name.replace(" ", "")
                                name = name.replace("PLUS", "+")
                                name = name.replace("＋", "+")
                                name = name.replace("(", "")
                                name = name.replace(")", "")
                                name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                                name = name.replace("CCTV1综合", "CCTV1")
                                name = name.replace("CCTV2财经", "CCTV2")
                                name = name.replace("CCTV3综艺", "CCTV3")
                                name = name.replace("CCTV4国际", "CCTV4")
                                name = name.replace("CCTV4中文国际", "CCTV4")
                                name = name.replace("CCTV5体育", "CCTV5")
                                name = name.replace("CCTV6电影", "CCTV6")
                                name = name.replace("CCTV7军事", "CCTV7")
                                name = name.replace("CCTV7军农", "CCTV7")
                                name = name.replace("CCTV7农业", "CCTV7")
                                name = name.replace("CCTV7国防军事", "CCTV7")
                                name = name.replace("CCTV8电视剧", "CCTV8")
                                name = name.replace("CCTV9记录", "CCTV9")
                                name = name.replace("CCTV9纪录", "CCTV9")
                                name = name.replace("CCTV10科教", "CCTV10")
                                name = name.replace("CCTV11戏曲", "CCTV11")
                                name = name.replace("CCTV12社会与法", "CCTV12")
                                name = name.replace("CCTV13新闻", "CCTV13")
                                name = name.replace("CCTV新闻", "CCTV13")
                                name = name.replace("CCTV14少儿", "CCTV14")
                                name = name.replace("CCTV少儿", "CCTV14")
                                name = name.replace("CCTV15音乐", "CCTV15")
                                name = name.replace("CCTV16奥林匹克", "CCTV16")
                                name = name.replace("CCTV17农业农村", "CCTV17")
                                name = name.replace("CCTV17农业", "CCTV17")
                                name = name.replace("CCTV5+体育赛视", "CCTV5+")
                                name = name.replace("CCTV5+体育赛事", "CCTV5+")
                                name = name.replace("CCTV5+体育", "CCTV5+")
                                if "/hls/" in urld:
                                    results.append(f"{name},{urld}")
                except:
                    continue
            except:
                continue
    except:
        continue

def natural_key(string):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', string)]

＃results.sort(key=natural_key)

with open("iptv.txt", 'w', encoding='utf-8') as file:
    file.write('央视频道,#genre#\n')
    for result in results:
        channel_name, channel_url = result.split(',')
        if 'CCTV' in channel_name or 'CHC' in channel_name or '地理' in channel_name or '风云' in channel_name:
            file.write(f"{channel_name},{channel_url}\n")
    file.write('卫视频道,#genre#\n')
    for result in results:
        channel_name, channel_url = result.split(',')
        if '卫视' in channel_name or '凤凰' in channel_name:
            file.write(f"{channel_name},{channel_url}\n")
    file.write('其他频道,#genre#\n')
    for result in results:
        channel_name, channel_url = result.split(',')
        if '乐游' in channel_name or '都市' in channel_name or '车迷' in channel_name or '汽摩' in channel_name or '旅游' in channel_name:
            file.write(f"{channel_name},{channel_url}\n")

with open(f'df.txt', 'r', encoding='utf-8') as in_file,open(f'iptv.txt', 'a') as file:
    data = in_file.read()
    file.write(data)
