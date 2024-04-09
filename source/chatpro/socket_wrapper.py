from config import *


class SocketWrapper(object):
    # the class of Socket Wrapper
    def __init__(self, sock):
        self.sock = sock

    def recv_data(self):
        try:
            recv_data = self.sock.recv(CONSTRICT_LENGTH)
            print(recv_data[0:4])
            if (recv_data[0:4] != bytes(UPLOAD_FILE_DATA + DELIMETER, 'utf-8')) and (
                    recv_data[0:4] != bytes(UPLOAD_AUDIO_DATA + DELIMETER, 'utf-8')):
                return recv_data.decode('utf-8')
            print(len(recv_data))
            return recv_data
        except:
            return ''

    def send_data(self, msg):
        return self.sock.send(msg.encode('utf-8'))

    def send_file(self, msg):
        return self.sock.send(msg)

    def close(self):
        self.sock.close()
