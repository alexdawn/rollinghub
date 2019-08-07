from rollinghub import create_app
import waitress
import os
from paste.translogger import TransLogger
import logging


logging.warning("Running on port {}".format(os.environ['PORT']))
app = create_app()
waitress.serve(TransLogger(app), port=os.environ['PORT'])
