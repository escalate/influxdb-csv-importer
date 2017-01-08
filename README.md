# influxdb-csv-importer
![Build Status](https://travis-ci.org/escalate/influxdb-csv-importer.svg?branch=master)

Imports CSV files into InfluxDB

## Dependencies
* [influxdb](https://pypi.python.org/pypi/influxdb)
* [click](https://pypi.python.org/pypi/click)
* [pytz](https://pypi.python.org/pypi/pytz)
* [dateutil](https://pypi.python.org/pypi/python-dateutil)

## Installation
Tested with Python 3.4.3 on Ubuntu 14.04

If you encounter issues with other 3.x versions of Python, please open a github issue.

### Requirements
Install needed requirements via pip

#### Production
```
pip install -r requirements.txt
```

#### Development
```
pip install -r dev-requirements.txt
```

### Run
Run tool from commandline
```
$ ./csvimporter.py
```

## Usage
```
$ ./csvimporter.py --help

Usage: csvimporter.py [OPTIONS] CSVFILE

  Commandline interface for CsvImporter

Options:
  --delimiter TEXT                Delimiter of .csv file (Default: ,)
  --server TEXT                   Server address (Default: localhost)
  --port TEXT                     Server port (Default: 8086)
  --user TEXT                     User for authentication
  --password TEXT                 Pasword for authentication
  --database TEXT                 Database name
  --measurement TEXT              Measurement name
  --timestamp-column TEXT         Name of the column to use as timestamp;
                                  if option is not set,
                                  the current timestamp is used
  --timestamp-format [epoch|datetime]
                                  Format of the timestamp column
                                  used to parse all timestamp               
                                  (Default: epoch timestamp);
                                  epoch = epoch / unix timestamp
                                  datetime = normal date and/or time notation
  --timestamp-timezone TEXT       Timezone of the timestamp column
  --locale TEXT                   Locale for ctype, numeric and monetary
                                  values e.g. de_DE.UTF-8
  --date-filter TEXT              Select only rows with a specific date
                                  in the timestamp column for import
                                  e.g. 2016-01-01
  --column-ignorelist TEXT        Ignore a list of columns for import
                                  e.g. col1,col2,col3
  --convert-int-to-float          Convert integer values to float
  --print-columns                 Print all column names in pretty json format
  --print-rows                    Print all rows in pretty json format
  --write-data                    Write data into InfluxDB
  --verbose                       Enable verbose logging output
  --help                          Show this message and exit.
```

## Other Projects
* A commandline tool to convert a CSV file into InfluxDB-compatible JSON written in Ruby [spuder/csv2influxdb](https://github.com/spuder/csv2influxdb)
* A commandline tool to import CSV files into InfluxDB with similar features like this project, but written in GO [jpillora/csv-to-influxdb](https://github.com/jpillora/csv-to-influxdb)
