import socket, threading

host_ip = '192.168.1.171'
port = 55555

text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

usernames = []
clients = []

def run():
    print(f"Listening for connections at {host_ip}...")
    text_server.bind((host_ip,port))
    text_server.listen()
    receive()
    
# Send a message to all clients
def broadcast(message: bytes):
    for client in clients:
        client.send(message)
    
# Send a message to all but a specified client
# Called whenever a user sends a message to prevent receiving a repeated message
def sendMessage(message, user: socket):
    for client in clients:
        if client != user:
            client.send(message)

def handle(user: socket.socket, username: str):
    # Manage sending and receiving messages from a specific user
    while True:
        # Receive message and send it to all users while ensuring the user does not receive the repeated message
        try:
            message = user.recv(1024)
            sendMessage(message, user)
        # Remove the client that sends a failed message
        # This is when the client terminates its socket, thus terminating its connection to the server
        except:
            clients.remove(user)
            usernames.remove(username)
            user.close()
            broadcast(f"{username} left the chat!".encode('ascii'))
            print(f"{username} left the chat!")
            break

# Function for accepting new clients into the TCP text server
def receive():
    while True:
        user, address = text_server.accept()
        print(f"Connected with {str(address)}")
        # Attempt to assign a username to a new user
        try:
            user.send("NAME".encode('ascii'))
            username = user.recv(1024).decode('ascii')
            usernames.append(username)
            clients.append(user)
            print(f"Username of the client is {username}!")
            sendMessage(f"{username} joined the chat!".encode('ascii'), username)
            user.send("Connected to the server!".encode('ascii'))
            handleUserChat_thread = threading.Thread(target=handle, args=(user, username,))
            handleUserChat_thread.start()
        # If a nickname was not received by the server, they disconnected before entering a username
        except Exception as e:
            print(e)
            print("User disconnected before entering a username")
            user.close()

if __name__ == '__main__':
    run()
