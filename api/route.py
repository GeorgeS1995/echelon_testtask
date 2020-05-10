from .view import NetworkMethodView
from flask import Blueprint

bp = Blueprint('api_v1', __name__, url_prefix='/api/v1/')
bp.add_url_rule('/network', view_func=NetworkMethodView.as_view('network'))
