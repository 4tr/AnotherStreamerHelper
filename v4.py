print("[CORE] INIT")
import time
import funcs

print("[CORE] FUNCS OK")
funcs.load_all_modules()

from data import app_data
hook = app_data.hook

print("[CORE] all loads init cycler")

try:
    while app_data.stop == False:
        time.sleep(5)
except KeyboardInterrupt:
    print("Цикл прерван пользователем")        
   
except Exception as e:
    print(f"Произошла ошибка: {e}")
   
finally:
    #нужно добавить вызов сохранялок
    print("[*] Сохраняю данные перед выходом...")
        

print("[CORE] END")

