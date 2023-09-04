# Filename: TCPvideoserver.py
# Description: File for TCP video server that sends a video to a client
# Credits to pyshine (online website tutorial)

import socket, cv2, pickle, struct

# Create server socket
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = socket.gethostbyname(socket.gethostname())
print('Host IP:',host_ip)
port = 9999
socket_address = (host_ip,port)

# Socket Bind
server_socket.bind(socket_address)

# Socket Listen
server_socket.listen(5)
print("Listening at:",socket_address)

# Socket Accept
while True:
    client_socket,address = server_socket.accept()
    print('Connection established from:',address)

    if client_socket:
        vid = cv2.VideoCapture(0)
        while(vid.isOpened()): 
            img,frame = vid.read()
            a = pickle.dumps(frame)
            message = struct.pack("Q",len(a))+a
            client_socket.sendall(message)
            cv2.imshow('Transmitting video',frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                client_socket.close()
                cv2.destroyAllWindows()