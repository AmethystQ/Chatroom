from server_socket import ServerSocket
from config import *
import threading
import socket_wrapper
import response_protocol
import database
import os
import time

# The core part to construct the server class
class Server(object):
    def __init__(self):
        # generate the server socket
        self.server_socket = ServerSocket()

        # define the (id-service type) corresponding relationship dictionary
        self.request_handle_function = {}
        self.request_handle_function[REQUEST_LOGIN] = self.request_login_handle
        self.request_handle_function[REQUEST_CHAT] = self.request_chat_handle
        self.request_handle_function[UPLOAD_FILE] = self.file_upload_handle
        self.request_handle_function[UPLOAD_FILE_DATA] = self.file_receive_handle
        self.request_handle_function[UPLOAD_FILE_END] = self.file_end_handle
        self.request_handle_function[FILE_ACCEPT] = self.file_accept_handle
        self.request_handle_function[UPLOAD_AUDIO] = self.audio_upload_handle
        self.request_handle_function[UPLOAD_AUDIO_DATA] = self.audio_receive_handle
        self.request_handle_function[UPLOAD_AUDIO_END] = self.audio_end_handle
        self.request_handle_function[AUDIO_ACCEPT] = self.audio_accept_handle

        # create the dictionary storing the current login users
        self.clients = {}

        # create the database storing the users information
        self.db=database.DataBase()

        self.file={}

        self.audio={}

        self.file_client_soc =None

        self.audio_client_soc = None

    def startup(self):
        while True:
            print('client connection loading')
            soc, addr = self.server_socket.accept()
            print('client connection loaded')
            # generate the socket wrapper
            client_soc = socket_wrapper.SocketWrapper(soc)
            threading.Thread(target=lambda: self.request_handle(client_soc)).start()

    def request_handle(self, client_soc):
        # handle the request of client
        while True:
            msg = client_soc.recv_data()
            if msg == '':
                self.remove_offline_user(client_soc)
                client_soc.close()
                break

            if msg[0:4]==bytes(UPLOAD_FILE_DATA+DELIMETER,'utf-8'):
                self.file_receive_handle(client_soc,msg[4:])
                continue

            if msg[0:4]==bytes(UPLOAD_AUDIO_DATA+DELIMETER,'utf-8'):
                self.audio_receive_handle(client_soc,msg[4:])
                continue

            # response the client according to the type of request
            parse_data = self.parse_request_text(msg)
            #print('receive the content:%s' % parse_data)
            handle_function = self.request_handle_function.get(parse_data['request_id'])
            if handle_function:
                handle_function(client_soc, parse_data)

    # detect that a client is offline
    def remove_offline_user(self, client_soc):
        print('a client offline')
        for username,info in self.clients.items():
            if client_soc==info['soc']:
                del self.clients[username]
                self.broadcast_user_list()
                break

    # resolve the received data
    # format: login: REQUEST_LOGIN#username#password
    #         chat:  REQUEST_CHAT#username#messages
    def parse_request_text(self, msg):
        print('parse:' + msg)
        recv_list = msg.split(DELIMETER)
        recv_data = {}
        recv_data['request_id'] = recv_list[0]
        # request login
        if recv_data['request_id'] == REQUEST_LOGIN:
            recv_data['username'] = recv_list[1]
            recv_data['password'] = recv_list[2]

        # request chat
        elif recv_data['request_id'] == REQUEST_CHAT:
            recv_data['username'] = recv_list[1]
            recv_data['messages'] = recv_list[2]

        # upload file
        elif recv_data['request_id']==UPLOAD_FILE:
            recv_data['username'] = recv_list[1]
            recv_data['file_name'] = recv_list[2]
            recv_data['length']=recv_list[3]

        # download file accept
        elif recv_data['request_id']==FILE_ACCEPT:
            recv_data['ret']=recv_list[1]

        # upload audio
        elif recv_data['request_id'] == UPLOAD_AUDIO:
            recv_data['username'] = recv_list[1]
            recv_data['file_name'] = recv_list[2]
            recv_data['length'] = recv_list[3]

        # download audio accept
        elif recv_data['request_id'] == AUDIO_ACCEPT:
            recv_data['ret'] = recv_list[1]

        return recv_data

    def request_login_handle(self, client_soc, request_data):
        print('login request accepted')

        # check the account and the password
        username = request_data['username']
        password = request_data['password']
        ret, nickname, username = self.check_user_login(username, password)
        if ret == '1':
            # add the user to the online user list
            self.clients[username] = {'soc': client_soc, 'nickname': nickname}

        # assemble the feedback information and send it to the client
        response_info = response_protocol.ResponseProtocol.response_login_result(ret, nickname, username)
        client_soc.send_data(response_info)

        # broadcast the new user list
        self.broadcast_user_list()

    def request_chat_handle(self, client_soc, request_data):
        print('chat request accepted')

        # get the message information
        username=request_data['username']
        messages=request_data['messages']
        nickname=self.clients[username]['nickname']

        # transmit the message to other online clients
        transmit_info=response_protocol.ResponseProtocol.response_chat(nickname,messages)
        for user_name,info in self.clients.items():
            if username==user_name:
                # there is no need to transmit the message to the client who send it
                continue
            info['soc'].send_data(transmit_info)

    def file_upload_handle(self,client_soc,request_data):
        print('file upload request accepted')

        # ready to receive the file
        username=request_data['username']
        file_name=request_data['file_name']
        length=request_data['length']
        path=STORE_PATH+username
        if not (os.path.exists(path)):
            os.makedirs(path)
        location=path+'/'+file_name
        print(location)
        file=open(location,'wb')
        self.file[client_soc]={'length':length,'location':location,'username':username,'file_name':file_name,'file':file,'uncompleted':length}

    def file_receive_handle(self,client_soc,data):
        file=self.file[client_soc]['file']
        file.write(data)
        uncompleted=int(self.file[client_soc]['uncompleted'])-len(data)
        self.file[client_soc]['uncompleted']=str(uncompleted)
        print('file receiving...',uncompleted)

    def file_end_handle(self,client_soc,request_data):
        file = self.file[client_soc]['file']
        print(int(self.file[client_soc]['uncompleted']))
        if int(self.file[client_soc]['uncompleted'])!=0:
            print('Unexpected Error!')
        else:
            print('Normal End of Uploading')
            username=self.file[client_soc]['username']
            nickname=self.clients[username]['nickname']
            file_name=self.file[client_soc]['file_name']
            length=self.file[client_soc]['length']
            self.file_client_soc=client_soc
            self.download_file(username,nickname,file_name,length)
        file.close()

    def file_accept_handle(self,client_soc,request_data):
        ret=request_data['ret']
        if ret=='1':
            print('start downloading')
            file=open(self.file[self.file_client_soc]['location'],'rb')
            file_data=file.read(2000)
            while file_data!=b'':
                send_data=response_protocol.ResponseProtocol.download_file_data()
                client_soc.send_file(send_data+file_data)
                print(len(file_data))
                time.sleep(0.001)
                file_data = file.read(2000)
            print('over')
            send_data=response_protocol.ResponseProtocol.download_file_end()
            client_soc.send_data(send_data)
            file.close()
        #del self.file[self.file_client_soc]
        #self.file_client_soc=None

    def audio_upload_handle(self,client_soc,request_data):
        print('audio upload request accepted')

        # ready to receive the audio
        username=request_data['username']
        file_name=request_data['file_name']
        length=request_data['length']
        path=STORE_PATH+username
        if not (os.path.exists(path)):
            os.makedirs(path)
        location=path+'/'+file_name
        print(location)
        file=open(location,'wb')
        self.audio[client_soc]={'length':length,'location':location,'username':username,'file_name':file_name,'file':file,'uncompleted':length}

    def audio_receive_handle(self,client_soc,data):
        file=self.audio[client_soc]['file']
        file.write(data)
        uncompleted=int(self.audio[client_soc]['uncompleted'])-len(data)
        self.audio[client_soc]['uncompleted']=str(uncompleted)
        print('audio receiving...',uncompleted)

    def audio_end_handle(self,client_soc,request_data):
        file = self.audio[client_soc]['file']
        print(int(self.audio[client_soc]['uncompleted']))
        if int(self.audio[client_soc]['uncompleted'])!=0:
            print('Unexpected Error!')
        else:
            print('Normal End of Uploading')
            username=self.audio[client_soc]['username']
            nickname=self.clients[username]['nickname']
            file_name=self.audio[client_soc]['file_name']
            length=self.audio[client_soc]['length']
            self.audio_client_soc=client_soc
            self.download_audio(username,nickname,file_name,length)
        file.close()

    def audio_accept_handle(self,client_soc,request_data):
        ret=request_data['ret']
        if ret=='1':
            print('start downloading')
            file=open(self.audio[self.audio_client_soc]['location'],'rb')
            file_data=file.read(2000)
            while file_data!=b'':
                send_data=response_protocol.ResponseProtocol.download_audio_data()
                client_soc.send_file(send_data+file_data)
                print(len(file_data))
                time.sleep(0.001)
                file_data = file.read(2000)
            print('over')
            send_data=response_protocol.ResponseProtocol.download_audio_end()
            client_soc.send_data(send_data)
            file.close()

    def check_user_login(self, username, password):
        # check whether the client login successfully
        # query the user information from the database
        result=self.db.query("select * from users WHERE user_name='%s'" % username)
        if not result:
            return '0','',''
        if password!=result['user_password']:
            return '0','',''
        return '1', result['user_nickname'], username

    def broadcast_user_list(self):
        # select the online users information
        user_info = {}
        for index in range(len(self.clients)):
            key = list(self.clients.keys())[index]
            user_info[key] = self.clients[key]['nickname']
        send_info = response_protocol.ResponseProtocol.broadcast_userlist(str(user_info))

        # broadcast the list information to every online client
        for index in range(len(self.clients)):
            client_soc=list(self.clients.values())[index]['soc']
            client_soc.send_data(send_info)

    def download_file(self,username,nickname,file_name,length):
        send_info = response_protocol.ResponseProtocol.download_file(nickname, file_name,length)
        print(send_info)
        for user_name, info in self.clients.items():
            if username == user_name:
                # there is no need to transmit the file to the client who send it
                continue
            info['soc'].send_data(send_info)

    def download_audio(self,username,nickname,file_name,length):
        send_info = response_protocol.ResponseProtocol.download_audio(nickname, file_name,length)
        print(send_info)
        for user_name, info in self.clients.items():
            if username == user_name:
                # there is no need to transmit the file to the client who send it
                continue
            info['soc'].send_data(send_info)

if __name__ == '__main__':
    Server().startup()