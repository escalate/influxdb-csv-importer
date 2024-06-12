#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
from datetime import datetime
from tempfile import NamedTemporaryFile

import pytest
from pytz import timezone

from csvimporter import CsvImporter

FIXTURES_DIR = os.path.abspath('tests/fixtures')


@pytest.mark.parametrize('epoch_timestamp,date_str', [
    # 2016-12-01T00:00:00+00:00
    ('1480550400', '2016-12-01'),
    # 2016-12-01T00:00:01+00:00
    ('1480550401', '2016-12-01'),
    # 2016-12-01T23:59:59+00:00
    ('1480636799', '2016-12-01')
])
def test_match_date_positiv(epoch_timestamp, date_str):
    assert CsvImporter.match_date(epoch_timestamp, date_str) is True


@pytest.mark.parametrize('epoch_timestamp,date_str', [
    # 2016-11-30T23:59:59+00:00
    ('1480550399', '2016-12-01'),
    # 2016-12-02T00:00:00+00:00
    ('1480636800', '2016-12-01')
])
def test_match_date_negativ(epoch_timestamp, date_str):
    assert CsvImporter.match_date(epoch_timestamp, date_str) is False


@pytest.mark.parametrize('date_str,fmt,tz,expected', [
    # Winterzeit Europa/Berlin
    ('2016-11-04 07:43:19', 'datetime', 'Europe/Berlin',
        datetime(2016, 11, 4, 6, 43, 19, tzinfo=timezone('UTC'))),
    ('1478241799', 'epoch', 'UTC',
        datetime(2016, 11, 4, 6, 43, 19, tzinfo=timezone('UTC'))),
    ('1478241799', 'epoch', 'Europe/Berlin',
        datetime(2016, 11, 4, 6, 43, 19, tzinfo=timezone('UTC'))),
    # Sommerzeit Europe/Berlin
    ('2016-09-02 10:00:11', 'datetime', 'Europe/Berlin',
        datetime(2016, 9, 2, 8, 0, 11, tzinfo=timezone('UTC'))),
    ('1472803211', 'epoch', 'UTC',
        datetime(2016, 9, 2, 8, 0, 11, tzinfo=timezone('UTC'))),
    ('1472803211', 'epoch', 'Europe/Berlin',
        datetime(2016, 9, 2, 8, 0, 11, tzinfo=timezone('UTC'))),
    # Raw
    ('1718109826000000000', 'raw', 'UTC', 1718109826000000000),
    # Unsupported format
    ('1472803211', 'foobar', 'UTC',
        datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone('UTC')))
])
def test_convert_into_utc_timestamp(date_str, fmt, tz, expected):
    assert CsvImporter.convert_into_utc_timestamp(date_str, fmt, tz) == expected


@pytest.mark.parametrize('data,expected,tags_columns', [
    # Without tags_columns
    ({'positiv_integer': '1'}, {'positiv_integer': 1.0}, None),
    ({'negativ_integer': '-1'}, {'negativ_integer': -1.0}, None),
    ({'positiv_float': '1.0'}, {'positiv_float': 1.0}, None),
    ({'negativ_float': '-1.0'}, {'negativ_float': -1.0}, None),
    ({'string': 'one'}, {'string': 'one'}, None),
    ({'datetime': '2017-01-01 16:30'}, {'datetime': '2017-01-01 16:30'}, None),
    ({'date': '2017-01-01'}, {'date': '2017-01-01'}, None),
    ({'date_german': '01.01.2017'}, {'date_german': '01.01.2017'}, None),
    ({'time': '16:30'}, {'time': '16:30'}, None),
    (None, None, None),
    # With tags_columns
    ({'positiv_integer': '1'}, {'positiv_integer': 1.0}, ['tag1']),
    ({'tag1': 'xyz'}, {'tag1': 'xyz'}, ['tag1'])
])
def test_convert_int_to_float(data, expected, tags_columns):
    assert CsvImporter.convert_int_to_float(data, tags_columns) == expected


class TestClass(object):
    @classmethod
    def setup_class(cls):
        temp_file = NamedTemporaryFile()
        cls.actual = CsvImporter(temp_file.name)

    @classmethod
    def teardown_class(cls):
        del cls.actual

    def test_set_server(self):
        expected = '192.168.1.2'
        self.actual.set_server(expected)
        assert self.actual.cfg_server == expected

    def test_set_port(self):
        expected = '8080'
        self.actual.set_port(expected)
        assert self.actual.cfg_port == expected

    def test_set_user(self):
        expected = 'player1'
        self.actual.set_user(expected)
        assert self.actual.cfg_user == expected

    def test_set_password(self):
        expected = 'secret'
        self.actual.set_password(expected)
        assert self.actual.cfg_password == expected

    def test_set_database(self):
        expected = 'mydb'
        self.actual.set_database(expected)
        assert self.actual.cfg_database == expected

    @pytest.mark.parametrize('measurement,expected', [
        ('lowercase', 'lowercase'),
        ('UPPERCASE', 'uppercase'),
        ('CamelCase', 'camelcase'),
        ('Mi-nus', 'mi_nus'),
        ('Under_Score', 'under_score'),
        ('Dots.Dots.Dots', 'dots_dots_dots'),
        ('W h i t e Spaces', 'w_h_i_t_e_spaces')
    ])
    def test_set_measurement(self, measurement, expected):
        self.actual.set_measurement(expected)
        assert self.actual.cfg_measurement == expected

    @pytest.mark.parametrize('tags_columns,expected', [
        ('col1', ['col1']),
        ('col1,col2', ['col1', 'col2']),
        ('col1,col2,col3', ['col1', 'col2', 'col3']),
    ])
    def test_set_tags_columns(self, tags_columns, expected):
        self.actual.set_tags_columns(tags_columns)
        assert self.actual.cfg_tags_columns == expected

    def test_set_timestamp_column(self):
        expected = 'date_col1'
        self.actual.set_timestamp_column(expected)
        assert self.actual.cfg_timestamp_column == expected

    @pytest.mark.parametrize('fmt', [
        'epoch',
        'datetime'
    ])
    def test_set_timestamp_format(self, fmt):
        expected = fmt
        self.actual.set_timestamp_format(expected)
        assert self.actual.cfg_timestamp_format == expected

    @pytest.mark.parametrize('tz', [
        'UTC',
        'Europe/Berlin',
        'US/Eastern'
    ])
    def test_set_timestamp_timezone(self, tz):
        expected = tz
        self.actual.set_timestamp_timezone(expected)
        assert self.actual.cfg_timestamp_timezone == expected

    @pytest.mark.parametrize('lc', [
        'de_DE.UTF-8',
        'en_GB.UTF-8'
    ])
    def test_set_locale(self, lc):
        expected = lc
        self.actual.set_locale(expected)
        assert self.actual.cfg_locale == expected

    def test_set_date_filter(self):
        expected = '2020-01-01'
        self.actual.set_date_filter(expected)
        assert self.actual.cfg_date_filter == expected

    @pytest.mark.parametrize('columns,expected', [
        ('col1,col2,col3', ['col1', 'col2', 'col3']),
        ('col1, col2, col3', ['col1', 'col2', 'col3']),
        ('col1 , col2 , col3 ', ['col1', 'col2', 'col3']),
        ('col1 , ', ['col1']),
        ('col1 ,', ['col1']),
        ('col1', ['col1'])
    ])
    def test_set_column_ignorelist(self, columns, expected):
        self.actual.set_column_ignorelist(columns)
        assert self.actual.cfg_column_ignorelist == expected

    @pytest.mark.parametrize('toggle', [
        True,
        False
    ])
    def test_set_convert_int_to_float(self, toggle):
        expected = toggle
        self.actual.set_convert_int_to_float(expected)
        assert self.actual.cfg_convert_int_to_float == expected


class OutputTestCase(unittest.TestCase):
    def setUp(self):
        simple_csv_file = '{fixtures_dir}/simple.csv'.format(fixtures_dir=FIXTURES_DIR)
        self.actual = CsvImporter(simple_csv_file)

    def tearDown(self):
        del self.actual

    def test_print_columns(self):
        expected = '[\n    "col1",\n    "col2"\n]'
        assert self.actual.print_columns() == expected

    def test_print_rows(self):
        expected = '[\n    {\n        "col1": "a",\n        "col2": "b"\n    },\n    {\n        "col1": "c",\n        "col2": "d"\n    }\n]'
        assert self.actual.print_rows() == expected
