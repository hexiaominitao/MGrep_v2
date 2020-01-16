from flask import (Blueprint, jsonify, request)
from flask_cors import CORS

api_v2 = Blueprint('api_v2', __name__, url_prefix="/api")
CORS(api_v2)

