from config_cli import *
import socket


class ClientSocket(socket.socket):
    # the socket of client
    def __init__(self):
        # use the ipv4 address and the tcp protocol
        super(ClientSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        # connect to the server
        super(ClientSocket, self).connect((SERVER_IP, SERVER_PORT))

    def recv_data(self):
        # receive the data and decode it
        recv_data = self.recv(CONSTRICT_LENGTH)
        print(recv_data[0:4])
        if (recv_data[0:4] != bytes(DOWNLOAD_FILE_DATA + DELIMETER, 'utf-8')) and (
                recv_data[0:4] != bytes(DOWNLOAD_AUDIO_DATA + DELIMETER, 'utf-8')):
            return recv_data.decode('utf-8')
        print(len(recv_data))
        return recv_data

    def send_data(self, message):
        # send the data after encoding it
        return self.send(message.encode('utf-8'))

    def send_file(self, data):
        return self.send(data)

    def receive_file(self):
        return self.recv(CONSTRICT_LENGTH)
