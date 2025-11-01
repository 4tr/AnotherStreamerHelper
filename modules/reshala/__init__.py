# обязательный блок описания
__plugin__ = {
    "name": "Модуль принятия решений",
    "description": "Добавляет активности исходя из сообщений чата",
    "type": "test" ,
    "autorun":True, # на данный момент используется как команда к загрузке модуля (пока нет других настроек заменяющее это)
    "first_load": False, # переносит модуль в список загружаемых в первую очередь
    "run_mode": 1 #0 - standart,  1 - thread, 2 - multiprocessing    
}

import subprocess
import socket
import time
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
def play_music_md(music_id):
    mid=safe_int(music_id)
    url = 'https://api.modarchive.org/downloads.php?moduleid=' + str(mid)  # URL до файла
    
    save_path = md_mus + str(mid)     
    if os.path.isfile(save_path):
        if os.path.getsize(save_path) < 20: 
            print("Нет такой музыки!!");
            return    
    else:
        print("Качаю музяку");
        #if not os.path.isdir(md_mus):
        if not os.path.exists(md_mus):            
            os.makedirs(md_mus)
            
        urllib.request.urlretrieve(url, save_path)
    vlc_cmd('enqueue',save_path)   
        
def analizv3(data):
    preffect=""
    match data['id']:
        case "console":
            preffect="console.mp3"
        case "AI":
            preffect="r2d2.mp3"
        case "Bot":
            preffect="bot.mp3"
        case _:
            preffect="radio.mp3"
        
            
    msg = data['msg']
    spl = msg.split(" ")
    if spl[0] == "!sr" :
        if safe_int(spl[1]) != 0 :
            # я заказал музыку
            demonFFplay(effect_dir + "ammo_pickup.mp3",2)
            #govorilda("я заказал музыку! слушаем все!",data.snippet.author_channel_id)
            play_music_md(spl[1])
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
        vol = safe_int(spl[1],127)
        if vol < 0:
            vol = 0
        if vol > 255:
            vol = 255
        vlc_cmd("volume",str(vol))
        demonFFplay(effect_dir + "button3.mp3",2)
        #govorilda("Поправил громкость",data.snippet.author_channel_id)    
    elif spl[0] == "!next":
        demonFFplay(effect_dir + "button3.mp3",2)
        vlc_cmd("next")
        
    elif spl[0] == "!prev":
        demonFFplay(effect_dir + "button3.mp3",2)
        vlc_cmd("prev")
        
    elif spl[0] == "!play":
        demonFFplay(effect_dir + "button3.mp3",2)
        vlc_cmd("play")
        
    elif spl[0] == "!stop":
        demonFFplay(effect_dir + "button3.mp3",2)
        vlc_cmd("stop")
        
    elif spl[0] == "!pause":
        demonFFplay(effect_dir + "button3.mp3",2)
        vlc_cmd("pause")    
    
   
        
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
    print()
    #print("["+__name__.split(".")[-1]+"] OK") 
    
# пока не используется но обязательно***
def save():
    print("сохранение")

# пока не используется но обязательно***
def load():
    print("загрузка") 
    


