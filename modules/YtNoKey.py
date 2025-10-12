__plugin__ = {
    "name": "Youtube chat parser no token",
    "description": "Парсер чата без токенов",
    "type": "chat" ,
    "autorun" : False,
    "run_mode": 2 #0 - standart,  1 - thread, 2 - multiprocessing    
}
ifProxy = False

import httpx
import socksio
import pytchat
from data import app_data
ho = app_data.hook


def run(com_queue):
    video_id="CRLxeCk7lTY"

    if ifProxy:
        proxy = httpx.Proxy("socks5://127.0.0.1:8888")
        transport = httpx.HTTPTransport(proxy=proxy)
        client = httpx.Client(transport=transport, timeout=20.0)
        chat = pytchat.create(video_id=video_id, client=client)
    else:
        chat = pytchat.create(video_id=video_id)
            

    while chat.is_alive():
        for c in chat.get().sync_items():
            print(f"[Youtube] {c.author.name}: {c.message}")
            
            #tmp = c.author.__dict__.items()
            #for i in tmp:
            #    print(i)
            parts = {}    
            parts["name"]=c.author.name
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
    print("Привет из testm")

def load():
    print("Привет из testm")


