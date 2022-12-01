import speech_recognition as sr
import pprint
from txtai.pipeline import Transcription
import whisper
from whisper import load_model
audio_file = "sample1.wav"


def whisper():
    model = load_model("base")
    result = model.transcribe(audio_file)
    print(result["text"])
    with open("audio_sample.txt", "w+") as f:
        f.write(result["text"])


#files = [audio_file]
def googleAI():
    r = sr.Recognizer()
    pp = pprint.PrettyPrinter(width=90, compact=True)

    AUDIO_FILE = (audio_file)
    r = sr.Recognizer()
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


whisper()
googleAI()
#
# transcribe = Transcription()
# transcribe = Transcription("openai/whisper-base")
# for text in transcribe(files):
#   print("Whisper AI transcribed your recording successfully")
#   captured_text1 = text
# pp = pprint.PrettyPrinter(width=90, compact=True)
#
# print("Whisper AI thinks you said: \n \n ")
#
# pp.pprint(captured_text1)