import threading
import multiprocessing
import os
import sys
import time
import json
os.environ['HF_HOME'] = os.getcwd() + "/cache/huggingface"






class AppData:
    def __init__(self):
        self.com_queue = multiprocessing.Queue()
        self.com = [] # помойка комментариев
        self.stop = False
        self._lock = threading.Lock()  # блокируем доступ для потокобезопасности
        self.value = 0
        self.messages = []
        self.module_dir = "modules"
        self.required_funcs = ["run", "save", "load"]
        self.modules = {}
        self.threads = {}
        self.multiprocess = {}
        self.hooks = {}
        self.updmarker = {"__upd__": {
                                "label": "маркер обновленной конфигурапции",
                                "name": "__upd__",                                
                                "type": "h_bool",
                                "value": True
                            } 
                          }
        # шаблоны для чата для консоли и нейронки
        self.com_Prep = {
            "Console" :{"name": "Console", "id": "Console", "pl" : "l", "t" : "2025-09-07T23:53:27.303543+00:00", "a" : "static/img/console.png", "msg" : ""},
            "AI" : {"name": "AI", "id": "AI", "pl" : "l", "t" : "2025-09-07T23:53:27.303543+00:00", "a" : "static/img/AI.png", "msg" : ""},
            "Bot" : {"name": "Bot", "id": "Bot", "pl" : "l", "t" : "2025-09-07T23:53:27.303543+00:00", "a" : "static/img/Bot.png", "msg" : ""}
        }
        # список элементов в сообщении чата
        self.com_keys = ["name", "id", "pl", "t", "a","msg"]
    def get_config_v2(self, module_name , cfg_name = "default"):
        cfg = self.get_cfg(module_name,cfg_name)    
        if cfg == None:
            return cfg
        ret = {}
        for i in cfg:
            ret[i]=cfg[i]['value']
        return ret    
    
    def cfg_predata(self, module_name , cfg_name = "default"):
        ret = {}
        #print("------------------------------",module_name)
        ret["name"] = module_name.replace(self.module_dir + ".","")
        #print("------------------------------",ret["name"])
        
        #otn = module_name.replace(".","/")
        otn = self.module_dir + "/" + ret["name"]
        t = __file__.split("/")
        root = '/'.join(t[:len(t)-1])
        addr = root+"/"+otn
        work_dir =root + "/" + self.module_dir
        f_cfg_name = cfg_name
        if os.path.isdir(addr):
            work_dir=addr + "/cfg"         
        else:            
            f_cfg_name = ret["name"] + "_" + cfg_name
        ret["file"] = work_dir + "/" + f_cfg_name + ".json"
        return ret["name"],ret["file"]      
    
    def save_cfg(self, module_name , cfg, cfg_name = "default"): 
        name,file= self.cfg_predata(module_name,cfg_name)
        # первым делом залью то что попросили в файл
        with open(file, "w") as fc:
            json.dump(cfg, fc, indent=2)
            fc.close()
        #print("[core]["+name+"] save " + file)
        # теперь для основных потоков обновить данные внутри модулей в переменной __cfg__
        mod = self.modules[module_name]
        if (mod["info"]["run_mode"] < 2): # прямое выполение или поток
            try:
                mod['module'].__cfg__[cfg_name]=cfg
                mod['module'].__cfg__[cfg_name]=self.updmarker["__upd__"]
                
            except Exception as e:  
                print("[CFG ",module_name,"] Error ",e)      
        #это очень сырой вариант и тут очень много всего доделывать предстоит
        
    def get_cfg(self, module_name , cfg_name = "default"):
        ## todo костыль с точками. нужно получать иначе
        name,file= self.cfg_predata(module_name,cfg_name)
        #print("FILE - ", file)    
        #if os.path.exists(file):        
        if os.path.isfile(file):
            with open(file, "r") as f:
                cfg = json.load(f)
                f.close()
            return cfg  
        else:
            mod = self.modules[name]["module"]
            ret = getattr(mod, "__cfg__", None)
            if ret == None: 
                print("[",name,"] not cfg file and class 0_o return None")
            else:
                ret = ret.get(cfg_name, None)
                if  ret == None: 
                    print("[",name,"] not find [",cfg_name,"] in cfg class 0_о")
                else:
                    return ret
                                       
        return None
    def queue_process_messages(self):
        """Обрабатывает входящие данные из очереди."""
        while True:
            msg = self.com_queue.get()
            if msg is None:
                break
            #print(f"[QUEUE] {msg['name']}: {msg['msg']}")
            self.add_com(msg)
    
    def add_com(self,msg, uid = None):
        #print("[pre HOOK]",msg['msg'])        
        self.hook("add_com",msg)
        #print("[post HOOK]",msg['msg'])
        
        if uid == None:        
            params = msg.copy()
        else:
            if (uid != "AI") and (uid != "Bot") and (uid != "Console"):
                return
            params = self.comPrep[uid].copy()
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
        try:
            a = self.hooks.get(hook_name,{})        
            for v in a:
                a[v](*args, **kwargs)
        except Exception as e:  
            print("[HOOK ",hook_name,"] Error ",e)        
            
    def add_threads(self, func, name):
        t = threading.Thread(target=func, daemon=True)
        t.start()
        self.threads[name]=t
            
    def add_multiprocess(self, func, name):
        #t = multiprocessing.Process(target=func, daemon=True)
        com_queue=self.com_queue
        t = multiprocessing.Process(target=func, daemon=True , args=(com_queue,))
        t.start()
        self.multiprocess[name]=t
        
    def get_process_module(self,module_name):
        m = self.modules[module_name]
        if m['info']['run_mode'] == 1:
            return self.threads[module_name]
        if m['info']['run_mode'] == 2:
            return self.multiprocess[module_name]
        if m['info']['run_mode'] == 0:
            return None
        
        
                
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

# запускаем в потоке нюхатель очереди queue обеспечивающий обмен данными 
print('[queue_com] подготовка')
threading.Thread(target=app_data.queue_process_messages, daemon=True).start()
print('[queue_com] OK')






