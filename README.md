# Python Chat Application (Unoptimized Branch)
This is the Unoptimized Branch for Python Chat App. These implementations are the basic versions that work, but include a lot of inefficiencies. Unlike the latency and main branch, this branch does not display user ping.

## Modules
The modules used in the python chat application are opencv-python, tk, imutils, sockets, threaded, numpy, pipwin, pyaudio, and time. The sockets module is used to create and use sockets. The threaded module (imported as threading) is used for creating and managing threads. These two modules are in all iterations of the chat application. The module tk (known as tkinter) is used to create the user interface for chat clients. The modules opencv-python, imutils, and numpy are used for video chat. The modules pipwin and pyaudio are used to download pyaudio and record/listen to audio respectively. The time module is used for sending audio in increments for implementations with voice chat.

## Files and Basic Description
`basicchatclient.py` and `basicchatserver.py` - Text chat with terminal (For users and server respectively) **Handles 2 or more clients**

`TextMsgClient.py` and `TextMsgServer.py` - Text chat client and server **Handles 2 or more clients**

`TCPvideoclient.py` and `TCPvideoserver.py` - Streaming video with TCP. Client can only receive a feed from the server. This isn't implemented that well because UDP is a better choice for video. **Handles 1 client**

`UDPvideoclient.py`, `UDPvideoclientTest.py`, and `UDPvideoserver.py` - Video chat client and server (The test client uses a particular video file as camera) **Handles only 2 clients**

`TCPaudioclient.py` and `TCPaudioserver.py` - Voice chat client and server **Handles only 2 clients**

`TextMsgVideoClient.py` and `TextMsgVideoServer.py` - Text & Video chat client and server **Handles only 2 clients**

`ChatClient.py` and `ChatServer.py` - Text, Video, & Voice chat client and server **Handles only 2 clients**

`GUI_Test.py` - File used to test the client window created for `TextMsgClient.py`

## Instructions
After installing Python 3, run the following pip commands in a terminal. Make sure to do this before using any of the files otherwise they may not work.

pip install virtualenv

python -m venv venv

source venv/Scripts/activate

pip install opencv-python

pip install tk

pip install imutils

pip install sockets

pip install threaded

pip install numpy

For windows (pyaudio errors):

pip install pipwin

pipwin install pyaudio

For linux (pyaudio errors and tk errors):

sudo apt-get install python3-pyaudio

sudo apt-get install python3-tk