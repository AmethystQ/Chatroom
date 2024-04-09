from config import *


class ResponseProtocol(object):
    @staticmethod
    # generate the user login result string
    def response_login_result(result, nickname, username):
        return DELIMETER.join([RESPONSE_LOGIN, result, nickname, username])

    @staticmethod
    def response_chat(nickname, messages):
        return DELIMETER.join([RESPONSE_CHAT, nickname, messages])

    @staticmethod
    def broadcast_userlist(userlist):
        return DELIMETER.join([BROADCAST_USERLIST,userlist])

    @staticmethod
    def download_file(nickname,file_name,length):
        return DELIMETER.join([DOWNLOAD_FILE,nickname,file_name,length])

    @staticmethod
    def download_file_data():
        return (DOWNLOAD_FILE_DATA+DELIMETER).encode('utf-8')

    @staticmethod
    def download_file_end():
        return DOWNLOAD_FILE_END+DELIMETER

    @staticmethod
    def download_audio(nickname, file_name, length):
        return DELIMETER.join([DOWNLOAD_AUDIO, nickname, file_name, length])

    @staticmethod
    def download_audio_data():
        return (DOWNLOAD_AUDIO_DATA + DELIMETER).encode('utf-8')

    @staticmethod
    def download_audio_end():
        return DOWNLOAD_AUDIO_END + DELIMETER