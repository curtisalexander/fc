# standard library
from os.path import join
import datetime
import logging
import time

# third party
import requests

# local modules
import fc.utils as utils


logger = logging.getLogger()

# WARNING level and worse for requests
logging.getLogger('requests').setLevel(logging.WARNING)

def process_one_email(q, count, id_val, dt, email):
    """ Submit an email address to the Full Contact Person API and process
    the responses

    Process the response object based on the return status code

    Parameters
    ----------
    q : an instance of a Priority Queue

    count : the count from the original placement in the queue

    id_valm : id associated with email address

    dt : datetime when the id was created

    email : email address

    Returns
    -------
    null
    """
    # import global
    from fc import (OUT_DIR,
                    RETRY_TIME)

    dt = dt.split()[0]

    logger.info(('Post | email: {_email}  id: {_id}'
                 ' | {_email} posted to the Full Contact Person API')
            .format(_email=email, _id=id_val))
    # blocking operation - not to worry as each request is
    # its own thread
    r = query_person('email', email)

    # log results
    # if status code is not in 200, 202, 404 then the
    #   header values are not available
    if r.status_code in (200, 202, 404):
        post_msg = ('Return | email: {_email}  id: {_id}'
                    ' | return status code: {_status}'
                    ' | datetime: {_dt}'
                    ' | rate limit: {_rl} calls / 60 seconds'
                    ' | rate limit remaining: '
                    '{_rlrem} calls / {_rlres} seconds')
        post_msg = post_msg.format(_email=email,
                                   _id=id_val,
                                   _status=r.status_code,
                                   _dt=r.headers['Date'],
                                   _rl=r.headers['X-Rate-Limit-Limit'],
                                   _rlrem=r.headers['X-Rate-Limit-Remaining'],
                                   _rlres=r.headers['X-Rate-Limit-Reset'])
    else:
        post_msg = ('Return | email: {_email}  id: {_id}'
                    ' | return status code: {_status}')
        post_msg = post_msg.format(_email=email,
                                   _id=id_val,
                                   _status=r.status_code)
    logger.info(post_msg)
    out_file = join(OUT_DIR,
            '{_dt}_{_id}.json'.format(_dt=dt,
                                       _id=id_val))
    logging_desc = ('Results | email: {_email}  id: {_id}'
                    ' | status {_status}')
    logging_desc = logging_desc.format(_email=email,
                                       _id=id_val,
                                       _status=r.status_code)
    # process responses
    if r.status_code == 200:
        logging_desc += ' | success | writing to {_dt}_{_id}.json'
        logging_desc = \
                logging_desc.format(_dt=dt, _id=id)
        logger.info(logging_desc)

        utils.write_json(r.json(), out_file)
    elif r.status_code == 202:
        logging_desc += (' | request is being processed'
                         ' | adding email: {_email}  id: {_id}'
                         ' back to the queue and waiting {_retry}'
                         ' seconds before resubmitting')
        logging_desc = logging_desc.format(_email=email,
                                           _id=id_val,
                                           _retry=RETRY_TIME)
        logger.info(logging_desc)

        utils.write_json(r.json(), out_file)

        # adding back to the queue
        execute_time = time.time() + RETRY_TIME
        q.put((execute_time, count, id_val, dt, email))
    elif r.status_code == 400:
        logging_desc += ' | bad / malformed request'
        logger.info(logging_desc)

        utils.write_json(r.json(), out_file)
    elif r.status_code == 403:
        logging_desc += (' | forbidden'
                         ' | api key is invalid, missing, or exceeded quota')
        logger.info(logging_desc)

        utils.write_json(r.json(), out_file)
    elif r.status_code == 404:
        logging_desc += (' | not found'
                         ' | person searched in the past 24 hours'
                         ' and nothing was found')
        logger.info(logging_desc)

        utils.write_json(r.json(), out_file)
    elif r.status_code == 405:
        logging_desc += (' | method not allowed'
                         ' | queried the API with an unsupported HTTP method')
        logger.info(logging_desc)

        utils.write_json(r.json(), out_file)
    elif r.status_code == 410:
        logging_desc += ' | gone | the resource cannot be found'
        logger.info(logging_desc)

        utils.write_json(r.json(), out_file)
    elif r.status_code == 422:
        logging_desc += ' | invalid ==> invalid or missing API query parameter'
        logger.info(logging_desc)

        utils.write_json(r.json(), out_file)
    elif r.status_code == 500:
        logging_desc += (' | internal server error'
                         ' | an unexpected error at Full Contact; please contact'
                         'support@fullcontact.com')
        logger.info(logging_desc)

        utils.write_json(r.json(), out_file)
    elif r.status_code == 503:
        logging_desc += (' | service temporarily down'
                         ' | check the Retry-After header')
        logger.info(logging_desc)

        utils.write_json(r.json(), out_file)


def query_person(lookup, lookup_value):
    """ Query the Full Contact Person API

    Parameters
    ----------
    lookup : lookup type
        possible values include email, phone, or twitter handle

    lookup_value : lookup value associated with lookup
        for instance, if the type of lookup is email then provide the
        email string

    Returns
    -------
    r : requests object
    """

    API_KEY = utils.get_api_key('fc_key')
    URL = 'https://api.fullcontact.com/v2/person.json'

    headers = {'X-FullContact-APIKey': API_KEY}

    # parameters
    parameters = {'prettyPrint': 'true'}
    if lookup == 'email':
        parameters['email'] = lookup_value
    elif lookup == 'phone':
        no_dash_paren = string.maketrans('', '', '()-')
        parameters['phone'] = '+1' + lookup_value.translate(no_dash_paren)
    elif lookup == 'twitter':
        parameters['twitter'] = lookup_value
    else:
        raise ValueError('lookup should be one of email, phone, or twitter')

    # post request
    r = requests.post(URL, headers=headers, params=parameters)

    return r
