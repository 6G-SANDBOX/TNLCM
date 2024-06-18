from flask_mail import Mail

mail = Mail()

def init_mail(app):
    """
    Initializes Flask-Mail extension with the given Flask application

    :param app: Flask application instance to initialize the mail extension with, ``Flask``
    """
    mail.init_app(app)