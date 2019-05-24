"""
Aid httpserver v3.0
"""

from socket import *
import sys
from threading import Thread
from httpserver.config import *
import re
import json

# 　服务器地址
ADDR = (HOST, PORT)


# 　和WebFrame通信
def connect_frame(env):
    s = socket()
    try:
        s.connect((frame_ip, frame_port))  # 连接ｗｅｂｆｒａｍｅ
    except Exception as e:
        print(e)
        return
    # 　将请求字典转换为ｊｓｏｎ数据发送
    data = json.dumps(env)
    s.send(data.encode())
    # 　接收ｗｅｂｆｒａｍｅ数据,接收ｊｓｏｎ
    data = s.recv(4096 * 100).decode()
    return json.loads(data)  # 返回数据字典


# 　封装ｈｔｔｐｓｅｒｖｅ基本功能
class HTTPServer(object):
    def __init__(self, address):
        self.address = address
        self.create_socket()
        self.bind()

    # 　创建套接字
    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, DEBUG)

    # 　绑定地址
    def bind(self):
        self.sockfd.bind(self.address)
        self.ip = self.address[0]
        self.port = self.address[1]

    # 　启动服务器
    def serve_forever(self):
        self.sockfd.listen(5)
        print("Listen the port %d..." % self.port)
        while True:
            connfd, addr = self.sockfd.accept()
            print("Connect from", addr)
            client = Thread(target=self.handle, args=(connfd,))
            client.setDaemon(True)
            client.start()

    # 　处理具体的客户端请求
    def handle(self, connfd):
        request = connfd.recv(4096).decode()
        pattern = r"(?P<method>[A-Z]+)\s+(?P<info>/\S*)"
        try:
            env = re.match(pattern, request).groupdict()
        except:
            connfd.close()
            return
        else:
            data = connect_frame(env)
            if data:
                self.response(connfd, data)

    # 　将数据整理为响应格式发送给浏览器
    def response(self, connfd, data):
        # data {'status':'200',data:'content'}
        if data['status'] == '200':
            responseHeaders = "HTTP/1.1 200 OK\r\n"
            responseHeaders += "Content-Type:text/html\r\n"
            responseHeaders += "\r\n"
            responseBody = data['data']
        elif data['status'] == '404':
            responseHeaders = "HTTP/1.1 404 Not Found\r\n"
            responseHeaders += "Content-Type:text/html\r\n"
            responseHeaders += "\r\n"
            responseBody = data['data']
        elif data['status'] == '500':
            pass

        # 　将数据发送给浏览器
        response_data = responseHeaders + responseBody
        connfd.send(response_data.encode())


if __name__ == "__main__":
    httpd = HTTPServer(ADDR)
    httpd.serve_forever()
