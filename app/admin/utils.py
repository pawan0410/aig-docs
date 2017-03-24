from decorator import decorator

from flask_login import current_user
from werkzeug.exceptions import Forbidden


@decorator
def admin_required(f, *args, **kwargs):
    try:
        is_admin = current_user.is_admin
        if not is_admin:
            raise Forbidden()
    except AttributeError:
        raise Forbidden()

    return f(*args, **kwargs)

