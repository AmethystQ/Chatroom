import tkinter


class WindowLogin(tkinter.Tk):
    # the login window
    def __init__(self):
        # initialization
        super(WindowLogin,self).__init__()
        # set the property of the window
        self.window_init()

        # fill in the widget
        self.add_widgets()

    def window_init(self):
        # set the title of the window
        self.title('登录窗口')
        # the window cannot be stretched
        self.resizable(False,False)
        # set the size of the window
        window_width=255
        window_height=105
        pos_x=(self.winfo_screenwidth()-window_width)/2
        pos_y=(self.winfo_screenheight()-window_height)/2
        self.geometry('%dx%d+%d+%d' % (window_width,window_height,pos_x,pos_y))

    def add_widgets(self):
        # username
        label_username=tkinter.Label(self)
        label_username['text']='用户名:'
        label_username.grid(row=0,column=0,padx=10,pady=7)
        entry_username=tkinter.Entry(self,name='entry_username')
        entry_username['width']=25
        entry_username.grid(row=0,column=1)

        # password
        label_password=tkinter.Label(self)
        label_password['text'] = '密  码:'
        label_password.grid(row=1, column=0)
        entry_password = tkinter.Entry(self, name='entry_password')
        entry_password['width'] = 25
        entry_password['show']='*'
        entry_password.grid(row=1, column=1)

        # button frame
        frame_button=tkinter.Frame(self,name='frame_button')
        button_reset = tkinter.Button(frame_button, name='button_reset')
        button_reset['text'] = ' 重置 '
        button_reset.pack(side=tkinter.LEFT,padx=20)
        button_login = tkinter.Button(frame_button, name='button_login')
        button_login['text'] = ' 登录 '
        button_login.pack(side=tkinter.LEFT)
        frame_button.grid(row=2, columnspan=2,pady=7)

    def get_username(self):
        # get the user name
        return self.children['entry_username'].get()

    def get_password(self):
        # get the user name
        return self.children['entry_password'].get()

    def clear_entry(self):
        # clear all the input
        self.children['entry_username'].delete(0,tkinter.END)
        self.children['entry_password'].delete(0, tkinter.END)

    def button_login_on_click(self,command):
        # the response of login button
        button_login=self.children['frame_button'].children['button_login']
        button_login['command']=command

    def button_reset_on_click(self,command):
        # the response of reset button
        button_reset=self.children['frame_button'].children['button_reset']
        button_reset['command']=command

    def window_on_closed(self,command):
        # the response when the window is closed
        self.protocol('WM_DELETE_WINDOW',command)


if __name__ == '__main__':
    window=WindowLogin()
    window.mainloop()