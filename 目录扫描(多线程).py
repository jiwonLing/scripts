# coding=utf-8
import requests  # 用于发送HTTP请求
from concurrent.futures import ThreadPoolExecutor, as_completed  # 用于多线程并发执行
from urllib.parse import urlparse, urljoin  # 用于解析和拼接URL
from colorama import Fore, init  # 用于在终端中显示彩色文本
from tqdm import tqdm  # 用于显示进度条
import argparse  # 用于解析命令行参数
import yaml  # 用于加载配置文件
import time  # 用于控制请求延迟
import random  # 用于随机选择User-Agent

# 初始化colorama，自动重置终端颜色
init(autoreset=True)

# 默认配置
DEFAULT_CONFIG = {
    'timeout': 5,  # 请求超时时间
    'threads': 20,  # 扫描线程数
    'delay': 0.2,  # 请求间隔时间
    'user_agents': [  # 默认的User-Agent列表
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    ],
    'valid_codes': [200, 301, 302, 403],  # 有效的HTTP状态码
    'output_file': 'scan_results.txt'  # 扫描结果保存文件
}


# 加载配置文件
def load_config(config_file):
    try:
        # 打开配置文件并加载内容，与默认配置合并
        with open(config_file) as f:
            return {**DEFAULT_CONFIG, **yaml.safe_load(f)}
    except FileNotFoundError:
        # 如果配置文件不存在，返回默认配置
        return DEFAULT_CONFIG


# 规范化目标URL，确保其以http/https开头，并以/结尾
def normalize_url(target):
    parsed = urlparse(target)
    if not parsed.scheme:
        target = f"http://{target}"  # 如果没有协议头，添加http
    return target.rstrip('/') + '/'  # 去除尾部的/后重新添加


# 检查单个目录是否存在
def check_directory(base_url, directory, config):
    try:
        # 拼接完整的目录URL
        url = urljoin(base_url, directory)
        # 随机选择一个User-Agent
        headers = {'User-Agent': random.choice(config['user_agents'])}

        # 创建会话并发送GET请求
        with requests.Session() as session:
            response = session.get(
                url,
                headers=headers,
                timeout=config['timeout'],
                allow_redirects=False  # 禁止自动重定向
            )

            # 根据配置的延迟时间暂停
            time.sleep(config['delay'])

            # 如果状态码在有效范围内，返回结果
            if response.status_code in config['valid_codes']:
                return (url, response.status_code)

    except Exception as e:
        # 如果发生异常，返回异常信息
        return (url, str(e))

    # 如果目录不存在，返回None
    return None


# 扫描目标网站的目录
def scan_directories(target, config, dictionary_file):
    # 规范化目标URL
    target = normalize_url(target)

    try:
        # 从字典文件中读取目录列表
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            directories = [line.strip() for line in f if line.strip()]

        # 打印扫描信息
        print(f"{Fore.CYAN}开始扫描: {target}")
        print(f"{Fore.BLUE}使用字典: {dictionary_file}")
        print(f"{Fore.YELLOW}线程数: {config['threads']}")

        # 用于存储扫描结果
        results = []
        # 创建线程池
        with ThreadPoolExecutor(max_workers=config['threads']) as executor:
            # 提交目录扫描任务
            futures = {
                executor.submit(check_directory, target, dir, config): dir
                for dir in directories
            }

            # 显示进度条
            with tqdm(total=len(futures), desc="扫描进度") as pbar:
                for future in as_completed(futures):
                    pbar.update(1)  # 更新进度条
                    result = future.result()
                    if result:
                        results.append(result)  # 如果有结果，添加到结果列表中

        # 扫描完成，打印结果
        print(f"\n{Fore.GREEN}扫描完成! 发现 {len(results)} 个有效路径")

        # 将结果保存到文件
        with open(config['output_file'], 'w') as f:
            for url, status in results:
                f.write(f"{status}\t{url}\n")

        print(f"结果已保存到 {config['output_file']}")

    except Exception as e:
        # 如果发生异常，打印错误信息
        print(f"{Fore.RED}发生错误: {str(e)}")


# 主程序入口
if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="网站目录扫描工具")
    parser.add_argument("target", help="目标URL")
    parser.add_argument("-c", "--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("-d", "--dictionary", default="top7k.txt", help="字典文件路径")
    args = parser.parse_args()  # 解析命令行参数

    # 加载配置文件
    config = load_config(args.config)
    # 开始扫描目录
    try:
        scan_directories(args.target, config, args.dictionary)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}用户中断扫描，正在退出...")
    except Exception as e:
        print(f"{Fore.RED}发生错误: {str(e)}")
