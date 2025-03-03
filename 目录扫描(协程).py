import asyncio
import aiohttp
from urllib.parse import urlparse, urljoin
from colorama import Fore, init
from tqdm.asyncio import tqdm_asyncio
import argparse
import yaml
import random

# 初始化colorama，自动重置终端颜色
init(autoreset=True)

# 默认配置
DEFAULT_CONFIG = {
    'timeout': 5,  # 请求超时时间
    'concurrency': 20,  # 并发协程数
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
        with open(config_file) as f:
            return {**DEFAULT_CONFIG, **yaml.safe_load(f)}
    except FileNotFoundError:
        return DEFAULT_CONFIG

# 规范化目标URL
def normalize_url(target):
    parsed = urlparse(target)
    if not parsed.scheme:
        target = f"http://{target}"
    return target.rstrip('/') + '/'

# 检查单个目录是否存在（异步函数）
async def check_directory(session, base_url, directory, config):
    try:
        url = urljoin(base_url, directory)
        headers = {'User-Agent': random.choice(config['user_agents'])}
        async with session.get(url, headers=headers, timeout=config['timeout'], allow_redirects=False) as response:
            if response.status in config['valid_codes']:
                return (url, response.status)
    except Exception as e:
        return (url, str(e))
    return None

# 扫描目标网站的目录（异步函数）
async def scan_directories(target, config, dictionary_file):
    target = normalize_url(target)
    try:
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            directories = [line.strip() for line in f if line.strip()]
        print(f"{Fore.CYAN}开始扫描: {target}")
        print(f"{Fore.BLUE}使用字典: {dictionary_file}")
        print(f"{Fore.YELLOW}并发数: {config['concurrency']}")

        async with aiohttp.ClientSession() as session:
            tasks = [check_directory(session, target, dir, config) for dir in directories]
            results = []
            for future in tqdm_asyncio.as_completed(tasks, desc="扫描进度"):
                result = await future
                if result:
                    results.append(result)

        print(f"\n{Fore.GREEN}扫描完成! 发现 {len(results)} 个有效路径")
        with open(config['output_file'], 'w') as f:
            for url, status in results:
                f.write(f"{status}\t{url}\n")
        print(f"结果已保存到 {config['output_file']}")

    except Exception as e:
        print(f"{Fore.RED}发生错误: {str(e)}")

# 主程序入口
async def main():
    parser = argparse.ArgumentParser(description="网站目录扫描工具")
    parser.add_argument("target", help="目标URL")
    parser.add_argument("-c", "--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("-d", "--dictionary", default="top7k.txt", help="字典文件路径")
    args = parser.parse_args()

    config = load_config(args.config)
    try:
        await scan_directories(args.target, config, args.dictionary)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}用户中断扫描，正在退出...")
    except Exception as e:
        print(f"{Fore.RED}发生错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())