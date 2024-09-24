from flask import Blueprint
import json
from utils import get_return_payload

general_view = Blueprint('general_bp', __name__)

@general_view.route("/", methods = ['GET'])
def home():
    return get_return_payload(True, "Welcome to flask server!")

@general_view.route("/health", methods  = ['GET'])
def health():
    return get_return_payload(True, "OK")


@general_view.route("/version", methods  = ['GET'])
def statusz():
    version = None
    with open("./version.sha", "r") as fp:
        version = str(fp.read())
    return get_return_payload(True, "OK", version)


