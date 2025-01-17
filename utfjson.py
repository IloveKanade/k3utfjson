#!/usr/bin/env python2
# coding: utf-8

# utfjson use python3 json module in python2.
#
# json module in python2 does not support disabling decoding string into
# unicode when json.loads().
#
# Thus if we do not know encoding of the json string we just can't load it.
# But the reality is that user input can be in any encoding or the input
# string might be an arbitrary byte array.
#
# In this case we need to laod json without decoding.
#
# Thus we ported python3 json module here and have made modification in order
# to let it pass python2 json test suites.
import json


# expected behavior to dump '我':
#           source             encoding=None  encoding='utf-8'
# unicode  u'\u6211'           '"\\u6211"'    '"\xe6\x88\x91"'
# str       '\xe6\x88\x91'     TypeError      '"\xe6\x88\x91"'


# ensure_ascii behavior to dump '我', in p3json:
#
#           source             ensure_ascii=True         ensure_ascii=False
# unicode  u'\u6211'           '"\\u6211"'               u'"\u6211"'
# str       '\xe6\x88\x91'     '"\\u00e6\\u0088\\u0091"' '"\xe6\x88\x91"'


def dump(obj, encoding='utf-8', indent=None):
    # - Using non-unicode with ensure_ascii=True results in unexpected output:
    #       p3fjson.dump('我',  ensure_ascii=True)  --> '"\\u00e6\\u0088\\u0091"'
    #
    #   We do not allow this to happen.
    #
    #
    # - Using nonunicode with ensure_ascii=False results in unexpected output:
    #       p3json.dump(u'我', ensure_ascii=False) --> u'"\u6211"'
    #
    #   It is rare to use unicode string in a serialized string.
    #   When transmitting object over network what we need is a byte
    #   series(str).
    #   Thus if input is unicode and ecoding is specified, we convert unicode
    #   to a utf-8 string first.
    if encoding is None:
        ensure_ascii = True

    else:
        obj = encode_str(obj, encoding)
        # We do not need to convert non-ascii chars in a encoded string.
        ensure_ascii = False

    return json.dumps(obj, ensure_ascii=ensure_ascii, indent=indent)


def ensure_str(o):

    if isinstance(o, bytes):
        raise TypeError('string({o} {tp}) must be str'
                        ' if ensure_ascii is True'.format(o=o, tp=type(o)))

    if isinstance(o, dict):
        for k, v in o.items():
            ensure_str(k)
            ensure_str(v)

    elif isinstance(o, (list, tuple)):
        for v in o:
            ensure_str(v)


def encode_str(o, encoding):
    if isinstance(o, bytes):
        return o.decode(encoding)

    if isinstance(o, dict):
        rst = {}
        for k, v in o.items():
            rst[encode_str(k, encoding)] = encode_str(v, encoding)

    elif isinstance(o, (list, tuple)):
        rst = []
        for v in o:
            rst.append(encode_str(v, encoding))
    else:
        rst = o

    return rst


def load(s, encoding=None):
    # By default, do not try to decode non-unicode string in result.
    # There could be invalid chars.

    if s is None:
        return None
    if isinstance(s, bytes):
        if encoding is None:
            s = decode(s, encoding="utf-8")
        else:
            s = decode(s, encoding)
        s = "\"" + s + "\""
    rst = json.loads(s)

    return rst


def decode(o, encoding):
    if isinstance(o, bytes):
        return o.decode(encoding)

    if isinstance(o, dict):
        rst = {}
        for k, v in o.items():
            rst[decode(k, encoding)] = decode(v, encoding)

    elif isinstance(o, list):
        rst = []
        for v in o:
            rst.append(decode(v, encoding))
    else:
        rst = o

    return rst
