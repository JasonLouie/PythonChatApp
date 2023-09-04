# Python Chat Application
The Python Chat Application is an application that allows two users to communicate through voice, video, and text chat. Text chat is fully functional for multiple users, but voice and video chat only work for two users at a time. This is mainly accomplished through the use of the python modules sockets and threaded. Multithreading was especially crucial to the project since a chat server and client must be able to receive and send data simultaneously. Upon opening the chat client, the user is prompted to connect to the server by providing a unique username. Upon leaving, the username will be available to new users. Whenever a new user joins the server, a welcome message is sent to the other users and a confirmation message is sent to the user upon successfully connecting to the server. By default, video and voice chat are disabled when a user joins the server. Users can send text messages to one another by pressing enter or the send button. Users can video chat one another by toggling their video camera on or off. The same is true for voice chat. Clients send packets of data to the server and the server broadcasts it to all users excluding the sender. All implementations (except for terminal text chat and TCP video chat) display the user's ping on the top left corner. These are the finalized versions of each chat implementation meaning functions work as desired.

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
