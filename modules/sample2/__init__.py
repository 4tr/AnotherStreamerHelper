# обязательный блок описания
__plugin__ = {
    "name": "sample2 module(directory)",
    "description": "пример минимального кода для модуля в виде папки", 
    "type": "test" ,
    "autorun":True, # на данный момент используется как команда к загрузке модуля (пока нет других настроек заменяющее это)
    "first_load": False, # в данном случае я указал False чтобы этот модуль загрузился позже и гарантировать что хук который о триггернет при запуске уже был задействован первым тестовым модулем 
    "run_mode": 0 #0 - standart,  1 - thread, 2 - multiprocessing    
}

__cfg__ ={
    "default" : {
        "channel": {
            "label": "описание параментра",
            "name": "channel",
            "type": "text",
            "value": "ЫЫЫЫЫ"
        }  
    }
}

# не обязательно, но необходимо для того чтобы предоставить другим модулям "точку входа" в виде хуков
from data import app_data
import os
ho = app_data.hook

class hook:
    def test_hook_one(data):        
        print("Привет из хука test_hook_one тестового модуля2 ", data)
        return # !!! ВАЖНО указать в каждой функции хука. если вывод не писать хук будет забракован при загрузке
    def test_hook_two(data):        
        print("Привет из хука test_hook_two тестового модуля2 ", data)
        return # !!! ВАЖНО указать в каждой функции хука. если вывод не писать хук будет забракован при загрузке

print("__________________________",__name__ ,"__________")        
# запускается после помещения модуля в список загруженных модулей (приложения) 
def run():  
    print(os.path.dirname(os.path.realpath(__file__)))
    print(__file__)
    
    
    
   
    cfg = app_data.get_cfg(__name__)
    #print(cfg)
    #exit()
      
    print("["+__name__.split(".")[-1]+"] OK")    
    print(" а теперь чтобы окончателно запутать тебя ")    
    text = "---данные с модуля2---"
    print("запускается хук : test_hook_one из модуля2 ")
    ho("test_hook_one",text)
    print("запускается хук : test_hook_two из модуля2 ")
    ho("test_hook_two",text)    
    print("["+__name__.split(".")[-1]+"] завершил работу функции запуска")    
    
    

# пока не используется но обязательно***
def save():
    print("сохранение")

# пока не используется но обязательно***
def load():
    print("загрузка") 
    


