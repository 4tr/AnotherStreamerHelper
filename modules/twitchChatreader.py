__plugin__ = {
    "name": "Twitch chat reader",
    "description": "Получает коменты с чатика на твиче",
    "type": "chat",
    "autorun":True,
    "thread":True    
}

#import websockets
import socket

channel = 'vexviscera'  # канал указывать без '#'

import ssl
from data import app_data
ho = app_data.hook

def run():
   # listen(add_message=app_data.add_message, channel_name="malic_vr")
    print("Twitch chat module RUN")

    
    server = 'irc.chat.twitch.tv'
    port = 6667
    #nickname = 'YourTwitchLogin'
    nickname = f"justinfan67420"  # Анонимный ник для чтения
    #token = 'oauth:xxxxxxxxxxxxxxxxxxxxxx'  # получить на twitchapps.com/tmi
    token = 'SCHMOOPIIE'  
    
    

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
                        primer = {
                            '@badge-info': '', 
                            'badges': '', 
                            'color': '', 
                            'display-name': 'ChannelCanalDuke', 
                            'emotes': '', 
                            'first-msg': '0', 
                            'flags': '', 
                            'id': '9296a811-f4cd-4ea9-ab2a-3843263318d1', 
                            'mod': '0', 
                            'returning-chatter': '0', 
                            'room-id': '105458682', 
                            'subscriber': '0', 
                            'tmi-sent-ts': '1760093268055', 
                            'turbo': '0', 
                            'user-id': '1351814626', 
                            'user-type': ''} 
                        
                        parts["name"]=parts["display-name"]
                        del parts["display-name"]
                        parts["id"]=parts["user-id"]
                        del parts["user-id"]
                        parts["pl"] = "tw"
                        parts["t"] = parts["tmi-sent-ts"]
                        del parts["tmi-sent-ts"]
                        parts["a"] = ""
                        
                        print(mail)   
                        
                        test = text[1].split("\n")
                        if len(test) > 1 :
                            text[1]=test[0]
                            #ho("translate",text) 
                            print("\033[0;31m[Twitch]\033[0;39m \033[0;35m",parts["name"],"\033[0;39m:", text[1])
                            
                        else:
                            #ho("translate",text)                             
                            print("[Twitch] \033[0;35m",parts["name"],"\033[0;39m:", text[1])
                        parts["msg"] = text[1]    
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