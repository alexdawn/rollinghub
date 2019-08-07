from rollinghub import create_app
import waitress
import os
from paste.translogger import TransLogger

app = create_app()
waitress.serve(TransLogger(app), port=os.environ['PORT'])