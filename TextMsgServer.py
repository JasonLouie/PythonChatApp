import threading, socket

# socket.gethostbyname(socket.gethostname())
# The above line of code receives the ipv4 address of the client that this program is running on.
# I had to change it to 192.168.1.171 since the line of code above started returning the wrong ipv4 address
# This assumes that the server is being ran on my computer.
host = '192.168.1.171'
chatPort = 55555

clients = []

class User:
    def __init__(self, name: str, text_socket: socket.socket):
        self.username = name
        self.text_socket = text_socket

    def getUsername(self)->str:
        return self.username
    
    def getTextSocket(self)->socket.socket:
        return self.text_socket
    
    def endConnection(self):
        self.text_socket.close()

class Server:
    def __init__(self):
        # TCP socket for text message server
        self.text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Start server
    def start(self):
        print(f"Listening for connections at {host}...")
        self.text_server.bind((host,chatPort))
        self.text_server.listen()
        self.receive()
    
    # Shutdown server
    def shutdown(self):
        self.broadcast("#CLOSING#".encode('ascii'))
        self.text_server.close()

    # Send a message to all clients
    def broadcast(self, message: bytes):
        for client in clients:
            client.getTextSocket().send(message)
    
    # Send a message to all but a specified client
    # Called whenever a user sends a message to prevent receiving a repeated message
    def sendMessage(self, message: bytes, user: socket.socket):
        for client in clients:
            if client.getTextSocket() != user:
                client.getTextSocket().send(message)

    # Function for handling a new user
    def handle(self, user: socket.socket):
        # Attempt to assign a username to a new user
        try:
            user.send("NAME".encode('ascii'))
            username = user.recv(1024).decode('ascii')
            newUser = User(username, user)
            clients.append(newUser)
            print(f"Username of the client is {username}!")
            self.broadcast(f"{username} joined the chat!".encode('ascii'))
            user.send("Connected to the server!".encode('ascii'))
        # If a nickname was not received by the server, they disconnected before entering a username
        except:
            print("User disconnected before entering a username")
            user.close()
            return

        # Manage sending and receiving messages from a specific user
        while True:
            # Receive message and send it to all users while ensuring the user does not receive the repeated message
            try:
                message = user.recv(1024)
                self.sendMessage(message, user)
            # Remove the client that sends a failed message
            # This is when the client terminates its socket, thus terminating its connection to the server
            except:
                clients.remove(newUser)
                newUser.endConnection()
                self.broadcast(f"{newUser.getUsername()} left the chat!".encode('ascii'))
                print(f"{newUser.getUsername()} left the chat!")
                break

    # Function for accepting new clients into the TCP text server
    def receive(self):
        while True:
            try:
                user, address = self.text_server.accept()
                print(f"Connected with {str(address)}")
                handleUser_thread = threading.Thread(target=self.handle, args=(user,))
                handleUser_thread.start()
            except KeyboardInterrupt:
                print("Shutting down...")
                self.shutdown()
                break
        
if __name__ == '__main__':
    server = Server()
    server.start()