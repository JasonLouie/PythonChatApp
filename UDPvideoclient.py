# Filename: UDPvideoclient.py
# Description: File for UDP video chat client

import cv2, imutils, socket, numpy as np, time, threading
from tkinter import *

bg_color = "#17202A"
ping_color = "#6BFF64"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"
buffer_size = 65536
host_ip = socket.gethostbyname(socket.gethostname())
videoPort = 55666

class VideoClient:
    def __init__ (self):
        # Video socket (UDP)
        self.user_vid = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.user_vid.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)

        # Preview and send video threads
        self.preview_thread = threading.Thread(target=self.displayPreview)
        self.sendvideo_thread = threading.Thread(target=self.sendVideo)

        self.runThread = True
        self.showVideo = False
        self.showPreview = False
        self.viewStream = False
        self.canDisplay = False
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.clientWindow = Tk()
        self.setupWindow()
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)

    def setupWindow(self):
        self.clientWindow.title("Video Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=400, height=400, bg=bg_color)

        # Label for video chat ping
        self.video_ping = Label(self.clientWindow, bg=bg_color, fg=ping_color, text="V-Ping:", pady=10, justify=LEFT, anchor='w')
        self.video_ping.place(relwidth=0.4, relx=0.01)

        # Stream video
        self.send_video = Button(self.clientWindow, text="Share Video", width=40, bg=bg_bottom, command=self.shareVideo)
        self.send_video.place(relx=0.3, rely=0.27, relheight=0.07, relwidth=0.4)

        # Display preview
        self.show_preview = Button(self.clientWindow, text="Show Preview", width=40, bg=bg_bottom, command=self.allowPreview)
        self.show_preview.place(relx=0.3, rely=0.38, relheight=0.07, relwidth=0.4)

        # Toggle viewing others' video feed
        self.view_stream = Button(self.clientWindow, text="View Stream", width=40, bg=bg_bottom, command=self.enableViewing)
        self.view_stream.place(relx=0.3, rely=0.49, relheight=0.07, relwidth=0.4)

    def run(self):
        try:
            self.user_vid.sendto("First Time".encode('ascii'), (host_ip, videoPort))
            self.receive_thread = threading.Thread(target=self.receiveVideo, daemon=True)
            self.receive_thread.start()
            threading.Thread(target=self.writeSendVideoPing, daemon=True).start()
            self.clientWindow.mainloop()
        except:
            print("UDP Video Server is offline. Please try again later.")
            self.runThread = False
            self.video.release()
    
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
                if key == ord('q') and self.showPreview == True:
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

    def sendVideo(self):
        WIDTH = 400
        self.user_vid.sendto("START".encode('ascii'), (host_ip, videoPort))
        while self.showVideo:
            try:
                _,frame = self.video.read()
                frame = imutils.resize(frame,width=WIDTH)
                encoded,buffer = cv2.imencode('.jpg',frame)
                self.user_vid.sendto(buffer, (host_ip, videoPort))
            except:
                print("ERROR SHOWING VIDEO")
                self.user_vid.sendto("END".encode('ascii'), (host_ip, videoPort))
                return
        
        # Cannot send the END keyword if UDP server is down
        try:
            self.user_vid.sendto("END".encode('ascii'), (host_ip, videoPort))
        except:
            pass

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
                            if key == ord('q') and self.viewStream:
                                self.enableViewing()
                        if cnt == frame_count:
                            try:
                                fps = round(frame_count/(time.time()-st))
                                st=time.time()
                                cnt=0
                            except:
                                pass
                        cnt+=1
                    else:
                        try:
                            cv2.destroyWindow("Receiving Video")
                        except:
                            pass
            except:
                break
    
    def quit(self):
        self.showVideo = False
        self.showPreview = False
        self.canDisplay = False
        self.runThread = False
        self.viewStream = False
        try:
            self.user_vid.sendto("BYE".encode('ascii'), (host_ip, videoPort))
        except:
            # Case for server shutdown (attempts to send bye won't work since server socket is closed)
            pass
        if self.preview_thread.is_alive():
            self.preview_thread.join()
        if self.sendvideo_thread.is_alive():
            self.sendvideo_thread.join()
        self.user_vid.close()
        self.video.release()
        cv2.destroyAllWindows()
        self.clientWindow.destroy()

if __name__ == '__main__':
    video_client = VideoClient()
    video_client.run()
    