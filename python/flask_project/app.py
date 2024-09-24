from flask import Flask, url_for, jsonify, request, g
from views.general_views import general_view
import argparse, os, time, csv, uuid
from utils import Logger, do_data_screening, get_return_payload
from pathlib import Path

logger = Logger.getInstance()

RUN_IN_DEBUG_MODE = os.environ.get('RUN_IN_DEBUG_MODE', False)
PORT = os.environ.get("PORT", 5500)
LOG_DIR = os.environ.get("LOG_DIR", "./logs")
REQUEST_LOGS_PATH =  os.environ.get("REQUEST_LOG_PATH", "request_logs.csv")
RESPONSE_LOGS_PATH =  os.environ.get("RESPONSE_LOG_PATH", "response_logs.csv")

app=Flask(__name__)
app.secret_key="<generate-a-really-long-secret-key>"
app.register_blueprint(general_view)

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route("/sitemap")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append(url)
    # links is now a list of url, endpoint tuples
    return get_return_payload(True, "OK", links)

@app.before_request
def before_request_func():    
    g.id = uuid.uuid4()
    req = {
        "id" : g.id,
        "timestamp" : time.time(),
        "remote_address" : request.remote_addr,
        "method" : request.method,
        "path" : request.path,
        "headers" : dict(request.headers),
        "args" : dict(request.args),
        "data" : request.data
    }

    logger.info(f"Incoming Request --> {g.id}")

    if not os.path.exists(REQUEST_LOGS_PATH):
        Path(REQUEST_LOGS_PATH).touch()

        with open(REQUEST_LOGS_PATH,"w") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(req.keys()))
            writer.writeheader()

    with open(REQUEST_LOGS_PATH, "a") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(req.keys()))
        writer.writerow(req)

@app.after_request
def after_request_func(response):
    resp = {
        "id" : g.id,
        "path" : request.path,
        "timestamp" : time.time(),
        "status" : response._status,
        "status_code" : response._status_code,
        "direct_passthrough" : response.direct_passthrough,
        "response" : response.response,
        "headers" : dict(response.headers),
    }

    logger.info(f"Outgoing Response --> {g.id}")

    if not os.path.exists(RESPONSE_LOGS_PATH):
        Path(RESPONSE_LOGS_PATH).touch()

        with open(RESPONSE_LOGS_PATH,"w") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(resp.keys()))
            writer.writeheader()

    with open(RESPONSE_LOGS_PATH, "a") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(resp.keys()))
        writer.writerow(resp)
    return response

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--PORT', help = "port to run", default = PORT)
    args = parser.parse_args()

    app.run(debug = RUN_IN_DEBUG_MODE, host='0.0.0.0', port=args.PORT)

