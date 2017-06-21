# -*- coding: utf-8 -*-
u"""
Copyright 2017 Telefónica Investigación y Desarrollo, S.A.U.
This file is part of Toolium.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import codecs
import os
import sys

import pytest


def test_join_list_with_utf8_strings_and_unicode():
    """
    This case fails in behave with Python 2 when captured logs contain utf8 characters
    behave/log_capture.py, getvalue() method, line 99
    """
    utf8_list = [u'year', 'año']
    if sys.version_info > (3, 0):
        assert ';'.join(utf8_list) == u'year;año'
    else:
        with pytest.raises(UnicodeDecodeError):
            ';'.join(utf8_list)

    # Solution 1: decode each element list -> works in Py2, fails in Py 3
    if sys.version_info > (3, 0):
        with pytest.raises(AttributeError):
            # 'str' object has no attribute 'decode'
            [elem.decode('utf-8') for elem in utf8_list]
    else:
        decoded = [elem.decode('utf-8') for elem in utf8_list]
        assert ';'.join(decoded) == u'year;año'

    # Solution 2: decode each element list capturing exceptions
    def utf8_decode(encoded_string):
        try:
            return encoded_string.decode('utf-8')
        except Exception:
            return encoded_string
    decoded = [utf8_decode(elem) for elem in utf8_list]
    assert ';'.join(decoded) == u'year;año'

    # Solution 3: only decode when join fails
    try:
        joined = ';'.join(utf8_list)
    except UnicodeDecodeError:
        joined = ';'.join([elem.decode('utf-8') for elem in utf8_list])
    assert joined == u'year;año'


def test_format_cp1252_string_to_unicode():
    """
    This case fails in behave with Python 2 when Selenium connection fails and system error contains cp1252 strings
    behave/_types.py, describe() method, line 59
    """
    cp1252_string = u'año'.encode('cp1252')
    if sys.version_info > (3, 0):
        # UnicodeDecodeError is not thrown in Python 3, but string should be decoded
        assert u'year;{}'.format(cp1252_string) == u"year;b'a\\xf1o'"
    else:
        with pytest.raises(UnicodeDecodeError):
            u'year;{}'.format(cp1252_string)

    # Solution: decode string from cp1252
    decoded = cp1252_string.decode('cp1252')
    assert u'year;{}'.format(decoded) == u'year;año'


def test_print_cp1252_unicode():
    """
    This case fails in behave with Python 2 when Selenium connection fails and system error contains cp1252 strings
    After resolving 'test_format_cp1252_string_to_unicode' error, appears this one when behave tries to print system
    error message in a non-utf8 console
    behave/runner.py, run_hook() method, line 477
    """
    cp1252_string = u'año'.encode('cp1252')
    decoded = cp1252_string.decode('cp1252')
    try:
        print(decoded)
    except UnicodeEncodeError:
        print('UnicodeEncodeError due to stdout encoding: %s, %s, %s', sys.stdin.encoding, sys.stdout.encoding,
              sys.stderr.encoding)
        # Solution 1: update IO to utf8 with a system property PYTHONIOENCODING=UTF-8
        # Solution 2: update IO to utf8 from python code
        sys.stdout = codecs.getwriter('utf8')(sys.stdout)
        sys.stderr = codecs.getwriter('utf8')(sys.stderr)
        print(decoded)


def test_print_os_configuration():
    """
    Print OS configuration

    sys.version:
        Win Py2: 2.7.10 (default, May 23 2015, 09:40:32) [MSC v.1500 32 bit (Intel)]
        Win Py3: 3.5.0 (v3.5.0:374f501f4567, Sep 13 2015, 02:27:37) [MSC v.1900 64 bit (AMD64)]
        Linux Py2: 2.7.9 (default, Feb  5 2015, 15:48:42) [GCC 4.6.3]
        Linux Py3: 3.3.5 (default, Feb  5 2015, 16:01:18) [GCC 4.6.3]
        Linux Py3: 3.4.2 (default, Feb  5 2015, 15:56:51) [GCC 4.6.3]
        Linux Py3: 3.5.3 (default, Jun 18 2017, 15:07:36) [GCC 4.6.3]
        Linux Py3: 3.6.1 (default, Jun 18 2017, 15:12:33) [GCC 4.6.3]

                                    Py2   / Py3
    os.getenv('PYTHONIOENCODING'):  None  / utf-8
    sys.getdefaultencoding():       ascii / utf-8

                                    Win Py2 / Win Py3 / Linux Py2 / Linux Py3
    sys.platform:                   win32   / win32   / linux2    / linux
    sys.getfilesystemencoding():    mbcs    / mbcs    / UTF-8     / utf-8
    sys.stdin.encoding:             None    / cp1252  / UTF-8     / UTF-8
    sys.stdout.encoding:            None    / cp1252  / UTF-8     / UTF-8
    sys.stderr.encoding:            None    / cp1252  / UTF-8     / UTF-8

    sys.getwindowsversion():
        Win Py2: (major=6, minor=2, build=9200, platform=2, service_pack='')
        Win Py3: (major=10, minor=0, build=14393, platform=2, service_pack='')
        Linux: AttributeError: 'module' object has no attribute 'getwindowsversion'
    """
    print('sys.platform: %s' % sys.platform)
    print('sys.version: %s' % sys.version)
    print("os.getenv('PYTHONIOENCODING'): %s" % os.getenv('PYTHONIOENCODING', None))
    print('sys.getdefaultencoding(): %s' % sys.getdefaultencoding())
    print('sys.getfilesystemencoding(): %s' % sys.getfilesystemencoding())
    print('sys.stdin.encoding: %s' % sys.stdin.encoding)
    print('sys.stdout.encoding: %s' % sys.stdout.encoding)
    print('sys.stderr.encoding: %s' % sys.stderr.encoding)

    try:
        print('sys.getwindowsversion(): %s' % str(sys.getwindowsversion()))
    except AttributeError as e:
        print('%s: %s' % (e.__class__.__name__, e))
