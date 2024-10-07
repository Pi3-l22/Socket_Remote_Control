# Socket远程连接

[English](README.md) | [简体中文](README_CN.md)

一个基于Python Socket的远程控制程序。

项目的详细介绍可以参见我的博客文章：[Pi3'Notes](https://blog.pi3.fun/post/2023/11/%E5%9F%BA%E4%BA%8Esocket%E7%9A%84%E8%BF%9C%E7%A8%8B%E6%8E%A7%E5%88%B6%E7%A8%8B%E5%BA%8F/)

## 功能

- 远程命令执行
- 远程文件上传
- 远程文件下载
- 获取远程主机截图
- 获取和解密微信数据
  - 使用[pywxdump](https://github.com/xaoyaoo/PyWxDump)项目
  - 服务器必须运行在Windows系统上

## 依赖

查看[requirements.txt](requirements.txt)获取所需的Python包列表。

## 使用方法

1. 设置服务器：
   - 编辑`server.py`，如有需要可以配置`port`变量。
   - 在控制机器上运行`server.py`：
     ```
     python server.py
     ```

2. 设置客户端：
   - 编辑`client.py`，将`ip`变量设置为你的服务器IP地址。
   - 在目标机器上运行`client.py`：
     ```
     python client.py
     ```

3. 连接成功后，你可以在服务器控制台使用各种命令：
   - 执行shell命令
   - `get <文件名>`：从客户端下载文件
   - `put <文件名>`：上传文件到客户端
   - `screen`：捕获客户端屏幕截图
   - `wxinfo`：获取客户端的微信信息
   - `wxchat`：从客户端获取并解密微信数据
   - `flask`：启动Flask服务器查看聊天记录（在获取微信数据之后）
   - `exit`：关闭连接

## 实现原理

本项目使用Python的`socket`库实现反向连接，客户端尝试连接服务器，在服务器和客户端之间建立TCP连接。服务器可以向客户端发送命令，这些命令随后在客户端机器上执行。文件传输通过自定义协议实现，该协议在发送实际文件内容之前发送文件元数据。

对于微信数据的获取和解密，项目利用了`pywxdump`库。解密后的数据被压缩并发送回服务器进行分析。

截图功能使用`PIL`库捕获客户端的屏幕并将其发送回服务器。

## 衍生

基于此程序，我还编写了`peppa_pig.py`这个简单的程序，这个程序源于[Python - 100天从新手到大师](https://github.com/Pi3-l22/Python-Learn)项目中的示例程序。而在此项目中，我用来隐藏`client.py`的执行。可以将`peppa_pig.py`和`client.py`使用[pyinstaller](https://pyinstaller.org/en/stable/)工具打包为exe文件，并命名为一个不起眼的名称，这样在执行该程序时，不会引起对方的警觉，屏幕上只会出现一个peppa_pig的绘图程序，后台则会同时运行`client.py`，实现木马功能。

利用类似的思想，你可以将控制程序隐藏在任何程序中，比如游戏、网盘等。

## 注意

此工具以及其衍生项目仅用于教育目的。在使用它之前，请确保你有权限操作目标系统。

利用此工具对他人进行网络攻击是违法的，请勿用于非法用途！

对于使用本项目进行非法操作，造成严重后果的，均与本人无关！

## 待完成

- [X] 优化远程主机反弹shell后的交互
- [ ] 监控鼠标位置
- [ ] 监控键盘输入
- [ ] 控制主机屏幕操作

## 许可证

[MIT许可证](LICENSE)
