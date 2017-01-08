#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nose2.tools import params
from nose2.tools.such import helper
import logging
from datetime import datetime
from pytz import timezone
from csvimporter import CsvImporter


@params(
    # 2016-12-01T00:00:00+00:00
    ('1480550400', '2016-12-01'),
    # 2016-12-01T00:00:01+00:00
    ('1480550401', '2016-12-01'),
    # 2016-12-01T23:59:59+00:00
    ('1480636799', '2016-12-01')
)
def test_match_date_positiv(epoch_timestamp, date_str):
    assert CsvImporter.match_date(epoch_timestamp, date_str) == True


@params(
    # 2016-11-30T23:59:59+00:00
    ('1480550399', '2016-12-01'),
    # 2016-12-02T00:00:00+00:00
    ('1480636800', '2016-12-01')
)
def test_match_date_negativ(epoch_timestamp, date_str):
    assert CsvImporter.match_date(epoch_timestamp, date_str) == False


@params(
    # Winterzeit Europa/Berlin
    ('2016-11-04 07:43:19', 'datetime', 'Europe/Berlin', datetime(2016, 11, 4, 6, 43, 19, tzinfo=timezone('UTC'))),
    ('1478241799', 'epoch', 'UTC', datetime(2016, 11, 4, 6, 43, 19, tzinfo=timezone('UTC'))),
    ('1478241799', 'epoch', 'Europe/Berlin', datetime(2016, 11, 4, 6, 43, 19, tzinfo=timezone('UTC'))),
    # Sommerzeit Europe/Berlin
    ('2016-09-02 10:00:11', 'datetime', 'Europe/Berlin', datetime(2016, 9, 2, 8, 0, 11, tzinfo=timezone('UTC'))),
    ('1472803211', 'epoch', 'UTC', datetime(2016, 9, 2, 8, 0, 11, tzinfo=timezone('UTC'))),
    ('1472803211', 'epoch', 'Europe/Berlin', datetime(2016, 9, 2, 8, 0, 11, tzinfo=timezone('UTC'))),
    # Unsupported format
    ('1472803211', 'foobar', 'UTC', datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone('UTC')))
)
def test_convert_into_utc_timestamp(date_str, fmt, tz, result):
    assert CsvImporter.convert_into_utc_timestamp(date_str, fmt, tz) == result


@params(
    ({'positiv_integer': '1'}, {'positiv_integer': 1.0}),
    ({'negativ_integer': '-1'}, {'negativ_integer': -1.0}),
    ({'positiv_float': '1.0'}, {'positiv_float': 1.0}),
    ({'negativ_float': '-1.0'}, {'negativ_float': -1.0}),
    ({'string': 'one'}, {'string': 'one'}),
    ({'datetime': '2017-01-01 16:30'}, {'datetime': '2017-01-01 16:30'}),
    ({'date': '2017-01-01'}, {'date': '2017-01-01'}),
    ({'date_german': '01.01.2017'}, {'date_german': '01.01.2017'}),
    ({'time': '16:30'}, {'time': '16:30'}),
    (None, None)
)
def test_convert_int_to_float(data, result):
    assert CsvImporter.convert_int_to_float(data) == result
