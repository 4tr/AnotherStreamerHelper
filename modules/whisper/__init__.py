# обязательный блок описания
__plugin__ = {
    "name": "Подслушивалка Whisper",
    "description": "STT whisper", 
    "type": "test" ,
    "autorun":True, # на данный момент используется как команда к загрузке модуля (пока нет других настроек заменяющее это)
    "first_load": False, # в данном случае я указал False чтобы этот модуль загрузился позже и гарантировать что хук который о триггернет при запуске уже был задействован первым тестовым модулем 
    "run_mode": 1 #0 - standart,  1 - thread, 2 - multiprocessing    
}

from data import app_data
import whisper
import torch
import sounddevice as sd
import numpy as np

SAMPLE_RATE = 16000
BLOCK_DURATION = 5  # секунд
# Custom static data

def record_and_transcribe():
    model = whisper.load_model("large")  # можно tiny, medium и т.д.
    while True:
        audio = sd.rec(int(SAMPLE_RATE * BLOCK_DURATION), samplerate=SAMPLE_RATE, channels=1, dtype=np.float32)
        sd.wait()
        audio = np.squeeze(audio)
        #print("Processing...")
        result = model.transcribe(audio, fp16=torch.cuda.is_available())
        parts= {"name": "Whisper", "id": "Whisper", "pl" : "l", "t" : "2025-09-07T23:53:27.303543+00:00", "a" : "static/img/whisper.png", "msg" : ""}
        parts["msg"]=result["text"].strip()
        if len(parts["msg"]) > 0:
            print("["+__name__+"]",parts["msg"])
            app_data.add_com(parts)
def run():  
    record_and_transcribe()    
# пока не используется но обязательно***
def save():    
    print("сохранение")
# пока не используется но обязательно***
def load():
    print("загрузка") 
    

