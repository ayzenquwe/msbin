__author__ = 'Aleksey Lagoshin'

import datetime
import struct
from msbin.constants import *


# Whether to preserve namespaces in element's names
PRESERVE_NAMESPACES = False


data = None
index = 0


def parse(data_bytes):
    global data, index
    data = data_bytes
    index = 0

    try:
        return parse_record()
    except:
        print("Exception while parsing data near position " + str(index))
        raise


def parse_record():
    result = None
    tag_end = False

    while not tag_end and index < len(data):
        record_type = parse_byte()
        if record_type == TAG_END:
            tag_end = True
        elif record_type in ATTRIBUTE_TYPES:
            skip_attribute(record_type)
        elif record_type in ELEMENT_TYPES:
            element_name = parse_element_name(record_type)
            element_value = parse_record()
            if result is None:
                # It's the first nested element so far
                result = {element_name: element_value}
            elif type(result) is dict:
                # Result already has some elements
                if element_name in result:
                    # If result already has an element with the same name, treat the result as a list
                    result = [{element_name: result[element_name]}, {element_name: element_value}]
                else:
                    # Just another nested element
                    result[element_name] = element_value
            else:
                # Just another list element
                result.append({element_name: element_value})
        elif record_type in VALUE_TYPES:
            result, tag_end = parse_value(record_type)

    return result


def skip_attribute(record_type):
    """
    Skips attribute of XML element. Currently all attributes are omitted since they are not heavily used in MC-NBFS.
    :param record_type: the type of record
    """
    if record_type == SHORT_ATTRIBUTE_TYPE or record_type in PREFIX_ATTRIBUTE_TYPES:
        parse_string()
        parse_value(parse_byte())
    elif record_type == ATTRIBUTE_TYPE:
        parse_string()
        parse_string()
        parse_value(parse_byte())
    elif record_type == SHORT_DICTIONARY_ATTRIBUTE_TYPE or record_type in PREFIX_DICTIONARY_ATTRIBUTE_TYPES:
        parse_multibyte()
        parse_value(parse_byte())
    elif record_type == DICTIONARY_ATTRIBUTE_TYPE:
        parse_string()
        parse_multibyte()
        parse_value(parse_byte())
    elif record_type == SHORT_XMLNS_ATTRIBUTE_TYPE:
        parse_string()
    elif record_type == XMLNS_ATTRIBUTE_TYPE:
        parse_string()
        parse_string()
    elif record_type == SHORT_DICTIONARY_XMLNS_ATTRIBUTE_TYPE:
        parse_multibyte()
    elif record_type == DICTIONARY_XMLNS_ATTRIBUTE_TYPE:
        parse_string()
        parse_multibyte()


def parse_element_name(record_type):
    """
    Parses XML element name and returns it with or without prefix, depending on PRESERVE_NAMESPACES constant.
    :param record_type: the type of record
    :return: the name of XML element
    """
    if record_type == SHORT_ELEMENT:
        return parse_string()
    elif record_type == ELEMENT:
        return generate_name(parse_string(), parse_string())
    elif record_type == SHORT_DICTIONARY_ELEMENT:
        return DICTIONARY[parse_multibyte()]
    elif record_type == DICTIONARY_ELEMENT:
        return generate_name(parse_string(), DICTIONARY[parse_multibyte()])
    elif record_type in PREFIX_DICTIONARY_ELEMENTS:
        return generate_name(chr(record_type), DICTIONARY[parse_multibyte()])
    elif record_type in PREFIX_ELEMENTS:
        return generate_name(chr(record_type), parse_string())


def generate_name(prefix, name):
    return prefix + ":" + name if PRESERVE_NAMESPACES else name


def parse_value(record_type):
    tag_end = record_type % 2 != 0
    record_type = record_type - 1 if tag_end else record_type

    if record_type == VALUE_ZERO:
        result = 0
    elif record_type == VALUE_ONE:
        result = 1
    elif record_type == VALUE_FALSE:
        result = False
    elif record_type == VALUE_TRUE:
        result = True
    elif record_type == VALUE_INT8:
        result = parse_integer()
    elif record_type == VALUE_INT16:
        result = parse_integer(2)
    elif record_type == VALUE_INT32:
        result = parse_integer(4)
    elif record_type == VALUE_INT64:
        result = parse_integer(8)
    elif record_type == VALUE_FLOAT:
        result = parse_float()
    elif record_type == VALUE_DOUBLE:
        result = parse_double()
    elif record_type == VALUE_DATETIME:
        # This is not very accurate, because TimeZone is not parsed
        try:
            result = datetime.datetime.fromtimestamp(parse_integer(8, False)/10000000 - 62135596800)
        except ValueError:
            result = datetime.datetime.max
    elif record_type == VALUE_CHARS8:
        result = parse_chars(1)
    elif record_type == VALUE_CHARS16:
        result = parse_chars(2)
    elif record_type == VALUE_CHARS32:
        result = parse_chars(4)
    elif record_type == VALUE_EMPTY_TEXT:
        result = ""
    elif record_type == VALUE_DICTIONARY:
        result = DICTIONARY[parse_multibyte()]
    elif record_type == VALUE_UNIQUEID:
        result = parse_uniqueid()
    elif record_type == VALUE_UINT64:
        result = parse_integer(8, False)
    else:
        raise Exception('Value parsing is not implemented, type=' + hex(record_type))

    return result, tag_end


def parse_byte():
    global index

    result = data[index]
    index += 1

    return result


def parse_multibyte():
    result = 0

    for i in range(0, 4):
        byte = parse_byte()
        result |= (byte & 0b01111111) << (7 * i)
        if byte & 0b10000000 == 0:
            break

    return result


def parse_string():
    global index

    length = parse_multibyte()
    index += length

    return data[index-length:index].decode()


def parse_chars(length_size):
    global index

    length = parse_integer(length_size, signed=(length_size == 4))
    index += length

    return data[index-length:index].decode()


def parse_integer(size=1, signed=True):
    global index
    index += size

    return int.from_bytes(data[index-size:index], byteorder='little', signed=signed)


def parse_float():
    global index
    index += 4

    return struct.unpack('<f', bytes(data[index-4:index]))[0]


def parse_double():
    global index
    index += 8

    return struct.unpack('<d', bytes(data[index-8:index]))[0]


def parse_uniqueid():
    global index
    index += 16

    return "UniqueID is not implemented"