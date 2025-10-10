
from data import app_data

#import importlib
#print(hasattr(importlib, "import_module")) 
# python -m ensurepip --upgrade
import subprocess
import sys

# нужно для анализа модуля перед его загрузкой
import ast
from types import ModuleType

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
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
def uninstall(package):
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", package])

import importlib

def require(package, pip_name=None):
    try:
        return importlib.import_module(package)
    except ImportError:
        install(pip_name or package)
        return importlib.import_module(package)

# пример
requests = require("requests")
flask = require("flask")



import threading
import importlib
import os
import inspect


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
    print(f"[{module_name}] запуск модуля")
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
        return {"ok":False,"e":f"\033[0;31mОшибка при загрузке {module_name}: {e}\033[0;39m"}

#распознает что на входе и распарсивает соответственно
def module_select_checker(mod,name):
    if type(mod) is dict:
        info = mod["m"].get("__plugin__",None)        
        t = get_plugin_info(info,name)
        if t["ok"] != True:
            return t
        info = t["info"]
        ls_funcs = mod["f"]
    elif isinstance( mod , ModuleType):
        info = getattr(mod, "__plugin__", None)
        name = mod.__name__                  
        t = get_plugin_info(info,name)
        if t["ok"] != True:
            return t
        info = t["info"]
        ls_funcs = get_list_functions_module(mod)
    else:
        return {"ok":False,"e":f"\033[101m \033[0;31m Модуль {name} протух?\033[0;39m"}
    if info == None:
        return {"ok":False,"e":f"\033[101m \033[0;31m В модуле {name} хуйня странная] \033[0;39m"}
    
    return {"ok":True,"e":"","info":info,"name":name,"ls_funcs":ls_funcs}

def get_plugin_info(info, name = "WTF 0_o"):
    if info == None:
            return {"ok":False,"e":f"\033[101m \033[0;31m В модуле {name} нет описания __plugin__ \033[0;39m"}  
    info['autorun'] = info.get("autorun",False)    
    info['thread'] = info.get("thread",False)        
    info['first_load'] = info.get("first_load",False)
    if info['autorun'] == False:            
        return {"ok":False,"e":f"\033[43m \033[49m \033[33mМодуль {name} помечен как не запускаемый автоматически \033[0;39m"}
    return {"ok":True,"e":False,"info":info}
    
def validate_module(mod, name = "WTF 0_o"):
    tmp = module_select_checker(mod,name)
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
    
        

def loader(mod,name,first_load = True): 
    vm = validate_module(mod)
    if mod and vm["ok"]:    
        info = vm["info"]
        if info["first_load"] != first_load:
            return         
        app_data.add_mod({"name": name, "module": mod, "info": info})
        get_hooks_module(name,mod)
        print("\033[42m \033[0;39m успешно загружен:<", name , "> \033[1;97m", info["name"], "\033[0;39m ")
        if info['thread'] == True:
            app_data.add_threads(mod.run,name)
        else:    
            mod.run()
    else:
        print(vm["e"])  
# попытка проанализоровать модуль до того как он загрузится
def pre_validate_module(name):
    r = inspect_module(name)
    return validate_module(r,name)
        
def load_all_modules(path=app_data.module_dir):
    available = list_modules(path)    
    #сформировать ОДИН Б**ь раз список валидных модулей для работы
    valid_first = []
    valid_other = []
    for name in available:
        t = pre_validate_module(available[name])
        if t["ok"]:
            if t["info"]["first_load"]:
                valid_first.append(name)            
            else:
                valid_other.append(name)    
        else:
            print(t["e"])        
   
    #старый код требуется нормальная очередь !!!!!!!!!!!
    #сначала пройдемся по модулям с пометкой first_load 
    for name in valid_first:
        r = lmd(name, package=path) 
        if r["ok"] == True:
            loader(r["mod"],name,True)        
            
    #теперь пройдемся по модулям без пометки first_load или с false
    for name in valid_other:
        r = lmd(name, package=path)        
        if r["ok"] == True:
            loader(r["mod"],name,False)        






    







