import json
import os
import urllib.request as request

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
