# обязательный блок описания
__plugin__ = {
    "name": "OBSRC",
    "description": "OBS Remote Control", 
    "type": "test" ,
    "autorun":False, # на данный момент используется как команда к загрузке модуля (пока нет других настроек заменяющее это)
    "first_load": True, # в данном случае я указал False чтобы этот модуль загрузился позже и гарантировать что хук который о триггернет при запуске уже был задействован первым тестовым модулем 
    "run_mode": 0 , #0 - standart,  1 - thread, 2 - multiprocessing  
    "requirements": ['obs-websocket-py']  
}

__cfg__ ={
    "default" : {
        "IP": {
            "label": "IP",
            "name": "IP",
            "type": "text",
            "value": "127.0.0.1"
        },
        "PORT": {
            "label": "port",
            "name": "PORT",
            "type": "text",
            "value": "4455"
        },
        "password": {
            "label": "password",
            "name": "password",
            "type": "password",
            "value": "****"
        }  
    }
}
# obs-websocket-py
# install('obs-websocket-py') 
from obswebsocket import obsws, requests, events

# не обязательно, но необходимо для того чтобы предоставить другим модулям "точку входа" в виде хуков
from data import app_data
import os
ho = app_data.hook

class hook:
    def test(data):        
        print("Привет из хука test_hook_one тестового модуля2 ", data)
        
def on_event(message):
    print("Got message: {}".format(message))


def on_switch(message):
    print("You changed the scene to {}".format(message.getSceneName()))
    
import sys
import time    
# запускается после помещения модуля в список загруженных модулей (приложения) 
def run():  
    cfg = app_data.get_config_v2(__name__)  
    
    ws = obsws(cfg["IP"], int(cfg['PORT']), cfg['password'])
    ws.connect()

    # Получить список сцен
   # scenes = ws.call(requests.GetSceneList())
    #print("высрато ",scenes)
    #for v in scenes.__dict__.items():
    #    print(v)
   # for v in scenes.datain:
   #     print(v)
  
    try:
        scenes = ws.call(requests.GetSceneList())
        for s in scenes.getScenes():
            name = s['sceneName']
            print("Switching to {}".format(name))
            ws.call(requests.SetCurrentProgramScene(sceneName=name))
            time.sleep(2)

        print("End of list")

    except KeyboardInterrupt:
        pass

    ws.disconnect()
    
  
    print("["+__name__.split(".")[-1]+"] завершил работу функции запуска")    
    
# пока не используется но обязательно***
def save():
    print("сохранение")

# пока не используется но обязательно***
def load():
    print("загрузка") 
    


