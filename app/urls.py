"""
Urls
"""

from app.core import include

default_module = include('default.views', '/')
admin_module = include('admin.views', '/admin')
main_module = include('main.views', '/main')

modules = (
    default_module,
    admin_module,
    main_module,
)


