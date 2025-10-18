




# обязательный блок описания
__plugin__ = {
    "name": "Говорилка Silero",
    "description": "TTS Silero", 
    "type": "test" ,
    "autorun":True, # на данный момент используется как команда к загрузке модуля (пока нет других настроек заменяющее это)
    "first_load": False, # в данном случае я указал False чтобы этот модуль загрузился позже и гарантировать что хук который о триггернет при запуске уже был задействован первым тестовым модулем 
    "run_mode": 0 #0 - standart,  1 - thread, 2 - multiprocessing    
}

from data import app_data

import os
import torch
sample_rate = 48000

device = torch.device('cpu')
torch.set_num_threads(4)
local_file = 'v3_en.pt'
#if not os.path.isfile(local_file):
#    torch.hub.download_url_to_file('https://models.silero.ai/models/tts/en/v3_en.pt',
#                                   local_file)  
model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)

def govorilda(example_text,audio_path = 'cache/silero/text.wav'):
    speaker='random'

    audio_paths = model.save_wav(text=example_text,
                             speaker=speaker,
                             sample_rate=sample_rate,
                             audio_path=audio_path)

    
def run():  
    print("kek")    
# пока не используется но обязательно***
def save():    
    print("сохранение")
# пока не используется но обязательно***
def load():
    print("загрузка") 
    


