import os
import socket

1
# 基于 ping 命令检测子域名是否存在
def ping_domain(main_domain):
    print(f"开始使用 ping 命令检测子域名（主域名：{main_domain}）...")
    with open('SubDomain.dic') as file:
        domain_list = file.readlines()
    for domain in domain_list:
        subdomain = f"{domain.strip()}.{main_domain}"
        result = os.popen(f"ping -n 2 -w 1000 {subdomain}").read()
        if "TTL" in result or "请求超时 " in result:
            print(f"[存在] {subdomain}")
        else:
            print(f"[不存在] {subdomain}")
    print("ping 检测完成。")


# 基于 socket.gethostbyname 检测子域名是否存在
def socket_domain(main_domain):
    print(f"开始使用 socket 检测子域名（主域名：{main_domain}）...")
    with open('SubDomain.dic') as file:
        domain_list = file.readlines()
    for domain in domain_list:
        subdomain = f"{domain.strip()}.{main_domain}"
        try:
            ip = socket.gethostbyname(subdomain)
            print(f"[存在] {subdomain}, IP: {ip}")
        except socket.gaierror:
            print(f"[不存在] {subdomain}")
    print("socket 检测完成。")


if __name__ == '__main__':
    # 用户输入主域名
    main_domain = input("请输入主域名（例如：example.com）：").strip()
    if not main_domain:
        print("主域名不能为空，程序退出。")
        exit()

    # 选择运行的函数
    print("\n请选择检测方式：")
    print("1. 使用 ping 命令检测")
    print("2. 使用 socket 检测")
    choice = input("请输入选项（1 或 2）：")
    if choice == '1':
        ping_domain(main_domain)
    elif choice == '2':
        socket_domain(main_domain)
    else:
        print("无效选项，程序退出。")