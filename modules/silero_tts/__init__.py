




# обязательный блок описания
__plugin__ = {
    "name": "Говорилка Silero",
    "description": "TTS Silero", 
    "type": "test" ,
    "autorun":False, # на данный момент используется как команда к загрузке модуля (пока нет других настроек заменяющее это)
    "first_load": False, # в данном случае я указал False чтобы этот модуль загрузился позже и гарантировать что хук который о триггернет при запуске уже был задействован первым тестовым модулем 
    "run_mode": 0 #0 - standart,  1 - thread, 2 - multiprocessing    
}

from data import app_data

import os
import torch
import subprocess
sample_rate = 48000

device = torch.device('cpu')
torch.set_num_threads(4)
mod_dir = os.path.dirname(os.path.realpath(__file__))
local_file = mod_dir + '/models/v4_ru.pt'
#if not os.path.isfile(local_file):
#    torch.hub.download_url_to_file('https://models.silero.ai/models/tts/en/v3_en.pt',
#                                   local_file)  
model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)
class hook:
    def add_com_last(data):
        tempGovorilda(data)
    
    
def tempGovorilda(data):
    govorilda(text = data["translate"], voice_path = data["id"]) 
        
def demonFFplay(music, printed = 1, user = ""):    
    #subprocess.Popen(["ffplay", "-af", "volume=0.3", "-autoexit", music ],
    if printed == 1:
        print("проигрываю :" + music)
        subprocess.Popen(["ffplay", "-nodisp", "-autoexit", music ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True)
    if printed == 0:
        #bC = "ffplay -nodisp -autoexit -loglevel info " + music
        bC = "ffplay -loglevel info -nodisp -autoexit '" + music + "' 2>&1 | grep -E 'Stream|Duration|M-A'"
        os.system(bC)
    if printed == 2:
        bC = "ffplay -loglevel fatal -nodisp -autoexit '" + music + "'"
        os.system(bC)



def govorilda(text,
              ssml_text=None,
              speaker: str = 'random',
              audio_path: str = '',
              sample_rate: int = 48000,
              put_accent=True,
              put_yo=True,
              voice_path=None):
    if not audio_path:
        audio_path = mod_dir + '/wav/text.wav'
    
    if voice_path != None:        
        voice_path = mod_dir + "/voices/" + voice_path
        if not os.path.isfile(voice_path):            
            random_emb = torch.randn(2, model.emb_dim, requires_grad=False).to(model.device)
            model.random_emb = random_emb
            model.save_random_voice(voice_path)  
            
    audio = model.apply_tts( text=text,
                            ssml_text=ssml_text,
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_yo=put_yo,
                            put_accent=put_accent,
                            voice_path=voice_path)
    model.write_wave(path=audio_path,
        audio=(audio * 32767).numpy().astype('int16'),
        sample_rate=sample_rate)
    demonFFplay(audio_path,0,voice_path)
    #audio_paths = model.save_wav(text=example_text,
    #                         speaker=speaker,
    #                         sample_rate=sample_rate,
    #                         audio_path=audio_path)

    
def run():  
    print("пуньк среньк")  
    #govorilda(text = "швабра кадабра", voice_path = "test_golosilda") 
    #govorilda(text = "тумба юмба", voice_path = "test_golosilda") 
    #govorilda(text = "КаТэ когда дид? когда когда когда когда когда когда ", voice_path = "test2") 
    #exit()
# пока не используется но обязательно***
def save():    
    print("сохранение")
# пока не используется но обязательно***
def load():
    print("загрузка") 
    


