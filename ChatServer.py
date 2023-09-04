# Final implementation of chatserver with audio and video streaming as well as text messaging
import threading,socket

# socket.gethostbyname(socket.gethostname())
# The above line of code receives the ipv4 address of the client that this program is running on.
# I had to change it to 192.168.1.171 since the line of code above started returning the wrong ipv4 address
# This assumes that the server is being ran on my computer.
host = '192.168.1.171'
chatPort = 55555
videoPort = 55666
audioPort = 55777
buffer_size = 65536

clients = []

class User:
    def __init__(self, name: str, text_socket: socket.socket):
        self.username = name
        self.text_socket = text_socket
        self.audio_socket = socket.socket()
        self.address = ""
    
    def setAddress(self, addr: str):
        self.address = addr
    
    def setAudioSocket(self, audioSocket: socket.socket):
        self.audio_socket = audioSocket

    def getUsername(self)->str:
        return self.username
    
    def getAddress(self)->str:
        return self.address
    
    def getTextSocket(self)->socket.socket:
        return self.text_socket
    
    def getAudioSocket(self)->socket.socket:
        return self.audio_socket
    
    def endAudio(self):
        self.audio_socket.close()
    
    def endText(self):
        self.text_socket.close()

class Server:
    def __init__(self):
        # TCP socket for text message server
        self.text_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TCP Socket for audio streaming server
        self.audio_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # UDP socket for video streaming server
        self.video_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Start server
    def start(self):
        print(f"Listening for connections at {host}...")
        self.text_server.bind((host,chatPort))
        self.text_server.listen()

        self.audio_server.bind((host,audioPort))
        self.audio_server.listen()

        # Change buffer size for UDP socket so that the particular resolution of jpg packets can be sent
        self.video_server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        self.video_server.bind((host, videoPort))

        # Handle packets of data for receiving video stream within the UDP Server
        handleVideo_thread = threading.Thread(target=self.videoReceive)
        handleVideo_thread.start()

        # Handle packets of data for receiving audio stream
        handleAudio_thread = threading.Thread(target=self.receiveAudio)
        handleAudio_thread.start()

        # Handle packets of data for receiving text messages
        self.receive()
    
    # Shutdown server
    def shutdown(self):
        print("Shutting Down...")
        self.text_server.close()
        self.video_server.close()

    # Send a message to all clients
    def broadcast(self, message: bytes):
        for client in clients:
            client.getTextSocket().send(message)
    
    # Send a message to all but a specified client
    # Called whenever a user sends a message to prevent receiving a repeated message
    def sendMessage(self, message: bytes, user: str):
        for client in clients:
            if client.getTextSocket() != user:
                client.getTextSocket().send(message)
    
    # Find a particular client from their username
    def findClient(self, username: str):
        for client in clients:
            if username == client.getUsername():
                return client
        return User("", socket.socket())

    # Send video to all clients but the sender
    def sendVideo(self, addr: str, packet: bytes):
        # No need to send video if there is only one client in the server
        if len(clients) >= 2:
            for client in clients:
                if client.getAddress() != addr:
                    self.video_server.sendto(packet, client.getAddress())
    
    # Function for handling a new user
    def handle(self, user: socket.socket):
        # Attempt to assign a username to a new user
        try:
            user.send('NAME'.encode('ascii'))
            username = user.recv(1024).decode('ascii')
            newUser = User(username, user)
            clients.append(newUser)
            print(f"Username of the client is {username}!")
            self.broadcast(f'{username} joined the chat!'.encode('ascii'))
            user.send("Connected to the server!".encode('ascii'))
        # If a nickname was not received by the server, they disconnected before entering a username
        except:
            print("User disconnected before entering a username")
            user.close()
            return

        # Create thread to handle video; see comments on top of function self.videoReceive
        handleVideo_thread = threading.Thread(target=self.videoReceive)
        handleVideo_thread.start()

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
                newUser.endText()
                self.broadcast(f'{newUser.getUsername()} left the chat!'.encode('ascii'))
                print(f'{newUser.getUsername()} left the chat!')
                break
    
    # Function for accepting new clients into the TCP text server
    def receive(self):
        while True:
            try:
                user, address = self.text_server.accept()
                print(f"Connected to text chat server with {str(address)}")
                handleUser_thread = threading.Thread(target=self.handle, args=(user,))
                handleUser_thread.start()
            except KeyboardInterrupt:
                print("Shutting down...")
                self.shutdown()

    # Function that handles receiving data within the UDP server for video streaming
    # Called through the creation of a thread. An initial thread is created while starting the server.
    # These videoReceive threads are generic and ensures that at least one is running at all times.
    # It must be able to handle all of the specific conditions such as updating a user on the server's side with their specific return address.
    # The socket function recvfrom simply receives data without much regard for who the sender is.
    # What I mean by this is that this function returns two parameters: data and sender's return address, but the server has no way of
    # ensuring that a particular client is sending data to the server. This means that in a server of 2 clients for instance, the packets of data
    # can be received in any of the three threads of videoReceive running in the background of the server.
    def videoReceive(self):
        while True:
            packet,addr = self.video_server.recvfrom(buffer_size)
            # Check whether the packet is a string (decodable in ascii?)
            try:
                msg = packet.decode('ascii')
                # Update address of client for streaming video (this return address is used to send video data)
                if msg[0:6] == "FIRST:":
                    client = self.findClient(msg[6:])
                    if client.getUsername():
                        client.setAddress(addr)
                # End thread for receiving video when user disconnects
                elif msg == "BYE":
                    break
            # If packet cannot be decoded with ascii it is encoded as jpg and can be sent to other clients
            except:
                self.sendVideo(addr, packet)
    
    # Send audio packets to all clients except sender
    def sendAudio(self, audio: bytes, user: socket.socket):
        for client in clients:
            if client.getAudioSocket() != user:
                try:
                    client.getAudioSocket().send(audio)
                except:
                    print("Error has occurred")
    
    # Handles audio from client
    def handleAudio(self, user: socket.socket, address: str):
        try:
            user.send("Hello".encode('ascii'))
            msg = user.recv(1024).decode('ascii')
            if msg[0:7] == "Joined:":
                print("Updated audio socket")
                client = self.findClient(msg[7:])
                client.setAudioSocket(user)
        except:
            print("Connection error")
            user.close()
            return

        while True:
            try:
                audio = user.recv(1024*8)
                self.sendAudio(audio, user)
            except:
                # remove the client that sends a failed message
                user.close()
                # print(f"{address} disconnected from audio server.")
                break

    # Handle users joining server
    def receiveAudio(self):
        while True:
            user, address = self.audio_server.accept()
            print(f"Connected to audio server with {str(address)}")
            handleAudio_thread = threading.Thread(target=self.handleAudio, args=(user, address,))
            handleAudio_thread.start()
        
if __name__ == '__main__':
    server = Server()
    server.start()