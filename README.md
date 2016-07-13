# Full Contact
Query the Full Contact RESTful [Person API](https://www.fullcontact.com/developer/docs/person)

Able to accomplish by 
* querying unique email addresses seen in last hour (from an internal database in order to populate a list of email addresses to query the Person API)
* comparing the email addresses to those seen in the past
    * during the initial 'seeding' time period, gathering all email addresses
    * after 'seeding' checking to see if an email address has been queried in the last 10 days
* querying the Full Contact Person API
* saving the resulting JSON

## Webhooks and Priority Queues
In lieu of using [webhooks](https://www.fullcontact.com/developer/docs/webhooks/), continually submit email addresses and poll for success criteria.  This is necessary because the Full Contact API will return a status code of `202` which corresponds to  `Accepted, Your request is currently being processed. You can check again later to see the request has been processed.`  Thus, there is a need to check back with the API to see if the email address has finished processing.  Again, the most natural (and preferred) way is to use a webhook.

Rather than use a webhook, create a [priority queue](https://docs.python.org/3/library/queue.html?highlight=queue#queue.PriorityQueue) to continually process emails.  All email addresses are added to the queue initially and sent to the Person API.  If a `202` is returned, then the email address is added back to the queue with a datetime of +30 seconds (the datetime is what sets the priority within the queue).  This is controlled by `RETRY_TIME` within `fc/__init__.py`.  The datetime associated with the next email to process on the queue is continually checked against the current time.  If the datetime associated with the next email is greater than the current time, then email address is re-sent to the Person API for consideration.  If a `200` (or any other HTTP error code) is received, then the returned JSON file is saved.  It is the combination of the priority queue with a datetime as the priority criteria and a separate process to continually check datetimes to see if processing can continue that gets around the lack of a webhook.

## API Key
Full Contact API key is required.  Place the key in the following location.

`~/.fc_key`

## Software Requirements
#### [requests](http://docs.python-requests.org/en/latest) - HTTP for Humans
```
pip install requests
```
or
```
conda install requests
```

#### [lxml](http://lxml.de) - Processing HTML and XML with Python
```
pip install lxml
```
or
```
conda install lxml
```

#### [pymssql](http://www.pymssql.org/en/latest) - simple database interface for Python to access Microsoft SQL Server
```
# use system FreeTDS
pip install pymssql

# use bundled FreeTDS
export PYMSSQL_BUILD_WITH_BUNDLED_FREETDS=1; pip install pymssql
```
or

In order to install using `conda`, first install `setuptools-git`.

```
conda skeleton pypi setuptools-git
conda build setuptools-git
conda install --use-local setuptools-git
```

Now build a skeleton for `pymssql` using `conda`.

```
conda skeleton pypi pymssql
```

Add `setuptools-git` as a dependency within the `meta.yaml` file for `pymssql` as `conda skeleton` does not include.  Below is the relevant section in `meta.yaml` that needs to be updated.

```
requirements:
  build:
    - python
    - setuptools
    - setuptools-git
```

Now finish building and installing.

```
conda build pymssql
conda install --use-local pymssql
```

## Tests
There are only minimal tests at this time.  The tests have been developed for functions that make use of metaprogramming hacks.

#### [pytest](http://pytest.org/latest) - helps you write better programs
```
pip install pytest
```
or
```
conda install pytest
```

## Reprocessing
At times there are issues and processing needs to restart from an earlier time.  In order to reprocess from a specific time, make the following adjustments.

* Within `fc/__init__.py`, set the variable `REPROCESS` to `True`.
    * **Note:** Don't forget to reset `REPROCESS` to `False` after completion.
* Within `main.py`, update ~ lines 38-39 with the start time at which reprocessing needs to begin.


