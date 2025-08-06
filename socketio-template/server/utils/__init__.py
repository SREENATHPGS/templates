import logging, os

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