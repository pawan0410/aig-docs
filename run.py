"""
Run application
"""

from app.application import application

application = application('production')

if __name__ == '__main__':
    application.run(host='0.0.0.0')

