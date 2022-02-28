from flask import Blueprint

app = Blueprint('app', __name__, template_folder='templates', url_prefix='/')

from linkedin.app import index
