# standard lib
import logging
import os

# local imports
from .emails import *

from .person import *

from .scheduler import *

from .utils import *

###
# constants
###
RATE_LIMIT = 300  # calls per rate limit remaining
RATE_LIMIT_REMAINING = 60  # calls remaining in seconds

# if nothing can be pulled from the priority queue for __ seconds
#   then there is a timeout and the program completes
QUEUE_TIMEOUT = 60.0
MAX_WORKERS = 100  # maximum number of worker threads

# directory containing the Full Contact returned JSON
OUT_DIR = '/work/JSON Files'

# if receive a 202 response code, wait __ seconds before trying again
RETRY_TIME = 30.0

# testing
TEST_FLAG = False

# does the data need to be seeded?
# if so, then we will not check for dupes within the last 10 days
#   but instead will check dupes against what we have already processed
# after 10 days then we will revert back to checking dupes within the last
#   10 days ala a form of caching
first_execution = datetime.datetime(2016, 3, 11, 13, 0, 0)
if datetime.datetime.now() < first_execution + datetime.timedelta(days=10):
    SEED = True
else:
    SEED = False

# sometimes we need to reprocess files due to errors
REPROCESS = False

###
# logging
###
LOGNAME = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       '..',
                       'logs/fc.log')
logging.basicConfig(filename=LOGNAME,
                    format='%(asctime)s.%(msecs)03d | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
