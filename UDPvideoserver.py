# Filename: UDPvideoserver.py
# Description: File for UDP video chat server

import socket, time, threading
from tkinter import *

buffer_size = 65536
host_ip = socket.gethostbyname(socket.gethostname())
videoPort = 55666

class User:
    def __init__(self, address: str):
        self.address = address
    
    def getAddress(self)->str:
        return self.address

class VideoServer:
    def __init__(self):
        self.video_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.runThread = True
        self.clients = []
    
    def start(self):
        self.video_server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        self.video_server.bind((host_ip, videoPort))
        print(f"Listening for UDP Video connections at {host_ip}")
        threading.Thread(target=self.receiveVideo,daemon=True).start()
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
    
    # Handle shutting server down
    def shutdown(self):
        print("Shutting down...")
        self.broadcastVideo("#CLOSING#".encode('ascii'), "", 1)
        self.video_server.close()
    
    # Find a specific client
    def findClient(self, address: str)->User:
        for client in self.clients:
            if client.getAddress() == address:
                return client
        return User("")

    # Receive video from clients and forward it to others
    def receiveVideo(self):
        while self.runThread:
            try:
                packet, address = self.video_server.recvfrom(buffer_size)
                try:
                    msg = packet.decode('ascii')
                    if msg == "First Time":
                        print(f"Connected with {address}")
                        self.clients.append(User(address))
                    elif msg[0:6] == "#PING:":
                        ping = self.writeRecvPing(float(msg[6:]))
                        self.video_server.sendto(f"V-{ping}".encode('ascii'), address)
                    elif msg == "END":
                        # LET CLIENT KNOW TO CLOSE VIDEO WINDOW
                        # Set third param to 1 so stop keyword is sent to an individual client if it is the only one left
                        self.broadcastVideo("#STOP#".encode('ascii'), address, 1)
                    elif msg == "START":
                        # LET CLIENT KNOW TO OPEN VIDEO WINDOW
                        self.broadcastVideo("#START#".encode('ascii'), address)
                    elif msg == "BYE":
                        # REMOVE CLIENT FROM LIST
                        client = self.findClient(address)
                        if client.getAddress():
                            self.clients.remove(client)
                        print(f"Removed client at {address}")
                except:
                    self.broadcastVideo(packet, address)
            except:
                break

    # Send video to all clients but the sender
    # Additional 3rd parameter to prevent sending video when there is only one client in the server.
    def broadcastVideo(self, packet: bytes, sent_addr: str, numClients=2):
        if len(self.clients) >= numClients:
            for client in self.clients:
                if client.getAddress() != sent_addr:
                    try:
                        self.video_server.sendto(packet, client.getAddress())
                    except socket.error as err:
                        print(f"Removed client because {err}")
                        self.clients.remove(client)

if __name__ == '__main__':
    video_server = VideoServer()
    video_server.start()
