from config_cli import *
import pyaudio
import wave
import os


class AudioProcess(object):
    def __init__(self):
        self.flag = False
        self.frames = []
        self.stream = None
        self.audio = None

    def record_initialize(self):
        self.audio = pyaudio.PyAudio()

        # open the data stream
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=CHANNELS,
                                      rate=RATE,
                                      input=True,
                                      frames_per_buffer=CHUNK)

    def record_audio(self):
        print("& Start Recording & :")

        while not self.flag:
            data = self.stream.read(CHUNK)
            self.frames.append(data)

        # start a new thread to record the data
        #threading.Thread(target=lambda: self.recording()).start()

        # for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        # while not flag:
        #    data = stream.read(CHUNK)
        #   frames.append(data)

        print("#### done recording ####")
        # stop the data stream
        self.stream.stop_stream()
        self.stream.close()

        # close the pyaudio
        self.audio.terminate()

        wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(self.frames))
        wave_file.close()
        self.frames=[]
        self.flag=False

    def play_audio(self):
        chunk = 1024
        wave_file = wave.open(WAVE_OUTPUT_FILENAME, "rb")
        self.audio = pyaudio.PyAudio()

        # open the data stream
        self.stream = self.audio.open(format=self.audio.get_format_from_width(wave_file.getsampwidth()),
                                      channels=wave_file.getnchannels(),
                                      rate=wave_file.getframerate(),
                                      output=True)

        # read the data
        data = wave_file.readframes(chunk)

        # play the audio
        while data != b'':
            self.stream.write(data)
            data = wave_file.readframes(chunk)

        # stop the stream
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        wave_file.close()

