# Filename: basicchatclient.py
# Description: File for terminal text chat (for users)
# NOTE: This is an unoptimized implementation so some features may not work as desired.

import socket, threading
from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"

host_ip = socket.gethostbyname(socket.gethostname())
port = 55555

username = ""
while not username:
    username = input("Enter a username: ")

user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
user.connect((host_ip, port))

def receive():
    while True:
        try:
            message = user.recv(1024).decode('ascii')
            if message == "NAME":
                user.send(username.encode('ascii'))
            elif message:
                print(message)
        except:
            print("An error occurred!")
            user.close()
            break

def write():
    while True:
        try:
            # Wait for a new message 
            message = input("")
            if message:
                try:
                    user.send(f"{username}: {message}".encode('ascii'))
                    print(f"You: {message}")
                except:
                    break
        except:
            break

if __name__ == '__main__':
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()