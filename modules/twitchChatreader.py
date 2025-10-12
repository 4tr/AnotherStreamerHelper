__plugin__ = {
    "name": "Twitch chat reader",
    "description": "Получает коменты с чатика на твиче",
    "type": "chat",
    "autorun":True,
    "run_mode": 1 #0 - standart,  1 - thread, 2 - multiprocessing      
}


#import websockets
import socket
import requests

channel = 'arti9m'  # канал указывать без '#'
nickname = f"justinfan67420"  # Анонимный ник для чтения
token = 'SCHMOOPIIE'  
 
import ssl
from data import app_data
ho = app_data.hook

def get_global_emotes(client_id, token):
    url = "https://api.twitch.tv/helix/chat/emotes/global"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": client_id
    }
    resp = requests.get(url, headers=headers)
    data = resp.json()
    # `data["data"]` — список эмодзи, каждый c полями id, name, images
    return data["data"]

def sort_emote_item(ee):
    if len(ee) == 0:
        return []
    e = ee.copy()
    ret = []
    ret.append(e[0])
    del e[0]
    #print("___")
    #print(e)
    if len(e) == 0:
        return ret
    for ki,i in enumerate(e): 
        #print('__',i)           
        for kr,r in enumerate(ret):    
            if i[1] > r[2]:
                #print("-", kr, i)
                
                ret.insert(kr,i)
                #del e[ki]
                break
    return ret

def parse_emotes_tag(emotes_tag, message_text):
    """
    emotes_tag: строка как "25:0-4,1902:6-10"
    message_text: полный текст сообщения
    Возвращает список кортежей (emote_id, start_idx, end_idx, emote_text)
    """
    #print(emotes_tag)
    #print(message_text)
    result = []
    if not emotes_tag:
        return result    
    
    for item in emotes_tag.split('/'):  # иногда несколько наборов через '/' 
        #print("pair",pair)
        emote_id, ranges = item.split(':')
        for rang in ranges.split(','):            
            if not rang:
                continue
            start, end = rang.split('-')
            start = int(start)
            end = int(end)
            emote_text = message_text[start:end+1]
            result.append((emote_id, start, end, emote_text))
    return result

def run():
   # listen(add_message=app_data.add_message, channel_name="malic_vr")
    print("Twitch chat module RUN")

    
    server = 'irc.chat.twitch.tv'
    port = 6667
    #nickname = 'YourTwitchLogin'
   
    #token = 'oauth:xxxxxxxxxxxxxxxxxxxxxx'  # получить на twitchapps.com/tmi
    
    
    

    sock = socket.socket()
    sock.connect((server, port))

    sock.send(f"CAP REQ :twitch.tv/tags twitch.tv/commands".encode('utf-8'))
    sock.send(f"PASS {token}\r\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\r\n".encode('utf-8'))
    sock.send(f"JOIN #{channel}\r\n".encode('utf-8'))

    while True:
        resp = sock.recv(2048).decode('utf-8')
        if resp.startswith('PING'):
            sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
        else:
            #print(resp)
            if "PRIVMSG" in resp:
                try:
                    if resp.startswith("@"):                        
                        block = resp.split(" PRIVMSG #")
                        tmp = block[0].split(" :")
                        mail = tmp[1]
                        tmp_parts = tmp[0].split(";")                        
                        text = block[1].split(":", 1)
                        text[1] = text[1].strip()
                        parts={}
                        for i in tmp_parts:
                            t = i.split("=",1)
                            parts[t[0]]=t[1]

                       
                        #print(parts)
                        primer2 = {
                                '@badge-info': '', 
                                'badges': '', 
                                'client-nonce': '583425313e4e2cbb94209a1e29d58d77', 
                                'color': '#0000FF', 
                                'emote-only': '1', 
                                'emotes': '133468:0-11', 
                                'first-msg': '0', 
                                'flags': '', 
                                'id': '518271413', 
                                'mod': '0', 
                                'returning-chatter': '0', 
                                'room-id': '53558942', 
                                'subscriber': '0', 
                                'turbo': '0', 
                                'user-type': '', 
                                'name': 'HAXP9m', 
                                'pl': 'tw', 
                                't': '1760144204416', 
                                'a': '',
                                'msg': 'ItsBoshyTime'
                            }
                        
                        parts["name"]=parts["display-name"]
                        del parts["display-name"]
                        parts["id"]=parts["user-id"]
                        del parts["user-id"]
                        parts["pl"] = "tw"
                        parts["t"] = parts["tmi-sent-ts"]
                        del parts["tmi-sent-ts"]
                        parts["a"] = ""
                        
                        #print(mail)   
                        
                        test = text[1].split("\n")
                        if len(test) > 1 :
                            text[1]=test[0]
                            #ho("translate",text) 
                            print("\033[0;31m[Twitch]\033[0;39m \033[0;35m",parts["name"],"\033[0;39m:", text[1])
                            
                        else:
                            #ho("translate",text)                             
                            print("[Twitch] \033[0;35m",parts["name"],"\033[0;39m:", text[1])
                        parts["msg"] = text[1] 
                        parts["emotes"] = parse_emotes_tag(parts["emotes"],parts["msg"])
                        #print(parts["emotes"])    
                        ee = parts["emotes"]
                        #print(parts["emotes"])
                        #[('160402', 0, 7, 'SabaPing'), ('emotesv2_5d523adb8bbb4786821cd7091e47da21', 9, 15, 'PopNemo'), ('133468', 17, 28, 'ItsBoshyTime')]
                        ee = sort_emote_item(ee)                                              
                        for i in ee:
                            ib = i[1]
                            ie = i[2] + 1   
                            #print(parts['msg'][ie:])
                            #if ie == (len(parts['msg'])):
                            #    print("ok!!!!!!!!")
                            #    exit()
                            parts['msg']= parts['msg'][:ie] + '">' + parts['msg'][ie:]
                            parts['msg']= parts['msg'][:ib] + '<id="' + i[0]+ '" name="' + parts['msg'][ib:]
                            

                        app_data.add_com(parts)
                        
                        #print(app_data.com)    
                        #app_data.modules["AI_translate"]["module"].aitr.translate(text[1])
                        
                        #print(app_data.hook(hook_name="translate
                        # ",data=text[1]))
                        
                        #print("[Twitch AI tr] ", text[1])
                        
                        #print(app_data.hook("test_text_modificator",text))
                        
                        
                        
                    #else:   
                        
                        
                        #тут ломаные ответы                     
                        #print("\033[0;31m")
                        #print(resp)
                        #print("\033[0;39m")
                        
                        
                        
                        #parts = resp.split(" PRIVMSG #")
                        #username = parts[0].split("!")[0].replace(":", "").strip()
                        #message = resp.split(" :", 2)[-1].strip()                        
                        #print(f"[Twitch ] {username}: {message}")
                        #add_message([username, message])
                        
                except Exception as e:
                    print(f"[Twitch ] Ошибка парсинга: {e}")
            #else:
            #    print("\033[0;31m")
            #    print("no PRIVMSG #")
            #    print("\033[0;39m")        
                        


def save():
    print("Привет из testm")

def load():
    print("Привет из testm")                