import json
import os
import urllib.request as request
import re

def print_logo():
    print(r"===================================================")
    print(r"=            _____  _____ _   _ ______            =")
    print(r"=           |  __ \|_   _| \ | |  ____|           =")
    print(r"=           | |__) | | | |  \| | |__              =")
    print(r"=           |  _  /  | | | . ` |  __|             =")
    print(r"=           | | \ \ _| |_| |\  | |____            =")
    print(r"=           |_|  \_\_____|_| \_|______|           =")
    print(r"=                    Stickers                     =")
    print(r"=                                                 =")
    print(r"===================================================")

def init_runtime(runtime):
    if not os.path.exists(runtime) and not os.path.isdir(runtime):
        os.makedirs(runtime)
    
def load_token(runtime):
    filepath = runtime + "/token"
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            return file.readline()
    else:
        with open(filepath, "w") as file:
            file.write("Введите токен сюда.")
        print('Пожалуйста, введите токен в файл "' + os.path.abspath(filepath) + '" и перезапустите бота.')
        quit()

def check_connection(url):
    try:
        request.urlopen(url, timeout=5)
        return True
    except Exception:
        pass

def try_remove_prefix(text, bot):
    mentioned = re.sub(r'^((\[(\S+?)\|\S+?\])|(@(\S+)( \(\S+?\))?))', r'\3\5', text, re.IGNORECASE + re.DOTALL)
    if len(mentioned) != len(text):
        domain = mentioned.split()[0].lower()
        if domain == "id{}".format(bot.get_id()) or domain == bot.get_domain():
            return " ".join(mentioned.split()[1:])
        else:
            return text
    elif text.lower().startswith(bot.get_prefix()):
        return text[len(bot.get_prefix()):].strip()
    else:
        return text

def decode_text(text):
    return text.replace(r'&lt;', r'<').replace(r'&gt;', r'>').replace(r'&quot;', r'"').replace(r'&amp;', r'&')