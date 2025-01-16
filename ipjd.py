import os
import re
import time
import requests
import threading
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed

unique_configs = [
"60.220.167.99:8082",
"60.223.69.250:10000",
"60.223.72.3:8002",
"118.81.167.191:8083",
"171.118.121.141:8082",
"171.118.171.185:8084",
"183.184.43.191:8002",
"221.205.19.39:8082"
]

def check_ip(ip, port):
    try:
        url = f"http://{ip}:{port}/status"
        response = requests.get(url, timeout=1)  # 设置超时为1秒
        if response.status_code == 200 and 'udpxy status' in response.text:
            print(f"扫描到有效ip: {ip}:{port}")
            return f"{ip}:{port}"
    except requests.RequestException:
        return None
    return None

def generate_ips(ip_part):
    a, b, c, d = map(int, ip_part.split('.'))
    return [f"{a}.{b}.{c}.{d}" for d in range(1, 256)]

# 执行 IP 扫描
all_valid_ips = []
for ip_part, port in unique_configs:
    print(f"开始扫描 地址: {ip_part}, 端口: {port}")
    ips_to_check = generate_ips(ip_part)

    valid_ips = []
    total_ips = len(ips_to_check)
    checked_count = [0]

    def update_status(checked_count):
        while checked_count[0] < total_ips:
            print(f"扫描数量: {checked_count[0]}, 有效数量: {len(valid_ips)}")
            time.sleep(10)

    # 启动状态更新线程
    status_thread = threading.Thread(target=update_status, args=(checked_count,))
    status_thread.start()

    max_workers = 10 if option == 0 else 100  # 扫描IP线程数量
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(check_ip, ip, port): ip for ip in ips_to_check}
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            result = future.result()
            if result is not None:
                valid_ips.append(result)
            checked_count[0] += 1

    # 等待状态线程结束
    status_thread.join()
    all_valid_ips.extend(valid_ips)

for ip in all_valid_ips:
    print(ip)

import time
import os
import requests
import concurrent.futures
import re
import threading
import eventlet

urls = [
"http://1.192.248.1:9901",
"http://36.44.157.1:9901",
"http://58.53.152.1:9901",
"http://106.118.70.1:9901",
"http://112.6.165.1:9901",
"http://112.194.128.1:9901",
"http://112.234.21.1:9901",
"http://113.220.235.1:9999",
"http://118.81.242.1:9999",
"http://119.125.104.1:9901",
"http://119.125.134.1:9901",
"http://119.163.56.1:9901",
"http://119.163.57.1:9901",
"http://119.163.61.1:9901",
"http://120.197.43.1:9901",
"http://122.246.75.1:9901",
"http://123.7.110.1:9901",
"http://123.161.37.1:9901",
"http://124.228.160.1:9901",
"http://125.43.244.1:9901",
"http://125.114.241.1:9901",
"http://144.52.160.1:9901",
"http://171.117.15.1:9999",
"http://183.131.246.1:9901",
"http://219.145.59.1:8888",
"http://219.154.240.1:9901",
"http://219.154.242.1:9901",
"http://221.226.4.1:9901",
"http://221.13.235.1:9901",
"http://221.193.168.1:9901"
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
                        name = name.replace("CCTV少儿", "CCTV14")
                        name = name.replace("CCTV15音乐", "CCTV15")
                        name = name.replace("CCTV16奥林匹克", "CCTV16")
                        name = name.replace("CCTV17农业农村", "CCTV17")
                        name = name.replace("CCTV17农业", "CCTV17")
                        name = name.replace("CCTV5+体育赛视", "CCTV5+")
                        name = name.replace("CCTV5+体育赛事", "CCTV5+")
                        name = name.replace("CCTV5+体育", "CCTV5+")                       
                        if "txiptv" in urld:
                            results.append(f"{name},{urld}")
        except:
            continue
    except:
        continue

def natural_key(string):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', string)]

results.sort(key=natural_key)

#生成节目列表 省份运营商.txt
rtp_filename = f'rtp/山西_联通.txt'
txt_filename = f'iptv.txt'

with open(rtp_filename, 'r', encoding='utf-8') as file,open(txt_filename, 'w') as new_file:
    new_file.write('央视频道,#genre#\n')
    for data in file:
        if 'CCTV' in data or 'CHC' in data:
            for url in all_valid_ips:
                new_data = data.replace("rtp://", f"http://{url}/rtp/")
                new_file.write(new_data)
    for result in results:
        channel_name, channel_url = result.split(',')
        if 'CCTV' in channel_name or 'CHC' in channel_name or '地理' in channel_name or '风云' in channel_name:
            new_file.write(f"{channel_name},{channel_url}\n")            

with open(rtp_filename, 'r', encoding='utf-8') as file,open(txt_filename, 'a') as new_file:
    new_file.write('卫视频道,#genre#\n')
    for data in file:
        if '卫视' in data:
            for url in all_valid_ips:
                new_data = data.replace("rtp://", f"http://{url}/rtp/")
                new_file.write(new_data)
    for result in results:
        channel_name, channel_url = result.split(',')
        if '卫视' in channel_name or '凤凰' in channel_name:
            new_file.write(f"{channel_name},{channel_url}\n")
  
with open(f'df.txt', 'r', encoding='utf-8') as file,open(txt_filename, 'a') as new_file:
        data = file.read()
        new_file.write(data)

with open(rtp_filename, 'r', encoding='utf-8') as file,open(txt_filename, 'a') as new_file:
    new_file.write('其它频道,#genre#\n')
    for data in file:
        if 'CCTV' not in data and 'CHC' not in data and '卫视' not in data:
            for url in all_valid_ips:
                new_data = data.replace("rtp://", f"http://{url}/rtp/")
                new_file.write(new_data)

print(f'已生成播放列表，保存至{txt_filename}')
