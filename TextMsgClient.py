import socket, threading, time
from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"
ping_color = "#6BFF64"
# I used my public ip for the host_ip. If the following is being ran on another computer,
# and the server is not being ran on my computer please use socket.gethostbyname(socket.gethostname())
# for both server and client. If the following command does not work, replace this with your device's
# ipv4 address.
host_ip = '96.250.48.132' # socket.gethostbyname(socket.gethostname())
# '96.250.48.132'
# '192.168.1.171'
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
        self.ping = ""
    
    def setupWindow(self):
        self.clientWindow.title("Chat Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=470, height=550, bg=bg_color)

        # Label with ping
        self.text_ping = Label(self.clientWindow, bg=bg_color, fg=ping_color, text="Ping:", pady=10, justify=LEFT, anchor='w')
        self.text_ping.place(relwidth=0.4, relx=0.01)

        # Label for username
        self.username_label = Label(self.clientWindow, bg=bg_color, fg=text_color, text="Username:", pady=10, justify=LEFT, anchor='w')
        self.username_label.place(relwidth=0.3, relx=0.41)

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

    def run(self):
        try:
            self.user_chat.connect((host_ip, chatPort))
            # Thread to receive messages from the TCP text server
            # Updates the chat in the tkinter window with new messages from other clients and/or the server
            self.receiveMSG = threading.Thread(target=self.receiveChat, daemon=True)
            self.receiveMSG.start()
            self.clientWindow.mainloop()
        except:
            print("Text chat server is down. Try again later.")
    
    # Update ping for TCP text chat server
    def writeSendPing(self):
        if self.runThread:
            threading.Timer(1.0, self.writeSendPing).start()
            now = time.time()
            self.user_chat.send(f"#PING:{now}".encode('ascii'))
            
    # Function that handles pressing send or the enter key
    def pressedEnter(self, event):
        msg = self.user_input.get()
        # Update chat with new msg and send it to the server
        self.updateChat(msg, "You")

    # Function that handles sending messages and displaying them in the chat window
    # Also displays messages that were received
    def updateChat(self, msg: str, sender=""):
        try:
            # Do nothing if user tried to send an empty message
            if not msg:
                return
        
            # Handle user sending messages
            if sender == "You":
                # Clear user input
                self.user_input.delete(0, END)
                # If chat client does not have a username, assign one
                if not self.username:
                    self.username = msg
                    # Send username to server
                    self.user_chat.send(msg.encode('ascii'))
                    return

                # Send message to server in the format of "client's name: message"
                self.user_chat.send(f"{self.username}: {msg}".encode('ascii'))
                # Format message to display "You: message"
                msg = f"{sender}: {msg}"

            # Must allow chat window to be configured temporarily when a new message is added
            self.chat_window.configure(state=NORMAL)
            # Append message to the chat window
            self.chat_window.insert(END, f"{msg}\n")
            # Disable the chat window again so that the user cannot edit the displayed chat messages
            self.chat_window.configure(state=DISABLED)

            # Scroll to the bottom of the chat window everytime a new message is sent
            self.chat_window.see(END)
        except:
            self.quit()

    # Function for receiving text messages from the TCP chat server
    def receiveChat(self):
        while self.runThread:
            try:
                message = self.user_chat.recv(1024).decode('ascii')
                # Prompt user to enter a username
                if message == "#NAME#":
                    self.user_input.configure(state=NORMAL)
                    self.updateChat("Enter a username")
                # Update ping
                elif message[0:6] == "Ping: ":
                    self.text_ping['text'] = f"{message}ms"
                # Prompt user to enter a new username
                elif message == "#TAKEN#":
                    self.username = ""
                    self.updateChat("Username is taken. Enter another one.")
                elif message == "Connected to the server!":
                    self.updateChat(message)
                    self.username_label.configure(text=f"Username: {self.username}")
                    self.updateChat(f"Your username is: {self.username}")
                    # Thread for updating text chat ping
                    threading.Thread(target=self.writeSendPing,daemon=True).start()
                # Prompt client to shutdown when the server is not up
                elif message == "#CLOSING#":
                    self.quit()
                    break
                # Call self.updateChat to update the chat
                else:
                    self.updateChat(message)
            except:
                break
    
    # Handles closing client (closes all threads and sockets)
    def quit(self):
        self.user_chat.close()
        self.runThread = False
        self.clientWindow.destroy()

if __name__ == '__main__':
    chat_client = ChatClient()
    chat_client.run()