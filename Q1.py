#Implement a client-server file transfer application where the client sends a file to the server using sockets. 
#Before transmitting the file, pickle the file object on the client side. On the server side, receive the pickled file object, unpickle it, and save it to disk.

#Requirements:
#The client should provide the file path of the file to be transferred.
#The server should specify the directory where the received file will be saved.
#Ensure error handling for file I/O operations, socket connections, and pickling/unpickling.

##########Server (server.py):
import socket
import pickle
import os

def receive_file(connection, save_directory):
    try:
        #take inpickled file object from the client
        file_data = connection.recv(4096)
        file_object = pickle.loads(file_data)

        #get the filename and save the file path
        filename = os.path.basename(file_object['filename'])
        save_path = os.path.join(save_directory, filename)

        #save file to the disk
        with open(save_path, 'wb') as file:
            file.write(file_object['data'])

        print(f"File saved to: {save_path}")

    except Exception as e:
        print(f"Error receiving file: {e}")

def start_server(host, port, save_directory):
    #create a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        #bind the socket (the host and port)
        server_socket.bind((host, port))
        #listening to connect
        server_socket.listen()

        print(f"Server listening on {host}:{port}")

        while True:
            #accept client connection
            connection, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            #recieve and save the file
            receive_file(connection, save_directory)
            connection.close()

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 12345
    save_directory = 'server_received_files'

    #create the directory if there currently isn't an already existing one
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Start the server
    start_server(host, port, save_directory)


#########Client (client.py):
import socket
import pickle

def send_file(file_path, server_host, server_port):
    try:
        #read contents of the file
        with open(file_path, 'rb') as file:
            data = file.read()

        #make a new file directory
        file_object = {
            'filename': file_path,
            'data': data
        }

        #pickle the file object
        pickled_data = pickle.dumps(file_object)

        #make a new socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            #connecting to the server
            client_socket.connect((server_host, server_port))

            #send pickled file object to the server
            client_socket.sendall(pickled_data)

        print("File sent successfully!")

    except Exception as e:
        print(f"Error sending file: {e}")

if __name__ == "__main__":
    #replace with the filepath I'm transferring
    file_path = 'path/to/your/file.txt'
    server_host = '127.0.0.1'
    server_port = 12345

    #send the file to the server
    send_file(file_path, server_host, server_port)