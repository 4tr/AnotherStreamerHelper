__plugin__ = {
    "name": "AI Translator",
    "description": "nllb-200 переводчик",
    "type": "text_modificator" ,
    "run_mode": 0, #0 - standart,  1 - thread, 2 - multiprocessing    
    "first_load": True,
    "autorun": False
}

from transformers import pipeline
from langdetect import detect
import torch #нужно для автоустановки зависимостей при запуске модуля!!!

class AiTr:
    def __init__(self):
        #self._lock = threading.Lock()  # блокируем доступ для потокобезопасности
        self.translator = pipeline(
            task="translation",
            model="facebook/nllb-200-distilled-600M",   
            tgt_lang="rus_Cyrl",
            #device=0  # если есть GPU
        )     
        
    def translate(self, msg):
        
        #with self._lock: 
            src = str(detect(msg["clear_msg"]))  # вернёт 'fr'
            #print("SRC:",src)
            if src == "ru":
                msg["translate"] = "[" + src + "] " + msg["clear_msg"]
                return
            lang_map = {
                "en": "eng_Latn",
                "ru": "rus_Cyrl",
                "fr": "fra_Latn",
                "de": "deu_Latn",
                "es": "spa_Latn",
                # добавь нужные
            }
            
            src_lang = lang_map.get(src, "eng_Latn")
            #print("SRC_LANG:",src_lang)
            
            tr= self.translator(str(msg["clear_msg"]),src_lang=src_lang)
            #print("[AI translate] ", tr[0]["translation_text"])
            msg["translate"] = "[" + src + "] " +tr[0]["translation_text"]
            print("[HOOK translate]",msg["translate"])
            
aitr=AiTr();  
 
class hook:
    def add_com(data):
        aitr.translate(data)
    #def test_text_modificator(data):
    #    return "[HOOK]" + data
    
def run():
    print("["+__name__.split(".")[-1]+"] OK")     

def save():
    print("Привет из testm")

def load():
    print("Привет из testm")


