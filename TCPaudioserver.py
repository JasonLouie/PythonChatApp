import socket, threading
from tkinter import *

# socket.gethostbyname(socket.gethostname())
# The above line of code receives the ipv4 address of the client that this program is running on.
# I had to change it to 192.168.1.171 since the line of code above started returning the wrong ipv4 address
# This assumes that the server is being ran on my computer.
host = '192.168.1.171'
audioPort = 55777

clients = []

class User:
    def __init__(self, audioSock: socket.socket):
        self.audioSocket = audioSock
    
    def getAudioSocket(self)->socket.socket:
        return self.audioSocket
    
    def endAudio(self):
        self.audioSocket.close()

class AudioServer:
    def __init__(self):
        # TCP Socket for audio streaming server
        self.audio_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    # Start TCP audio server
    def start(self):
        print(f"Listening for connections at {host}...")
        self.audio_server.bind((host,audioPort))
        self.audio_server.listen()
        self.receiveAudio()
    
    # Send audio packets to all clients except sender
    def sendAudio(self, audio: bytes, user: socket.socket):
        for client in clients:
            if client.getAudioSocket() != user:
                try:
                    client.getAudioSocket().send(audio)
                except:
                    clients.remove(client)
                    client.endAudio()
                    print("Error has occurred")
    
    # Handles audio from client
    def handleAudio(self, user: socket.socket, address: str):
        try:
            user.send("Hello".encode('ascii'))
            if user.recv(1024).decode('ascii') == "Joining":
                newUser = User(user)
                clients.append(newUser)
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
                clients.remove(newUser)
                newUser.endAudio()
                print(f"{address} disconnected.")
                break

    # Handle users joining server
    def receiveAudio(self):
        while True:
            user, address = self.audio_server.accept()
            print(f"Connected with {str(address)}")
            handleAudio_thread = threading.Thread(target=self.handleAudio, args=(user, address,))
            handleAudio_thread.start()

if __name__ == '__main__':
    audio = AudioServer()
    audio.start()
