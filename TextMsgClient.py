# Filename: TextMsgClient.py
# Description: File for text chat client
# NOTE: This is an unoptimized implementation so some features may not work as desired.

import socket, threading
from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"
host_ip = socket.gethostbyname(socket.gethostname())
chatPort = 55555

class ChatClient:
    def __init__(self):
        # Chat socket (TCP)
        self.user_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.runThread = True
        self.clientWindow = Tk()
        self.setupWindow()
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)
        self.username = ""
        self.msg_to_send = ""
    
    def setupWindow(self):
        self.clientWindow.title("Chat Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=470, height=550, bg=bg_color)

        # Header with user info
        self.head_label = Label(self.clientWindow, bg=bg_color, fg=text_color, text="Username:", pady=10)
        self.head_label.place(relwidth=1)

        # Chat window
        self.chat_window = Text(self.clientWindow, width=20, height=2, bg=bg_color, fg=text_color, padx=4,pady=4)
        self.chat_window.place(relheight=0.675, relwidth=1, rely=0.1)
        self.chat_window.configure(state=DISABLED)

        # Scrollbar
        scrollbar = Scrollbar(self.chat_window)
        scrollbar.place(relheight=1, relx=0.967)
        scrollbar.configure(command=self.chat_window.yview)

        # Bottom label
        bottom_label = Label(self.clientWindow, bg=bg_bottom, height=80)
        bottom_label.place(relwidth=1, rely=0.8)
        
        # User input area
        self.user_input = Entry(bottom_label, bg=bg_entry, fg=text_color)
        self.user_input.place(relwidth=0.75, relheight=0.05, rely=0.01, relx=0.01)
        self.user_input.bind("<Return>", self.pressedEnter)
        self.user_input.configure(state=DISABLED)

        # Button for sending
        send_button = Button(bottom_label, text="Send", width=20, bg=bg_bottom, command=lambda: self.pressedEnter(None))
        send_button.place(relx=0.7, rely=0.01, relheight=0.05, relwidth=0.2)
    
    def connect(self):
        self.user_chat.connect((host_ip, chatPort))

    def run(self):
        try:
            self.connect()
        except:
            print("Servers are down. Try again later.")
            self.quit()

        # Thread to receive messages from the TCP text server
        # Updates the chat in the tkinter window with new messages from other clients and/or the server
        self.receiveMSG = threading.Thread(target=self.receiveChat, daemon = True)
        self.receiveMSG.start()

        # Thread to send messages to the TCP text server
        # Constantly check if self.msg_to_send is empty and send it to the server if it is not empty
        self.writeMSG = threading.Thread(target=self.write, daemon = True)
        self.writeMSG.start()

        self.clientWindow.mainloop()
    
    # Function that handles pressing send or the enter key
    def pressedEnter(self, event):
        msg = self.user_input.get()
        # Update chat with new msg and send it to the server
        self.updateChat(msg, "You")

    # Function that handles sending messages and displaying them in the chat window
    def updateChat(self, msg: str, sender: str):
        # Do nothing if user tried to send an empty message
        if not msg:
            return
        
        # Clear user input
        self.user_input.delete(0, END)

        # If chat client does not have a username, assign one
        # Skipped after there is a username
        if not self.username and sender == "You":
            self.username = msg
            self.msg_to_send = msg
            self.updateChat(f"Your username is: {self.username}", "")
            self.head_label.configure(text=f"Username: {self.username}")
            return

        # Format message
        if sender == "You":
            # Update self.msg_to_send to initiate sending the msg to the server
            self.msg_to_send = f"{self.username}: {msg}"
            msg = f"{sender}: {msg}"

        # Must allow chat window to be configured temporarily when a new message is added
        self.chat_window.configure(state=NORMAL)
        # Append message to the chat window
        self.chat_window.insert(END, f"{msg}\n")
        # Disable the chat window again so that the user cannot edit the displayed chat messages
        self.chat_window.configure(state=DISABLED)

        # Scroll to the bottom of the chat window everytime a new message is sent
        self.chat_window.see(END)

    # Function for receiving text messages from the TCP chat server
    def receiveChat(self):
        while self.runThread:
            try:
                message = self.user_chat.recv(1024).decode('ascii')
                # Prompt user to enter a username
                if message == "NAME":
                    self.user_input.configure(state=NORMAL)
                    self.updateChat("Enter a username", "")
                elif message == "#CLOSING#":
                    self.quit()
                # Call self.updateChat to update the chat
                else:
                    self.updateChat(message, "")
            except:
                break
    
    # Send a message if self.msg_to_send isn't empty
    # The reasoning is that the mentioned variable only changes whenever the user sends a message
    def write(self):
        while self.runThread:
            if self.msg_to_send != "":
                self.user_chat.send(self.msg_to_send.encode('ascii'))
                self.msg_to_send = ""
    
    # Handles closing client (closes all threads and sockets)
    def quit(self):
        self.user_chat.close()
        self.runThread = False
        self.clientWindow.destroy()

if __name__ == '__main__':
    chat_client = ChatClient()
    chat_client.run()
    