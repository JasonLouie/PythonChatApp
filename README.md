# Python Chat Application (latency branch)
This branch was used to display ping in all implementations (except for terminal text chat and TCP video chat). It was also used to optimize each implementation and work out any remaining issues. Some issues included chat servers and clients not terminating properly, handling video and audio feed when client is closed, and ensuring that each chat function worked in the final ChatClient.py and ChatServer.py properly.

## Modules
The modules used in the python chat application are opencv-python, tk, imutils, sockets, threaded, numpy, pipwin, pyaudio, cProfile, stats, and time. The sockets module is used to create and use sockets. The threading module is used for creating and managing threads. These two modules are in all iterations of the chat application. The module tk (known as tkinter) is used to create the user interface for chat clients. The modules opencv-python, imutils, and numpy are used for video chat. The modules pipwin and pyaudio are used to download pyaudio and record/listen to audio respectively. The cProfile and pstats are used for code profiling. The time module is used for calculating user ping and increments for sending audio in implementations with voice chat.

## Files and Basic Description
`basicchatclient.py` and `basicchatserver.py` - Text chat with terminal (For users and server respectively) **Handles 2 or more clients**

`TextMsgClient.py` and `TextMsgServer.py` - Text chat client and server **Handles 2 or more clients**

`TCPvideoclient.py` and `TCPvideoserver.py` - Streaming video with TCP. Client can only receive a feed from the server. This isn't implemented that well because UDP is a better choice for video. **Handles 1 client**

`UDPvideoclient.py`, `UDPvideoclientTest.py`, and `UDPvideoserver.py` - Video chat client and server (The test client uses a particular video file as camera) **Handles only 2 clients**

`TCPaudioclient.py` and `TCPaudioserver.py` - Voice chat client and server **Handles only 2 clients**

`TextMsgVideoClient.py` and `TextMsgVideoServer.py` - Text & Video chat client and server **Handles only 2 clients**

`ChatClient.py` and `ChatServer.py` - Text, Video, & Voice chat client and server **Handles only 2 clients**

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
