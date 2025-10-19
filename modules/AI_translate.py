__plugin__ = {
    "name": "AI Translator",
    "description": "nllb-200 переводчик",
    "type": "text_modificator" ,
    "run_mode": 0, #0 - standart,  1 - thread, 2 - multiprocessing    
    "first_load": True,
    "autorun": True
}

from transformers import pipeline
from langdetect import detect
import torch #нужно для автоустановки зависимостей при запуске модуля!!!

class AiTr:
    def __init__(self):
        #self._lock = threading.Lock()  # блокируем доступ для потокобезопасности
        self.translator = pipeline(
            task="translation",
            model="facebook/nllb-200-distilled-600M",   
            tgt_lang="rus_Cyrl",
            #device=0  # если есть GPU
        )     
        
    def translate(self, msg):
        
        #with self._lock: 
            src = str(detect(msg["clear_msg"]))  # вернёт 'fr'
            #print("SRC:",src)
            if src == "ru":
                msg["translate"] = msg["clear_msg"]
                msg["orig_lang"] = src
                return
            lang_map = {
                "af": "afr_Latn", "am": "amh_Ethi", "ar": "ara_Arab", "as": "asm_Beng",
                "az": "azj_Latn", "be": "bel_Cyrl", "bg": "bul_Cyrl", "bn": "ben_Beng",
                "bs": "bos_Latn", "ca": "cat_Latn", "ceb": "ceb_Latn", "ckb": "ckb_Arab",
                "cs": "ces_Latn", "cy": "cym_Latn", "da": "dan_Latn", "de": "deu_Latn",
                "el": "ell_Grek", "en": "eng_Latn", "eo": "epo_Latn", "es": "spa_Latn",
                "et": "est_Latn", "eu": "eus_Latn", "fa": "pes_Arab", "fi": "fin_Latn",
                "fil": "tgl_Latn", "fr": "fra_Latn", "gl": "glg_Latn", "gu": "guj_Gujr",
                "ha": "hau_Latn", "he": "heb_Hebr", "hi": "hin_Deva", "hr": "hrv_Latn",
                "hu": "hun_Latn", "hy": "hye_Armn", "id": "ind_Latn", "ig": "ibo_Latn",
                "is": "isl_Latn", "it": "ita_Latn", "ja": "jpn_Jpan", "jv": "jav_Latn",
                "ka": "kat_Geor", "kk": "kaz_Cyrl", "km": "khm_Khmr", "kn": "kan_Knda",
                "ko": "kor_Hang", "lb": "ltz_Latn", "lo": "lao_Laoo", "lt": "lit_Latn",
                "lv": "lav_Latn", "mg": "mlg_Latn", "mk": "mkd_Cyrl", "ml": "mal_Mlym",
                "mn": "khk_Cyrl", "mr": "mar_Deva", "ms": "zsm_Latn", "my": "mya_Mymr",
                "ne": "npi_Deva", "nl": "nld_Latn", "no": "nob_Latn", "ny": "nya_Latn",
                "pa": "pan_Guru", "pl": "pol_Latn", "ps": "pus_Arab", "pt": "por_Latn",
                "ro": "ron_Latn", "ru": "rus_Cyrl", "sd": "snd_Arab", "si": "sin_Sinh",
                "sk": "slk_Latn", "sl": "slv_Latn", "sm": "smo_Latn", "sn": "sna_Latn",
                "so": "som_Latn", "sq": "als_Latn", "sr": "srp_Cyrl", "su": "sun_Latn",
                "sv": "swe_Latn", "sw": "swh_Latn", "ta": "tam_Taml", "te": "tel_Telu",
                "th": "tha_Thai", "tl": "tgl_Latn", "tr": "tur_Latn", "uk": "ukr_Cyrl",
                "ur": "urd_Arab", "uz": "uzn_Latn", "vi": "vie_Latn", "xh": "xho_Latn",
                "yi": "ydd_Hebr", "yo": "yor_Latn", "zh-cn": "zho_Hans", "zh-tw": "zho_Hant",
                "zu": "zul_Latn"
            }
            
            src_lang = lang_map.get(src, "eng_Latn")
            #print("SRC_LANG:",src_lang)
            
            tr= self.translator(str(msg["clear_msg"]),src_lang=src_lang)
            #print("[AI translate] ", tr[0]["translation_text"])
            msg["translate"] = tr[0]["translation_text"]
            msg["orig_lang"] = src
            
            print("[HOOK translate]",msg["translate"])
            
aitr=AiTr();  
 
class hook:
    def add_com(data):
        aitr.translate(data)
    #def test_text_modificator(data):
    #    return "[HOOK]" + data
    
def run():
    print("["+__name__.split(".")[-1]+"] OK")     

def save():
    print("Привет из testm")

def load():
    print("Привет из testm")


