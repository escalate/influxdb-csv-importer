#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Commandline interface
to control CsvImporter class"""

import csv
import json
from datetime import datetime
from datetime import timedelta
import locale
import logging

from influxdb import InfluxDBClient
from pytz import timezone
from dateutil.parser import parse
import click


class CsvImporter(object):
    """Class to read .csv files
    and write the values to InfluxDB"""

    def __init__(self, csv_filename, delimiter=','):
        """Constructor"""
        logging.debug('CSV filename is set to "' + csv_filename + '"')
        logging.debug('CSV delimter is set to "' + delimiter + '"')
        self.csv_rows = []
        with open(csv_filename, 'r') as csv_file:
            csv_dict_reader = csv.DictReader(
                csv_file,
                delimiter=delimiter)
            for row in csv_dict_reader:
                self.csv_rows.append(row.copy())

        # Declare variables
        self.cfg_server = None
        self.cfg_port = None
        self.cfg_user = None
        self.cfg_password = None
        self.cfg_database = None
        self.cfg_measurement = None
        self.cfg_timestamp_column = None
        self.cfg_timestamp_format = None
        self.cfg_timestamp_timezone = None
        self.cfg_locale = None
        self.cfg_date_filter = None
        self.cfg_column_ignorelist = None
        self.cfg_convert_int_to_float = None
        self.influxdb_connection = None

    def set_server(self, server):
        """Sets the InfluxDB server address"""
        self.cfg_server = server
        logging.debug('InfluxDB sever address is set to "' +
                      self.cfg_server + '"')

    def set_port(self, port):
        """Sets the InfluxDB server port"""
        self.cfg_port = port
        logging.debug('InfluxDB sever port is set to "' +
                      self.cfg_port + '"')

    def set_user(self, user):
        """Sets the InfluxDB user for authentication"""
        self.cfg_user = user
        logging.debug('InfluxDB user is set to "' +
                      self.cfg_user + '"')

    def set_password(self, password):
        """Sets the InfluxDB password for authentication"""
        self.cfg_password = password
        logging.debug('InfluxDB password is set to "' +
                      self.cfg_password + '"')

    def set_database(self, database):
        """Sets the InfluxDB database"""
        self.cfg_database = database
        logging.debug('InfluxDB database is set to "' +
                      self.cfg_database + '"')

    def set_measurement(self, measurement):
        """Sets the InfluxDB measurement"""
        self.cfg_measurement = measurement \
            .lower() \
            .replace(' ', '_') \
            .replace('.', '_') \
            .replace('(', '') \
            .replace(')', '')
        logging.debug('InfluxDB measurement is set to "' +
                      self.cfg_measurement + '"')

    def set_timestamp_column(self, column):
        """Sets the column to use as timestamp"""
        self.cfg_timestamp_column = column
        logging.debug('Timestamp column is set to "' +
                      self.cfg_timestamp_column + '"')

    def set_timestamp_format(self, fmt):
        """Sets the format of the timestamp column"""
        self.cfg_timestamp_format = fmt
        logging.debug('Timestamp format is set to "' +
                      self.cfg_timestamp_format + '"')

    def set_timestamp_timezone(self, tz):
        """Sets the timezone of the timestamp column"""
        self.cfg_timestamp_timezone = tz
        logging.debug('Timestamp timezone is set to "' +
                      self.cfg_timestamp_timezone + '"')

    def set_locale(self, lc):
        """Sets the locale for ctype, numeric and monetary values"""
        self.cfg_locale = lc
        locale.setlocale(locale.LC_CTYPE, self.cfg_locale)
        logging.debug('Locale for ctype values is set to "' +
                      str(locale.getlocale(locale.LC_CTYPE)) + '"')
        locale.setlocale(locale.LC_NUMERIC, self.cfg_locale)
        logging.debug('Locale for numeric values is set to "' +
                      str(locale.getlocale(locale.LC_NUMERIC)) + '"')
        locale.setlocale(locale.LC_MONETARY, self.cfg_locale)
        logging.debug('Locale for monetary values is set to "' +
                      str(locale.getlocale(locale.LC_MONETARY)) + '"')

    def set_date_filter(self, date):
        """Sets the date for rows to filter"""
        self.cfg_date_filter = date
        logging.debug('Date filter is set to "' +
                      self.cfg_date_filter + '"')

    def set_column_ignorelist(self, columns):
        """Sets the list of columns to ignore"""
        columns = columns.split(',')
        columns = [x.strip(' ') for x in columns]
        columns = [x for x in columns if x]
        self.cfg_column_ignorelist = columns
        logging.debug('Column ignorelist is set to ' +
                      str(self.cfg_column_ignorelist))

    def set_convert_int_to_float(self, toggle):
        """Sets toggle for integer to float conversion"""
        self.cfg_convert_int_to_float = toggle
        logging.debug('Toggle for int to float conversion is set to "' +
                      str(self.cfg_convert_int_to_float) + '"')

    def print_columns(self):
        """Returns all column names in pretty json format"""
        columns = []
        for row in self.csv_rows:
            for key, value in row.items():
                columns.append(key)
            break
        j = json.dumps(sorted(columns), indent=4, sort_keys=True)
        return j

    def print_rows(self):
        """Returns all rows in pretty json format"""
        j = json.dumps(self.csv_rows, indent=4, sort_keys=True)
        return j

    @staticmethod
    def match_date(epoch_timestamp, date_str='2020-01-01'):
        """Returns true if timestamp is inside the range of date
        Returns false if timestamp is outside the range of date"""
        utc_timestamp = datetime.utcfromtimestamp(int(epoch_timestamp))
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_nextday = date_obj + timedelta(days=1)
        if utc_timestamp >= date_obj and utc_timestamp < date_nextday:
            return True
        else:
            return False

    @staticmethod
    def convert_int_to_float(data):
        """Returns a dictionary where all integer values
        are converted to float"""
        if data is not None:
            for key, value in data.items():
                try:
                    data[key] = float(locale.atof(value))
                except ValueError as exception:
                    logging.warning(exception)
        return data

    @staticmethod
    def convert_into_utc_timestamp(date_str, fmt, tz):
        """Converts a datetime or epoch string into UTC timezone
        because InfluxDB only works internally with UTC timestamps"""
        datetime_tz = timezone('UTC').localize(datetime.utcfromtimestamp(0))

        if fmt == 'epoch':
            datetime_naive = datetime.utcfromtimestamp(int(date_str))
            datetime_tz = timezone('UTC').localize(datetime_naive)
        elif fmt == 'datetime':
            datetime_naive = parse(date_str)
            datetime_tz = timezone(tz).localize(datetime_naive)
        else:
            logging.error('Time format is not supported')

        datetime_utc = datetime_tz.astimezone(timezone('UTC'))
        return datetime_utc

    def write_measurement(self, name, fields, tags=None, time=None):
        """Writes a single measurement to InfluxDB"""
        json_body = [
            {
                'measurement': name,
                'fields': fields
            }
        ]
        if tags is not None:
            json_body[0]['tags'] = tags
        if time is not None:
            json_body[0]['time'] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            logging.debug(json_body)
            self.influxdb_connection.write_points(json_body)
        except Exception as exception:
            logging.error(exception)
            raise

    def write_data(self):
        """Writes processed data to InfluxDB"""
        logging.debug('Initialize InfluxDB connection')
        self.influxdb_connection = InfluxDBClient(
            self.cfg_server,
            self.cfg_port,
            self.cfg_user,
            self.cfg_password,
            self.cfg_database)

        for row in self.csv_rows:
            utc_timestamp = None
            if self.cfg_timestamp_column is not None:
                utc_timestamp = CsvImporter.convert_into_utc_timestamp(
                    row[self.cfg_timestamp_column],
                    self.cfg_timestamp_format,
                    self.cfg_timestamp_timezone)

            row_copy = row.copy()
            if self.cfg_date_filter is not None and \
               self.cfg_timestamp_column is not None:
                match = CsvImporter.match_date(
                    row[self.cfg_timestamp_column],
                    self.cfg_date_filter)
                if not match:
                    row_copy = None

            if self.cfg_column_ignorelist is not None:
                for column in self.cfg_column_ignorelist:
                    if row_copy is not None:
                        del row_copy[column]

            if self.cfg_convert_int_to_float is True:
                if row_copy is not None:
                    row_copy = CsvImporter.convert_int_to_float(row_copy)

            if row_copy is not None:
                self.write_measurement(
                    self.cfg_measurement,
                    row_copy,
                    time=utc_timestamp)


@click.command()
@click.argument('csvfile',
                type=click.Path(exists=True))
@click.option('--delimiter',
              default=',',
              help='Delimiter of .csv file (Default: ,)')
@click.option('--server',
              default='localhost',
              help='Server address (Default: localhost)')
@click.option('--port',
              default='8086',
              help='Server port (Default: 8086)')
@click.option('--user',
              help='User for authentication')
@click.option('--password',
              help='Pasword for authentication')
@click.option('--database',
              help='Database name')
@click.option('--measurement',
              help='Measurement name')
@click.option('--timestamp-column',
              help='Name of the column to use as timestamp; \
              if option is not set, the current timestamp is used')
@click.option('--timestamp-format',
              default='epoch',
              type=click.Choice(['epoch', 'datetime']),
              help='Format of the timestamp column \
              used to parse all timestamp \
              \b \
              (Default: epoch timestamp); \
              epoch = epoch / unix timestamp \
              datetime = normal date and/or time notation')
@click.option('--timestamp-timezone',
              default='UTC',
              help='Timezone of the timestamp column')
@click.option('--locale',
              help='Locale for ctype, numeric and monetary \
              values \
              e.g. de_DE.UTF-8')
@click.option('--date-filter',
              help='Select only rows with a specific date \
              in the timestamp column for import e.g. 2020-01-01')
@click.option('--column-ignorelist',
              help='Ignore a list of columns for import \
              e.g. col1,col2,col3')
@click.option('--convert-int-to-float',
              is_flag=True,
              default=True,
              help='Convert integer values to float')
@click.option('--print-columns',
              is_flag=True,
              help='Print all column names in pretty json format')
@click.option('--print-rows',
              is_flag=True,
              help='Print all rows in pretty json format')
@click.option('--write-data',
              is_flag=True,
              help='Write data into InfluxDB')
@click.option('--verbose',
              is_flag=True,
              help='Enable verbose logging output')
def cli(*args, **kwargs):
    """Commandline interface for InfluxDB / CSV Importer"""

    # Configure logging
    log_format = '%(levelname)s: %(message)s'
    if kwargs['verbose']:
        logging.basicConfig(format=log_format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=log_format)

    # Instantiate CsvImporter
    csv_importer = CsvImporter(kwargs['csvfile'], kwargs['delimiter'])

    # Handle options
    if kwargs['server']:
        csv_importer.set_server(kwargs['server'])
    if kwargs['port']:
        csv_importer.set_port(kwargs['port'])
    if kwargs['user']:
        csv_importer.set_user(kwargs['user'])
    if kwargs['password']:
        csv_importer.set_password(kwargs['password'])
    if kwargs['database']:
        csv_importer.set_database(kwargs['database'])
    if kwargs['measurement']:
        csv_importer.set_measurement(kwargs['measurement'])
    if kwargs['timestamp_column']:
        csv_importer.set_timestamp_column(kwargs['timestamp_column'])
    if kwargs['timestamp_format']:
        csv_importer.set_timestamp_format(kwargs['timestamp_format'])
    if kwargs['timestamp_timezone']:
        csv_importer.set_timestamp_timezone(kwargs['timestamp_timezone'])
    if kwargs['locale']:
        csv_importer.set_locale(kwargs['locale'])
    if kwargs['date_filter']:
        csv_importer.set_date_filter(kwargs['date_filter'])
    if kwargs['column_ignorelist']:
        csv_importer.set_column_ignorelist(kwargs['column_ignorelist'])

    # Handle toggles
    csv_importer.set_convert_int_to_float(kwargs['convert_int_to_float'])

    # Handle actions
    if kwargs['print_columns']:
        columns = csv_importer.print_columns()
        click.echo(columns)
    if kwargs['print_rows']:
        rows = csv_importer.print_rows()
        click.echo(rows)
    if kwargs['write_data']:
        csv_importer.write_data()


if __name__ == '__main__':
    cli()
