# Filename: UDPvideoclientTest.py
# Description: File for UDP video chat client, but uses a video in place of a camera. Video file is not provided.
# NOTE: This is an unoptimized implementation so some features may not work as desired.

import cv2, imutils, socket, numpy as np, time, threading
from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"
buffer_size = 65536
host_ip = socket.gethostbyname(socket.gethostname())
port = 55666

message = "First Time"

class VideoClient:
    def __init__ (self):
        self.video = cv2.VideoCapture('testvideo.mp4')
        self.runThread = True
        self.showVideo = False
        self.showPreview = False
        self.clientWindow = Tk()
        self.setupWindow()
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)

    def setupWindow(self):
        self.clientWindow.title("Video Client Test")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=400, height=400, bg=bg_color)

        self.send_video = Button(self.clientWindow, text="Share Video", width=80, bg=bg_bottom, command=self.shareVideo)
        self.send_video.place(relx=0.5, rely=0.03, relheight=0.07, relwidth=0.35)

        self.show_preview = Button(self.clientWindow, text="Show Preview", width=80, bg=bg_bottom, command=self.allowPreview)
        self.show_preview.place(relx=0.5, rely=0.14, relheight=0.07, relwidth=0.35)

    def shareVideo(self):
        self.showVideo = not self.showVideo
        if not self.showVideo:
            self.send_video['text'] = 'Share Video'
        else:
            self.send_video['text'] = 'Stop Sharing Video'
            # SEND START
            socket_vid.sendto("START".encode('ascii'), (host_ip, port))

    def run(self):
        self.receive_thread = threading.Thread(target=self.receiveVideo)
        self.receive_thread.start()

        self.send_thread = threading.Thread(target=self.sendVideo)
        self.send_thread.start()

        self.preview_thread = threading.Thread(target=self.displayPreview)
        self.preview_thread.start()

        self.clientWindow.mainloop()

    def quit(self):
        time.sleep(1)
        # Wait before sending
        socket_vid.sendto("BYE".encode('ascii'), (host_ip, port))
        socket_vid.close()
        self.video.release()
        self.runThread = False
        self.clientWindow.destroy()
        cv2.destroyAllWindows()
    
    def allowPreview(self):
        self.showPreview = not self.showPreview
        if not self.showPreview:
            self.show_preview['text'] = 'Share Preview'
        else:
            self.show_preview['text'] = 'Stop Displaying Preview'
    
    def displayPreview(self):

        while self.runThread:
            WIDTH = 400
            fps, st, frame_count, cnt = (0, 0, 20, 0)
            while self.showPreview:
                _,frame = self.video.read()
                frame = imutils.resize(frame,width=WIDTH)

                frame = cv2.putText(frame,"FPS: "+str(fps), (10,40), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
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

    def sendVideo(self):
        while self.runThread:
            WIDTH = 400
            doneStreaming = False
            while self.showVideo:
                doneStreaming = True
                _,frame = self.video.read()
                frame = imutils.resize(frame,width=WIDTH)
                encoded,buffer = cv2.imencode('.jpg',frame)
                socket_vid.sendto(buffer, (host_ip, port))

            if doneStreaming and not self.showVideo:
                print("STREAM ENDED")
                time.sleep(1)
                socket_vid.sendto("END".encode('ascii'), (host_ip, port))

                doneStreaming = False

    def receiveVideo(self):
        fps, st, frame_count, cnt = (0, 0, 20, 0)

        while self.runThread:
            packet,_ = socket_vid.recvfrom(buffer_size)
            try:
                if packet.decode('ascii') == "STOP":
                    print("Received STOP")
                    try:
                        cv2.destroyWindow("Receiving Video")
                    except:
                        pass
                
            except:
                npdata = np.frombuffer(packet,dtype=np.uint8)
                frame = cv2.imdecode(npdata, 1)

                # Display framerate
                frame = cv2.putText(frame,"FPS: "+str(fps), (10,40), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
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

if __name__ == '__main__':
    try:
        socket_vid = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_vid.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        socket_vid.sendto(message.encode('ascii'), (host_ip, port))
        video_client = VideoClient()
        video_client.run()
    except:
        print("UDP Video Server is offline. Please try again later.")