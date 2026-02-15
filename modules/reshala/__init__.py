# обязательный блок описания
__plugin__ = {
    "name": "Модуль принятия решений",
    "description": "Добавляет активности исходя из сообщений чата",
    "type": "test" ,
    "autorun":False, #игнорируется*** заменен на конфиг настраиваемый с консоли при запуске
    "first_load": False, # переносит модуль в список загружаемых в первую очередь
    "run_mode": 1 #0 - standart,  1 - thread, 2 - multiprocessing    
}

import subprocess
import socket
import json
import time
import threading
import itertools
import urllib.request
from data import app_data
ho = app_data.hook
import os

mod_dir = os.path.dirname(os.path.realpath(__file__))
effect_dir = mod_dir + "/effects/"
md_mus = mod_dir + "/modarchive_music/"

VLC_HOST=str("127.0.0.1")
VLC_PORT=int("4444")
VLC_HTTP_PORT="4040"
VLC_PASSWORD=str("")
  # если задан пароль VLC --rc-password=тут
  
class MPVClient:    
    def openMPV(self,socket_path):
        print('INIT MPV reload')
        subprocess.Popen(["mpv", "--player-operation-mode=pseudo-gui", "--idle=yes", str("--input-ipc-server=" + socket_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True)  
        print('Connect MPV')
        time.sleep(2)
        #self.sock = socket.socket(socket.AF_UNIX)         
        self.sock.connect(socket_path)    
    
    def __init__(self, socket_path="/tmp/mpvsocket"):
        self.sock = socket.socket(socket.AF_UNIX)
        try:
            print('Connect MPV')           
            self.sock.connect(socket_path)
        except ConnectionRefusedError:
            self.openMPV(socket_path)
        except FileNotFoundError:    
            self.openMPV(socket_path)            
            
        self.sock.setblocking(True)

        self._req_id = itertools.count(1)
        self._responses = {}
        self._events = []

        self._lock = threading.Lock()

        self._reader = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader.start()
        ##
        self._condition = threading.Condition()
    def is_idle(self):
        return self.command("get_property", "idle-active")['data']
    def is_pause(self):  
        return self.command("get_property","pause")['data']    
    def run_play(self):
        return self.command("set_property","pause",False)            
    def run_init(self):
        return self.command("set_property","idle-active",False)            
        
    def _reader_loop(self):
        buffer = b""

        while True:
            chunk = self.sock.recv(4096)
            if not chunk:
                break

            buffer += chunk

            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)

                if not line.strip():
                    continue

                msg = json.loads(line.decode())
                #print("=)",msg)
                if "request_id" in msg:
                    with self._condition:  
                        self._responses[msg["request_id"]] = msg
                        self._condition.notify_all()                    
                    
                elif "event" in msg:
                    #print(" ")
                    with self._condition:
                        self._events.append(msg)
                        self._condition.notify_all()
                else:
                    #print('LOL ELSE')
                    with self._condition:
                        self._condition.notify_all()
                        

    def command_body(self, *args):
        req_id = next(self._req_id)
        
        msg = {
            "command": list(args),
            "request_id": req_id
        }        
        #print("=0",msg)
        with self._lock:                
            self.sock.send((json.dumps(msg) + "\n").encode())                            
        with self._condition:
            ok = self._condition.wait_for(lambda: req_id in self._responses,timeout=1)
            if not ok:
                raise TimeoutError("mpv did not respond")
        return req_id    
        
    def command(self, *args): 
        try:
            req_id =self.command_body(*args)
        except Exception as e:              
            self.__init__()
            req_id =self.command_body(*args)
            
        return self._responses.pop(req_id)
       
    def play(self):    
        self.run_play()    
        #return self.command("loadfile", file)
    def volume(self,int = 50):
        return self.command("set_property", "volume",int)
    def pause(self):
        if self.is_idle(): return
        return self.command("cycle", "pause")

    def stop(self):
        if self.is_idle(): return        
        ret = self.command("set_property","pause",True) 
        MPV.command("set_property", "time-pos",0)
        return ret
        #return self.command("stop")

    def next(self):
        if self.is_idle(): return       
        ret = self.command("playlist-next")    
        if self.is_pause(): self.run_play()
        return ret  
        
    def prev(self):  
        if self.is_idle(): return
        ret =  self.command("playlist-prev")
        if self.is_pause(): self.run_play() 
        return ret
        
    def playlist(self):        
        return self.command("get_property", "playlist")

    def sr_add(self,file):
        if self.is_idle(): 
            self.command("loadfile", file)
            self.volume(30)
        else:
            self.command("loadfile", file, "append")
        playlist = self.command("get_property", "playlist")["data"]        
        pos = len(playlist) - 1
        current_pos = next(i for i, item in enumerate(playlist) if item.get("current"))
        ret = self.command("playlist-move",pos,current_pos + 1)
        if self.is_pause(): 
            self.next()            
        return ret
        
            
        
        
    def track_title(self):
        playlist = self.command("get_property", "playlist")["data"]
        return next(item for i, item in enumerate(playlist) if item.get("current")).get("title")
                    
MPV = MPVClient()  
  
def demonFFplay(music, printed = 1, user = ""):
    #print("[FFPLAY]" + music)    
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

#доп функция отправки команд vlc
def send_command(sock, cmd):
    sock.sendall((cmd + '\n').encode('utf-8'))
    time.sleep(0.1)  # дать VLC время ответить
    response = sock.recv(4096).decode('utf-8')
    return response

        
# основная функция отправки команд VLC
def vlc_cmd(comm , other = ""):
    global VLC_HOST
    global VLC_PORT
    global VLC_HTTP_PORT
    global VLC_PASSWORD
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((VLC_HOST, VLC_PORT))
        except ConnectionRefusedError:
            subprocess.Popen(["vlc","--extraintf", "rc", "--rc-host=" + VLC_HOST + ":" + str(VLC_PORT)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True)      
            print('Кто-то забыл запустить плеер. но не беда. ща все будет')
            time.sleep(2)
            s.connect((VLC_HOST, VLC_PORT))
            
        delete=s.recv(4096).decode('utf-8')
        
        if VLC_PASSWORD:
            s.sendall((VLC_PASSWORD + '\n').encode('utf-8'))
            time.sleep(0.1)
            delete=s.recv(4096).decode('utf-8')
  
        if comm == "enqueue":
            ret =send_command(s, "status")
            #print(ret)
            if ret.split(" state ")[1].split(" ")[0] == "stopped":
                comm = "add"
        #print(send_command(s, comm + " " + other))
        send_command(s, comm + " " + other)
        
#проверка с конвертацией в целое
def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
#скачивание и запуск музыки с мдархив
def play_all_downloads_MD():
    files = [f for f in os.listdir(md_mus) if os.path.isfile(os.path.join(md_mus, f))]
    for f in files:
        ff = md_mus + f
        result = subprocess.run(
            ["file", "-b" ,ff],      # команда как список
            capture_output=True,       # захват stdout и stderr
            text=True                  # вывод как строка (не bytes)
        )
        output = result.stdout.strip()        
        print("add vlc playlist '",output,"'")
        MPV.sr_add(ff)
        #vlc_cmd('enqueue',ff)
    print("Готово!")

def play_music_md(music_id):
    mid=safe_int(music_id)
    url = 'https://api.modarchive.org/downloads.php?moduleid=' + str(mid)  # URL до файла
    
    save_path = md_mus + str(mid)     
    if os.path.isfile(save_path):
        if os.path.getsize(save_path) < 20: 
            print("Нет такой музыки!!")
            return    
    else:
        #print("Качаю музяку")
        #if not os.path.isdir(md_mus):
        if not os.path.exists(md_mus):            
            os.makedirs(md_mus)
            
        urllib.request.urlretrieve(url, save_path)
    MPV.sr_add(save_path)    
    #vlc_cmd('enqueue',save_path)   
        
def analizv3(data):
    
    preffect=""    
    match data['id']:
        case "Console":
            preffect="console.mp3"
        case "AI":
            preffect="r2d2.mp3"
        case "Bot":
            preffect="bot.mp3"
        case _:
            preffect="radio.mp3"
        
            
    msg = data['msg']
    spl = msg.split(" ")
    if spl[0] == "!sova" :
        demonFFplay(effect_dir + "ammo_pickup.mp3",2)
        #влупить весь скачанный контент ранее
        play_all_downloads_MD()        
    elif data['msg'] == "!help" :        
        txt = "!info - данные о текущем треке; !sr num заказать музыку с modarchive.org; !newVoice сгенерировать себе новый голос; говорилка текст - спросить у говорилки что-то; !volume !prev !stop !pause !play управление плеером; ну и еще некотрые функции."
        print(txt)
        #app_data.add_com('text',"Console")
        #app_data.add_com(msg=txt,uid="Bot")
    elif spl[0] == "!sr" :
        if safe_int(spl[1]) != 0 :
            # я заказал музыку
            demonFFplay(effect_dir + "ammo_pickup.mp3",2)
            #govorilda("я заказал музыку! слушаем все!",data.snippet.author_channel_id)
            play_music_md(spl[1])
        return    
    elif spl[0] == "!newVoice":
        if data != None:
            ho("govorilka_deletevoice",data["id"])
            temp = data.copy()
            demonFFplay(effect_dir + preffect,2)
            temp["msg"]="Сменил голос. Один два три... тест."
            ho("govorilka",data)                                    
    elif spl[0] == "говорилка":
            tmp = spl
            del tmp[0]
            print(tmp)
            a = " ".join(map(str, tmp))  
            print(a)
            del tmp   
            #if (cfget("AI") == True):
            #    try:
            #        r = aiReq(a)                             
            #    except requests.exceptions.ConnectionError:
            #        r = "у меня обед! атыбытэс!"
            #    govorilda(text,userid)
            #    print("----------------------------------------------------")
            #    print("--------------говорилка отвечает--------------------")
            #    print("----------------------------------------------------")
            #    print(r)
            #    print("----------------------------------------------------")
            #    save_msg(r,"AI")
            #    govorilda(r,"AI")  
            #else:
            #demonFFplay(effect_dir + preffect,2)
            demonFFplay(effect_dir + "button3.mp3",2)
            ho("govorilka",data)
                
    elif spl[0] == "!volume":
        demonFFplay(effect_dir + "button3.mp3",2)
        
        #vol = safe_int(spl[1],127)
        vol = safe_int(spl[1],50)
        if vol < 0:
            vol = 0
        if vol > 100:
            vol = 100
        #if vol > 255:
        #    vol = 255
        MPV.volume(vol)
        #vlc_cmd("volume",str(vol))
                
        #govorilda("Поправил громкость",data.snippet.author_channel_id)    
    elif spl[0] == "!next":
        demonFFplay(effect_dir + "button3.mp3",2)
        #vlc_cmd("next")
        MPV.next()
        
    elif spl[0] == "!prev":
        demonFFplay(effect_dir + "button3.mp3",2)
        #vlc_cmd("prev")
        MPV.prev()
        
    elif spl[0] == "!play":
        demonFFplay(effect_dir + "button3.mp3",2)
        MPV.play()
        #vlc_cmd("play")
    elif spl[0] == "!info":
        demonFFplay(effect_dir + "button3.mp3",2)
        print('Title track: ',app_data.col(MPV.track_title(),1,0,3))
                
    elif spl[0] == "!stop":
        demonFFplay(effect_dir + "button3.mp3",2)
        MPV.stop()
        #vlc_cmd("stop")
        
    elif spl[0] == "!pause":
        demonFFplay(effect_dir + "button3.mp3",2)
        #vlc_cmd("pause")    
        MPV.pause()
    
   
        
    elif data['msg'] == "отвал":
        demonFFplay(effect_dir + "415_404.mp3",2)
    elif data['msg'] == "крокодил":
        demonFFplay(effect_dir + "krokodil.mp3",2)
    elif data['msg'] == "АМД ТАЩИТ":
        demonFFplay(effect_dir + "АМД ТАЩИТ.mp3",2)        
    elif data['msg'] == "БЕЗ КУЛЛЕРА СГОРИТ":
        demonFFplay(effect_dir + "БЕЗ КУЛЛЕРА СГОРИТ.mp3")   
    else:	
        demonFFplay(effect_dir + preffect,2)
        ho("govorilka",data)
    #-tts






class hook:
    def add_com_last(data):        
        # внимание  это плохой подход.  нужно собирать данные по очереди не мещая процессу
        #ho("govorilka",data)
        analizv3(data)
        
# запускается после помещения модуля в список загруженных модулей (приложения) 
def run():
    print('425 res')
    #print("["+__name__.split(".")[-1]+"] OK") 
    
# пока не используется но обязательно***
def save():
    print("сохранение")

# пока не используется но обязательно***
def load():
    print("загрузка") 
    


