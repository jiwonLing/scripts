import os
import argparse
from multiprocessing import Pool
import importlib.util


# 动态加载 POC 模块
def load_poc_module(poc_script):
    spec = importlib.util.spec_from_file_location("poc_module", poc_script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# 定义漏洞检测函数
def detect_vulnerability(target, poc_module):
    try:
        # 解析目标 IP 和端口
        if ":" in target:
            ip, port = target.split(":")
            port = int(port)
        else:
            ip = target
            port = 7001  # 默认端口

        # 调用 POC 模块中的 poc 函数
        result = poc_module.poc(ip, port, index=0, timeout=3)
        if result:
            print(f"[+] {target} is vulnerable!")
        else:
            print(f"[-] {target} is not vulnerable.")
    except Exception as e:
        print(f"[!] Error occurred while testing {target}: {e}")


# 主函数
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vulnerability Detection Script")
    parser.add_argument("-u", "--url", help="Single target URL to test")
    parser.add_argument("-f", "--file", help="File containing multiple target URLs")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads for concurrent scanning (default: 10)")
    parser.add_argument("-p", "--poc", required=True, help="Path to the POC script")

    args = parser.parse_args()

    # 加载 POC 模块
    poc_module = load_poc_module(args.poc)

    if args.url:
        detect_vulnerability(args.url, poc_module)
    elif args.file:
        with open(args.file, "r") as f:
            targets = [line.strip() for line in f.readlines()]

        with Pool(processes=args.threads) as pool:
            pool.starmap(detect_vulnerability, [(target, poc_module) for target in targets])
    else:
        parser.print_help()