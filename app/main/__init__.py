from flask import Blueprint
import evertcore.websockets

# main application blueprint
main = Blueprint('main', __name__, static_folder='static', template_folder='templates')

# imported at bottom to prevent circular importing
from . import views
