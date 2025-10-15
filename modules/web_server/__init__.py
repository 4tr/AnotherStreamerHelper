
__plugin__ = {
    "name": "flask web server",
    "description": "веб сервер flask",
    "type": "web" ,
    "autorun":True, # на данный момент используется как команда к загрузке модуля (пока нет других настроек заменяющее это)
    "first_load": False, # переносит модуль в список загружаемых в первую очередь
    "run_mode": 1 #0 - standart,  1 - thread, 2 - multiprocessing    
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

@app.route('/config')
def config():
    return render_template("config.html")  

@app.route("/conf", methods=['GET', 'POST'])
def conf_get():
    m = app_data.modules
    mod_name = request.args.get("m")    
    if mod_name is not None:
        if mod_name in m:
            #app_data.get_cfg()
            cfg = app_data.get_cfg(app_data.module_dir+"."+mod_name)
        else:
            cfg = None        
    else:        
        cfg = None
    #print(cfg)
    #print(mod_name)
    if request.args.get("get") is not None:
        return jsonify(cfg)    
    
    if request.args.get("save") is not None:
        if mod_name is None:
            return False
        print("debug4" , mod_name)
        
        new_data = request.json
        print(new_data)
        return "KEKW"
        # обновляем значения
        #for item in cfg:
        upd = False
        for key, item in cfg.items():   
            print(item["name"])
            if new_data[item["name"]]["name"] is not None:
                print("22")
                if (item["value"] == new_data[item["name"]]["value"]):
                    print(item["name"] + " : сохранение не требуется")
                else:
                    upd=True
                    cfg[item["name"]]["value"] = new_data[item["name"]]["value"]
                    print(item["name"] + " : свежак")
                        
                #val = new_data[item["name"]]
                # привести типы
                #if item["type"] == "number":
                ##    item["value"] = int(val)
                #elif item["type"] == "checkbox":
                #    item["value"] = bool(val)
                #else:
                #    item["value"] = str(val)
               # sv_conf()
        return jsonify(cfg)
    
    
@app.route("/module", methods=["GET", "POST"])
def module_web():
       
    m = app_data.modules
    mod_name = request.args.get("m")
    if mod_name is not None:
        if mod_name in m:
            #app_data.get_cfg()
            cfg = app_data.get_cfg(app_data.module_dir+"."+mod_name)
                
        
@app.route("/modules", methods=["GET", "POST"])
def modules_web():   
    #print(app_data.get_process_module("YtNoKey"))
    return render_template("modules.html",m=app_data)

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
    
