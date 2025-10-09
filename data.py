import threading
import os
os.environ['HF_HOME'] = os.getcwd() + "/cache/huggingface"

class AppData:
    def __init__(self):
        self.stop = False
        self._lock = threading.Lock()  # блокируем доступ для потокобезопасности
        self.value = 0
        self.messages = []
        self.module_dir = "modules"
        self.required_funcs = ["run", "save", "load"]
        self.modules = {}
        self.threads = {}
        self.hooks = {}
    
    def add_hook(self, name_hook, hookfunc , modulename):
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








