#!/usr/bin/env python

# standard lib
from concurrent.futures import ThreadPoolExecutor
from os import remove
from os.path import dirname, isfile, join, realpath
import datetime
import logging
import queue
import time

# global vars
from fc import (MAX_WORKERS,
                RATE_LIMIT,
                RATE_LIMIT_REMAINING,
                REPROCESS,
                SEED,
                TEST_FLAG)

# local modules
import fc.emails as emails
import fc.person as person
import fc.scheduler as scheduler
import fc.utils as utils

if __name__ == '__main__':

    ###
    # datetimes
    ###

    now = datetime.datetime.now()
    # start_current_hr and start_prev_hr are in appropriate
    #   format for SQL 'YYYY-MM-DDTHH:MM:SS'
    start_current_hr = utils.hour_floor(now)

    if REPROCESS:
        # in order to reprocess do the following:
        #   set REPROCESS to True within fc/__init__.py
        #   set start_prev_hr to the start time at which data needs to be
        #     reprocessed
        #   set start_today to midnight on the same day as start_prev_hr
        start_prev_hr = datetime.datetime(2016, 6, 3, 19, 0, 0)
        start_today = datetime.datetime(2016, 6, 3, 0, 0, 0)
    else:
        start_prev_hr = start_current_hr - datetime.timedelta(hours=1)
        start_today = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)

    prev_10_days = start_today - datetime.timedelta(days=10)

    ###
    # logging
    ###

    logger = logging.getLogger()

    logger.info('Begin | process all apps from {_prev} to {_current}'
        .format(_prev=start_prev_hr, _current=start_current_hr))

    ###
    # emails
    ###

    # when pulling emails, they come back as a list of named tuples
    # [(id1, dt1, email1), (id2, dt2, email2)]

    # setup file paths
    script_dir = dirname(realpath(__file__))
    local_data_dir = join(script_dir, 'data')
    emails_10_days_file = join(local_data_dir, 'emails_10_days.json')
    emails_to_process_file = join(local_data_dir, 'emails_to_process.json')

    # remove data files if reprocessing
    if REPROCESS:
        if isfile(emails_10_days_file):
            remove(emails_10_days_file)
        if isfile(emails_to_process_file):
            remove(emails_to_process_file)

    # does the data need to be seeded?
    # if so, then we will not check for dupes within the last 10 days
    #   but instead will check dupes against what we have already processed
    # after 10 days then we will revert back to checking dupes within the last
    #   10 days as a form of caching

    # get unique emails seen in the last hour
    emails_hr_unique = emails.get_unique_emails(start_prev_hr,
                                                start_current_hr)
    # seed data
    if SEED:
        # if have processed files prior
        if isfile(emails_to_process_file):
            emails_processed = \
                    utils.read_json_as_namedtuple(emails_to_process_file,
                                                  'Emails')

            # dedupe the emails in the last hour against what we have seen
            #   in the past
            # the final list is that which will be used for query purposes
            emails_to_process = utils.compare_namedtuples(emails_hr_unique,
                                                          emails_processed,
                                                          ('id', 'email'))
        # if have never processed files before
        else:
            emails_to_process = emails_hr_unique

        utils.write_namedtuple_as_json(emails_to_process_file,
                                       emails_to_process, 'a')
    # no need to continue seeding data
    else:
        # if just completed seeding the data then emails_10_days.json has
        #   not been created
        if isfile(emails_10_days_file):
            # if first hour of the day then write out all email addresses
            #   seen in the last 10 days
            # only need to run this once a day
            # will append emails seen over the course of the day to this list
            if start_current_hr.hour == 1:
                emails_10_days = emails.get_unique_emails(prev_10_days,
                                                          start_today)
                # write the named tuples to disk as json
                utils.write_namedtuple_as_json(emails_10_days_file,
                                               emails_10_days, 'w')
            else:
                # read the json in as a list of named tuples
                emails_10_days = \
                        utils.read_json_as_namedtuple(emails_10_days_file,
                                                      'Emails')
        # create the emails_10_days.json file
        else:
            emails_10_days = emails.get_unique_emails(prev_10_days,
                                                      start_today)
            # write the named tuples to disk as json
            utils.write_namedtuple_as_json(emails_10_days_file,
                                           emails_10_days, 'w')

        # add emails seen since the beginning of the day until the start hour
        emails_today = emails.get_unique_emails(start_today, start_prev_hr)
        emails_10_days += emails_today

        # dedupe the emails in the last hour against what we have seen
        #   the last 10 days and against what we have seen today up to now
        # the final list is that which will be used for query purposes
        emails_to_process = utils.compare_namedtuples(emails_hr_unique,
                                                      emails_10_days,
                                                      ('id', 'email'))
        # write to the file (overwrite)
        utils.write_namedtuple_as_json(emails_to_process_file,
                                       emails_to_process,
                                       'w')

    if TEST_FLAG:
        from random import sample
        # for testing, get 10 random Email named tuples
        emails = [k for k in sample(emails_to_process, 10)]

        # make sure we always have at least one 200
        from collections import namedtuple
        Email = namedtuple('Email', ['id', 'dt', 'email'])
        emails.append(Email('000', '2016-01-01 00:00:00',
                            'bart@fullcontact.com'))
    else:
        emails = emails_to_process

    ###
    # setup and process queue
    ###

    # create an instance of a priority queue
    q = queue.PriorityQueue()

    # create a thread pool
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:

        # wait __ seconds before starting so that the entire
        #   queue can be built up
        execute_time = time.time() + 10

        # add to queue
        for i, email in enumerate(emails):
            logger.info(('Queue | email: {_email}  id: {_id}'
                        ' | add {_email} to the queue')
                    .format(_email=email.email, _id=email.id))
            q.put((execute_time, i, email.id,
                   email.dt, email.email))
            # update execute_time by __ seconds
            if TEST_FLAG:
                execute_time += 2
            else:
                # subtracting 100 gives 0.1 seconds of padding
                execute_time += (RATE_LIMIT_REMAINING/(RATE_LIMIT-100))

        # process the queue
        if TEST_FLAG:
            scheduler.process_queue(q, pool, utils.print_email)
        else:
            scheduler.process_queue(q, pool, person.process_one_email)

    logger.info('End | process all apps from {_prev} to {_current}'
            .format(_prev=start_prev_hr, _current=start_current_hr))
