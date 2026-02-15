import threading
import multiprocessing
import os
import sys
import time
import json
os.environ['HF_HOME'] = os.getcwd() + "/cache/huggingface"
os.environ["XDG_CACHE_HOME"] = os.getcwd() + "/cache/venv"





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
            "Console" :{"name": "Console", "id": "Console", "pl" : "lo", "t" : "2025-09-07T23:53:27.303543+00:00", "a" : "static/img/console.png", "msg" : ""},
            "AI" : {"name": "AI", "id": "AI", "pl" : "lo", "t" : "2025-09-07T23:53:27.303543+00:00", "a" : "static/img/AI.png", "msg" : ""},
            "Bot" : {"name": "Bot", "id": "Bot", "pl" : "lo", "t" : "2025-09-07T23:53:27.303543+00:00", "a" : "static/img/Bot.png", "msg" : ""}
        }
        #fixme
        self.com_Platforms ={
            "lo":{"label":"Local"    ,"color":9},
            "yt":{"label":"Youtube"  ,"color":10},
            "tw":{"label":"Twitch"   ,"color":6},
            "ERR":{"label":"???"   ,"color":2}
        }
        # список элементов в сообщении чата
        self.com_keys = ["name", "id", "pl", "t", "a","msg"]
        
    def col(self,txt = "" ,color = 0, worker = 0,color2 =0):
        #fixme syst = 0 - linux
        #worker 0 - begin+txt+end code ( end standart)
        #worker 1 - only begin code + txt 
        #worker 2 - txt+end code (end code = color )
         
        syst = 0
        color = str(color)
        color2 = str(color2)
        linux_colors = {
            "0" :{"label":"Стандартный",                  "text_code":"\033[0;39m","bg_code":"\033[49m"},
            "1" :{"label":"Чёрный",                       "text_code":"\033[0;30m","bg_code":"\033[40m"},
            "2" :{"label":"Тёмно-красный",                "text_code":"\033[0;31m","bg_code":"\033[41m"},
            "3" :{"label":"Тёмно-зелёный",                "text_code":"\033[0;32m","bg_code":"\033[42m"},
            "4" :{"label":"Тёмно-жёлтый «Оранжевый»",     "text_code":"\033[0;33m","bg_code":"\033[43m"},
            "5" :{"label":"Тёмно-синий",                  "text_code":"\033[0;34m","bg_code":"\033[44m"},
            "6" :{"label":"Темно-пурпурный",              "text_code":"\033[0;35m","bg_code":"\033[45m"},
            "7" :{"label":"Тёмно-голубой",                "text_code":"\033[0;36m","bg_code":"\033[46m"},
            "8" :{"label":"Светло-серый",                 "text_code":"\033[0;37m","bg_code":"\033[47m"},
            "9" :{"label":"Тёмно-серый",                  "text_code":"\033[1;90m","bg_code":"\033[100m"},
            "10":{"label":"Красный",                      "text_code":"\033[1;91m","bg_code":"\033[101m"},
            "11":{"label":"Зелёный",                      "text_code":"\033[1;92m","bg_code":"\033[101m"},
            "12":{"label":"Оранжевый",                    "text_code":"\033[1;93m","bg_code":"\033[103m"},
            "13":{"label":"Синий",                        "text_code":"\033[1;94m","bg_code":"\033[104m"},
            "14":{"label":"Пурпурный",                    "text_code":"\033[1;95m","bg_code":"\033[105m"},
            "15":{"label":"Голубой",                      "text_code":"\033[1;96m","bg_code":"\033[106m"},
            "16":{"label":"Белый",                        "text_code":"\033[1;97m","bg_code":"\033[107m"},
        }
        arr = linux_colors.copy()      
        
        #fixme shindows
        if worker == 0:
            return arr[color]['text_code'] + arr[color2]['bg_code'] + txt +  arr["0"]['text_code'] + arr["0"]['bg_code']
            #return arr[color]['text_code'] + txt + arr["0"]['text_code']
            
        if worker == 1:
            return arr[color]['text_code'] + txt
        if worker == 0:
            return txt + arr[color]['text_code']
    #fixme шинда*  
    def plat_decorator(self,pl = "ERR"):        
        plat = self.com_Platforms.get(pl,self.com_Platforms["ERR"])
        return self.col(str("["+plat['label']+"]"),plat["color"])    
        
    def get_config_v2(self, module_name , cfg_name = "default", full_data = False):
        cfg = self.get_cfg(module_name,cfg_name)    
        if cfg == None:
            return cfg
        ret = {}
        if full_data:
            return cfg
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
    
    def save_cfg(self, module_name , cfg, cfg_name = "default",save = 0): 
        name,file= self.cfg_predata(module_name,cfg_name)
        # первым делом залью то что попросили в файл
        if not os.path.exists(os.path.dirname(file)):
            # Создаем папку
            os.makedirs(os.path.dirname(file))
            
        with open(file, "w") as fc:
            json.dump(cfg, fc, indent=2)
            fc.close()
        #print("[core]["+name+"] save " + file)
        # теперь для основных потоков обновить данные внутри модулей в переменной __cfg__
        if save == 0:
            if module_name != "CORE":
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
            if module_name != "CORE":
                mo = self.modules.get(name,None)
                if mo != None:
                    mod = self.modules[name]["module"]                    
                    ret = getattr(mod, "__cfg__", None)
                else:
                    ret = None    
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
        if msg["msg"] == "":
            return
        #print("[pre HOOK]",msg['msg'])    
        if msg.get("clear_msg",None) == None:
            msg["clear_msg"]=msg["msg"]    
        #add system messages    
        if uid == None:        
            params = msg.copy()
        else:
            if (uid != "AI") and (uid != "Bot") and (uid != "Console"):
                return
            
            params = self.com_Prep[uid].copy()
            params['msg']=str(msg['msg'])
            params["clear_msg"]=str(msg["msg"])
        
        
        
        self.hook("add_com",params)
        #print('---')
        #print(params)
        self.hook("add_com_last",params)
        params["nn"]=len(self.com) 
        #print("[post HOOK]",msg['msg'])        
        print(self.plat_decorator(params['pl'])," ", params['name'] ,": " ,params['clear_msg'])    
        
                  
        
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
            #print(self)       
            
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
            #print(msg)
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






