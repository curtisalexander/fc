# standard lib
from collections import namedtuple

# local
from fc.utils import (compare_namedtuples,
                      unique_namedtuples)


def test_unique_namedtuples():
    """ Testing that the function works correctly as it makes use
    of metaprogramming using exec 
    """
    Hungry = namedtuple('Hungry', ['id', 'action', 'eat'])
    items = [Hungry(2, 'eat', 'apple'),
             Hungry(2, 'eat', 'banana'),
             Hungry(3, 'prep', 'carrot')]
    result = [Hungry(2, 'eat', 'apple'),
              Hungry(3, 'prep', 'carrot')]

    assert(unique_namedtuples(items, ('id', 'action')), result)


def test_compare_namedtuples():
    """ Testing that the function works correctly as it makes use
    of metaprogramming using exec 
    """
    Hungry = namedtuple('Hungry', ['id', 'action', 'eat'])
    items_base = [Hungry(2, 'eat', 'apple'),
                  Hungry(3, 'prep', 'carrot')]
    items_compare = [Hungry(2, 'eat', 'banana'),
                     Hungry(2, 'prep', 'apple'),
                     Hungry(3, 'eat', 'date'),
                     Hungry(4, 'prep', 'fennel')]
    result = [Hungry(3, 'prep', 'carrot')]

    assert(compare_namedtuples(items_base, items_compare,
                               ('id', 'action')), result)
