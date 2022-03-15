from flask import Flask
import os, multiprocessing, string, random, time, argparse
import logging as logger

RUN_IN_DEBUG_MODE = os.environ.get('RUN_IN_DEBUG_MODE', False)
PORT = os.environ.get("PORT", 6000)
LOG_DIR = os.environ.get("LOG_DIR", "./logs")

if not os.path.isdir("./logs"):
    logger.info(f"Creating {LOG_DIR} dir")
    os.mkdir("./logs")

logger.basicConfig(level="INFO")


app=Flask(__name__)

app.secret_key="addYourSecretKeyHere"

global taskQueue

def getUid(noOfCharecters=6):
    chars = string.ascii_letters + string.digits
    uid = ''.join(random.choice(chars) for n in range(noOfCharecters))
    return uid

@app.route('/', methods = ['GET'])
def stats():
    return "<h1>This is a HOMEPAGE</h1>"

def queueMonitor():

    while True:
        if not taskQueue.empty():
            print("Found a task.")
            try:
                task = taskQueue.get()
            except Exception as e:
                pass
        else:
            time.sleep(0.1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--PORT', help = "port to run", default = PORT)
    args = parser.parse_args()

    manager = multiprocessing.Manager()
    taskQueue = manager.Queue()

    queueMonitor = multiprocessing.Process(name = "queueMonitor", target = queueMonitor)

    print("Starting queue monitor.")
    queueMonitor.start()
    app.run(debug=True, host='0.0.0.0', port=args.PORT)
