# Full Contact
Query the Full Contact RESTful [Person API](https://www.fullcontact.com/developer/docs/person)

Able to accomplish by 
* querying unique email addresses seen in last hour
* compares the email addresses to those seen in the past
    * during the initial 'seeding' time period, gathering all email addresses
    * after 'seeding' check to see if an email address has been queried in the last 10 days
* queries the Full Contact Person API
* saves the resulting JSON

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


