#!/usr/bin/env python

import sys
import json
import datetime
from msbin import decoder


def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial


def print_dict(dictionary):
    print(json.dumps(dictionary, default=json_serial, indent=2, sort_keys=True))


if len(sys.argv) != 2:
    print('Usage: msbin path/to/file')
    exit()

file_path = sys.argv[1]

with open(file_path, 'rb') as data:
    data = data.read()
    parsed = decoder.parse(data)
    print_dict(parsed)
