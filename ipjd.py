import asyncio
import logging
import time
from urllib.parse import urlparse
import aiofiles
import aiohttp
import re
import os
from typing import List, Tuple

# 网段最小范围
min_network_segment = 1
# 网段最大范围
max_network_segment = 256
# 每个频道需要的个数
result_counter = 8
# 控制异步并发的信号量
semaphore = asyncio.Semaphore(200)
# 请求等待时间, 并发量越高时间要越长
time_out = 3
# 源URL
src_urls = [
"http://1.192.248.1:9901",
"http://36.44.157.1:9901",
"http://58.53.152.1:9901",
"http://106.118.70.1:9901",
"http://112.6.165.1:9901",
"http://113.220.235.1:9999",
"http://119.125.104.1:9901",
"http://119.163.56.1:9901",
"http://119.163.61.19901",
"http://120.197.43.1:9901",
"http://122.246.75.1:9901",
"http://123.7.110.1:9901",
"http://124.228.160.1:9901",
"http://125.43.244.1:9901",
"http://125.114.241.1:9901",
"http://144.52.160.1:9901",
"http://183.131.246.1:9901",    
"http://219.145.59.1:8888",    
"http://219.154.242.1:9901",    
"http://221.226.4.1:9901",
"http://221.13.235.1:9901",   
"http://221.193.168.1:9901",
"http://61.54.14.1:9901"
    ]

src_urls_test = src_urls[31:36]

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def modify_urls(src_url):
    # 正则替换IP第四位
    modified_urls = []
    pattern = r'\.(\d+)\:'
    request_param = "/iptv/live/1000.json?key=txiptv"
    for i in range(min_network_segment, max_network_segment):
        base_url = re.sub(pattern, f".{i}:", src_url)
        modified_url = f"{base_url}{request_param}"
        modified_urls.append(modified_url)
    return set(modified_urls)

async def check_url_code(url):
    # 校验url是否可用
    async with semaphore:  # 限制并发数
        try:
            async with aiohttp.ClientSession() as session:
                logging.info(f"开始校验: {url}")
                async with session.get(url, timeout=time_out) as resp:
                    if resp.status == 200:
                        return url
                    else:
                        return None
        except Exception:
            return None

async def get_valid_urls() -> list:
    # 获取所有有效的url

    tasks = []  # 用来存储所有异步任务

    for src_url in src_urls:
        urls = modify_urls(src_url)
        for url in urls:
            # 启动每个校验任务
            tasks.append(check_url_code(url))

    # 等待所有校验任务完成，并获取结果
    results = await asyncio.gather(*tasks)

    # 筛选出有效的url
    valid_urls = [url for url in results if url is not None]

    logging.info(f"共找到 {len(valid_urls)} 个有效的URL")
    return valid_urls

def replace_name(name: str) -> str:
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
    name = name.replace("CCTV少儿", "CCTV14")
    name = name.replace("CCTV15音乐", "CCTV15")
    name = name.replace("CCTV16奥林匹克", "CCTV16")
    name = name.replace("CCTV17农业农村", "CCTV17")
    name = name.replace("CCTV17农业", "CCTV17")
    name = name.replace("CCTV5+体育赛视", "CCTV5+")
    name = name.replace("CCTV5+体育赛事", "CCTV5+")
    name = name.replace("CCTV5+体育", "CCTV5+")
    return name

# 获取所有可用的电视名字和链接
async def get_iptv_name_m3u8s() -> List[Tuple[str, str, str]]:
    """
    遍历url，获取JSON并解析

    返回一个列表元组:
        1是tv名字,
        2是m3u8的url
    """
    m3u8_list = []
    urls = await get_valid_urls()

    for url in urls:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=2) as resp:
                    json_data = await resp.json()
            try:
                # 解析JSON文件，获取name和url字段
                for item in json_data['data']:
                    if isinstance(item, dict):
                        name = item.get('name')
                        url_param = item.get('url')
                        if ',' in url_param:
                            url_param = f"aaaaaaaa"
                        # if 'http' in urlx or 'udp' in urlx or 'rtp' in urlx:
                        if 'http' in url_param:
                            parsed_url = urlparse(url)
                            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                            m3u9_url = f"{url_param}"
                        else:
                            parsed_url = urlparse(url)
                            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                            m3u9_url = f"{base_url}{url_param}"
                        if name and url_param:
                            # 修改特定文字
                            m3u8_list.append((replace_name(name), m3u9_url, base_url))
            except:
                continue
        except:
            continue
    return m3u8_list

async def download_ts(m3u8_list: List[Tuple[str, str, str]]) -> Tuple[
    List[Tuple[str, str, str]], List[Tuple[str, str]]]:
    """
    下载ts测试url是否可用

    返回两个列表:
        第一个是结果
        第二个是错误
    """
    results = []
    error_channels = []

    async with aiohttp.ClientSession() as session:
        async def download_channel(name: str, url: str, base_url: str):
            try:
                async with session.get(url, timeout=2) as resp:
                    lines = (await resp.text()).strip().split('\n')
                    ts_lists = [line.split('/')[-1] for line in lines if not line.startswith('#')]  # 获取m3u8文件下视频流后缀
                    if not ts_lists:
                        raise ValueError(f"No video segments found for {name}")

                    ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
                    ts_url = f"{base_url}/{ts_lists[0]}"  # 拼接单个视频片段下载链接

                    # 获取TS文件内容并测量下载时间
                    start_time = time.time()
                    async with session.get(ts_url, timeout=1) as ts_response:
                        content = await ts_response.read()
                    end_time = time.time()
                    response_time = (end_time - start_time)

                    if content:
                        # 使用aiofiles异步写入文件
                        async with aiofiles.open(ts_lists_0, 'ab') as f:
                            await f.write(content)

                        file_size = len(content)
                        download_speed = file_size / response_time / 1024  # kB/s
                        normalized_speed = min(max(download_speed / 1024, 0.001), 100)  # 转换为MB/s并限制在1~100之间

                        os.remove(ts_lists_0)  # 删除下载的文件

                        result = (name, url, f"{normalized_speed:.3f} MB/s")
                        results.append(result)
                        numberx = (len(results) + len(error_channels)) / len(m3u8_list) * 100
                        logging.info(
                            f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(m3u8_list)} 个 , 总进度：{numberx:.2f} %。")
            except Exception as e:
                error_channel = (name, url)
                error_channels.append(error_channel)
                numberx = (len(results) + len(error_channels)) / len(m3u8_list) * 100
                logging.info(
                    f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(m3u8_list)} 个 , 总进度：{numberx:.2f} %。")

        # 使用 asyncio.gather 执行所有下载任务
        if m3u8_list != None:
            tasks = [download_channel(name, url, base_url) for name, url, base_url in m3u8_list]
            await asyncio.gather(*tasks)
        else:
            pass

    return results, error_channels

def results_sort(results) -> list:
    # 频道进行排序
    def channel_key(channel_name):
        match = re.search(r'\d+', channel_name)
        if match:
            return int(match.group())
        else:
            return float('inf')  # 返回一个无穷大的数字作为关键字

    results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
    results.sort(key=lambda x: channel_key(x[0]))
    return results

def write_itv_txt(results):
    # 写出txt类型
    results_sort(results)
    with open("iptv.txt", 'w', encoding='utf-8') as file:
        channel_counters = {}
        file.write('央视频道,#genre#\n')
        for result in results:
            channel_name, channel_url, speed = result
            if 'CCTV' in channel_name or 'CHC' in channel_name or '地理' in channel_name or '风云' in channel_name:
                if channel_name in channel_counters:
                    if channel_counters[channel_name] >= result_counter:
                        continue
                    else:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] += 1
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] = 1
        channel_counters = {}
        file.write('卫视频道,#genre#\n')
        for result in results:
            channel_name, channel_url, speed = result
            if '卫视' in channel_name or '凤凰' in channel_name:
                if channel_name in channel_counters:
                    if channel_counters[channel_name] >= result_counter:
                        continue
                    else:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] += 1
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] = 1
        channel_counters = {}
        file.write('其他频道,#genre#\n')
        for result in results:
            channel_name, channel_url, speed = result
            if '乐途' in channel_name or '都市' in channel_name or '车迷' in channel_name or '汽摩' in channel_name or '旅游' in channel_name:
                if channel_name in channel_counters:
                    if channel_counters[channel_name] >= result_counter:
                        continue
                    else:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] += 1
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] = 1

async def start():
    start_time = time.time()
    m3u8_list = await get_iptv_name_m3u8s()
    results, error_channels = await download_ts(m3u8_list)
    write_itv_txt(results)
    logging.info(f"成功频道: {len(results)}个.", )
    logging.info(f"错误频道: {len(error_channels)}个.")
    end_time = time.time()
    logging.info(f"耗时: {end_time - start_time}s.")

if __name__ == '__main__':
    asyncio.run(start())
            
with open(f'df.txt', 'r', encoding='utf-8') as in_file,open(f'iptv.txt', 'a') as file:
    data = in_file.read()
    file.write(data)
