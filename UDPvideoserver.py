import socket, threading, errno
from tkinter import *

# socket.gethostbyname(socket.gethostname())
# The above line of code receives the ipv4 address of the client that this program is running on.
# I had to change it to 192.168.1.171 since the line of code above started returning the wrong ipv4 address
# This assumes that the server is being ran on my computer.
host_ip = '192.168.1.171' # socket.gethostbyname(socket.gethostname())
buffer_size = 65536
videoPort = 55666

class User:
    def __init__(self, address: str):
        self.address = address
    
    def getAddress(self):
        return self.address
    

clients = []

class VideoServer:
    def __init__(self):
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def start(self):
        self.video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        self.video_socket.bind((host_ip, videoPort))
        self.receive()
    
    def shutdown(self):
        self.video_socket.close()
    
    def findClient(self, address: str)->User:
        for client in clients:
            if client.getAddress() == address:
                return client
        return User("")

    # Forwarding received data to the other clients
    def sendVideo(self, packet: bytes, sent_addr: str):
        if len(clients) >= 2:
            for client in clients:
                if client.getAddress() != sent_addr:
                    try:
                        self.video_socket.sendto(packet, client.getAddress())
                    except socket.error as err:
                        print(f"Removed client because {err}")
                        clients.remove(client)
    
    # Receive data from clients
    def receive(self):
        print(f"Listening for a connection...")
        while True:
            try:
                msg, address = self.video_socket.recvfrom(buffer_size)
                # Cannot decode the jpg frames of video from client
                try:
                    if msg.decode('ascii') == "First Time":
                        print(f"Connected to UDP video with {address}")
                        clients.append(User(address))
                    elif msg.decode('ascii') == "END":
                        # LET CLIENT KNOW TO CLOSE VIDEO WINDOW
                        self.sendVideo("STOP".encode('ascii'), address)
                    elif msg.decode('ascii') == "BYE":
                        # REMOVE CLIENT FROM LIST
                        client = self.findClient(address)
                        if client.getAddress():
                            clients.remove(client)
                            print(f"Removed client at {address}")
                except:
                    self.sendVideo(msg, address)
                    
            except OSError as err:
                print(err)

if __name__ == '__main__':
    video_server = VideoServer()
    video_server.start()
