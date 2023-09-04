import threading, socket, time
import cProfile, re

# socket.gethostbyname(socket.gethostname())
# The above line of code receives the ipv4 address of the client that this program is running on.
# I had to change it to 192.168.1.171 since the line of code above started returning the wrong ipv4 address
# This assumes that the server is being ran on my computer. Change it back to the commented line when using
# or replace it with your own ipv4 address.
host = '192.168.1.171'  # socket.gethostbyname(socket.gethostname())
chatPort = 55555

class User:
    def __init__(self, name: str, text_socket: socket.socket):
        self.username = name
        self.text_socket = text_socket
    
    def setUsername(self, username: str):
        self.username = username

    def getUsername(self)->str:
        return self.username
    
    def sendText(self, data: bytes):
        self.text_socket.send(data)
    
    def endConnection(self):
        self.text_socket.close()

class Server:
    def __init__(self):
        # TCP socket for text message server
        self.text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.runThread = True
        # List of clients in the server
        self.clients = []
    
    # Start server
    def start(self):
        print(f"Listening for connections at {host}...")
        self.text_server.bind((host,chatPort))
        self.text_server.listen()

        # Create a thread for accepting users into the text chat server
        handleChatJoin_thread = threading.Thread(target=self.receive, daemon=True)
        handleChatJoin_thread.start()

        # Run input on the main thread. Typing anything but ^C will shut the server properly.
        self.checkForExit()
    
    
    # Wait for user input on the server-side and use this as a way to shutdown the server
    # This works because the only line of code running on the main thread is the input command and after
    # there is input, the server will shutdown. Since all the other threads are daemon threads, they will
    # also terminate as soon as the main thread ends.
    def checkForExit(self):
        while True:
            try:
                input("Enter Ctrl + C to shutdown server\n")
            except KeyboardInterrupt:
                self.runThread = False
                self.shutdown()
                break
    
    # Function for handling user ping
    def writeRecvPing(self, ping: float)->str:
        now = time.time()
        return f"Ping: {((now-ping)*1000):.2f}"
    
    # Shutdown server
    def shutdown(self):
        print("Shutting Down...")
        self.broadcast("#CLOSING#".encode('ascii'), allClients=True)
        self.text_server.close()

    # Functionalities:
    # Send a message to all but sender
    # Send messages to all valid clients
    # Send messages to ALL clients (even the clients in the middle of entering username)
    def broadcast(self, message: bytes, sender = "", allClients = False):
        for client in self.clients:
            if (client.getUsername() != sender and client.getUsername()) or allClients:
                try:
                    client.sendText(message)
                except:
                    client.endConnection()
                    self.clients.remove(client)
    
    # Check for repeated usernames
    # Returns false if the username is not taken and true if it is taken
    def takenUsername(self, username: str)->bool:
        # Check all clients and if name is not taken then return false
        for client in self.clients:
            if client.getUsername() == username:
                return True
        return False
    
    # Function used for obtaining valid username from user
    def getValidUsername(self, user: socket.socket)->str:
        username = user.recv(1024).decode('ascii')
        while self.takenUsername(username):
            user.send("#TAKEN#".encode('ascii'))
            username = user.recv(1024).decode('ascii')
        user.send("Connected to the server!".encode('ascii'))
        return username

    # Function for handling a new user
    def handle(self, user: User, userSocket: socket.socket):
        # Attempt to assign a username to a new user
        try:
            user.sendText("#NAME#".encode('ascii'))
            username = self.getValidUsername(userSocket)
            user.setUsername(username)
            print(f"Username of the client is {username}!")
            self.broadcast(f"{username} joined the chat!".encode('ascii'), sender=username)
        # If a nickname was not received by the server, they disconnected before entering a username
        except:
            print("User disconnected before entering a username")
            self.clients.remove(user)
            user.endConnection()
            return

        # Manage sending and receiving messages from a specific user
        while self.runThread:
            # Receive message and send it to all users but the sender
            try:
                message = userSocket.recv(1024)
                if message[0:6].decode('ascii') == "#PING:":
                    ping = self.writeRecvPing(float(message[6:]))
                    user.sendText(ping.encode('ascii'))
                else:
                    self.broadcast(message, sender=username)
            # Remove the client that sends a failed message
            # This is when the client terminates its socket, thus terminating its connection to the server
            except:
                self.clients.remove(user)
                user.endConnection()
                self.broadcast(f"{username} left the chat!".encode('ascii'))
                print(f"{username} left the chat!")
                break

    # Function for accepting new clients into the TCP text server
    def receive(self):
        while self.runThread:
            try:
                socket, address = self.text_server.accept()
                print(f"Connected with {str(address)}")
                newUser = User("", socket)
                self.clients.append(newUser)
                handleUserChat_thread = threading.Thread(target=self.handle, args=(newUser,socket,), daemon=True)
                handleUserChat_thread.start()
            except:
                break
        
if __name__ == '__main__':
    server = Server()
    server.start()