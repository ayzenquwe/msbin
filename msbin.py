#!/usr/bin/env python

import sys
import json
from bson import json_util
from msbin import decoder


def print_dict(dictionary):
    print(json.dumps(dictionary, default=json_util.default, indent=2, sort_keys=True))


# if len(sys.argv) < 2 or len(sys.argv) > 3:
if len(sys.argv) != 2:
    print('Usage: msbin path/to/file')
    exit()

file_path = sys.argv[1]
# tag_name = sys.argv[2] if len(sys.argv) == 3 else None

with open(file_path, 'rb') as data:
    data = data.read()
    parsed = decoder.parse(data)
    print_dict(parsed)
