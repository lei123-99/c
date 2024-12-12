import os
import re
import time
import requests
import threading
from queue import Queue
from threading import Thread
from datetime import datetime
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def generate_ips(ip_part, option):
    a, b, c, d = map(int, ip_part.split('.'))
    if option == 0:
        return [f"{a}.{b}.{c}.{d}" for d in range(1, 256)]
    else:
        return [f"{a}.{b}.{c}.{d}" for c in range(0, 256) for d in range(0, 256)]


def read_config(config_path):
    configs = []
    try:
        with open(config_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    ip_port = parts[0].strip()  # 去除IP:端口部分前后的空格
                    if len(parts) == 2:
                        option = int(parts[1].strip())  # 去除扫描类型部分前后的空格，并转换为整数
                    else:
                        option = 0  # 默认为0
                    if ':' in ip_port:
                        ip, port = ip_port.split(':')
                        configs.append((ip, port, option))
                    else:
                        print(f"配置文件中的 IP:端口 格式错误: {line}")
    except FileNotFoundError:
        print(f"配置文件 '{config_path}' 不存在。")
        return []
    except ValueError as e:
        print(f"配置文件格式错误: {e}")
        return []
    except Exception as e:
        print(f"读取配置文件出错: {e}")
        return []
    return configs

# 定义一个集合，用于存储唯一的 IP 地址及端口组合
unique_ip_ports = set()

# 读取配置文件
config_path = f'config.txt'
configs = read_config(config_path)

# 使用集合去除配置文件内重复的 IP 地址及端口
unique_configs = []
for ip_part, port, option in configs:
    ip_port = f"{ip_part}:{port}"
    if ip_port not in unique_ip_ports:
        unique_ip_ports.add(ip_port)
        unique_configs.append((ip_part, port, option))


# 执行 IP 扫描
all_valid_ips = []
for ip_part, port, option in unique_configs:
    print(f"开始扫描 地址: {ip_part}, 端口: {port}, 类型: {option} （默认类型为0扫描D段，类型为1时扫描C,D段）")
    ips_to_check = generate_ips(ip_part, option)

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
                    
#生成节目列表 省份运营商.txt
rtp_filename = f'sxlt.txt'
txt_filename = f'iptv.txt'                
with open(rtp_filename, 'r', encoding='utf-8') as file,open(txt_filename, 'w') as new_file:
    new_file.write('央视频道,#genre#\n')
    for data in file:
        if 'CCTV' in data or 'CHC' in data:
            for url in all_valid_ips:                            
                new_data = data.replace("rtp://", f"http://{url}/rtp/")                            
                new_file.write(new_data)
                
with open(rtp_filename, 'r', encoding='utf-8') as file,open(txt_filename, 'a') as new_file:
    new_file.write('卫视频道,#genre#\n')
    for data in file:
        if '卫视' in data:  
            for url in all_valid_ips:                            
                new_data = data.replace("rtp://", f"http://{url}/rtp/")                            
                new_file.write(new_data)
                             
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