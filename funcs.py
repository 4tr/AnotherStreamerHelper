
from data import app_data

#import importlib
#print(hasattr(importlib, "import_module")) 
# python -m ensurepip --upgrade
import subprocess
import sys

# нужно для анализа модуля перед его загрузкой
import ast
from types import ModuleType

import traceback
import requests

import inquirer
from inquirer.themes import GreenPassion
import threading
import importlib
import os
import inspect
import select
import time
import numpy

import re
WAIT_TIME = 5  # секунды ожидания ввода для ручной конфигурации

def _get_ast_value(node):
    """Рекурсивно преобразует узел AST в простое значение Python"""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Dict):
        return {
            _get_ast_value(k): _get_ast_value(v)
            for k, v in zip(node.keys, node.values)
        }
    elif isinstance(node, ast.List):
        return [_get_ast_value(e) for e in node.elts]
    elif isinstance(node, ast.NameConstant):  # для True/False/None
        return node.value
    else:
        return None

def inspect_module(path):
    """Парсит Python-файл без исполнения кода.
       Возвращает (функции, переменные)"""
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)

    functions = []
    variables = {}

    for node in ast.walk(tree):
        # --- функции ---
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

        # --- простые и словарные присваивания ---
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    # Константа (число, строка, bool)
                    if isinstance(node.value, ast.Constant):
                        variables[name] = node.value.value

                    # Словарь (dict)
                    elif isinstance(node.value, ast.Dict):
                        d = {}
                        for key, val in zip(node.value.keys, node.value.values):
                            if isinstance(key, ast.Constant):
                                d[key.value] = _get_ast_value(val)
                        variables[name] = d
    return {"f":functions,"m":variables}

def install(package):
    #stupid fix я не понимаю какого фига но так у меня работает
    if package == "PyQt5.QtWebEngineWidgets":
        package = "PyQtWebEngine"
    if package == "obswebsocket":
        package = 'obs-websocket-py'    
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
def uninstall(package):
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", package])

def require(package, pip_name=None):
    try:
        return importlib.import_module(package)
    except ImportError:
        install(pip_name or package)
        return importlib.import_module(package)

def list_modules(path=app_data.module_dir):
    modules = {}
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if entry.endswith(".py") and entry != "__init__.py":
            modules[entry[:-3]]=full_path  # без .py
        elif os.path.isdir(full_path) and "__init__.py" in os.listdir(full_path):
            modules[entry]=full_path + "/__init__.py"  # имя папки = имя модуля
    return modules

# эта хреновина по сути УЖЕ грузит модуль и при ошибках пытается доустановить зависимости
def lmd(module_name, package=app_data.module_dir,last_err = ""):
    print(f"[{module_name}] импорт модуля")
    try:
        return {"ok":True,"e":"","mod":importlib.import_module(f"{package}.{module_name}")}
    except ModuleNotFoundError as e:                
        print(f"\033[0;31mОшибка {module_name}: {e}\033[0;39m")
        if last_err == e:
            return {"ok":False,"e":"\033[0;31mувы попытка установки уже была, ошибка повторилась =(\033[0;39m"}
        print(f"\033[0;31mпопытка установки  {e.name}")
        install(e.name)
        print(f"пробуем модуль {module_name} снова")
        return lmd(module_name,package,e)
    except Exception as e: 
        print("\033[0;31m------------------------------------------------------------------------------------")
        traceback.print_exc()       
        print("------------------------------------------------------------------------------------\033[0;39m")
        
        return {"ok":False,"e":f"\033[0;31mОшибка при загрузке {module_name}: {e}\033[0;39m"}
        

#распознает что на входе и распарсивает соответственно
def module_select_checker(mod,name, permAutorun = False):
    if type(mod) is dict:
        info = mod["m"].get("__plugin__",None)        
        t = get_plugin_info(info,name,permAutorun)
        if t["ok"] != True:
            return t
        info = t["info"]
        ls_funcs = mod["f"]
    elif isinstance( mod , ModuleType):
        info = getattr(mod, "__plugin__", None)
        name = mod.__name__                  
        t = get_plugin_info(info,name,permAutorun)
        if t["ok"] != True:
            return t
        info = t["info"]
        ls_funcs = get_list_functions_module(mod)
    else:
        return {"ok":False,"e":f"\033[101m \033[0;31m Модуль {name} протух?\033[0;39m"}
    if info == None:
        return {"ok":False,"e":f"\033[101m \033[0;31m В модуле {name} хуйня странная] \033[0;39m"}
    
    return {"ok":True,"e":"","info":info,"name":name,"ls_funcs":ls_funcs}

def get_plugin_info(info, name = "WTF 0_o", permAutorun = False):
    if info == None:
        return {"ok":False,"e":f"\033[101m \033[0;31m В модуле {name} нет описания __plugin__ \033[0;39m"}  
    info['autorun'] = info.get("autorun",False)   
    info['run_mode'] = info.get("run_mode",0)       
    info['first_load'] = info.get("first_load",False)
    if permAutorun == False:
        if info['autorun'] == False:            
            return {"ok":False,"e":f"\033[43m \033[49m \033[33mМодуль {name} помечен как не запускаемый автоматически \033[0;39m"}
    return {"ok":True,"e":False,"info":info}
    
def validate_module(mod, name = "WTF 0_o",permAutorun = False):
    tmp = module_select_checker(mod,name,permAutorun)
    if tmp["ok"] == False:
        return tmp
    else:
        info = tmp["info"]
        name = tmp["name"]
        ls_funcs = tmp["ls_funcs"]
    for fn in app_data.required_funcs:
        if fn not in ls_funcs:                                    
            return {"ok":False,"e":f"\033[101m \033[0;31m В модуле {name} нет функции {fn}\033[0;39m"}
    return {"ok":True,"e":"","info":info}

def get_list_functions_module(mod):
    try: 
        tmp = mod.__dict__.items()
    except Exception as e:
        print(f"Ошибка загрузки функций модуля: {e}")  
        return []
    list = []
    for k,v in tmp:
        if inspect.isfunction(v):            
            list.append(k)
    return list
    

def get_hooks_module(name,mod):
    
    ##!!! TODO хуки чтобы не досыпало  наследуемые  типа __module__ __dict__ __weakref__ __doc__

    if getattr(mod, "hook", None) == None:
        #print("нет хуков для добавления")
        return
    try: 
        tmp = mod.hook.__dict__.items()
    except Exception as e:
        print(f"[{name}] Ошибка загрузки хуков: {e}")  
        return
    #list = {}
    for k,v in tmp:
        if inspect.isfunction(v): 
                     
            app_data.add_hook(name_hook= k, hookfunc=v , modulename=  name)
            #list[k]=v
    
def runner(name):
        print("\033[42m \033[0;39m запуск:<", name , "> \033[0;39m ")        
        mod = app_data.modules[name]["module"]
        info = app_data.modules[name]["info"]        
        if info['run_mode'] == 1:
            app_data.add_threads(mod.run,name)
        elif info['run_mode'] == 2:
            app_data.add_multiprocess(mod.run,name)
        else:    
            mod.run()
    


def loader(mod,name,first_load = True,permAutorun = False): 
    vm = validate_module(mod,"WTF 0_0",permAutorun)
    if mod and vm["ok"]:    
        info = vm["info"]
        if info["first_load"] != first_load:
            return         
        app_data.add_mod({"name": name, "module": mod, "info": info})
        get_hooks_module(name,mod)
        print("\033[42m \033[0;39m успешно загружен:<", name , "> \033[1;97m", info["name"], "\033[0;39m ")        
    else:
        print(vm["e"])  
# попытка проанализоровать модуль до того как он загрузится
# permAutorun true дает команду не учитывать надстройку Autorun внутри модуля.
def pre_validate_module(name,permAutorun = False):
    r = inspect_module(name)
    return validate_module(r,name,permAutorun)
def sort_modules_autorun(ans,valid_first = [],valid_other = []):
    valid_first_filtered= []
    valid_other_filtered= []
    for n in valid_first:
        for s in ans:
            if n == s:
                valid_first_filtered.append(s)
    for n in valid_other:
        for s in ans:
            if n == s:
                valid_other_filtered.append(s)
    return valid_first_filtered, valid_other_filtered
def vopros(method = "q", msg = "",list = ["error"],default = None,name = ""):
    if (name == ""):
        name = method
    if (method == "features"):        
        q = [inquirer.Checkbox(name,message=msg,choices=list,default=default)]        
        return inquirer.prompt(q, theme=GreenPassion())[name]
    if (method == "list"):        
        q = [inquirer.List(name,message=msg,choices=list,default=default),]
        return inquirer.prompt(q, theme=GreenPassion())[name]
    if (method == 'text'):
        if name == 'number':
            q = [inquirer.Text(name,message=msg,default=default,validate=lambda _, x: re.fullmatch('\d+', x),),]
        else:    
            q = [inquirer.Text(name,message=msg,default=default,),]
        return inquirer.prompt(q, theme=GreenPassion())[name]    
        inquirer.Text('name', message="What's your name",default="123"),
    
        
def console_module_config(module_name = ""):
    c = app_data.get_config_v2(module_name=module_name,full_data=True)
    #print(c)
    l = []
    text = "список настроек модуля "+module_name
    if c != None:
        for i in c:
            #ret[i]=cfg[i]['value']
            l.append(i)
    else:
        text = "у модуля " + module_name + " нет настроек"
    l.append('>назад<')    
    #print(i)   
    a = vopros("list",text,l)
    if a == '>назад<':            
        return  
    default = ""
    if c[a]['type'] == "text": default = c[a]['value']
    if c[a]['type'] == "checkbox": 
        default = "Отключено"
        if c[a]['value']: 
            default = "Активно"
    if c[a]['type'] == "password": default = "***"
    if c[a]['type'] == "number": default = str(c[a]['value'])
    
    
    ##fixme добавить редактирование других полей
    txtt ="-"+c[a]['type']+"- редактируем поле '"+a+"'-'"+c[a]['label']+"' модуля '"+module_name+"'"
    if c[a]['type'] == "checkbox":
        e = vopros("list",txtt,list=['Активно','Отключено'], default=default)
        if e == "Активно":
            e = True
        else:
            e = False     
    else:
        if c[a]['type'] == "number":    
            e = vopros("text",txtt,default=default,name=c[a]['type'])
        else:
            e = vopros("text",txtt,default=default)
        
    if c[a]['type'] == "number": e = int(e)
        
    if e != c[a]['value']:
        s = vopros("list","Сохранить?",list=["Да","Нет"],default="Да")
        if s == "Да":
            if c[a]['type'] == "text": c[a]['value']=e
            if c[a]['type'] == "password": c[a]['value']=e                        
            if c[a]['type'] == "checkbox": c[a]['value']=e                        
            if c[a]['type'] == "number": c[a]['value']=e                        
            app_data.save_cfg(module_name,c,save = 1)
            print("Сохранено!")
            #exit()
    console_module_config(module_name)       
    
    
def  console_listmodules_configs(savedata_autorun=[]):
    ans_modulelist_q = savedata_autorun.copy()        
    ans_modulelist_q.append('>назад<')
    a = vopros("list","список активных модулей",ans_modulelist_q)
    if a == '>назад<':            
        return 
    console_module_config(a)
    return console_listmodules_configs(savedata_autorun)        
         
    #app_data.save_cfg("CORE" , answers['features'], "autorun_modules")

def consoleGraphMenu(valid_all = [] ,valid_first = [],valid_other = [],savedata_autorun = []):
    
    
    ans = vopros("list","Меню настроек",['включить/отключить модули','редактировать настройки активных  модулей','СТАРТ'])
    print("Вы выбрали:", ans)  
    if ans == 'СТАРТ':
        return sort_modules_autorun(savedata_autorun,valid_first,valid_other)
    if ans == 'редактировать настройки активных  модулей':
        console_listmodules_configs(savedata_autorun)
        return consoleGraphMenu(valid_all,valid_first,valid_other,savedata_autorun)
    if ans == 'включить/отключить модули':        
        if len(valid_all) == 0:
            print(" \033[91m Что ты хотел тут настраивать? у тебя нет модулей вообще! \033[39m")
            exit()
        items_default = []
        
        for n in valid_all:
            found = False        
            for m in savedata_autorun:
                if found == False:            
                    if n == m:
                        items_default.append(n)
                        found = True
        
            
        questions = [
            inquirer.Checkbox(
                'features',
                message="\033[0;97m Выберите модули из списка чтобы включить/отключить\033[0;39m",
                choices=valid_all,
                default=items_default
            )
        ]

        answers = inquirer.prompt(questions)
        #ЕСЛИ НИЧЕГО НЕ ПОМЕНЯЛОСЬ ТО И СОХРАНЯТЬ НЕ НАДО
        if numpy.array_equal(answers['features'], savedata_autorun) == False:
            q = [inquirer.List("Save", message="Сохранить?", choices=["Да", "Нет"], default="Да"),]
            an = inquirer.prompt(q, theme=GreenPassion())
            if ( an['Save'] == 'Да'):
                print('сохраняю ...')
                savedata_autorun = answers['features'].copy()
                app_data.save_cfg("CORE" , savedata_autorun, "autorun_modules")
        return consoleGraphMenu(valid_all,valid_first,valid_other,savedata_autorun)    
        #return sort_modules_autorun(savedata_autorun,valid_first,valid_other)
        
def load_all_modules(path=app_data.module_dir):
    available = list_modules(path)    
    #сформировать ОДИН Б**ь раз список валидных модулей для работы
    valid_first = []
    valid_other = []
    valid_all = []
    #шмат кода для ручной инициализации модулей 
    permAutorun = False
    openGraphMenu = False
    #пока вот так
    permAutorun = True
    savedata_autorun = app_data.get_cfg("CORE",'autorun_modules')             
    if savedata_autorun == None:
        savedata_autorun = []
    #print(savedata_autorun)
    
    if savedata_autorun == []:
        print(f"[CORE] \033[91m нет конфигураций модулей. принудительный ввод в настройку запуска модулей.\033[39m")    
        openGraphMenu = True
    else:        
        print(f"[CORE] \033[91m Для входа в режим конфигурации нажми enter. Таймер {WAIT_TIME} сек.\033[39m")

        start = time.time()
        while time.time() - start < WAIT_TIME:
            # select проверяет, есть ли данные в stdin
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:  # что-то ввели
                sys.stdin.readline()  # очистить ввод
                print("[CORE] Запущен ручной режим конфигурации модулей")
                permAutorun = True            
                openGraphMenu = True
                break
        if permAutorun == False:
            print("[CORE] Продолжается обычный запуск приложения")
            
    for name in available:
        t = pre_validate_module(available[name],permAutorun)
        if t["ok"]:   
            valid_all.append(name)         
            if t["info"]["first_load"]:
                valid_first.append(name)            
            else:
                valid_other.append(name)    
        else:            
            print(t["e"])        
          
    if openGraphMenu:
        valid_first , valid_other = consoleGraphMenu(valid_all,valid_first,valid_other,savedata_autorun)
    else:
        valid_first , valid_other = sort_modules_autorun(savedata_autorun,valid_first,valid_other)    
    for name in valid_first:
        r = lmd(name, package=path)         
        if r["ok"] == True:
            loader(r["mod"],name,True,permAutorun)              
            print('[debug] loader')
        else:
            valid_first.remove(name)
            print(r["e"]) #"ok":False,"e":f"\033[101m \033[0;31m В модуле {name} нет описания __plugin__ \033[0;39m"
            
    #теперь пройдемся по модулям без пометки first_load или с false
    for name in valid_other:
        r = lmd(name, package=path)              
        if r["ok"] == True:
            loader(r["mod"],name,False,permAutorun) 
            print('[debug] loader')       
        else:
            valid_other.remove(name)
            print(r["e"])    

    runWebWindow = False
    #запуск функций модулей
    for name in valid_first:        
        if name == "web_client": #костыль!!!
            runWebWindow = True
        else:    
            runner(name)     
    for name in valid_other:
        if name == "web_client": #костыль!!!
            runWebWindow = True
        else:    
            runner(name)     
    
    #print(app_data.multiprocess)
    #print(app_data.get_process_module("YtNoKey"))
    
    #exit()

    if runWebWindow :
        runner("web_client")
    
