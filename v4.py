
























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
    print("[*] Сохраняю(пока нет) данные перед выходом...")
        

print("[CORE] END")













exit()




def parse_emotes_tag(emotes_tag, message_text):
    """
    emotes_tag: строка как "25:0-4,1902:6-10"
    message_text: полный текст сообщения
    Возвращает список кортежей (emote_id, start_idx, end_idx, emote_text)
    """
    print(emotes_tag)
    print(message_text)
    result = []
    if not emotes_tag:
        return result    
    
    for item in emotes_tag.split('/'):  # иногда несколько наборов через '/' 
        #print("pair",pair)
        emote_id, ranges = item.split(':')
        for rang in ranges.split(','):            
            if not rang:
                continue
            start, end = rang.split('-')
            start = int(start)
            end = int(end)
            emote_text = message_text[start:end+1]
            result.append((emote_id, start, end, emote_text))
    return result

def sort_emote_item(ee):
    if len(ee) == 0:
        return []
    e = ee.copy()
    ret = []
    ret.append(e[0])
    del e[0]
    print("___")
    print(e)
    if len(e) == 0:
        return ret
    for ki,i in enumerate(e): 
        print('__',i)           
        for kr,r in enumerate(ret):    
            if i[1] > r[2]:
                print("-", kr, i)
                
                ret.insert(kr,i)
                #del e[ki]
                break
    return ret


#t= [3,3,3,3,3,4]
#for k,v in enumerate(t):
#    print("k",k,"_v-",v)
#exit()    
e = "emotesv2_5d523adb8bbb4786821cd7091e47da21:0-6,8-14,34-40,42-48/160402:16-23,25-32"
e = "305954156:14-21,23-30,32-39,41-48"

[('emotesv2_5d523adb8bbb4786821cd7091e47da21', 0, 6, 'PopNemo'), 
 ('emotesv2_5d523adb8bbb4786821cd7091e47da21', 8, 14, 'PopNemo'), 
 ('emotesv2_5d523adb8bbb4786821cd7091e47da21', 34, 40, 'PopNemo'), 
 ('emotesv2_5d523adb8bbb4786821cd7091e47da21', 42, 48, 'PopNemo'), 
 ('160402', 16, 23, 'SabaPing'), 
 ('160402', 25, 32, 'SabaPing')]
[('305954156', 14, 21, 'PogChamp'), 
 ('305954156', 23, 30, 'PogChamp'), 
 ('305954156', 32, 39, 'PogChamp'), 
 ('305954156', 41, 48, 'PogChamp')]



parts = {}
parts['msg'] = "PopNemo PopNemo SabaPing SabaPing PopNemo PopNemo"
parts['msg'] = "fdgdfgdfgdfdf PogChamp PogChamp PogChamp PogChamp"
ee = parse_emotes_tag(e,parts['msg'])
print(ee)
print("sort")
ee = sort_emote_item(ee) 
print(ee)
exit()                                            
for i in ee:
    ib = i[1]
    ie = i[2] + 1   
    #print(parts['msg'][ie:])
    #if ie == (len(parts['msg'])):
    #    print("ok!!!!!!!!")
    #    exit()
    parts['msg']= parts['msg'][:ie] + ">" + parts['msg'][ie:]
    parts['msg']= parts['msg'][:ib] + "<" + parts['msg'][ib:]

print(parts["msg"])
exit()
