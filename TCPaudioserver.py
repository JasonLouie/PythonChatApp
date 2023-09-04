# Filename: TCPaudioserver.py
# Description: File for voice chat server

import pyaudio, socket, threading, time
from tkinter import *

host = socket.gethostbyname(socket.gethostname())
chunk = 1024
# 16 bits per sample
audio_format = pyaudio.paInt16
channels = 1
# Record at 44100 samples per second
fs = 44100
# Number of seconds to record
seconds = 0.25
audioPort = 55777

class User:
    def __init__(self, audioSocket: socket.socket):
        self.audioSocket = audioSocket
    
    def __eq__(self, other)->bool:
        return self.audioSocket == other.audioSocket
    
    def __ne__(self, other)->bool:
        return self.audioSocket != other.audioSocket
    
    def sendAudio(self, data: bytes):
        self.audioSocket.send(data)
    
    def endAudio(self):
        self.audioSocket.close()

class AudioServer:
    def __init__(self):
        # TCP Socket for audio streaming server
        self.audio_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.runThread = True
        self.clients = []
    
    # Start TCP audio server
    def start(self):
        print(f"Listening for connections at {host}...")
        self.audio_server.bind((host,audioPort))
        self.audio_server.listen()
        audioReceive = threading.Thread(target=self.receiveAudio)
        audioReceive.daemon = True
        audioReceive.start()

        self.checkForExit()
    
    # Function for handling user ping
    def writeRecvPing(self, ping: float)->str:
        now = time.time()
        return f"Ping: {((now-ping)*1000):.2f}"
    
    # Wait for user input on the server-side and use this as a way to shutdown the server
    # This works because the only line of code running on the main thread is the input command and after
    # there is input, the server will shutdown.
    def checkForExit(self):
        while True:
            try:
                input("Enter Ctrl + C to shutdown server\n")
            except KeyboardInterrupt:
                self.runThread = False
                self.shutdown()
                break
    
    # Helper function for the shutdown function which kicks all clients out of the server.
    def removeAllClients(self):
        for client in self.clients:
            client.sendAudio("#CLOSING#".encode('ascii'))
            client.endAudio()
            self.clients.remove(client)

    # Shutdown server
    def shutdown(self):
        print("Shutting Down...")
        self.removeAllClients()
        self.audio_server.close()

    # Send audio packets to all clients except sender
    def sendAudio(self, audio, sender: User):
        for client in self.clients:
            if client != sender:
                # Note: the .sendAudio for client is the method from the Users class.
                try:
                    client.sendAudio(audio)
                except:
                    print("Error has occurred")
    
    # Handles audio from client
    def handleAudio(self, socket: socket.socket, address: str):
        newUser = User(socket)
        self.clients.append(newUser)
        while self.runThread:
            try:
                audio = socket.recv(1024*8)
                try:
                    msg = audio.decode('ascii')
                    if msg[0:6] == "#PING:":
                        ping = self.writeRecvPing(float(msg[6:]))
                        socket.send(f"A-{ping}".encode('ascii'))
                except:
                    self.sendAudio(audio, newUser)
            except:
                # remove the client that sends a failed message
                self.clients.remove(newUser)
                newUser.endAudio()
                print(f"{address} disconnected.")
                break

    # Handle users joining server
    def receiveAudio(self):
        while True:
            socket, address = self.audio_server.accept()
            print(f"Connected with {str(address)}")
            handleAudio_thread = threading.Thread(target=self.handleAudio, args=(socket, address,), daemon=True)
            handleAudio_thread.start()

if __name__ == '__main__':
    audio = AudioServer()
    audio.start()
