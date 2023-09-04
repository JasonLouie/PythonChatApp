# Filename: basicchatserver.py
# Description: File for the terminal text chat server

import socket, threading

host = socket.gethostbyname(socket.gethostname())
port = 55555

class User:
    def __init__(self, name: str, text_socket: socket.socket):
        self.username = name
        self.text_socket = text_socket

    def getUsername(self)->str:
        return self.username
    
    def sendText(self, data: bytes):
        self.text_socket.send(data)
    
    def endConnection(self):
        self.text_socket.close()

class Server:
    def __init__(self):
        self.text_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.clients = []

    def run(self):
        print(f"Listening for connections at {host}...")
        self.text_server.bind((host,port))
        self.text_server.listen()
        receiveThread = threading.Thread(target=self.receive, daemon=True)
        receiveThread.start()

        self.checkForExit()
    
    # Shutdown server
    def shutdown(self):
        print("Shutting Down...")
        self.broadcast("#CLOSING#".encode('ascii'))
        self.text_server.close()

    # Wait for user input on the server-side and use this as a way to shutdown the server
    # This works because the only line of code running on the main thread is the input command and after
    # there is input, the server will shutdown. Since all the other threads are daemon threads, they will
    # also terminate as soon as the main thread ends.
    def checkForExit(self):
        input("Press enter to shutdown server\n")
        self.shutdown()

    def broadcast(self, message: bytes, sender=""):
        for client in self.clients:
            if client.getUsername() != sender:
                client.sendText(message)

    def handle(self, user: socket.socket):
            # Attempt to assign a username to a new user
            try:
                user.send("NAME".encode('ascii'))
                username = user.recv(1024).decode('ascii')
                newUser = User(username, user)
                self.clients.append(newUser)
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
                    self.broadcast(message, username)
                # Remove the client that sends a failed message
                # This is when the client terminates its socket, thus terminating its connection to the server
                except:
                    self.clients.remove(newUser)
                    newUser.endConnection()
                    self.broadcast(f'{newUser.getUsername()} left the chat!'.encode('ascii'))
                    print(f'{newUser.getUsername()} left the chat!')
                    break

    # Function for accepting new clients into the TCP text server
    def receive(self):
        while True:
            try:
                user, address = self.text_server.accept()
                print(f"Connected with {str(address)}")
                handleUserChat_thread = threading.Thread(target=self.handle, args=(user,))
                handleUserChat_thread.daemon = True
                handleUserChat_thread.start()
            except:
                break


if __name__ == '__main__':
    server = Server()
    server.run()
