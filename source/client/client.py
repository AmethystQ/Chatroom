from config_cli import *
import tkinter
import tkinter.messagebox
import window_login
import request_protocol
import client_socket
import threading
import window_chat
import sys
import time
import os


# the core part to construct the client window
class Client(object):
    def __init__(self):
        # initialize the login window (main window)
        self.window=window_login.WindowLogin()
        self.window.button_reset_on_click(lambda: self.window.clear_entry())
        self.window.button_login_on_click(lambda: self.send_login_data())

        '''
        # initialize the choose window to select users
        self.window_choose=window_choose.WindowChoose()
        # make the window invisible when program is opened
        self.window_choose.withdraw()
        self.window_choose.button_choose_on_click(lambda: self.send_choose_info())
        '''

        # initialize the chat window
        self.window_chat=window_chat.WindowChat()
        # make the window invisible when program is opened
        self.window_chat.withdraw()
        self.window_chat.button_send_on_click(lambda: self.send_chat_data())
        self.window_chat.button_file_on_click(lambda: self.send_file())
        self.window_chat.button_audio_on_click(lambda: self.send_audio())

        # create the client socket
        self.socket=client_socket.ClientSocket()

        # define the (id-service type) corresponding relationship dictionary
        self.response_handle_function = {}
        self.response_handle_function[RESPONSE_LOGIN] = self.response_login_handle
        self.response_handle_function[RESPONSE_CHAT] = self.response_chat_handle
        self.response_handle_function[BROADCAST_USERLIST] = self.broadcast_userlist_handle
        self.response_handle_function[DOWNLOAD_FILE] = self.download_file_handle
        self.response_handle_function[DOWNLOAD_FILE_DATA] = self.download_data_handle
        self.response_handle_function[DOWNLOAD_FILE_END] = self.download_end_handle
        self.response_handle_function[DOWNLOAD_AUDIO] = self.download_audio_handle
        self.response_handle_function[DOWNLOAD_AUDIO_DATA] = self.download_audio_data_handle
        self.response_handle_function[DOWNLOAD_AUDIO_END] = self.download_audio_end_handle

        # online user name
        self.username=None

        # online user list
        self.userlist={}

        self.file_info=[]

        self.audio_info = []

        # release the resource when window is closed
        self.window.window_on_closed(lambda: self.exit())
        self.window_chat.window_on_closed(lambda: self.exit())

        # a mark to judge whether the client is running
        self.is_running=True

    def startup(self):
        # connect to the server
        self.socket.connect()

        # create a thread to receive the message sent from the server
        threading.Thread(target=lambda: self.response_handle()).start()

        self.window.mainloop()

    def send_login_data(self):
        # send the login data to the server
        username=self.window.get_username()
        password=self.window.get_password()
        request_data=request_protocol.RequestProtocol.request_login_result(username,password)
        print('send the message:%s' % request_data)
        self.socket.send_data(request_data)

    def send_chat_data(self):
        # get the content of the input text and send it to the server
        message=self.window_chat.get_text()
        self.window_chat.clear_input()

        # generate the send data according to the protocol format
        request_text=request_protocol.RequestProtocol.request_chat(self.username,message)

        # send the data to the server
        self.socket.send_data(request_text)

        # show the sent text on the window
        self.window_chat.append_message('我',message)

    def response_handle(self):
        # perpetually receive the latest message sent from the server
        while self.is_running:
            recv_data=self.socket.recv_data()

            # judge if it is a file data transmission
            if recv_data[0:4] == bytes(DOWNLOAD_FILE_DATA + DELIMETER, 'utf-8'):
                self.download_data_handle(recv_data[4:])
                continue

            # judge if it is a file data transmission
            if recv_data[0:4] == bytes(DOWNLOAD_AUDIO_DATA + DELIMETER, 'utf-8'):
                self.download_audio_data_handle(recv_data[4:])
                continue

            print('receive the message from the server: %s' % recv_data)

            # parse the message
            parse_data=self.parse_response_data(recv_data)
            handle_function=self.response_handle_function.get(parse_data['response_id'])
            if handle_function:
                handle_function(parse_data)

    @staticmethod
    def parse_response_data(recv_data):
        # resolve the message
        # format: login: REQUEST_LOGIN#result#nickname#username
        #         chat:  REQUEST_CHAT#nickname#messages
        #         users: REQUEST_USER_CHOOSE#ACK
        response_list=recv_data.split(DELIMETER)
        response_data={}
        response_data['response_id']=response_list[0]

        # response of login information
        if response_data['response_id']==RESPONSE_LOGIN:
            response_data['result']=response_list[1]
            response_data['nickname']=response_list[2]
            response_data['username'] = response_list[3]

        # response of chat messages
        elif response_data['response_id']==RESPONSE_CHAT:
            response_data['nickname'] = response_list[1]
            response_data['messages'] = response_list[2]

        # response of user list broadcast information
        elif response_data['response_id']==BROADCAST_USERLIST:
            response_data['userlist']=response_list[1]

        # response of the file data
        elif response_data['response_id']==DOWNLOAD_FILE:
            response_data['nickname'] = response_list[1]
            response_data['file_name'] = response_list[2]
            response_data['length']=response_list[3]

        # response of the audio data
        elif response_data['response_id'] == DOWNLOAD_AUDIO:
            response_data['nickname'] = response_list[1]
            response_data['file_name'] = response_list[2]
            response_data['length'] = response_list[3]

        return response_data

    def response_login_handle(self,response_data):
        # handle the login response
        print('login information accepted: ',response_data)
        result=response_data['result']
        if result=='1':
            nickname=response_data['nickname']
            self.username=response_data['username']
            print('登录成功，%s 昵称为 %s' % (self.username,nickname))
            tkinter.messagebox.showinfo('提示', '登录成功')

            # make the login invisible
            self.window.withdraw()

            # make the chat window visible
            self.window_chat.set_title(nickname)
            self.window_chat.update()
            self.window_chat.deiconify()
        else:
            tkinter.messagebox.showinfo('提示','登录失败')
            print('登录失败')
            return

    def response_chat_handle(self,response_data):
        # handle the chat message
        print('chat information accepted: ',response_data)
        sender=response_data['nickname']
        message=response_data['messages']
        self.window_chat.append_message(sender,message)

    def broadcast_userlist_handle(self,response_data):
        # handle the users list broadcast
        print('users list broadcast accepted:', response_data)
        self.userlist=eval(response_data['userlist'])
        print('userlist:',self.userlist)
        self.update_userlist(self.userlist)

    def download_file_handle(self,response_data):
        # handle the file download
        sender=response_data['nickname']
        print('file data accepted from ',sender)
        file_name = response_data['file_name']
        length = response_data['length']
        self.window_chat.append_message(sender, '向您传来一份文件:%s\n' % file_name,'blue')
        location=window_chat.WindowChat.choose_file_location(file_name)
        if location=='':
            print('Canceled')
            self.file_accept('0')
        else:
            print('ready to receive')
            position=location+'/'+file_name
            print(position)
            file=open(position,'wb')
            self.file_info=[position,file,length]
            self.file_accept('1')

    def download_data_handle(self, data):
        file=self.file_info[1]
        file.write(data)
        uncompleted = int(self.file_info[2]) - len(data)
        self.file_info[2] = str(uncompleted)
        print('file receiving...', uncompleted)

    def download_end_handle(self,response_data):
        file=self.file_info[1]
        if int(self.file_info[2])!=0:
            print('Unexpected Error!')
        else:
            print('Normal End of Downloading')
            tkinter.messagebox.showinfo('提示', '文件下载完毕')
        self.file_info=[]
        file.close()

    def download_audio_handle(self,response_data):
        # handle the file download
        sender=response_data['nickname']
        print('audio data accepted from ',sender)
        file_name = response_data['file_name']
        length = response_data['length']
        self.window_chat.append_message(sender, '向您传来一段语音:\n','blue')
        if_play = tkinter.messagebox.askokcancel('提示', '收到语音，是否要下载播放？')
        #location=window_chat.WindowChat.choose_file_location(file_name)
        if not if_play:
            print('Canceled')
            self.audio_accept('0')
        else:
            print('ready to receive')
            position=WAVE_OUTPUT_FILENAME
            file=open(position,'wb')
            self.audio_info=[position,file,length]
            self.audio_accept('1')

    def download_audio_data_handle(self, data):
        file=self.audio_info[1]
        file.write(data)
        uncompleted = int(self.audio_info[2]) - len(data)
        self.audio_info[2] = str(uncompleted)
        print('audio receiving...', uncompleted)

    def download_audio_end_handle(self,response_data):
        file=self.audio_info[1]
        if int(self.audio_info[2])!=0:
            print('Unexpected Error!')
            file.close()
        else:
            print('Normal End of Downloading')
            file.close()
            tkinter.messagebox.showinfo('提示', '语音下载完毕，即将播放')
            self.window_chat.audio_process.play_audio()
            os.remove(WAVE_OUTPUT_FILENAME)
        self.audio_info=[]


    def exit(self):
        # close the sub thread
        self.is_running=False

        # close the socket
        self.socket.close()
        sys.exit(0)

    def send_file(self):
        file_position=self.window_chat.get_file()
        if file_position!='':

            # open the selected file
            file=open(file_position,'rb')
            file_name=file.name.split('/')[-1]
            print('The name is:',file_name)
            file_data=file.read()
            file.close()
            file = open(file_position, 'rb')
            length=len(file_data)
            print('file length:',length)
            send_data=request_protocol.RequestProtocol.upload_file(self.username,file_name,str(length))
            self.socket.send_data(send_data)
            file_data = file.read(2000)
            while file_data!=b'':
                send_data=request_protocol.RequestProtocol.upload_file_data()
                self.socket.send_file(send_data+file_data)
                print(len(file_data))
                time.sleep(0.001)
                file_data = file.read(2000)
            print('over')
            send_data=request_protocol.RequestProtocol.upload_file_end()
            self.socket.send_data(send_data)
            file.close()
            tkinter.messagebox.showinfo('提示', '文件传输完毕')

    def send_audio(self):
        if_send=self.window_chat.audio_recording()
        if if_send:
            file = open(WAVE_OUTPUT_FILENAME, 'rb')
            file_name = file.name
            file_data = file.read()
            file.close()
            file = open(WAVE_OUTPUT_FILENAME, 'rb')
            length = len(file_data)
            print('file length:', length)
            send_data = request_protocol.RequestProtocol.upload_audio(self.username, file_name, str(length))
            self.socket.send_data(send_data)
            file_data = file.read(2000)
            while file_data != b'':
                send_data = request_protocol.RequestProtocol.upload_audio_data()
                self.socket.send_file(send_data + file_data)
                print(len(file_data))
                time.sleep(0.001)
                file_data = file.read(2000)
            print('over')
            send_data = request_protocol.RequestProtocol.upload_audio_end()
            self.socket.send_data(send_data)
            file.close()
            tkinter.messagebox.showinfo('提示', '语音传输完毕')

    def update_userlist(self,userlist):
        self.window_chat.set_userlist(userlist)

    def file_accept(self, ret):
        send_data=request_protocol.RequestProtocol.file_accept(ret)
        self.socket.send_data(send_data)

    def audio_accept(self, ret):
        send_data=request_protocol.RequestProtocol.audio_accept(ret)
        self.socket.send_data(send_data)

if __name__ == '__main__':
    client=Client()
    client.startup()
