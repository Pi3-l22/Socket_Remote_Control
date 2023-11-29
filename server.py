# -- coding:UTF-8 --
import socket
import json
import struct
import os
import time
from pathlib import Path

port = 8888


def get_file(conn):
    # 文件不存在的情况
    rev = conn.recv(1024)
    if rev == b'file_not_exist':
        print('文件不存在')
        return
    conn.send(b'start')
    # 接收文件头部大小
    try:
        rev = conn.recv(4)
        header_size = struct.unpack('i', rev)[0]
    except (struct.error, ConnectionResetError):
        print("An error occurred while receiving the header size.")
        return
    # 发送确认消息
    conn.send(b'size_ok')
    # 接收文件头部信息
    header_bytes = conn.recv(header_size).decode('UTF-8')
    header = json.loads(header_bytes)
    file_name = header['file_name']
    file_size = header['file_size']
    # 发送确认消息
    conn.send(b'header_ok')
    print(f'文件名称：{file_name}，文件大小：{file_size} B')
    print('开始接收文件...')
    try:
        with open(file_name, 'wb') as f:
            while file_size > 0:
                content = conn.recv(1024)
                file_size -= len(content)
                f.write(content)
    except IOError as e:
        print(f"An error occurred while writing the file: {e}")
        return
    print('接收文件完成')


def put_file(conn, file_path):
    rev = conn.recv(1024)
    if rev != b'put':
        print('发送文件失败')
        return
    file_name = Path(file_path).name
    if os.path.isfile(file_path):
        conn.send(b'file_exist')
        rev = conn.recv(1024)
        if rev != b'start':
            print('发送文件失败')
            return
        file_size = os.path.getsize(file_path)
        header = {
            'file_name': file_name,
            'file_size': file_size
        }
        header_json = json.dumps(header)
        header_bytes = header_json.encode('UTF-8')
        header_size = struct.pack('i', len(header_bytes))
        conn.send(header_size)
        rev = conn.recv(1024)
        if rev != b'size_ok':
            print('发送文件头部失败')
            return
        conn.send(header_bytes)
        rev = conn.recv(1024)
        if rev == b'header_ok':
            print(f'文件名称：{file_name}，文件大小：{file_size} B')
            print('开始发送文件...')
            try:
                with open(file_path, 'rb') as f:
                    while file_size > 0:
                        content = f.read(1024)
                        file_size -= len(content)
                        conn.send(content)
            except Exception as e:
                print(f"An error occurred: {e}")
                conn.send(b'')
            print('发送文件完成')
    else:
        conn.send(b'file_not_exist')
        print('文件不存在')


def get_screen(conn):
    pass


def main():
    try:
        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_server.bind(('', port))
        socket_server.listen(5)
    except socket.error as e:
        print(f'发生异常：{e}')
        return
    while True:
        print('等待客户端连接...')
        try:
            conn, address = socket_server.accept()
        except socket.error as e:
            print(f"An error occurred: {e}")
            continue
        print(f'接收到客户端连接，来自{address}')
        while True:
            try:
                data = input('>>> ').encode('UTF-8')
            except UnicodeEncodeError as e:
                print(f"An error occurred: {e}")
                continue
            if data == b'exit':
                conn.send(data)
                break
            elif data == b'\n' or data == b'':
                continue
            conn.send(data)
            command = data.split()
            if command[0] == b'get':
                get_file(conn)
                continue
            elif command[0] == b'put':
                file_path = data.decode('UTF-8').split()[1]
                put_file(conn, file_path)
                continue
            elif command[0] == b'screen':
                get_screen(conn)
                continue
            else:
                reply = conn.recv(102400000).decode("UTF-8")
                if reply == '':
                    continue
                print(reply)
        rev = input('是否断开连接？(y/n) ')
        if rev == 'y':
            conn.close()
            socket_server.close()
            break
        else:
            continue


if __name__ == '__main__':
    main()
