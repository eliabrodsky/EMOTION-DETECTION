from deepface import DeepFace
from datetime import datetime
import csv
import pytz
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os
import speech_recognition as sr
import pprint
import whisper
from whisper import load_model
from flask import Response

import base64
import io

global timeNow
max_emotion = "Default"
emotionlist = []
lock = threading.Lock()

class VideoRecorder:
    # Video class based on openCV
    def __init__(self):
        # print("in __init__")
        self.open = True
        self.device_index = 0
        self.fps = 6  # fps should be the minimum constant rate at which the camera can
        self.fourcc = "MJPG"  # capture images (with no decrease in speed over time; testing is required)
        self.frameSize = (640, 480)  # video formats and sizes also depend and vary according to the camera used
        self.video_filename = "temp_video.avi"
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
        self.frame_counts = 1
        self.start_time = time.time()

    def timeFunction(self, emotion):
        # print("in timeFunction")
        print(emotion)
        emotionlist.append(emotion)
        # now = datetime.now()
        dt_hongkong = datetime.now(pytz.timezone('Hongkong'))
        timeNow = dt_hongkong.strftime("%H:%M:%S")
        emotion_list = [timeNow, emotion, max_emotion]
        print(emotion_list)
        with open('emotion_time.csv', 'a', newline='') as csvfile:
            my_writer = csv.writer(csvfile, delimiter=',')
            my_writer.writerow(emotion_list)
            print("HEre")

    def most_common(self, emotionlist):
        print("in most_common")
        a = max(set(emotionlist), key=emotionlist.count, default=0)
        return a

    def deepFace(self, frame_deep):
        print("in deepFace")
        obj = DeepFace.analyze(img_path=frame_deep, actions=['emotion'])
        # print("Dominant Emotion: ")
        emotion = obj['dominant_emotion']
        # print(emotion)
        self.timeFunction(emotion)

    def generate(self, gen_frame):
        print("in generate")
        global lock
        cv2.imshow('Frame Deepface 2', gen_frame)
        print("in generate")
        # loop over frames from the output stream
        while True:
            # wait until the lock is acquired
            with lock:
                # check if the output frame is available, otherwise skip
                # the iteration of the loop
                if gen_frame is None:
                    continue
                # encode the frame in JPEG format
                (flag, encodedImage) = cv2.imencode(".jpg", gen_frame)
                # ensure the frame was successfully encoded
                if not flag:
                    continue
            # yield the output frame in the byte format
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodedImage) + b'\r\n')
    # Video starts being recorded

    def video_feed(self):
        # return the response generated along with the specific media
        # type (mime type)
        return Response(self.generate(),
                        mimetype="multipart/x-mixed-replace; boundary=frame")


    def record(self):

        global max_emotion
        # counter = 1
        timer_current = 0
        if not self.video_cap.isOpened():
            print("Error opening video file")

        while self.video_cap.isOpened():
            dt_hongkong = datetime.now(pytz.timezone('Hongkong'))
            timeNow = dt_hongkong.strftime("%H:%M:%S")

            timeSec = timeNow.split(':')
            timeSec = timeSec[2]
            print(timeSec)
            if timeSec == "30" or timeSec == "00":
                max_emotion = str(self.most_common(emotionlist))

            ret, video_frame = self.video_cap.read()
            if ret:
                cv2.imshow('Frame Deepface', video_frame)

                self.video_out.write(video_frame)
                self.frame_counts += 1

                try:
                    # print("try ret")
                    self.generate(video_frame)
                    self.deepFace(video_frame)

                except:
                    print("No Face Detected")

                # Press Q on keyboard to exit
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

                # Break the loop
            else:
                break

                # time.sleep(0.16)

            # cv2.waitKey(1)

            # 0.16 delay -> 6 fps
            #
        self.video_cap.release()
        # Closes all the frames
        cv2.destroyAllWindows()

    # Finishes the video recording therefore the thread too
    def stop(self):

        if self.open == True:
            self.open = False
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()

        else:
            pass

    # Launches the video recording function using a thread
    def start(self):
        video_thread = threading.Thread(target=self.record)
        video_thread.start()



class AudioRecorder:

    # Audio class based on pyAudio and Wave
    def __init__(self):

        self.open = True
        self.rate = 44100
        self.frames_per_buffer = 1024
        self.channels = 2
        self.format = pyaudio.paInt16
        self.audio_filename = "temp_audio.wav"
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.frames_per_buffer)
        self.audio_frames = []

    # Audio starts being recorded
    def record(self):

        self.stream.start_stream()
        while (self.open == True):
            data = self.stream.read(self.frames_per_buffer)
            self.audio_frames.append(data)
            if self.open == False:
                break

    # Finishes the audio recording therefore the thread too    
    def stop(self):

        if self.open == True:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

            waveFile = wave.open(self.audio_filename, 'wb')
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b''.join(self.audio_frames))
            waveFile.close()

        pass

    # Launches the audio recording function using a thread
    def start(self):
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()


def start_AVrecording(filename):
    global video_thread
    global audio_thread

    video_thread = VideoRecorder()
    audio_thread = AudioRecorder()

    audio_thread.start()
    video_thread.start()

    return filename


def start_video_recording(filename):
    global video_thread

    video_thread = VideoRecorder()
    video_thread.start()

    return filename


def start_audio_recording(filename):
    global audio_thread

    audio_thread = AudioRecorder()
    audio_thread.start()

    return filename

def googleAI():
    print("TEST TEST")
    print(AudioRecorder.audio_filename)
    audio_file = "sample1.wav"

    r = sr.Recognizer()
    pp = pprint.PrettyPrinter(width=90, compact=True)

    AUDIO_FILE = (audio_file)
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.adjust_for_ambient_noise(source)
        audio = r.record(source)
        # read the entire audio file

    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        captured_text = r.recognize_google(audio)
        print("Google Speech Recognition transcribed your audio to 'captured_text' ")
        print("Google Speech Recognition thinks you said: \n \n ")
        pp.pprint(captured_text)

    except sr.UnknownValueError:
        pp.pprint("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        pp.pprint("Could not request results from Google Speech Recognition service; {0}".format(e))


def whisper():
    audio_file = "sample1.wav"
    model = load_model("base")
    result = model.transcribe(audio_file)
    print(result["text"])
    with open("audio_sample.txt", "w+") as f:
        f.write(result["text"])

def stop_AVrecording(filename):
    audio_thread.stop()
    frame_counts = video_thread.frame_counts
    elapsed_time = time.time() - video_thread.start_time
    recorded_fps = frame_counts / elapsed_time
    print("total frames " + str(frame_counts))
    print("elapsed time " + str(elapsed_time))
    print("recorded fps " + str(recorded_fps))
    video_thread.stop()
    whisper()
    # googleAI()

    # Makes sure the threads have finished
    # while threading.active_count() > 1:
    #     print(threading.active_count())
    #     print("STOP HERE")
    time.sleep(5)
    #     print("STOP after SLEEP")


    print("MERGE")
    #	 Merging audio and video signal

    if abs(recorded_fps - 6) >= 0.01:  # If the fps rate was higher/lower than expected, re-encode it to the expected

        print("Re-encoding")
        cmd = "ffmpeg -r " + str(recorded_fps) + " -i temp_video.avi -pix_fmt yuv420p -r 6 temp_video2.avi"
        subprocess.call(cmd, shell=True)

        print("Muxing")
        cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video2.avi -pix_fmt yuv420p " + filename + ".avi"
        subprocess.call(cmd, shell=True)

    else:

        print("Normal recording\nMuxing")
        cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video.avi -pix_fmt yuv420p " + filename + ".avi"
        subprocess.call(cmd, shell=True)

        print("..")


# Required and wanted processing of final files
def file_manager(filename):
    local_path = os.getcwd()

    if os.path.exists(str(local_path) + "/temp_audio.wav"):
        os.remove(str(local_path) + "/temp_audio.wav")

    if os.path.exists(str(local_path) + "/temp_video.avi"):
        os.remove(str(local_path) + "/temp_video.avi")

    if os.path.exists(str(local_path) + "/temp_video2.avi"):
        os.remove(str(local_path) + "/temp_video2.avi")

    if os.path.exists(str(local_path) + "/" + filename + ".avi"):
        os.remove(str(local_path) + "/" + filename + ".avi")


if __name__ == "__main__":
    filename = "Default_user"
    file_manager(filename)

    start_AVrecording(filename)

    time.sleep(30)

    stop_AVrecording(filename)
    print("Done")
