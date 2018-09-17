import os, logging, time
from .. import basedir


# Because Gunicorn does not run on Windows, a pure Python WSGI 
# server, called Waitress, is used for Windows.
# Waitress sends its logging output (including application exception 
# renderings) to the Python logger object named waitress. 
# Details: https://docs.pylonsproject.org/projects/waitress/en/latest/#logging
logger = logging.getLogger('waitress')
logger_filename = os.path.join(basedir, 
                               'Project_Wiki_Data', 
                               'log', 
                               '{}.log'.format(time.strftime('%Y%m%d')))
format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=logger_filename,
                    filemode='a',
                    format=format,
                    level=logging.INFO)