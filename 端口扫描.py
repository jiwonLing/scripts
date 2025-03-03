# import socket
# import threading
# import time   # 计算运行时间
#
# def socket_port_thread(ip, start):
#     for port in range(start, start+10):
#         try:
#             s = socket.socket()
#             s.settimeout(0.5)  # 设置无法连接情况下超时时间，提升扫描效率（不用重发数据包）
#             s.connect((ip, port))
#             print(f"端口{port}可用")
#             s.close()
#         except:
#             pass
#
#
# if __name__ == '__main__':
#     ip = '192.168.111.128'
#     threads = []
#     start_time = time.time()
#
#     for i in range(1, 100, 10):
#         thread = threading.Thread(target=socket_port_thread, args=(ip, i))
#         threads.append(thread)
#         thread.start()
#
#     #  等待所有线程完成
#     for thread in threads:
#         thread.join()
#
#     end_time = time.time()
#     total_time = end_time - start_time
#     print(f"扫描完成，总运行时间：{total_time:.2f}秒")
#
#
#
import socket
import threading
import time


# 定义扫描单个端口的函数
def scan_port(ip, port, results):
    """
    扫描指定 IP 地址的单个端口，判断端口状态。

    参数:
        ip (str): 目标主机的 IP 地址。
        port (int): 需要扫描的端口号。
        results (list): 用于存储扫描结果的共享列表。
    """
    try:
        # 创建一个 TCP 套接字
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # 设置连接超时时间为 0.5 秒
            s.settimeout(0.5)
            # 使用 connect_ex 方法尝试连接端口，返回错误码
            result = s.connect_ex((ip, port))
            if result == 0:
                # 如果返回值为 0，表示端口开放
                status = "Open"
            else:
                # 如果返回值非 0，表示端口关闭
                status = "Closed"
    except Exception as e:
        # 如果发生异常，记录错误信息
        status = f"Error ({str(e)})"

    # 将结果存储到共享列表中
    results.append((port, status))


# 主函数，用于启动端口扫描
def main():
    # 目标主机的 IP 地址
    ip = '10.11.153.249'
    # 描的起始端口号
    start_port = 79
    # 扫描的结束端口号
    end_port = 81
    # 最大线程数
    max_threads = 10
    # 用于存储扫描结果的列表
    results = []
    # 用于存储线程对象的列表
    threads = []

    # 记录扫描开始时间
    start_time = time.time()

    # 创建并启动线程
    for port in range(start_port, end_port + 1):
        # 如果线程数量达到最大值，等待一个线程完成
        if len(threads) >= max_threads:
            # 等待第一个线程完成
            threads[0].join()
            # 移除已完成的线程
            threads.pop(0)

        # 创建新线程
        thread = threading.Thread(target=scan_port, args=(ip, port, results))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 记录扫描结束时间
    end_time = time.time()
    # 计算总运行时间
    total_time = end_time - start_time

    # 打印扫描结果
    for port, status in sorted(results):
        print(f"Port {port}: {status}")

    # 打印扫描完成信息
    print(f"扫描完成，总运行时间：{total_time:.2f}秒")


# 程序入口
if __name__ == '__main__':
    main()

