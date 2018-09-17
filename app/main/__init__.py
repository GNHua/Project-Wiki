from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors, forms
from ..models import Permission


@main.app_context_processor
def inject_permissions_and_search_bar():
    return dict(Permission=Permission, searchform_nav=forms.SearchForm())
