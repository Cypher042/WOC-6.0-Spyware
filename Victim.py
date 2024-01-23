import socket
import os
import pandas as pd
import pickle
import time
import pathlib
import threading
global directory
directory = "D:\\Downloads"
def start():
    while(1):
        ScanDirectory(directory)
def get_size(path):  # get and converts the size of a file into KB/MB/GB
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} bytes"
    elif size < pow(1024, 2):
        return f"{round(size / 1024, 2)} KB"
    elif size < pow(1024, 3):
        return f"{round(size / (pow(1024, 2)), 2)} MB"
    elif size < pow(1024, 4):
        return f"{round(size / (pow(1024, 3)), 2)} GB"


def scanRecurse(baseDir):  # Recursive function that ensure that all folders within the directories are scanned
    for ent in os.scandir(baseDir):
        if ent.is_file():
            yield ent
        else:
            yield from scanRecurse(ent.path)


def ScanDirectory(directory):  # Scans Directory duh

    Filename = []
    Filesize = []
    Filecreate = []
    FileExt = []
    FilePath = []

    try:
        for item in scanRecurse(directory):
            Filename.append(item.name)
            Filesize.append(get_size(item.path))
            Filecreate.append(time.ctime(os.path.getctime(item.path)))
            FileExt.append(pathlib.Path(item).suffix)
            FilePath.append(item.path)
        global df
        df = pd.DataFrame()
        # global df
        df["FileName"] = Filename
        df["FileSize"] = Filesize
        df["FileExtension"] = FileExt
        df["FilePath"] = FilePath
        df["Filecreated"] = Filecreate
        # print(directory)
        # time.sleep(1)
    except Exception as e:
        pass
        df = pd.DataFrame()


# Server configuration
HOST = '127.0.0.1'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print("aaa")
print(f"Server listening on {HOST}:{PORT}")
# args=list(directory.split("`"))
Scanner = threading.Thread(target=start)
print("oo")
Scanner.start()
print("hmm")
while True:
    print("yo")
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")

    while True:
        command = client_socket.recv(1024).decode('utf-8')

        if not command:
            print(f"Client {addr} disconnected.")
            break

        if command == 'list':
            df_bytes = pickle.dumps(df)
            client_socket.sendall(str(len(df_bytes)).encode('utf-8'))
            client_socket.recv(1024)
            client_socket.sendall(df_bytes)
        elif command.startswith('download'):
            filename = command.split(' ')[1]
            file_path = os.path.join(directory, filename)
            for index, row in df.iterrows():
                if row["FileName"] == filename:
                    file_path = row["FilePath"]
            try:
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    client_socket.sendall(str(len(file_data)).encode('utf-8'))
                    client_socket.recv(1024)
                    client_socket.sendall(file_data)
            except FileNotFoundError:
                print(f"File '{filename}' not found.")
                client_socket.sendall(b"File not found")
        elif command.startswith('cd'):
            target_directory = command.split(' ')[1]
            if os.path.exists(target_directory) and os.path.isdir(target_directory):
                directory = target_directory
                client_socket.sendall(b"Directory changed successfully.")
            else:
                client_socket.sendall(b"Invalid directory.")

        else:
            print("Invalid command received.")
    client_socket.close()
