# Filename: ChatClient.py
# Description: File for text, video, and voice chat client

import cv2, imutils, socket, numpy as np, time, threading, pyaudio
from tkinter import *

bg_color = "#17202A"
ping_color = "#6BFF64"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"
host_ip = socket.gethostbyname(socket.gethostname())
chatPort = 55555
videoPort = 55666
audioPort = 55777
buffer_size = 65536
# audio will be in chunks of 1024 sample
chunk = 1024
# 16 bits per sample
audio_format = pyaudio.paInt16
channels = 1
# Record at 44100 samples per second
fs = 44100
# Number of seconds to record audio before sending
seconds = 0.1

class ChatClient:
    def __init__(self):
        # PortAudio interface
        self.p = pyaudio.PyAudio()
        # Chat socket (TCP)
        self.user_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Video socket (UDP)
        self.user_vid = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.user_vid.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        # Audio socket (TCP)
        self.user_audio = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        # Preview and send video threads
        self.preview_thread = threading.Thread(target=self.displayPreview)
        self.sendvideo_thread = threading.Thread(target=self.sendVideo)

        self.shareAudio = False
        self.canHear = False
        self.showVideo = False
        self.viewStream = False
        self.showPreview = False
        self.runThread = True
        self.canDisplay = False
        self.clientWindow = Tk()
        self.setupWindow()
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.username = ""
    
    def setupWindow(self):
        self.clientWindow.title("Chat Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=600, height=600, bg=bg_color)

        # Label for text chat ping
        self.text_ping = Label(self.clientWindow, bg=bg_color, fg=ping_color, text="T-Ping:", pady=10, justify=LEFT, anchor='w')
        self.text_ping.place(relwidth=0.4, relheight=0.05, relx=0.01, rely=0)

        # Label for video chat ping
        self.video_ping = Label(self.clientWindow, bg=bg_color, fg=ping_color, text="V-Ping:", pady=10, justify=LEFT, anchor='w')
        self.video_ping.place(relwidth=0.4, relheight=0.05, relx=0.01, rely=0.04)

        # Label for audio chat ping
        self.audio_ping = Label(self.clientWindow, bg=bg_color, fg=ping_color, text="A-Ping:", pady=10, justify=LEFT, anchor='w')
        self.audio_ping.place(relwidth=0.4, relheight=0.05, relx=0.01, rely=0.08)

        # Label for username
        self.username_label = Label(self.clientWindow, bg=bg_color, fg=text_color, text="Username:", pady=10, justify=LEFT, anchor='w')
        self.username_label.place(relwidth=0.3, relx=0.41)

        # Chat window
        self.chat_window = Text(self.clientWindow, width=20, height=2, bg=bg_color, fg=text_color, padx=4,pady=4)
        self.chat_window.place(relheight=0.675, relwidth=(470/600), rely=0.14)
        self.chat_window.configure(state=DISABLED)

        # Stream video
        self.send_video = Button(self.clientWindow, text="Share Video", width=40, bg=bg_bottom, command=self.shareVideo)
        self.send_video.place(relx=0.79, rely=0.27, relheight=0.07, relwidth=0.18)
        self.send_video.configure(state=DISABLED, text="Share Video")

        # Display preview
        self.show_preview = Button(self.clientWindow, text="Show Preview", width=40, bg=bg_bottom, command=self.allowPreview)
        self.show_preview.place(relx=0.79, rely=0.38, relheight=0.07, relwidth=0.18)

        # Toggle viewing others' video feed
        self.view_stream = Button(self.clientWindow, text="View Stream", width=40, bg=bg_bottom, command=self.enableViewing)
        self.view_stream.place(relx=0.79, rely=0.49, relheight=0.07, relwidth=0.18)

        # Stream audio
        self.send_audio = Button(self.clientWindow, text="Start Speaking", width=40, bg=bg_bottom, command=self.allowAudio)
        self.send_audio.place(relx=0.79, rely=0.60, relheight=0.07, relwidth=0.18)
        self.send_audio.configure(state=DISABLED, text="Start Speaking")

        # Deafen audio
        self.hear_audio = Button(self.clientWindow, text="Start Listening", width=40, bg=bg_bottom, command=self.hearAudio)
        self.hear_audio.place(relx=0.79, rely=0.71, relheight=0.07, relwidth=0.18)
        self.hear_audio.configure(state=DISABLED, text="Start Listening")

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

    def run(self):
        try:
            self.user_chat.connect((host_ip, chatPort))
            # Thread to receive messages from the TCP text server
            # Updates the chat in the tkinter window with new messages from other clients and/or the server
            receiveMSG = threading.Thread(target=self.receiveChat,daemon=True)
            receiveMSG.start()
            self.clientWindow.mainloop()
        except:
            print("Servers are down. Try again later.")
            self.runThread = False
            self.video.release()
    
    #### FUNCTIONS FOR TCP CHAT ####

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
    def updateChat(self, msg: str, sender=""):
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

    # Function for receiving text messages from the TCP chat server
    def receiveChat(self):
        while self.runThread:
            try:
                message = self.user_chat.recv(1024).decode('ascii')
                # Prompt user to enter a username
                if message == "#NAME#":
                    self.user_input.configure(state=NORMAL)
                    self.updateChat("Enter a username")
                # Informs client to expect a video stream from the server
                elif message[0:7] == "T-Ping:":
                    self.text_ping['text'] = f"{message}ms"
                elif message == "#STARTVID#":
                    self.canDisplay = True
                # Informs client that video stream from the server has ended
                elif message == "#ENDVID#":
                    self.canDisplay = False
                 # Prompt user to enter a new username
                elif message == "#TAKEN#":
                    self.username = ""
                    self.updateChat("Username is taken. Enter another one.")
                # Prompt client to shutdown when the server is not up
                elif message == "#CLOSING#":
                    self.quit()
                    break
                # Enable video streaming button and send a packet of data to allow server to obtain the client's return address
                # Also enable audio streaming button and send data to allow server to update client's TCP audio socket on server's side
                elif message == "Connected to the server!":
                    self.updateChat(message)
                    self.updateChat(f"Your username is: {self.username}")
                    self.username_label.configure(text=f"Username: {self.username}")
                    # Thread for updating text chat ping
                    threading.Thread(target=self.writeSendPing,daemon=True).start()
                    self.send_video.configure(state=NORMAL)
                    self.user_vid.sendto(f"FIRST:{self.username}".encode('ascii'), (host_ip, videoPort))
                    # Thread to receive jpg packets from the UDP server
                    # Updates the frames of the video window that pops up using opencv-python with the live feed from a different client
                    receiveVideo = threading.Thread(target=self.receiveVideo, daemon=True)
                    receiveVideo.start()
                    # Thread for updating video chat ping
                    threading.Thread(target=self.writeSendVideoPing, daemon=True).start()
                    try:
                        self.user_audio.connect((host_ip, audioPort))
                        self.user_audio.send(f"Joined:{self.username}".encode('ascii'))
                        if self.user_audio.recv(1024).decode('ascii') == "#VERIFIED#":
                            self.send_audio.configure(state=NORMAL)
                            self.hear_audio.configure(state=NORMAL)
                            # Thread to receive audio packets and update ping
                            hearAudioThread = threading.Thread(target=self.receiveAudio, daemon=True)
                            hearAudioThread.start()
                            # Thread for updating audio chat ping
                            threading.Thread(target=self.writeSendAudioPing, daemon=True).start()       
                    except:
                        print("Audio server is offline try again later...")
                # Prompt client to shutdown when the server is not up
                elif message == "#CLOSING#":
                    self.quit()
                    break
                # Call self.updateChat to update the chat
                else:
                    self.updateChat(message, "")
            except:
                break
    
    #### END OF FUNCTIONS FOR TCP TEXT CHAT ####
    
    #### FUNCTIONS FOR UDP VIDEO STREAMING ####

    # Update ping for UDP video chat server
    def writeSendVideoPing(self):
        if self.runThread:
            threading.Timer(1.0, self.writeSendVideoPing).start()
            now = time.time()
            self.user_vid.sendto(f"#PING:{now}".encode('ascii'),(host_ip,videoPort))

    # Toggle sharing video
    def shareVideo(self):
        self.showVideo = not self.showVideo
        if not self.showVideo:
            self.send_video['text'] = "Share Video"
        else:
            self.send_video['text'] = "End Video"
            # Thread to send jpg packets to the UDP server
            # Constantly send the frames of the client's webcam to the server when allowed
            self.sendvideo_thread = threading.Thread(target=self.sendVideo)
            self.sendvideo_thread.start()
    
    # Toggle viewing stream
    def enableViewing(self):
        self.viewStream = not self.viewStream
        if not self.viewStream:
            self.view_stream['text'] = "View Stream"
        else:
            self.view_stream['text'] = "End Stream"
    
    # Toggle viewing preview
    def allowPreview(self):
        self.showPreview = not self.showPreview
        if not self.showPreview:
            self.show_preview['text'] = "Show Preview"
        else:
            self.show_preview['text'] = "End Preview"
            # Thread to handle viewing a preview of a client's webcam
            # Creates a new cv2 window with live feed of client's webcam and opens/terminates when prompted
            self.preview_thread = threading.Thread(target=self.displayPreview)
            self.preview_thread.start()
    
    # Show preview of video
    def displayPreview(self):
        WIDTH = 400
        fps, st, frame_count, cnt = (0, 0, 20, 0)
        while self.showPreview:
            _,frame = self.video.read()
            frame = imutils.resize(frame,width=WIDTH)
            # Display framerate
            frame = cv2.putText(frame, f"FPS: {fps}", (10,40), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
            cv2.imshow("Preview of Video",frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or self.showPreview == False:
                cv2.destroyWindow("Preview of Video")
                # If user terminated window with q, then update button
                if key == ord('q') and self.showPreview:
                    self.allowPreview()
                break
            if cnt == frame_count:
                try:
                    fps = round(frame_count/(time.time()-st))
                    st=time.time()
                    cnt=0
                except:
                    pass
            cnt+=1
    
    # Send video to UDP server
    def sendVideo(self):
        self.user_vid.sendto("START".encode('ascii'), (host_ip, videoPort))
        WIDTH = 400
        while self.showVideo:
            try:
                _,frame = self.video.read()
                frame = imutils.resize(frame,width=WIDTH)
                encoded,buffer = cv2.imencode('.jpg',frame)
                self.user_vid.sendto(buffer, (host_ip, videoPort))
            except:
                break
        
        # Cannot send #ENDVID# when server shuts down and client is streaming
        try:
            self.user_vid.sendto("END".encode('ascii'), (host_ip, videoPort))
        except:
            pass

    # Receive video content from clients via UDP server
    def receiveVideo(self):
        fps, st, frame_count, cnt = (0, 0, 20, 0)
        while self.runThread:
            try:
                packet,_ = self.user_vid.recvfrom(buffer_size)
                try:
                    msg = packet.decode('ascii')
                    if msg == "#STOP#":
                        self.canDisplay = False
                        try:
                            cv2.destroyWindow("Receiving Video")
                        except:
                            pass
                    elif msg == "#START#":
                        self.canDisplay = True
                    elif msg[0:6] == "V-Ping":
                        self.video_ping['text'] = f"{msg}ms"
                    elif msg == "#CLOSING#":
                        self.quit()
                        break
                except:
                    if self.canDisplay and self.viewStream:
                        npdata = np.frombuffer(packet,dtype=np.uint8)
                        frame = cv2.imdecode(npdata, 1)

                        # Display framerate
                        frame = cv2.putText(frame, f"FPS: {fps}", (10,40), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
                        cv2.imshow("Receiving Video",frame)
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q') or not self.viewStream or not self.canDisplay:
                            cv2.destroyWindow("Receiving Video")
                            if key == ord('q'):
                                self.enableViewing()
                        if cnt == frame_count:
                            try:
                                fps = round(frame_count/(time.time()-st))
                                st=time.time()
                                cnt=0
                            except:
                                pass
                        cnt+=1
            except:
                break
        
        try:
            cv2.destroyWindow("Receiving Video")
        except:
            pass

    #### END OF FUNCTIONS FOR UDP VIDEO STREAMING ####

    #### FUNCTIONS FOR TCP AUDIO CHAT ####

    # Update ping for TCP audio chat server
    def writeSendAudioPing(self):
        if self.runThread:
            threading.Timer(1.0, self.writeSendAudioPing).start()
            now = time.time()
            self.user_audio.send(f"#PING:{now}".encode('ascii'))

    # Toggle hearing
    def hearAudio(self):
        self.canHear = not self.canHear
        if not self.canHear:
            self.hear_audio['text'] = "Start Listening"
        else:
            self.hear_audio['text'] = "Stop Listening"

    # Toggle audio
    def allowAudio(self):
        self.shareAudio = not self.shareAudio
        if not self.shareAudio:
            self.send_audio['text'] = "Start Speaking"
        else:
            self.send_audio['text'] = "Stop Speaking"
            # Thread to record audio
            recordAudio = threading.Thread(target=self.record, daemon=True)
            recordAudio.start()
    
    # Send audio
    def sendAudio(self, data: bytes):
        if self.runThread:
            self.user_audio.sendall(data)

    # Record audio from microphone
    def record(self):
        stream = self.p.open(format=audio_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
        while self.shareAudio:
            data=b""
            # Record and send audio every 0.05 seconds
            for i in range(0, int(fs / chunk * (seconds/2))):
                data+=stream.read(chunk)
            threading.Thread(target=self.sendAudio, args=(data,)).start()

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
    
    # Plays received audio
    def playAudio(self, data):
        p = pyaudio.PyAudio()
        stream = p.open(format=audio_format, channels=channels, rate=fs, frames_per_buffer=chunk,output=True)
        stream.write(data)
        stream.stop_stream()
        stream.close()
        p.terminate()

    # Receives audio packets from server
    def receiveAudio(self):
        while self.runThread:
            # Every 0.1 seconds audio will be played
            data=b""
            for i in range(0, int(fs / chunk * seconds)):
                try:
                    audio = self.user_audio.recv(1024*8)
                    try:
                        audio_ping = audio.decode('ascii')
                        if audio_ping[0:7] == "A-Ping:":
                            self.audio_ping['text'] = f"{audio_ping}ms"
                    except:
                        if self.canHear:
                            data+=audio
                except:
                    break
            # Plays the audio after 0.1 seconds on a separate thread
            # Client will still receive audio while previous audio plays
            # These threads terminate after audio is played
            if self.canHear:
                thread = threading.Thread(target=self.playAudio, args=(data,), daemon=True)
                thread.start()
    
    #### END OF AUDIO CHAT FUNCTIONS ####
    
    # Handles closing client (closes all threads and sockets)
    def quit(self):
        self.showVideo = False
        self.showPreview = False
        self.canDisplay = False
        self.runThread = False
        self.viewStream = False
        self.canHear = False
        self.shareAudio = False
        # Terminate PortAudio interface
        self.p.terminate()
        self.user_chat.close()
        self.user_audio.close()
        if self.preview_thread.is_alive():
            self.preview_thread.join()
        if self.sendvideo_thread.is_alive():
            self.sendvideo_thread.join()
        self.user_vid.close()
        self.video.release()
        cv2.destroyAllWindows()
        self.clientWindow.destroy()

if __name__ == '__main__':
    chat_client = ChatClient()
    chat_client.run()
    