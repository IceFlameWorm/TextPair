from functools import wraps
from flask import request, abort

import os

AUTHED_TOKEN_TXT = os.path.join(os.path.dirname(__file__), 'authed_token.txt')
def get_authed_token():
    with open(AUTHED_TOKEN_TXT, 'r', encoding = 'utf-8') as f:
        authed_token = f.read().strip()
    return authed_token

def access_token_required(fun):
    @wraps(fun)
    def _fun(*args, **kwargs):
        access_token = request.args.get('access_token')
        authed_token = get_authed_token()
        if access_token != authed_token:
            abort(401)
        return fun(*args, **kwargs)

    return _fun