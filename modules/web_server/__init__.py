
__plugin__ = {
    "name": "flask web server",
    "description": "веб сервер flask",
    "type": "web" ,
    "autorun":True, # на данный момент используется как команда к загрузке модуля (пока нет других настроек заменяющее это)
    "first_load": False, # переносит модуль в список загружаемых в первую очередь
    "thread": True   # нужно для модулей которые имеют собственные бесконечные циклы дабы не фризить работу кода
}

from data import app_data
ho = app_data.hook

IP="127.0.0.1"
PORT = 5000
import os
from flask import Flask, render_template, request, jsonify

#template_dir = os.path.abspath('../../frontend/src')
#template_dir = os.path.abspath('/modules/frontend/src')
#template_dir = os.path.abspath('')
template_dir = os.path.dirname(os.path.realpath(__file__))



app = Flask(__name__, template_folder=template_dir + "/templates" , static_folder= template_dir + "/static")
        
        
@app.route("/", methods=["GET", "POST","HEAD"])
def index():
    return render_template("index.html")

@app.route("/comments", methods=["GET", "POST"])
def comments():    
    return render_template("com.html")

@app.route("/get")
def get():    
    last = int(request.args.get("last", ""))
    tmp=[]
    for v in app_data.com:
        if v["nn"] > last:
            tmp.append(v)
    return jsonify(tmp)

        
# запускается после помещения модуль в список загруженных модулей (приложения) 
def run():
    app.run(host=IP, port=PORT)
    print("["+__name__.split(".")[-1]+"] OK")    

# пока не используется но обязательно***
def save():
    print("сохранение")

# пока не используется но обязательно***
def load():
    print("загрузка") 
    
