"""
Run application
"""

from app.application import application

application = application('development')

if __name__ == '__main__':
    application.run()

