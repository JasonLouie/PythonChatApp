import pyaudio, socket, threading
from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"
audioPort = 55777
host_ip = '68.237.86.46'
# audio will be in chunks of 1024 sample
chunk = 1024
# 16 bits per sample
audio_format = pyaudio.paInt16
channels = 1
# Record at 44100 samples per second
fs = 44100
# Number of seconds to play audio (Play audio every 0.25 sec)
seconds = 0.25

class AudioClient:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.user_audio = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.clientWindow = Tk()
        self.shareAudio = False
        self.runThread = True
        self.setupWindow()
    
    def setupWindow(self):
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)
        self.clientWindow.title("Audio Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=400, height=400, bg=bg_color)

        self.send_audio = Button(self.clientWindow, text="Start Speaking", width=80, bg=bg_bottom, command=self.allowAudio)
        self.send_audio.place(relx=0.5, rely=0.5, relheight=0.07, relwidth=0.35)
        self.send_audio.configure(state=DISABLED)
    
    def run(self):
        try:
            self.user_audio.connect((host_ip, audioPort))
            if self.user_audio.recv(1024).decode('ascii') == "Hello":
                self.user_audio.send("Joining".encode('ascii'))

                recordAudio = threading.Thread(target=self.record)
                recordAudio.start()

                hearAudioThread = threading.Thread(target=self.receiveAudio)
                hearAudioThread.start()

                self.send_audio.configure(state=NORMAL)
                self.clientWindow.mainloop()
        except:
            print("Audio server is offline try again later...")
    
    # Toggle audio
    def allowAudio(self):
        self.shareAudio = not self.shareAudio
        if not self.shareAudio:
            self.send_audio['text'] = "Start Speaking"
        else:
            self.send_audio['text'] = "Stop Speaking"
    
    # Record audio from microphone
    def record(self):
        while self.runThread:
            if self.shareAudio:
                # print("Recording")
                stream = self.p.open(format=audio_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
                while self.shareAudio:
                    data = stream.read(chunk)
                    self.user_audio.sendall(data)
                
                # print("Stopped recording")
                # Stop and close the stream
                stream.stop_stream()
                stream.close()
    
    # Plays received audio
    def playAudio(self, data: bytes):
        p = pyaudio.PyAudio()
        stream = p.open(format=audio_format, channels=channels, rate=fs, frames_per_buffer=chunk,output=True)
        stream.write(data)
        stream.stop_stream()
        stream.close()
        p.terminate()

    # Receives audio packets from server
    def receiveAudio(self):
        while self.runThread:
            data=b""
            for i in range(0, int(fs / chunk * seconds)):
                try:
                    data+=self.user_audio.recv(1024*8)
                except:
                    # Error receiving audio
                    break
            thread = threading.Thread(target=self.playAudio,args=(data,))
            thread.start()
    
    def quit(self):
        self.clientWindow.destroy()
        self.user_audio.close()
        self.runThread = False
        self.shareAudio = False
        # Terminate PortAudio interface
        self.p.terminate()       

if __name__ == '__main__':
    audio = AudioClient()
    audio.run()
