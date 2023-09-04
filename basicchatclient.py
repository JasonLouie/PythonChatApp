# Filename: basicchatclient.py
# Description: File for terminal text chat (for users)

import socket, threading

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
            else:
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
    receive_thread = threading.Thread(target=receive, daemon=True)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()