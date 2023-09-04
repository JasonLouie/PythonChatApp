# Filename: TCPaudioclient.py
# Description: File for voice chat client

import pyaudio, socket, threading, time
from tkinter import *

bg_color = "#17202A"
ping_color = "#6BFF64"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"

audioPort = 55777
host_ip = socket.gethostbyname(socket.gethostname())
# audio will be in chunks of 1024 sample
chunk = 1024
# 16 bits per sample
audio_format = pyaudio.paInt16
channels = 1
# Record at 44100 samples per second
fs = 44100
# Number of seconds to record audio before sending
seconds = 0.1

class AudioClient:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.user_audio = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.clientWindow = Tk()
        self.shareAudio = False
        self.runThread = True
        self.canHear = False
        self.setupWindow()
    
    def setupWindow(self):
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)
        self.clientWindow.title("Audio Client")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=300, height=200, bg=bg_color)

        self.audio_ping = Label(self.clientWindow, bg=bg_color, fg=ping_color, text="A-Ping:", pady=10, justify=LEFT, anchor='w')
        self.audio_ping.place(relwidth=0.4, relheight=0.1, relx=0.01, rely=0.05)

        self.send_audio = Button(self.clientWindow, text="Start Speaking", width=80, bg=bg_bottom, command=self.allowAudio)
        self.send_audio.place(relx=0.5, rely=0.1, relheight=0.2, relwidth=0.5)

        self.hear_audio = Button(self.clientWindow, text="Start Listening", width=80, bg=bg_bottom, command=self.hearAudio)
        self.hear_audio.place(relx=0.5, rely=0.4, relheight=0.2, relwidth=0.5)
    
    # Run client
    def run(self):
        try:
            self.user_audio.connect((host_ip, audioPort))
            self.user_audio.send("Joining".encode('ascii'))

            hearAudioThread = threading.Thread(target=self.receiveAudio, daemon=True)
            hearAudioThread.start()

            threading.Thread(target=self.writeSendAudioPing, daemon=True).start()

            self.send_audio.configure(state=NORMAL)
            self.clientWindow.mainloop()
        except:
            print("Audio server is offline try again later...")
    
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
            # Every 0.1 seconds audio will be played
            data=b""
            for i in range(0, int(fs / chunk * seconds)):
                try:
                    audio = self.user_audio.recv(1024*8)
                    try:
                        audio_ping = audio.decode('ascii')
                        if audio_ping[0:7] == "A-Ping:":
                            self.audio_ping['text'] = f"{audio_ping}ms"
                        elif audio_ping == "#CLOSING#":
                            self.quit()
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
    
    # Quit client
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
