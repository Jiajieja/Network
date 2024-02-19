import socket
import sys
import threading
import os

def receive_message(s, username):
    receiving_file = False
    file = None
    download_folder = f"{username}_download"
    os.makedirs(download_folder, exist_ok=True)

    while True:
        data = s.recv(1024)
        if not data:
            if receiving_file and file:
                file.close()
                print(f"File download complete, saved to {download_folder}")

            break

        if receiving_file:
            if b'END' in data:
                end_index = data.find(b'END')
                file.write(data[:end_index])  # 只写入'END'之前的数据
                file.close()
                file = None
                receiving_file = False
                print(f"File download complete, saved to {download_folder}")
            else:
                file.write(data)
        else:
            try:
                message = data.decode('utf-8')
                if message.startswith('FILE:'):
                    filename = message[5:].strip()
                    receiving_file = True
                    file_path = os.path.join(download_folder, filename)
                    file = open(file_path, 'wb')
                    print(f"Start downloading the file: {filename}, save to {download_folder}.")
                    print(f"The file will be saved to: {file_path}")  # 打印文件保存路径
                else:
                    print(message)
            except UnicodeDecodeError:
                continue



def send_message(s, username):
    while True:
        message = input("")
        s.send(message.encode('utf-8'))

        if message.startswith("download "):
            # 当下载命令发送时，等待 receive_message 函数处理文件下载
            pass
        elif message == "exitchat":
            print(f"User {username} logged out of chat")
            break
    s.close()

def start_client(username, hostname, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((hostname, port))
        s.send(username.encode('utf-8'))
        
        thread = threading.Thread(target=receive_message, args=(s, username))
        thread.start()

        send_message(s, username)

if __name__ == "__main__":
    USERNAME = sys.argv[1]
    HOSTNAME = sys.argv[2]
    PORT = int(sys.argv[3])
    start_client(USERNAME, HOSTNAME, PORT)
