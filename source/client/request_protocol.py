from config_cli import *


class RequestProtocol(object):
    @staticmethod
    def request_login_result(username='user1',password='123456'):
        # construct the sending message by format TYPE#user#password
        return DELIMETER.join([REQUEST_LOGIN,username,password])

    @staticmethod
    def request_chat(username,messages):
        # construct the sending message by format TYPE#user#password
        return DELIMETER.join([REQUEST_CHAT,username,messages])

    @staticmethod
    def request_choose_users(username):
        # construct the sending message by format TYPE#userlist
        return DELIMETER.join([REQUEST_USER_CHOOSE,username])

    @staticmethod
    def upload_file(username,file_name,length):
        # construct the sending message by format TYPE#user#file_name#file_data
        return DELIMETER.join([UPLOAD_FILE, username,file_name,length])

    @staticmethod
    def upload_file_data():
        # construct the sending message by format TYPE#user#file_name#file_data
        return (UPLOAD_FILE_DATA+DELIMETER).encode('utf-8')

    @staticmethod
    def upload_file_end():
        # construct the sending message by format TYPE#user#file_name#file_data
        return (UPLOAD_FILE_END + DELIMETER)

    @staticmethod
    def file_accept(ret):
        return DELIMETER.join([FILE_ACCEPT, ret])

    @staticmethod
    def upload_audio(username, file_name, length):
        # construct the sending message by format TYPE#user#file_name#file_data
        return DELIMETER.join([UPLOAD_AUDIO, username, file_name, length])

    @staticmethod
    def upload_audio_data():
        # construct the sending message by format TYPE#user#file_name#file_data
        return (UPLOAD_AUDIO_DATA + DELIMETER).encode('utf-8')

    @staticmethod
    def upload_audio_end():
        # construct the sending message by format TYPE#user#file_name#file_data
        return (UPLOAD_AUDIO_END + DELIMETER)

    @staticmethod
    def audio_accept(ret):
        return DELIMETER.join([AUDIO_ACCEPT, ret])
