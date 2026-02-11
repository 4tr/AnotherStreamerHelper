print("[CORE] INIT")
import time
import funcs
import threading
import queue



print("[CORE] FUNCS OK")
funcs.load_all_modules()

from data import app_data
hook = app_data.hook
print("[CORE] all loads itit console listener")
input_queue = queue.Queue()
def console_listener():
    while True:
        try:
            user_input = input()
            input_queue.put(user_input)
        except EOFError:
            break
threading.Thread(target=console_listener, daemon=True).start()
print("[CORE] init cycler")

try:
    while not app_data.stop:
        while not input_queue.empty():
            cmd={}
            cmd['msg'] = input_queue.get()                        
            app_data.add_com(msg=cmd,uid="Console")
            #if cmd == "exit":
            #    app_data.stop = True
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Цикл прерван пользователем")        
   
except Exception as e:
    print(f"Произошла ошибка: {e}")
   
finally:
    #нужно добавить вызов сохранялок
    print("[*] Сохраняю(пока нет) данные перед выходом...")
        

print("[CORE] END")