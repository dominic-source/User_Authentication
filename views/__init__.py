from flask import Blueprint
app_views = Blueprint('app_views', __name__)

from views.user import *
from views.organization import *
