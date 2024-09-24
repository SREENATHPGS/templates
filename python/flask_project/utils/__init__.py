import logging, os, string, random
from flask import jsonify

def create_dirs(dirs):
    if type(dirs) == str:
        dirs = [dirs]

    for directory in dirs:
        if not os.path.isdir(directory):
            print(f"Creating dir {directory}")
            os.makedirs(directory)

def get_logger():
    log_format =logging.Formatter('%(asctime)s-%(process)d-%(levelname)s-%(message)s')
    logger = logging.getLogger() 
    logger.setLevel(logging.INFO)
    create_dirs("./logs/")
    fileHandler = logging.FileHandler("./logs/app.log")
    fileHandler.setFormatter(log_format)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(log_format)
    logger.addHandler(consoleHandler)

    return logger


class Logger:
 
    __shared_instance = get_logger()
 
    @staticmethod
    def getInstance():
        """Static Access Method"""
        if not isinstance(Logger.__shared_instance, logging.RootLogger):
            Logger()
        return Logger.__shared_instance
 
    def __init__(self):
        """virtual private constructor"""
        if not isinstance(self.__shared_instance, logging.RootLogger):
            raise Exception("This class is a singleton class !")
        else:
            Logger.__shared_instance = self


def replace_banned_charecters(st):
    cs =  "".join(["_" if s in ["<", ">"] else s  for s in st])
    print(cs)
    return cs

def do_data_screening(d):
    out = {}
    for key, value in d.items():
        out[replace_banned_charecters(key)] = replace_banned_charecters(value)
    
    # logger.info(f"After data screening : {out}")

    return out

def get_return_payload(status, message = "", data = None):
    return jsonify({"status": status, "message":message, "data" : data})

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))