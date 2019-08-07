from rollinghub import create_app
import waitress
import os
import sys
import logging
waitress_logger = logging.getLogger('waitress')
waitress_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(filename='tmp.log')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
waitress_logger.addHandler(handler)
waitress_logger.addHandler(file_handler)

app = create_app()
waitress_logger.warning("FOO")
waitress.serve(app, port=os.environ['PORT'])