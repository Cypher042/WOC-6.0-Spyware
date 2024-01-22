import socket
import pickle
import pandas as pd
from tabulate import tabulate

HOST = '127.0.0.1'
PORT = 12345


def PrintDatabase(df):
    print(tabulate(df, headers='keys', tablefmt='psql'))


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))
while True:
    command = input("Enter command ('list' or 'download <filename>' or export or cd): ")

    client_socket.sendall(command.encode('utf-8'))

    if command == 'list':
        data_length = int(client_socket.recv(1024).decode('utf-8'))

        client_socket.sendall(b"ACK")

        received_data = b""
        while len(received_data) < data_length:
            data_chunk = client_socket.recv(1024)
            if not data_chunk:
                break
            received_data += data_chunk
        global received_df
        received_df = pickle.loads(received_data)
        PrintDatabase(received_df)
    elif command.startswith('download'):
        data_length = int(client_socket.recv(1024).decode('utf-8'))
        client_socket.sendall(b"ACK")
        file_data = b""
        while len(file_data) < data_length:
            data_chunk = client_socket.recv(1024)
            if not data_chunk:
                break
            file_data += data_chunk

        if file_data != b"File not found":
            filename = command.split(' ')[1]
            with open(filename, 'wb') as file:
                file.write(file_data)
                print(f"File '{filename}' downloaded successfully.")
        else:
            filename = command.split(' ')[1]
            print(f"File '{filename}' not found on the server.")

    elif command == 'exit':
        break

    elif command.startswith('cd'):
        response = client_socket.recv(1024).decode('utf-8')
        print(response)
    elif command == 'export':
        received_df.to_csv("D:\\Malware Test\\Database.csv")
        print("Exported the Database")
    else:
        print("Invalid command.")
client_socket.close()
