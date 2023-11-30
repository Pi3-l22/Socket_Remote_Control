from pathlib import Path  # 导入Path类
from secrets import token_bytes  # 导入生成随机字节串的函数
import sys  # 导入sys模块
import time  # 导入time模块
import alist as at  # 导入alist模块


sys.set_int_max_str_digits(0)  # 解除int转str的长度限制
key_store = Path("C:\\KEY_STORE")  # 密钥库路径


# FIXME 进行量子加密的过程中，只需要把生成随机数的函数改成量子随机数生成器即可


def random_key(length):
    key = token_bytes(nbytes=length)  # 生成随机字节串
    key_int = int.from_bytes(key, 'big')  # 将字节串转换成整数
    return key_int


def encrypt(content):
    key_int = random_key(len(content))  # 调用生成大随机数
    content_encrypted = int.from_bytes(
        content, 'big') ^ key_int  # 字节串转整数类型 并异或
    return content_encrypted, key_int


def decrypt(content_length, content_encrypted, key_int):
    content_decrypted = content_encrypted ^ key_int  # 异或解密
    # return int.to_bytes(content_decrypted, length=len(content), byteorder='big').decode()
    # 整数转字节串返回
    return int.to_bytes(content_decrypted, length=content_length, byteorder='big')


# 在指定密钥库中寻找相对应的密钥路径
def find_key_path(download_file_path):
    download_file_name = download_file_path.name  # 获取文件名
    file_name = download_file_name.split('[')[0]  # 从文件名中提取文件名称
    time_id = download_file_name.split(']')[-2].split('[')[-1]  # 从文件名中提取时间戳
    dir_keyword = f"*{file_name}*{time_id}*"  # 需要同时满足 文件名和时间戳
    key_keyword = f"*{file_name}*{time_id}*.key"  # 密钥文件的关键字
    key_store_path = key_store  # 密钥库路径
    dirs = list(key_store_path.glob(dir_keyword))  # 寻找密钥库中的指定文件夹
    if len(dirs) == 0:
        print("没有找到密钥文件夹")
        return 0
    for di in dirs:  # 遍历文件夹
        if di.is_dir():  # 判断是否为文件夹
            key_path = di.glob(key_keyword)  # 寻找密钥文件
            key_paths = list(key_path)  # 迭代器转列表
            if not key_paths:
                print("没有找到密钥文件!")
                return 0
            # 把每个 key 都验证一遍，验证通过之间返回
            for key in key_paths:
                if verify_key(key, download_file_path):
                    print("找到密钥:" + str(key))
                    return key
    print("没有找到密钥文件!!")
    return 0


# 验证密钥文件的大小是否正确
def verify_key(key_path: Path, download_file_path: Path):
    # 匹配密钥和加密文件的长度 相差不超过1B
    if key_path.stat().st_size - 1 <= download_file_path.stat().st_size <= key_path.stat().st_size + 1:
        print("密钥文件大小正确！")
        return 1
    # if key_path.stat().st_size == download_file_path.stat().st_size:
    #     print("密钥文件大小正确！")
    #     return 1
    print("密钥文件大小不正确！")
    return 0


def encrypt_file(file_path):  # key-->
    etime = str(time.time()).replace(".", "-")  # 获取时间戳作为文件标识
    path = Path(file_path)  # 转化为Path对象
    stem = path.stem.replace(' ', '_')  # 获取文件名 去除空格 替换为下划线
    key_store_path = key_store  # 密钥库路径
    key_store_path.mkdir(exist_ok=True)  # 创建密钥库 文件夹已存在不执行
    dir_path = key_store_path / f'{str(stem)}[{etime}]'  # C盘桌面文件夹路径
    dir_path.mkdir(exist_ok=True)  # 创建文件夹 文件夹已存在不执行
    encrypted_file_path = dir_path / f'{str(stem)}[{etime}]{path.suffix}'  # 加密文件路径
    key_path = dir_path / f'{str(stem)}[{etime}].key'  # 密钥文件路径 加上文件名和时间戳
    data_length_path = dir_path / f'{str(stem)}[{etime}].length'  # 数据长度文件路径
    data = path.read_bytes()  # 读取文件内容
    data_length = len(data)  # 获取文件长度
    data_encrypted, key = encrypt(data)  # 加密
    with encrypted_file_path.open('wb') as f1, \
            key_path.open('wb') as f2, \
            data_length_path.open('wb') as f3:
        # 写入文件
        # 将大整数转换为字节数组
        byte_array = data_encrypted.to_bytes(
            (data_encrypted.bit_length() + 7) // 8, byteorder='big')
        # 将字节数组写入文件
        f1.write(byte_array)
        # 将大整数转换为字节数组
        byte_array = data_length.to_bytes(
            (data_length.bit_length() + 7) // 8, byteorder='big')
        # # 将字节数组写入文件
        f3.write(byte_array)
        # 将大整数转换为字节数组
        byte_array = key.to_bytes((key.bit_length() + 7) // 8, byteorder='big')
        # 将字节数组写入文件
        f2.write(byte_array)

    return str(encrypted_file_path)


def decrypt_file(path_encrypted, key_path):
    # path_encrypted = Path(encrypted_file_path)  # 转化为Path对象
    # key_path = Path(key_path)  # 转化为Path对象
    # key_path = path_encrypted.parent / 'key'  # 密钥文件路径
    file_time = str(key_path).split(".")[0]
    file_name = str(path_encrypted).split('[')[0].split('\\')[-1] \
                + str(path_encrypted.suffix)  # 还原文件名
    data_length_path = key_path.parent / f'{file_time}.length'  # 数据长度文件路径
    dir_path = path_encrypted.parent / f'{str(path_encrypted.stem)}_decrypted'  # 解密文件夹路径
    dir_path.mkdir(exist_ok=True)  # 创建文件夹 文件夹已存在不执行
    # decrypted_file_path = dir_path / path_encrypted.name  # 解密文件路径
    decrypted_file_path = dir_path / file_name  # 解密文件路径
    if not path_encrypted.exists() or not key_path.exists():
        print("加密文件不存在！")
        return 0
    if not key_path.exists():
        print("密钥文件不存在！")
        return 0
    with path_encrypted.open('rb') as f1, \
            key_path.open('rb') as f2, \
            decrypted_file_path.open('wb') as f3, \
            data_length_path.open('rb') as f4:
        # 读取文件内容
        data_encrypted = int.from_bytes(f1.read(), byteorder='big')
        key = int.from_bytes(f2.read(), byteorder='big')
        # 通过key的大小获取data_length的大小
        # data_length = key.bit_length() // 8
        # print(data_length)
        data_length = int.from_bytes(f4.read(), byteorder='big')
        decrypted = decrypt(data_length, data_encrypted, key)
        f3.write(decrypted)  # 将明文写入文件
    # 删除加密文件
    path_encrypted.unlink()
    return 1


def upload_file(path):
    print("正在加密中...")
    file_path = encrypt_file(path)
    if file_path:
        print("加密成功！")
    else:
        print("加密失败！")
        return 0
    print("正在上传中...")
    if at.upload(file_path):  # 上传文件
        Path(file_path).unlink()  # 删除加密文件 防止占用空间
        print("上传成功！")
        return 1
    else:
        print("上传失败！")
        return 0


def download_file(file_name, path):
    print("正在下载中...")
    if at.download(file_name, path):
        print("下载成功！")
    else:
        print("下载失败！")
        return 0
    download_file_path = Path(path) / file_name
    key_path = find_key_path(download_file_path)
    if not key_path:
        print("找不到密钥文件")
        return 0
    print("正在解密中...")
    if decrypt_file(download_file_path, key_path):
        print("解密成功！")
        return 1
    else:
        print("解密失败！")
        return 0


def main():
    while True:
        choose = input("请选择：1.上传文件 2.下载文件 3.退出\n")
        if choose == '1':
            path = input("请输入文件路径：")
            upload_file(path)
        elif choose == '2':
            print("文件列表：")
            file_lists = at.list_files()
            for file in file_lists:
                print(file)
            file_name = input("请输入下载文件名：")
            path = input("请输入文件下载位置：")
            download_file(file_name, path)
        elif choose == '3':
            print("退出成功！")
            return 1
        else:
            print("输入错误！")


if __name__ == '__main__':
    find_key_path(Path('C:\desktop\实验2_添加系统调用小组题目[1699637101-405479].docx'))

