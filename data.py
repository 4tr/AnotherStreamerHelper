import threading
import os
os.environ['HF_HOME'] = os.getcwd() + "/cache/huggingface"




class AppData:
    def __init__(self):
        self.com = [] # помойка комментариев
        self.stop = False
        self._lock = threading.Lock()  # блокируем доступ для потокобезопасности
        self.value = 0
        self.messages = []
        self.module_dir = "modules"
        self.required_funcs = ["run", "save", "load"]
        self.modules = {}
        self.threads = {}
        self.hooks = {}
        # шаблоны для чата для консоли и нейронки
        self.com_Prep = {
            "Console" :{"name": "Console", "id": "Console", "pl" : "l", "t" : "2025-09-07T23:53:27.303543+00:00", "a" : "static/img/console.png", "msg" : ""},
            "AI" : {"name": "AI", "id": "AI", "pl" : "l", "t" : "2025-09-07T23:53:27.303543+00:00", "a" : "static/img/AI.png", "msg" : ""},
            "Bot" : {"name": "Bot", "id": "Bot", "pl" : "l", "t" : "2025-09-07T23:53:27.303543+00:00", "a" : "static/img/Bot.png", "msg" : ""}
        }
        # список элементов в сообщении чата
        self.com_keys = ["name", "id", "pl", "t", "a","msg"]
    
    def add_com(self,msg, uid = None):
        
        if uid == None:        
            params = msg.copy()
        else:
            if (uid != "AI") and (uid != "Bot") and (uid != "Console"):
                return
            params = comPrep[uid].copy()
            params['msg']=str(msg[msg])
        
        params["nn"]=len(self.com)           
        
        # чекнуть пользователя *** 
                
        self.com.append(params)    
    
    def add_hook(self, name_hook, hookfunc , modulename):
        #print("[",modulename,"] добавление хука ", name_hook)
        try:
            tmp = type(self.hooks[name_hook])
        except KeyError:
            self.hooks[name_hook] = {}        
        self.hooks[name_hook][modulename]=hookfunc
        
    def hook(self, hook_name,*args, **kwargs):
        a = self.hooks.get(hook_name,{})        
        for v in a:
            a[v](*args, **kwargs)
            
    def add_threads(self, func, name):
        t = threading.Thread(target=func, daemon=True)
        t.start()
        self.threads[name]=t
            
    def add_mod(self, mod):
        with self._lock:  
            self.modules[mod['name']]=mod
            
    def mod(self, name, full = False):
        with self._lock:  
            if full:
                return self.modules[name]    
            else:
                return self.modules[name].module
            
    def add_message(self, msg: str):
        with self._lock:  
            print(msg)
            self.messages.append(msg)

    def get_messages(self):
        with self._lock:
            return list(self.messages)  # возвращаем копию

# создаём глобальный объект
app_data = AppData()








