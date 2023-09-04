# Filename: TCPaudiotesting.py
# Description: Testing pyaudio along with recording and playing audio from microphone

import pyaudio, threading
from tkinter import *

bg_color = "#17202A"
text_color = "#A9A9A9"
bg_bottom = "#686A68"
bg_entry = "#2C3E50"
# audio will be in chunks of 1024 sample
chunk = 1024
# 16 bits per sample
audio_format = pyaudio.paInt16
channels = 1
# Record at 44100 samples per second
fs = 44100
# Number of seconds to record
seconds = .25
filename = "audio_output.wav"


class Audio:
    def __init__(self):
        self.clientWindow = Tk()
        self.shareAudio = False
        self.runThread = True
        self.setupWindow()
    
    def setupWindow(self):
        self.clientWindow.protocol("WM_DELETE_WINDOW", self.quit)
        self.clientWindow.title("Audio Recorder")
        self.clientWindow.resizable(width=False, height=False)
        self.clientWindow.configure(width=400, height=400, bg=bg_color)

        self.send_audio = Button(self.clientWindow, text="Start Speaking", width=80, bg=bg_bottom, command=self.allowAudio)
        self.send_audio.place(relx=0.5, rely=0.5, relheight=0.07, relwidth=0.35)
    
    def run(self):
        recordAudio = threading.Thread(target=self.record)
        recordAudio.start()
        self.clientWindow.mainloop()
    
    def quit(self):
        self.clientWindow.destroy()
        self.runThread = False
        self.shareAudio = False
    
    # Toggle audio
    def allowAudio(self):
        self.shareAudio = not self.shareAudio
        if not self.shareAudio:
            self.send_audio['text'] = 'Start Speaking'
        else:
            self.send_audio['text'] = 'Stop Speaking'
    
    # Record audio from microphone
    def record(self):
        while self.runThread:
            if self.shareAudio:
                p = pyaudio.PyAudio()
                stream1 = p.open(format=audio_format, channels=channels, rate=fs, frames_per_buffer=chunk,input=True)
                stream2 = p.open(format=audio_format, channels=channels, rate=fs, frames_per_buffer=chunk,output=True)
                # Initialize array for frames
                # frames = []
                # Store data in chunks for as long as audio is shared
                while self.shareAudio:
                    data= stream1.read(chunk)
                    stream2.write(data)
                    # frames.append(data)
        
                # Stop and close the stream
                stream1.stop_stream()
                stream1.close()
                stream2.stop_stream()
                stream2.close()
                # Terminate PortAudio interface
                p.terminate()

                # Save recorded data as WAV file
                # wf = wave.open(filename, 'wb')
                # wf.setnchannels(channels)
                # wf.setsampwidth(p.get_sample_size(audio_format))
                # wf.setframerate(fs)
                # wf.writeframes(b''.join(frames))
                # wf.close()

                # self.playAudio()
    

if __name__ == '__main__':
    audio = Audio()
    audio.run()
