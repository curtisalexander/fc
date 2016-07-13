from collections import namedtuple
import datetime
import json
import logging
import os
import random
import time

logger = logging.getLogger()

def compare_namedtuples(items_base, items_compare, dedupe):
    """ Return named tuples in a base list against a comparison list

    Comparison is based on elements of the parameter dedupe

    This function is too clever >:-(

    Parameters
    ----------
    items_base : list containing named tuples that is to be deduped
        assumes items_base has already been deduped

    items_compare: list containing named tuples to be compared against

    dedupe : tuple containing the named tuple elements to dedupe on
        akin to the 'by' statement in a sort procedure

    Returns
    -------
    output : a filtered list of named tuples
    """
    # exec and metaprogramming hacks to dynamically create code
    # assuming the parameter dedupe is the tuple ('a', 'b', 'c')
    #   then the resulting strings would become
    #       dedupe_code ==> (item.a, item.b, item.c)
    #       append_code ==> items_compare_sub.append((item.a, item.b, item.c))
    #       item_code ==> _item = (item.a, item.b, item.c)
    for i, d in enumerate(dedupe):
        if i == 0:
            dedupe_code = '(item.{}'.format(d)
            item_code = '_item = (item.{}'.format(d)
        elif i > 0:
            dedupe_code += ', item.{}'.format(d)
            item_code += ', item.{}'.format(d)

    dedupe_code += ')'
    item_code += ')'

    append_code = 'items_compare_sub.append({})'.format(dedupe_code)

    # convert the items_compare list to just a list of tuples
    #   based on the elements of the parameter dedupe
    # assuming the parameter dedupe is the tuple ('a', 'b', 'c')
    #   then the code that is to be executed would be
    #       items_compare_sub.append((item.a, item.b, item.c))
    items_compare_sub = []
    for item in items_compare:
        loc = locals()
        glb = { }
        exec(append_code, glb, loc)

    # compare items in items_base against items_compare_sub
    # the comparison is just based on a subset of the tuple elements
    #   in the named tuple
    # assuming the parameter dedupe is the tuple ('a', 'b', 'c')
    #   then the code that is to be executed would be
    #       _item = (item.a, item.b, item.c)
    # the tuple _item is compared against the tuples within items_compare_sub
    # if there is not a match, then the original named tuple is written to
    #   the list named output
    output = []
    for item in items_base:
        loc = locals()  # metaprogramming hack
        glb = { }  # metaprogramming hack
        exec(item_code, glb, loc)  # metaprogramming hack
        _item = loc['_item']  # tuple with just the elements of dedupe
        if _item not in items_compare_sub:
            output.append(item)

    return output


def get_api_key(api_file):
    """ Return an API key from the user's home directory

    Parameters
    ----------
    api_file : file where api key or password is located
        assumes the file is a dotfile in the user's home directory

    Returns
    -------
    api_key : the actual api key or password
    """
    with open('{_home}/.{_api_file}'.format(_home = os.path.expanduser('~'),
                                            _api_file = api_file)) as f:
        api_key = f.read().replace('\n', '')
    return api_key


def hour_floor(dt):
    """ Round a datetime down to the nearest hour

    For example if it is 2015-05-01 14:45:07, returns 2015-05-01 14:00:00

    Parameters
    ----------
    dt : a datetime object

    Returns
    -------
    hour_floor : a datetime rounded down to the nearest hour
    """
    seconds_in_day = (dt - dt.min).seconds
    # // is floor division
    hours = seconds_in_day // (60*60)
    hour_floor = datetime.datetime(dt.year, dt.month, dt.day, hours, 0, 0)
    return hour_floor


def print_email(email):
    """ Print the email address to be processed

    Useful for testing the processing of the priority queue rather than
    hitting the API endpoint.

    Parameters
    ----------
    email : email address

    Returns
    -------
    email : email address
        returns the email address to test the result() method from a thread
        pool instance
    """
    logger.info('Print | print {email}'.format(email=email))
    return email


def random_lines(file_path, num_lines):
    """ Randomly sample lines from a file

    The function reads the entire file into a list, so beware of large files!

    Parameters
    ----------
    file_path : path to the file that will be sampled

    num_lines : number of lines from the file to be sampled

    Returns
    -------
    rand_lines : a list containing a random sample of lines from the file
    """
    with open(file_path) as f:
        rand_lines = random.sample(f.read().splitlines(), num_lines)

    return rand_lines


def read_json_as_namedtuple(file_path, nt):
    """ Read a file of newline delimited json into a list of named tuples

    Parameters
    ----------
    file_path : full path to the file to write as json

    nt : name of the named tuple

    Returns
    -------
    list_nt : a list of named tuples
    """
    with open(file_path, 'r') as f:
        items_json = f.read().splitlines()

        list_nt = []
        for item in items_json:
            item_nt = json.loads(item,
                object_hook=lambda d: namedtuple(nt, d.keys())(*d.values()))
            list_nt.append(item_nt)
    return list_nt


def sort_text(text_path):
    """ Sort a text file in place

    Useful for scanning for duplicates

    Parameters
    ----------
    f : file handle

    Returns
    -------
    null
    """
    with open(text_path, 'r') as f:
        for line in sorted(f):
            print(line, end='')


def unique_namedtuples(items, dedupe):
    """ Extract unique named tuples based on a subset of elements

    Comparison is based on elements of the parameter dedupe

    This function is too clever >:-(

    For instance, for a list with the named tuples

        items = [(id=2, action='eat', food='apple'),
                 (id=2, action='eat', food='banana'),
                 (id=3, action='prep', food='carrot')]

    and dedupe parameter

        dedupe = ('id', 'action')

    only keep the unique tuples based on id and action

        output = [(id=2, action='eat', food='apple'),
                  (id=3, action='prep', food='carrot')]


    Parameters
    ----------
    items : list containing named tuples

    dedupe : tuple containing the named tuple elements to dedupe on
        akin to the 'by' statement in a sort procedure

    Returns
    -------
    output : a filtered list of named tuples
    """
    seen = set()
    output = []

    # exec and metaprogramming hacks to dynamically create code
    # assuming the parameter dedupe is the tuple ('a', 'b', 'c')
    #   then the resulting strings would become
    #       dedupe_code ==> (item.a, item.b, item.c)
    #       seen_code ==> seen.add((item.a, item.b, item.c))
    #       item_code ==> _item = (item.a, item.b, item.c)
    for i, d in enumerate(dedupe):
        if i == 0:
            dedupe_code = '(item.{}'.format(d)
            item_code = '_item = (item.{}'.format(d)
        elif i > 0:
            dedupe_code += ', item.{}'.format(d)
            item_code += ', item.{}'.format(d)

    dedupe_code += ')'
    item_code += ')'

    seen_code = 'seen.add({})'.format(dedupe_code)

    # the comparison is just based on a subset of the tuple elements
    #   in the named tuple
    # assuming the parameter dedupe is the tuple ('a', 'b', 'c')
    #   then the code that is to be executed would be
    #       _item = (item.a, item.b, item.c)
    # the tuple _item is compared against what has been seen before
    # if there is not a match, then the original named tuple is written to
    #   the list named output
    for item in items:
        loc = locals()  # metaprogramming hack
        glb = { }  # metaprogramming hack
        exec(item_code, glb, loc)  # metaprogramming hack
        _item = loc['_item']  # tuple with just the elements of dedupe
        if _item not in seen:
            loc = locals()  # metaprogramming hack
            glb = { }  # metaprogramming hack
            exec(seen_code, glb, loc)  # metaprogramming hack
            output.append(item)
    return output


def write_json(json_data, json_path):
    """ Write JSON content within a requests object to a file

    Parameters
    ----------
    json_data : json

    json_path : full path to the json file

    Returns
    -------
    null
    """
    with open(json_path, 'w') as j:
        json.dump(json_data, j)
        j.write('\n')


def write_namedtuple_as_json(file_path, list_nt, file_mode):
    """ Write a list of named tuples as newline delimited json

    Parameters
    ----------
    file_path : full path to the file to write as json

    list_nt : list of named tuples to write

    file_mode : file mode

    Returns
    -------
    null
    """
    with open(file_path, file_mode) as f:
        for nt in list_nt:
            json.dump(nt._asdict(), f)
            f.write('\n')
