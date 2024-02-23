#Real-Time Chat Application with Pickling:

#Develop a simple real-time chat application where multiple clients can communicate with each other via a central server using sockets. 
#Messages sent by clients should be pickled before transmission. The server should receive pickled messages, unpickle them, and broadcast them to all connected clients.

#Requirements:
#Implement separate threads for handling client connections and message broadcasting on the server side.
#Ensure proper synchronization to handle concurrent access to shared resources (e.g., the list of connected clients).
#Allow clients to join and leave the chat room dynamically while maintaining active connections with other clients.
#Use pickling to serialize and deserialize messages exchanged between clients and the server.

##########Server (server.py):
import socket
import threading
import pickle

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []  #this is an empty array to store the sockets of the clients
        self.lock = threading.Lock()  #to ensure thread saftey this is a lock

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Server listening on {self.host}:{self.port}")

        #this is a thread for handling the connections of clients
        threading.Thread(target=self.accept_clients).start()

        #this is a thread for broadcasting the client's messages
        threading.Thread(target=self.broadcast_messages).start()

    def accept_clients(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"New connection from {client_address}")

            with self.lock:
                self.clients.append(client_socket)

            #this is a thread for handling the connect client's messages
            threading.Thread(target=self.receive_messages, args=(client_socket,)).start()

    def receive_messages(self, client_socket):
        while True:
            try:
                #receiving the client's pickled message
                message_data = client_socket.recv(4096)
                if not message_data:
                    break

                message = pickle.loads(message_data)

                #brocasting this message to all clients
                with self.lock:
                    for other_client in self.clients:
                        if other_client != client_socket:
                            other_client.sendall(pickle.dumps(message))

            except Exception as e:
                print(f"Error receiving message: {e}")
                break

        #remove any diconnected clients
        with self.lock:
            self.clients.remove(client_socket)
            client_socket.close()

    def broadcast_messages(self):
        while True:
            message = input("Server: ")
            message_data = pickle.dumps({"username": "Server", "message": message})

            #broadcasting the server's message to all clients
            with self.lock:
                for client_socket in self.clients:
                    client_socket.sendall(message_data)

if __name__ == "__main__":
    server = ChatServer('127.0.0.1', 12345)
    server.start()



#################Client (client.py):
import socket
import threading
import pickle

class ChatClient:
    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server on {self.host}:{self.port}")

        #this is a thread to recieve and display the server's messages
        threading.Thread(target=self.receive_messages).start()

        #this is a thread for sending messages to server
        threading.Thread(target=self.send_messages).start()

    def receive_messages(self):
        while True:
            try:
                #receiving pickled message from the server
                message_data = self.client_socket.recv(4096)
                if not message_data:
                    break

                message = pickle.loads(message_data)
                print(f"{message['username']}: {message['message']}")

            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_messages(self):
        while True:
            message = input("")
            message_data = pickle.dumps({"username": self.username, "message": message})

            #zending the pickled message to the server
            self.client_socket.sendall(message_data)

if __name__ == "__main__":
    username = input("Enter your username: ")
    client = ChatClient('127.0.0.1', 12345, username)
    client.start()
