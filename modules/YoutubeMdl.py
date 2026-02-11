__plugin__ = {
    "name": "Youtube chat parser",
    "description": "Парсер чата без токенов. токен нужен для запроса имен каналов",
    "type": "chat" ,
    "autorun" : False, #игнорируется*** заменен на конфиг настраиваемый с консоли при запуске
    "first_load": True,
    "run_mode": 2 #0 - standart,  1 - thread, 2 - multiprocessing    
}

__cfg__={
    "default": {
        "video_id": {
            "label": "Идентификатор свидео",
            "name": "video_id",
            "type": "text",
            "value": "KOT-666"            
        },  
        "API_KEY": {
            "label": "API_KEY",
            "name": "API_KEY",
            "type": "password",
            "value": "*************************"
        }  
    }
}

cfg={}

userlist = {}
ifProxy = False
import httpx
import socksio
import pytchat
import requests
from typing import List, Dict

from data import app_data
ho = app_data.hook

BASE_URL = "https://www.googleapis.com/youtube/v3/channels"

def chunked(iterable, n):
    """Разбивает iterable на чанки длины n."""
    it = list(iterable)
    for i in range(0, len(it), n):
        yield it[i:i+n]
# откат е*учего собачьего ютуб никономайзера
def get_channel_titles_by_ids(channel_ids: List[str]) -> Dict[str, str]:
    """
    Возвращает словарь channel_id -> channel_title (snippet.title).
    Делает batch-запросы по 50 id за раз.
    """
    print("----------------------запрос ников----------------------------")
    print(channel_ids)
    result = {}
        
    for chunk in chunked(channel_ids, 50):
        params = {
            "part": "snippet",
            "id": ",".join(chunk),
            "key": cfg["API_KEY"],
            "maxResults": 50
        }
        resp = requests.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # В ответе data["items"] — список объектов каналов
        for item in data.get("items", []):
            cid = item.get("id")
            title = item.get("snippet", {}).get("title")
            result[cid] = title

        # Если каких-то ID нет в items => канал удалён/скрыт/не найден
        for cid in chunk:
            result.setdefault(cid, None)

    return result    

def get_channel_name(id , dog):
    saved = False
    tmpname = dog[1:]
    u = userlist.get(id, None)  
    if u == None:
        i = {"dog":dog,
             "list":[],
             "name":tmpname,
             "id":id}
        userlist[id]=i
        saved = True          
    else:
        un = u.get("name", None)
        if un == None:
            userlist[id]['name'] = tmpname
            saved = True     
    if len(userlist[id]["list"]) == 0:
        saved = True 
        t = get_channel_titles_by_ids([id])
        userlist[id]["list"]=[t[id]]
        if t[id] != None:
            userlist[id]["name"]=t[id]       
        
    if saved:
        save()
            
    return userlist[id]['name']    
    

def run(com_queue):       
    global cfg    
    cfg = app_data.get_config_v2(__name__)
    load()
    video_id=cfg["video_id"]    
    if ifProxy:
        proxy = httpx.Proxy("socks5://127.0.0.1:8888")
        transport = httpx.HTTPTransport(proxy=proxy)
        client = httpx.Client(transport=transport, timeout=20.0)
        chat = pytchat.create(video_id=video_id, client=client)
    else:
        chat = pytchat.create(video_id=video_id)
            

    while chat.is_alive():
        for c in chat.get().sync_items():
            #print(f"[Youtube] {c.author.name}: {c.message}")  
            
            #tmp = c.author.__dict__.items()
            #tmp = c.__dict__.items()
            #for i in tmp:
            #    print(i)
            parts = {}  
            tmpname = c.author.name
            tmpname =tmpname[1:]
            parts["name"]=get_channel_name(c.author.channelId , c.author.name)
            #parts["name"]=c.author.name
            #parts["name"] =parts["name"][1:]
            parts["pl"] = "yt"
            parts["t"] = c.timestamp
            parts["msg_id"] = c.id                        
            parts["id"]=c.author.channelId
            parts["a"] = c.author.imageUrl
            parts["msg"] = c.message
            parts["messageEx"]= c.messageEx
            parts["channelUrl"]=c.author.channelUrl
            parts["Verified"]=c.author.isVerified
            parts["ChatOwner"]=c.author.isChatOwner
            parts["ChatSponsor"]=c.author.isChatSponsor
            parts["ChatModerator"]=c.author.isChatModerator
            msg = ""
            msg_con = ""
            for i in parts["messageEx"]:
                if type(i) is str: 
                    msg_con = msg_con + i
                    msg = msg + i
                else:
                    msg = msg + "<img src=\"" + i['url']+"\" id=\""+ i['id'] +"\" title=\""+ i["txt"] +"\">"                    
            parts['msg'] = msg                    
            parts['clear_msg'] = msg_con                    
                      
            print(f"[Toutube]\033[0;31m",parts["name"],"\033[0;39m:",msg_con)            
            com_queue.put(parts)    # такой код для модуля работающего в режиме multiprocessing
            # app_data.add_com(parts)  а такой в режиме thread
            #print(parts)            
        #author.badgeUrl
        #author.type
        #type  textMessage
        #id
        #datetime
        #amountValue
        #amountString
        #currency
        #bgColor
        
    return



    

def save():    
    app_data.save_cfg(__name__ , userlist, "userlist",1)

def load():
    global userlist
    temp = app_data.get_cfg(__name__ ,"userlist")
    if temp is None:
        save()
    else:
        userlist = temp    
    #запрос НОРМАЛЬНЫХ НИКОВ с апи
    listIds = []
    saved = False
    for k in userlist:
        if len(userlist[k]["list"]) == 0:
            listIds.append(k)
    if len(listIds) > 0:    
        titles = get_channel_titles_by_ids(listIds)
        for cid, title in titles.items():
            saved = True            
            if title != None :
                userlist[cid]['name']=title            
            userlist[cid]['list']=[title]
            #print(cid, "->", title)        
    if saved == True:
        save()
    short = {}    
    for k in userlist:
        short[k]=[userlist[k]["dog"],userlist[k]["name"]]
    app_data.save_cfg(__name__ , short, "short",1)
          

