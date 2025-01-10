import time
import os
import requests
import concurrent.futures
import re
import threading
import eventlet

urls = [
"http://14.106.236.1:9901",
"http://14.106.239.1:9901",
"http://14.204.108.1:9901",
"http://14.204.109.1:9901",
"http://14.204.29.1:9901",
"http://14.204.46.1:9901",
"http://14.204.53.1:9901",
"http://14.212.185.1:9901",
"http://14.216.204.1:8883",
"http://14.216.215.1:8883",
"http://14.216.218.1:8883",
"http://14.216.220.1:8883",
"http://14.216.221.1:8883",
"http://14.216.227.1:8883",
"http://14.29.76.1:9901",
"http://219.137.202.2:9999",
"http://219.145.20.1:9988",
"http://219.145.59.1:8888",   
"http://219.146.83.2:9902",
"http://219.146.90.2:9901",
"http://219.154.240.2:9901",
"http://219.154.241.2:9901",
"http://219.154.242.2:9901",
"http://219.154.243.2:9901",
"http://219.156.143.2:9901",
"http://219.159.194.2:8181",
"http://61.54.14.1:9901"
    ]

def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/iptv/live/1000.json?key=txiptv"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)

    return modified_urls

def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None

results = []

x_urls = []
for url in urls:  # 对urls进行处理，ip第四位修改为1，并去重
    url = url.strip()
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    ip_dot_start = url.find(".") + 1
    ip_dot_second = url.find(".", ip_dot_start) + 1
    ip_dot_three = url.find(".", ip_dot_second) + 1
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_dot_three]
    port = url[ip_end_index:]
    ip_end = "1"
    modified_ip = f"{ip_address}{ip_end}"
    x_url = f"{base_url}{modified_ip}{port}"
    x_urls.append(x_url)
urls = set(x_urls)  # 去重得到唯一的URL列表

valid_urls = []
#   多线程获取可用url
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    futures = []
    for url in urls:
        url = url.strip()
        modified_urls = modify_urls(url)
        for modified_url in modified_urls:
            futures.append(executor.submit(is_url_accessible, modified_url))

    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            valid_urls.append(result)

for url in valid_urls:
    print(url)
# 遍历网址列表，获取JSON文件并解析
for url in valid_urls:
    try:
        # 发送GET请求获取JSON文件，设置超时时间为0.5秒
        ip_start_index = url.find("//") + 2
        ip_dot_start = url.find(".") + 1
        ip_index_second = url.find("/", ip_dot_start)
        base_url = url[:ip_start_index]  # http:// or https://
        ip_address = url[ip_start_index:ip_index_second]
        url_x = f"{base_url}{ip_address}"

        json_url = f"{url}"
        response = requests.get(json_url, timeout=0.5)
        json_data = response.json()

        try:
            # 解析JSON文件，获取name和url字段
            for item in json_data['data']:
                if isinstance(item, dict):
                    name = item.get('name')
                    urlx = item.get('url')
                    if ',' in urlx:
                        urlx=f"aaaaaaaa"
                    #if 'http' in urlx or 'udp' in urlx or 'rtp' in urlx:
                    if 'http' in urlx:
                        urld = f"{urlx}"
                    else:
                        urld = f"{url_x}{urlx}"

                    if name and urlx:
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
                        name = name.replace("CCTV15音乐", "CCTV15")
                        name = name.replace("CCTV16奥林匹克", "CCTV16")
                        name = name.replace("CCTV17农业农村", "CCTV17")
                        name = name.replace("CCTV17农业", "CCTV17")
                        name = name.replace("CCTV5+体育赛视", "CCTV5+")
                        name = name.replace("CCTV5+体育赛事", "CCTV5+")
                        name = name.replace("CCTV5+体育", "CCTV5+")
                        results.append(f"{name},{urld}")
        except:
            continue
    except:
        continue
        
def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字

# 对频道进行排序
results.sort(key=lambda x: channel_key(x[0]))

with open("iptv.txt", 'w', encoding='utf-8') as file:
    file.write('央视频道,#genre#\n')
    for result in results:
        channel_name, channel_url = result.split(',',1)
        if 'CCTV' in channel_name or 'CHC' in channel_name:
            file.write(f"{channel_name},{channel_url}\n")
    file.write('卫视频道,#genre#\n')
    for result in results:
        channel_name, channel_url = result.split(',',1)
        if '卫视' in channel_name:
            file.write(f"{channel_name},{channel_url}\n")
    file.write('其他频道,#genre#\n')
    for result in results:
        channel_name, channel_url = result.split(',',1)
        if 'CCTV' not in channel_name and '卫视' not in channel_name and '测试' not in channel_name and 'CHC' not in channel_name:
            file.write(f"{channel_name},{channel_url}\n")
                
with open(f'df.txt', 'r', encoding='utf-8') as in_file,open(f'iptv.txt', 'a') as file:
    data = in_file.read()
    file.write(data)
