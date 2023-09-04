import cv2, imutils, socket, numpy as np, time, threading
from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"
host_ip = '68.237.86.46'
chatPort = 55555
videoPort = 55666
buffer_size = 65536

class ChatClient:
    def __init__(self):
        # Chat socket (TCP)
        self.user_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Video socket (UDP)
        self.user_vid = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.shareAudio = False
        self.showVideo = False
        self.showPreview = False
        self.runThread = True
        self.canDisplay = False
        self.clientWindow = Tk()
        self.setupWindow()
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)
        self.video = cv2.VideoCapture(0)
        self.username = ""
        self.msg_to_send = ""
    
    def setupWindow(self):
        self.clientWindow.title("Chat Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=600, height=550, bg=bg_color)

        # Header with user info
        self.head_label = Label(self.clientWindow, bg=bg_color, fg=text_color, text="Username:", pady=10)
        self.head_label.place(relwidth=(470/600))

        # Chat window
        self.chat_window = Text(self.clientWindow, width=20, height=2, bg=bg_color, fg=text_color, padx=4,pady=4)
        self.chat_window.place(relheight=0.675, relwidth=(470/600), rely=0.1)
        self.chat_window.configure(state=DISABLED)

        # Stream video
        self.send_video = Button(self.clientWindow, text="Share Video", width=40, bg=bg_bottom, command=self.shareVideo)
        self.send_video.place(relx=0.79, rely=0.27, relheight=0.07, relwidth=0.18)
        self.send_video.configure(state=DISABLED, text="Share Video", fg=text_color)

        # Display preview
        self.show_preview = Button(self.clientWindow, text="Show Preview", width=40, bg=bg_bottom, command=self.allowPreview)
        self.show_preview.place(relx=0.79, rely=0.38, relheight=0.07, relwidth=0.18)

        # Stream audio
        # self.send_audio = Button(self.clientWindow, text="Mic Off", width=40, bg=bg_bottom, command=self.allowAudio)
        # self.send_audio.place(relx=0.79, rely=0.49, relheight=0.07, relwidth=0.18)

        # Scrollbar
        scrollbar = Scrollbar(self.chat_window)
        scrollbar.place(relheight=1, relx=0.967)
        scrollbar.configure(command=self.chat_window.yview)

        # Bottom label
        bottom_label = Label(self.clientWindow, bg=bg_bottom, height=80)
        bottom_label.place(relwidth=(470/600), rely=0.8)
        
        # User input area
        self.user_input = Entry(bottom_label, bg=bg_entry, fg=text_color)
        self.user_input.place(relwidth=0.75, relheight=0.05, rely=0.01, relx=0.01)
        self.user_input.bind("<Return>", self.pressedEnter)
        self.user_input.configure(state=DISABLED, bg=bg_entry, fg=text_color)

        # Button for sending
        send_button = Button(bottom_label, text="Send", width=20, bg=bg_bottom, command=lambda: self.pressedEnter(None))
        send_button.place(relx=0.7, rely=0.01, relheight=0.05, relwidth=0.2)
    
    def connect(self):
        self.user_chat.connect((host_ip, chatPort))
        self.user_vid.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)

    def run(self):
        try:
            self.connect()
        except:
            print("Servers are down. Try again later.")
            self.quit()

        # Thread to receive messages from the TCP text server
        # Updates the chat in the tkinter window with new messages from other clients and/or the server
        receiveMSG = threading.Thread(target=self.receiveChat, daemon = True)
        receiveMSG.start()

        # Thread to send messages to the TCP text server
        # Constantly check if self.msg_to_send is empty and send it to the server if it is not empty
        self.writeMSG = threading.Thread(target=self.write, daemon = True)
        self.writeMSG.start()

        # Thread to receive jpg packets from the UDP server
        # Updates the frames of the video window that pops up using opencv-python with the live feed from a different client
        receiveVideo = threading.Thread(target=self.receiveVideo, daemon = True)
        receiveVideo.start()

        # Thread to send jpg packets to the UDP server
        # Constantly send the frames of the client's webcam to the server when allowed
        sendVideo = threading.Thread(target=self.sendVideo, daemon = True)
        sendVideo.start()

        # Thread to handle viewing a preview of a client's webcam
        # Creates a new cv2 window with live feed of client's webcam and opens/terminates when prompted
        self.preview_thread = threading.Thread(target=self.displayPreview, daemon = True)
        self.preview_thread.start()

        self.clientWindow.mainloop()
    
    #### FUNCTIONS FOR TCP CHAT ####
    
    # Function that handles pressing send or the enter key
    def pressedEnter(self, event):
        msg = self.user_input.get()
        # Update chat with new msg and send it to the server
        self.updateChat(msg, "You")

    # Function that handles sending messages and displaying them in the chat window
    def updateChat(self, msg, sender):
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
                if message == 'NAME':
                    self.user_input.configure(state=NORMAL)
                    self.updateChat("Enter a username", "")
                # Informs client to expect a video stream from the server
                elif message == 'STARTVID':
                    self.canDisplay = True
                # Informs client that video stream from the server has ended
                elif message == 'ENDVID':
                    self.canDisplay = False
                # Enable video streaming button and send a packet of data to allow server to obtain the client's return address
                elif message == "Connected to the server!":
                    self.send_video.configure(state=NORMAL)
                    self.user_vid.sendto(f"FIRST:{self.username}".encode('ascii'), (host_ip, videoPort))
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
    
    #### END OF FUNCTIONS FOR TCP TEXT CHAT ####
    
    #### FUNCTIONS FOR VIDEO CHAT ####

    # Toggle sharing video
    def shareVideo(self):
        self.showVideo = not self.showVideo
        if not self.showVideo:
            self.send_video['text'] = "Share Video"
        else:
            self.send_video['text'] = "End Video"
    
    # Toggle viewing preview
    def allowPreview(self):
        self.showPreview = not self.showPreview
        if not self.showPreview:
            self.show_preview['text'] = "Show Preview"
        else:
            self.show_preview['text'] = "End Preview"
    
    # Show preview of video
    def displayPreview(self):
        while self.runThread:
            WIDTH = 400
            fps, st, frame_count, cnt = (0, 0, 20, 0)
            while self.showPreview:
                _,frame = self.video.read()
                frame = imutils.resize(frame,width=WIDTH)

                frame = cv2.putText(frame, f"FPS: {fps}", (10,40), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
                cv2.imshow("Preview of Video",frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or self.showPreview == False:
                    cv2.destroyWindow("Preview of Video")
                    break
                if cnt == frame_count:
                    try:
                        fps = round(frame_count/(time.time()-st))
                        st=time.time()
                        cnt=0
                    except:
                        pass
                cnt+=1
            try:
                cv2.destroyWindow("Preview of Video")
            except:
                pass
    
    # Send video to UDP server
    def sendVideo(self):
        doneStreaming = False
        while self.runThread:
            WIDTH = 400
            while self.showVideo:
                if not doneStreaming:
                    self.user_chat.send("STARTVID".encode('ascii'))
                    doneStreaming = True
                _,frame = self.video.read()
                frame = imutils.resize(frame,width=WIDTH)
                encoded,buffer = cv2.imencode('.jpg',frame)
                self.user_vid.sendto(buffer, (host_ip, videoPort))

            if doneStreaming:
                self.user_chat.send("ENDVID".encode('ascii'))
                doneStreaming = False

    # Receive video content from clients via UDP server
    def receiveVideo(self):
        fps, st, frame_count, cnt = (0, 0, 20, 0)
        while self.runThread:
            while self.canDisplay:
                packet,_ = self.user_vid.recvfrom(buffer_size)
                npdata = np.frombuffer(packet,dtype=np.uint8)
                frame = cv2.imdecode(npdata, 1)

                # Display framerate
                frame = cv2.putText(frame, f"FPS: {fps}", (10,40), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
                cv2.imshow("Receiving Video",frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                if cnt == frame_count:
                    try:
                        fps = round(frame_count/(time.time()-st))
                        st=time.time()
                        cnt=0
                    except:
                        pass
                cnt+=1
            try:
                cv2.destroyWindow("Receiving Video")
            except:
                pass

    #### END OF FUNCTIONS FOR UDP VIDEO STREAMING ####
    
    # Handles closing client (closes all threads and sockets)
    def quit(self):
        if self.showVideo:
            self.showVideo = False
        if self.showPreview:
            self.showPreview = False
            try:
                cv2.destroyWindow("Preview of Video")
            except:
                print("Already closed preview")
        if self.canDisplay:
            self.canDisplay = False
        self.user_chat.close()
        self.user_vid.sendto("BYE".encode('ascii'), (host_ip, videoPort))
        self.user_vid.close()
        cv2.destroyAllWindows()
        self.runThread = False
        self.clientWindow.destroy()

if __name__ == '__main__':
    chat_client = ChatClient()
    chat_client.run()
    