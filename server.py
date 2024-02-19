import socket
import threading
import os
import sys
import logging

logging.basicConfig(filename='server.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s: %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')
clients = {}

def broadcast(message, sender):
    for client, username in clients.items():
        if client != sender:
            try:
                client.send(message.encode())
                logging.info(f"Broadcast messages: {message} from {username}")
            except:
                client.close()
                del clients[client]
                logging.info(f"Client {username} disconnected, removed from online list")

def private_message(sender, recipient_username, message):
    recipient_conn = None
    for conn, username in clients.items():
        if username == recipient_username:
            recipient_conn = conn
            break

    if recipient_conn:
        try:
            sender_username = clients[sender]
            recipient_conn.send(f"{sender_username} send to you: {message}".encode())
            logging.info(f"Private massage from {sender_username} to {recipient_username}: {message}")
        except Exception as e:
            logging.error(f"Error sending private message: {e}")
            recipient_conn.close()
            del clients[recipient_conn]
    else:
        sender.send(f"User not found: {recipient_username}".encode())
        logging.warning(f"Private message failed to send, user not found: {recipient_username}")

def send_file_list(connection):
    download_folder = 'download'
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    files = os.listdir(download_folder)
    files_list = ', '.join(files) if files else "Download folder is empty"
    connection.send(files_list.encode())


def send_file(conn, file_path):
    file_name = os.path.basename(file_path)
    conn.send(f"FILE:{file_name}".encode())  # 发送文件名
    with open(file_path, 'rb') as file:
        while True:
            byteData = file.read(1024)
            if byteData:
                conn.send(byteData)
            else:
                break
        conn.send(b'END')  # 发送结束标记




def client_thread(conn, addr):
    username = conn.recv(1024).decode()
    clients[conn] = username
    broadcast(f"{username} joined servers", conn)
    logging.info(f"User {username} joined servers，the IP Address is：{addr[0]}" )
    print(f"{username}  joined servers，the IP Address is{addr[0]}")

    online_users = "，".join(clients.values())
    welcome_message = f"Login successful! Welcome to this online chat room, current online users:{online_users}"
    conn.send(welcome_message.encode())

    while True:
        try:
            message = conn.recv(1024).decode()
            if message:
                logging.info(f"Message received from {username}: {message}")
                if message == "get file list":
                    send_file_list(conn)
                    logging.info(f"User {username} requests a list of files to download")
                elif message.startswith("download "):
                    file_name = message[len("download "):].strip()
                    file_path = os.path.join('download', file_name)
                    if os.path.exists(file_path):
                        send_file(conn, file_path)
                        logging.info(f"User {username} requesting file download {file_name}")
                    else:
                        conn.send(b'File not found')
                        logging.warning(f"User {username} requested to download file {file_name}, but the file does not exist.")
                elif message == "exitchat":
                    logging.info(f"User {username} has logged out of the chat room")
                    break
                elif message.startswith("send to "):
                    parts = message[8:].strip().split(" ", 1)
                    if len(parts) == 2:
                        recipient, private_message_content = parts
                        private_message(conn, recipient, private_message_content)
                    else:
                        conn.send("Private message format error, please use 'send to [username] [message]'".encode())
                        logging.warning(f"User {username} sent private message in wrong format.")
                else:
                    broadcast(f"{username} to all: {message}", conn)
                    logging.info(f"User {username} to all: {message}")
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            print(f"Error processing message: {e}")
            break
    
    broadcast(f"User {username} has logged out", conn)
    print(f"{username} has logged out")
    logging.info(f"{username} has logged out")
    conn.close()
    if conn in clients:
        del clients[conn]

def start_server(port):
    if not os.path.exists('download'):
        os.makedirs('download')
        logging.info("Create 'download' folder")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', port))
    server.listen()
    logging.info(f"Server is up, waiting for client to connect...")
    print("Server is up, waiting for client to connect...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=client_thread, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    PORT = int(sys.argv[1])
    start_server(PORT)
