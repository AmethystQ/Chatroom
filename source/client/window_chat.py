import tkinter
import tkinter.scrolledtext
import tkinter.filedialog
import tkinter.messagebox
import time
import emoji
import audio_process
import threading


class WindowChat(tkinter.Toplevel):
    def __init__(self):
        super(WindowChat,self).__init__()
        
        # set the size of the window
        self.geometry('%dx%d'% (795,505))
        self.resizable(False,False)
        
        # add the widgets
        self.add_widgets()

        # initialize the audio module
        self.audio_process=audio_process.AudioProcess()
        self.set_title('itcast1')

        self.button_send_on_click(lambda: self.append_message('Young','Hello'))

    def add_widgets(self):
        # chat messages area
        scroll_chat = tkinter.scrolledtext.ScrolledText(self)
        scroll_chat['width'] = 92
        scroll_chat['height'] = 30
        scroll_chat.place(x=10, y=10,anchor='nw')
        scroll_chat.tag_config('green',foreground='#008B00')
        scroll_chat.tag_config('blue', foreground='#66CCFF')
        scroll_chat.tag_config('black', foreground='#000000')
        scroll_chat.tag_config('system', foreground='red')
        self.children['scroll_chat']=scroll_chat

        # user list area
        label_users = tkinter.Label(self,name='label_users',fg='#303F9F')
        label_users['width'] = 20
        label_users['height'] = 15
        label_users['text'] = '在线用户:'
        label_users.place(x=660, y=10)

        # text input area
        text_chat=tkinter.Text(self,name='text_chat')
        text_chat['width']=100
        text_chat['height']=6
        text_chat.place(x=10,y=413)

        # new audio button
        button_audio = tkinter.Button(self, name='button_audio')
        button_audio['width'] = 10
        button_audio['height'] = 2
        button_audio['text'] = '语音聊天'
        button_audio.place(x=690, y=260)

        # file button
        button_file=tkinter.Button(self,name='button_file')
        button_file['width'] = 10
        button_file['height'] = 2
        button_file['text'] = '文件传输'
        button_file.place(x=690, y=335)

        # send button
        button_send=tkinter.Button(self,name='button_send')
        button_send['width']=5
        button_send['height']=2
        button_send['text'] ='发送'
        button_send.place(x=733,y=430)

    def set_title(self,title):
        # set the title of the window
        self.title(emoji.emojize(':sparkles:欢迎 %s 进入聊天室！:sparkles:' % title))

    def set_userlist(self,userlist):
        # set the online user list
        value=list(userlist.values())
        print('value:',value)
        text='在线用户：'
        for i in range(len(userlist)):
            text=text+'\n\n'+value[i]
        self.children['label_users']['text']=text

    def button_send_on_click(self,command):
        # when the send button is pressed
        self.children['button_send']['command']=command

    def button_file_on_click(self,command):
        # when the file button is pressed
        self.children['button_file']['command'] = command

    def button_audio_on_click(self,command):
        # when the audio button is pressed
        self.children['button_audio']['command'] = command

    def get_text(self):
        return self.children['text_chat'].get(0.0,tkinter.END)

    def clear_input(self):
        # clear the input text
        self.children['text_chat'].delete(0.0,tkinter.END)

    def append_message(self,sender,message,color='black'):
        # add a new message to the chat scroll
        send_time= time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        send_info='%s: %s\n' % (sender,send_time)
        message=emoji.emojize(message)
        self.children['scroll_chat'].insert(tkinter.END, send_info, 'green')
        self.children['scroll_chat'].insert(tkinter.END, ' '+message+'\n', color)

        # scroll the chat scroll automatically
        self.children['scroll_chat'].yview_scroll(3,tkinter.UNITS)

    def get_file(self):
        # get the file from local position
        file_position =tkinter.filedialog.askopenfilename()
        print('file position: ',file_position)
        return file_position

    @staticmethod
    def choose_file_location(name):
        # choose a proper position to store the file
        tkinter.messagebox.showinfo('提示', '您收到一份文件: %s' % name)
        file_position=tkinter.filedialog.askdirectory()
        return file_position

    def audio_recording(self):
        # record audio
        flag=tkinter.messagebox.askokcancel('提示', '是否开始录制音频？')
        if_send=False
        if flag:
            self.audio_process.record_initialize()
            threading.Thread(target=lambda: self.audio_process.record_audio()).start()
            tkinter.messagebox.askokcancel('正在录制……', '录制完毕后请关闭本窗口')
            self.audio_process.flag=True
            if_play=tkinter.messagebox.askokcancel('录制完毕', '是否要播放？')
            if if_play:
                self.audio_process.play_audio()
            if_send = tkinter.messagebox.askokcancel('播放完毕', '是否要发送？')
        return if_send

    def window_on_closed(self,command):
        # release the resource when the window is closed
        self.protocol('WM_DELETE_WINDOW',command)

if __name__ == '__main__':
    WindowChat().mainloop()