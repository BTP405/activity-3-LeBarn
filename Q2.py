#Distributed Task Queue with Pickling:

#Create a distributed task queue system where tasks are sent from a client to multiple worker nodes for processing using sockets. 
#Tasks can be any Python function that can be pickled. Implement both the client and worker nodes. 
#The client sends tasks (pickled Python functions and their arguments) to available worker nodes, and each worker node executes the task and returns the result to the client.

#Requirements:
#Implement a protocol for serializing and deserializing tasks using pickling.
#Handle task distribution, execution, and result retrieval in both the client and worker nodes.
#Ensure fault tolerance and scalability by handling connection errors, timeouts, and dynamic addition/removal of worker nodes.

#########Worker Node that acts like a server (worker.py):
import socket
import pickle
import traceback

#this function executes a recieved task that was from the client
def execute_task(task):
    try:
        #unpack the task and execute
        function, args = pickle.loads(task)
        result = function(*args)
        return result
    except Exception as e:
        #return an error message in case of exceptions 
        return f"Error executing task: {e}\n{traceback.format_exc()}"

#starting function to run worker node
def start_worker(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Worker node listening on {host}:{port}")

        while True:
            try:
                connection, client_address = server_socket.accept()
                print(f"Connection from {client_address}")

                #receive clients task
                task = connection.recv(4096)
                result = execute_task(task)

                #send result back to client
                connection.sendall(pickle.dumps(result))
                connection.close()

            except Exception as e:
                #return an error message in case of exceptions or failures during execution
                print(f"Error handling task: {e}")

if __name__ == "__main__":
    #set the worker node's host and port
    worker_host = '127.0.0.1'
    worker_port = 12346

    #run worker node
    start_worker(worker_host, worker_port)


###########Client (client.py):
import socket
import pickle
import time

#the sender function for the worker node to do a task 
def send_task(task, worker_node):
    for worker_node in worker_nodes:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                #set a timeout for connection attempts in case there are failuers to connect
                client_socket.settimeout(5)
                client_socket.connect(worker_node)

                #send the task to the worker node
                client_socket.sendall(task)

                #receive the result from the worker node
                result = client_socket.recv(4096)
                return pickle.loads(result)

        except (socket.timeout, ConnectionError) as e:
             #return an error message in case of exceptions or failures during execution
            print(f"Error connecting to worker node {worker_node}: {e}")
            continue
        except Exception as e:
             #return an error message in case of exceptions or failures during execution
            print(f"Error processing task: {e}")
            return None

#distributor function to give out tasks to multiple worker nodes
def distribute_tasks(tasks, worker_nodes):
    results = []
    for task in tasks:
        #send each task to a worker node and get the result
        result = send_task(pickle.dumps(task), worker_nodes)
        if result is not None:
            results.append(result)

    return results

if __name__ == "__main__":
    #listing all worker nodes with their actual addresses
    worker_nodes = [('127.0.0.1', 12346), ('127.0.0.1', 12347)]

    #define tasks as functions with arguments
    def add(a, b):
        return a + b

    def multiply(x, y):
        return x * y

    tasks = [(add, (1, 2)), (multiply, (3, 4))]

    #distribute tasks to worker nodes and get results
    results = distribute_tasks(tasks, worker_nodes)

    print("Results:", results)