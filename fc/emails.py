# standard lib
from operator import attrgetter
from os.path import expanduser
from collections import namedtuple

# third party
from lxml import etree as et
import pymssql

# local modules
import fc.utils as utils

def db_row_iter(crsr, arraysize=1000):
    """ Return an iterator that uses fetchmany

    Parameters
    ----------
    crsr : a database cursor

    arraysize: number of records to fetch at any one time

    Returns
    -------
    row : yields one row at a time
        meant to be used as an iterator

    Notes
    -----
    http://code.activestate.com/recipes/137270-use-generators-for-fetching-large-db-record-sets/
    """
    while True:
        rows = crsr.fetchmany(arraysize)
        if not rows:
            break
        for row in rows:
            yield row


def get_emails(time_start, time_end):
    """ Query a SQL server database to get a list of email addresses

    Parameters
    ----------
    time_start : start time for querying email addresses
        used as part of where clause when executing SQL

    time_end : end time for querying email addresses
        used as part of where clause when executing SQL

    Returns
    -------
    email_addresses : list of tuples (id, dt, email)
    """
    # Microsoft SQL Server syntax
    sql_string = '''
    select  dt
           ,id
           ,XML
    from schema.dbtable (nolock)
    where dt between '{_time_start}' and '{_time_end}'
    '''.format(_time_start=time_start, _time_end=time_end)

    # get password for SQL connection
    my_pw = utils.get_api_key('mypw')

    # establish connection
    # 'server' must match the bracketed entry name within /etc/freetds.conf
    cnxn = pymssql.connect(server='myservername:1433',
                           database='mydatabase',
                           user='DOMAIN\username',
                           password=my_pw)

    crsr = cnxn.cursor(as_dict=True)  # get a cursor
    crsr.execute(sql_string)  # execute the SQL

    Email = namedtuple('Email', ['id', 'dt', 'email'])
    email_addresses = set()  # want a set in order to remove duplicates 
    for row in db_row_iter(crsr):
        # setup xpath and namespace
            nsmap = {'ns0': 'http://custom-ns0',
                     'ns1': 'http://custom-ns1',
                     'ns2': 'http://custom-ns2'}
            email_xpath = '/ns0:some/ns1:long/ns2:xpath/ns2:email/text()'
        else:
            break

        tree = et.fromstring(row['XML'])
        try:
            # email is a list, so extract the string from the first element
            email = tree.xpath(email_xpath, namespaces=nsmap)[0]  # execute xpath query
            id_val = row['id']
            dt = row['dt'].strftime('%Y-%m-%d %H:%M:%S')
            e = Email(id_val, dt, str(email))
            email_addresses.add(e)
        except IndexError:
            pass

    return list(email_addresses)


def get_unique_emails(time_start, time_end):
    """ Get a unique list of email addresses

    Uniqueness is determined by the combination of id and email

    Parameters
    ----------
    time_start : start time for querying email addresses
        passed on and used as part of where clause when executing SQL

    time_end : end time for querying email addresses
        passed on and used as part of where clause when executing SQL

    Returns
    -------
    email_unique : list of tuples (id, dt, email) without dupes
        based on id and email
    """
    emails_dups = get_emails(time_start, time_end)

    # sort before passing off to unique_namedtuples
    #   that way the ids with the later datetimes are removed
    #   and the ids with the earliest datetime is preserved
    emails_dups = sorted(emails_dups,
                         key=attrgetter('id', 'email', 'dt'))

    # only want unique email addresses
    emails_unique = utils.unique_namedtuples(emails_dups,
                                             ('id', 'email'))

    return emails_unique
