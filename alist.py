import requests  # 导入requests库
import urllib  # 编码解码
from urllib import parse  # 编码解码
from pathlib import Path  # 导入Path类
from requests_toolbelt import MultipartEncoder  # put请求所需的模块

alist_url = 'http://120.27.210.48:51122'  # 云盘远程地址
root_dir = 'Encrypted Files'  # 加密文件目录
token = ''  # token


# 检查服务器是否上线 连通性ping检测
def check_server():
    try:
        r = requests.get(alist_url)
        if r.status_code == 200:
            return 'The Remote Server is online.'
        else:
            return 'The Remote Server is offline.'
    except:
        return 'The Remote Server is offline.'


# 得到token
def get_token(username, password):
    url = alist_url + '/api/auth/login'  # 接口地址
    data = {
        "Username": username,
        "Password": password
    }
    r = requests.post(url, data=data)
    d = r.json()
    if d['code'] == 400:  # 400 为用户名或密码错误
        return '400'
    if d['code'] == 429:  # 429 为登录错误次数过多
        return '429'
    if d['code'] == 401:
        return '401'
    token = d['data']['token']
    return token


# 获取当前用户信息
def get_user_info():
    url = alist_url + '/api/me'  # 接口地址
    headers = {
        'Authorization': token
    }
    r = requests.get(url, headers=headers)
    if r is None:
        return 0
    if r.json()['code'] == 401:
        return '401'
    user_dict = r.json()['data']
    return user_dict


def list_files():
    url = alist_url + '/api/fs/list'  # 接口地址
    headers = {
        'Authorization': token
    }
    data = {
        "path": root_dir,
        "password": "",
        "page": 1,
        "per_page": 100,
        "refresh": 'false'
    }
    r = requests.post(url, headers=headers, data=data)
    # 解析json数据
    r_dict = r.json()
    # 如果没有数据 返回0
    if r_dict['data']['content'] is None:
        return 0
    file_lists = []  # 创建空列表
    for file in r_dict['data']['content']:  # 遍历每一行
        file_dict = {
            'type': 'D' if file['is_dir'] else 'F',
            'name': file['name'],
            'size': file['size'],
            'time': file['modified'].split('.')[0].replace('T', ' ')
        }  # 拆分成字典
        file_lists.append(file_dict)  # 将字典添加到列表中
    return file_lists


# 上传文件
def upload(file_path):
    url = alist_url + '/api/fs/form'  # 接口地址
    file_name = Path(file_path).name  # 获取文件名
    data = MultipartEncoder(
        fields={
            'file': (file_name, open(file_path, 'rb'))
        }
    )
    file_name = urllib.parse.quote(file_name, 'utf-8')  # 对文件名进行URL编码
    headers = {
        'Authorization': token,
        'Content-Type': data.content_type,
        'file-path': root_dir + '/' + file_name
    }
    r = requests.put(url=url, headers=headers, data=data)
    if r.status_code == 200:
        return 1
    else:
        return 0


# 下载文件
def download(file_name, path):
    url = alist_url + '/api/fs/get'  # 接口地址
    headers = {
        'Authorization': token
    }
    data = {
        'path': root_dir + '/' + file_name,
    }
    r = requests.post(url=url, headers=headers, data=data)
    raw_url = r.json()['data']['raw_url']
    r = requests.get(raw_url)
    if r.status_code == 200:
        with open(path + '/' + file_name, 'wb') as f:
            f.write(r.content)
        return 1
    else:
        return 0
