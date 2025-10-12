
__plugin__ = {
    "name": "web client ",
    "description": "веб сервер flask",
    "type": "web" ,
    "autorun":True, # на данный момент используется как команда к загрузке модуля (пока нет других настроек заменяющее это)
    "first_load": False, # переносит модуль в список загружаемых в первую очередь
    "run_mode": 0 #0 - standart,  1 - thread, 2 - multiprocessing    
}
ifProxy =True


from data import app_data
ho = app_data.hook

import os,sys
#web
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
#import PyQtWebEngine 

#proxy 
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
#from PyQt5.QtCore import *
#from PyQt5.QtWidgets import *
#from PyQt5.QtGui import *
#from PyQt5.QtWebEngineWidgets import *

IP="127.0.0.1"
PORT = 5000

def web_wind(url = "",win_name = ""):
    browser = QWebEngineView()
    browser.setWindowTitle(win_name)
    browser.resize(800, 600)
    browser.load(QUrl(url))
    browser.show()
    return browser
        
# запускается после помещения модуль в список загруженных модулей (приложения) 
def run():   
    if ifProxy:
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--proxy-server=socks5://localhost:8888"
    windows_app = QApplication(sys.argv)        
    cm = web_wind("http://"+IP+":"+str(PORT)+"/comments","Коментарии")            
    print("["+__name__.split(".")[-1]+"] OK")  
    #windows_app.exec_()                  
    sys.exit(windows_app.exec_())
     
       

# пока не используется но обязательно***
def save():
    print("сохранение")

# пока не используется но обязательно***
def load():
    print("загрузка") 
    
