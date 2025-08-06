import time, sys
from flask import Flask, render_template, request, jsonify, Blueprint
import requests
from flask_socketio import SocketIO, disconnect as socketDisconnect, join_room
import base64, os, json, string, random, argparse, multiprocessing, traceback, psutil, pickle
from utils import Logger
import uuid, psutil, datetime
from statistics import mean

for directory in ["./logs"]:
    if not os.path.isdir(directory):
        print(f"Creating dir {directory}")
        os.makedirs(directory)

logger = Logger.getInstance()

global clients
clients = {}

global sessions
sessions = {}

global room_url
room_url = ""

sio = None
engine_logs = True

def queueMonitor():

    while True:
        try:
            if not buff.empty():
                logger.info("Processing task...")
                ticket = buff.get()
                logger.info("TICKET: {}".format(ticket))
        except Exception as e:
            logger.error("Error in executing task")
            logger.error(e)
            traceback.print_exc()

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def b64Decode(base64String):
    return base64.b64decode(base64String.split(",")[1])

def get_return_payload(status, message = "", data = None):
    return jsonify({"status": status, "message":message, "data" : data})

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

logger.info("Starting with logs.")
sio = SocketIO(app, logger=True, engineio_logger=True,  async_mode="eventlet", cors_allowed_origins="*", header = [{"Strict-Transport-Security":"max-age=31536000"}])

bp = Blueprint('frontend', __name__)

@bp.after_request
def changeserverheader(response):
    response.headers['server'] = 'none'
    return response

@sio.on_error_default
def default_error_handler(e):
    print("Error: {}".format(e))
    sio.stop()

@sio.on('connect')
def connect():
    #logger.info(request.args)
    if not "uid" in request.args:
        socketDisconnect()
    
    logger.info("Existing Clients")
    logger.info(clients)
    clients[request.args.get("space_id")][request.args.get("uid")]= request.sid
    sio.emit("message","Ack.: Connection accepted", room=request.sid)

@sio.on('join')
def join(message):
    #?print(message)
    username = message['username']
    room = message['room']
    join_room(room)
    #print('RoomEvent: {} has joined the room {}\n'.format(username, room))
    sio.emit('wsack',{"type":"room_accept", "room":room}, room = request.sid )
    sio.emit('wsready', {"username": username}, to=room, skip_sid=request.sid)

def emit_error(message, sid):
        logger.error(message)
        sio.emit("backend-error", data = message, room = sid)

@sio.on('data')
def transfer_data(message):
    clientUid = request.args.get("uid")

    logger.info(message)

    buff.put(message)

@sio.on('disconnect')
def disconnect():
    uid = request.args.get("uid")
    print(f"popping from clients - {uid}")
    clients.pop(uid, None) 
    print(clients)
    RECORDING_SESSION = None
    # sessions.remove()
    logger.info('disconnect ')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--PORT', help = "port to run", default = 5050)
    args = parser.parse_args()

    manager = multiprocessing.Manager()
    shareWithProcesses = manager.dict()
    clients = manager.dict()
    buff = manager.Queue()

    queueMonitor = multiprocessing.Process(name = "queueMonitor", target = queueMonitor)
    queueMonitor.start()
       
    sio.run(app, debug = True, log_output = True, port=args.PORT, host='0.0.0.0',use_reloader=False)
