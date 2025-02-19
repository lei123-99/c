import time
import os
import requests
import concurrent.futures
import re

urls = [
    "http://60.220.147.1:808",
    "http://183.191.0.1:9003",
    "http://110.183.49.1:808"
]

def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/ZHGXTV/Public/json/live_interface.txt"
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
for url in urls:
    url = url.strip()
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    ip_dot_start = url.find(".") + 1
    ip_dot_second = url.find(".", ip_dot_start) + 1
    ip_dot_three = url.find(".", ip_dot_second) + 1
    base_url = url[:ip_start_index]
    ip_address = url[ip_start_index:ip_dot_three]
    port = url[ip_end_index:]
    ip_end = "1"
    modified_ip = f"{ip_address}{ip_end}"
    x_url = f"{base_url}{modified_ip}{port}"
    x_urls.append(x_url)

urls = set(x_urls)

valid_urls = []
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
    try:
        response = requests.get(url, timeout=0.5)
        json_data = response.content.decode('utf-8')

        lines = json_data.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                name, channel_url = line.split(',', 1)
                urls = channel_url.split('/', 3)
                url_data = json_url.split('/', 3)
                if len(urls) >= 4:
                    urld = f"{urls[0]}//{url_data[2]}/{urls[3]}"
                else:
                    urld = f"{urls[0]}//{url_data[2]}"

                if name and urld:
                    name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                    # 这里可以添加更多的名称替换逻辑
                    if "/hls/" in urld:
                        results.append(f"{name},{urld}")
    except Exception as e:
        print(f"Error processing URL {url}: {e}")

rtp_filename = 'mb.txt'
txt_filename = 'itv.txt'

# 确保 mb.txt 文件存在
if not os.path.exists(rtp_filename):
    print(f"{rtp_filename} 文件不存在，请检查。")
else:
    with open(rtp_filename, 'r', encoding='utf-8') as file, open(txt_filename, 'w') as new_file:
        for data in file:
            data = data.strip()
            if data and not data.startswith("#"):
                if "#genre#" in data:
                    new_file.write(data + '\n')
                else:
                    for result in results:
                        channel_name, channel_url = result.split(',')
                        if channel_name == data:
                            new_file.write(f"{channel_name},{channel_url}\n")

    # 追加 df.txt 的内容
    df_filename = 'df.txt'
    if os.path.exists(df_filename):
        with open(df_filename, 'r', encoding='utf-8') as file, open(txt_filename, 'a') as new_file:
            data = file.read()
            new_file.write(data)
    else:
        print(f"{df_filename} 文件不存在，请检查。")
