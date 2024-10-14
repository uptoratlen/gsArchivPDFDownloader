"""
Tests for command line interface (CLI)
"""
import os
import pytest

def test_help():
    """
    Does the help get displayed
    """
    exit_status = os.system('python -m gsArchivPDFDownloader --help')
    assert exit_status == 0

def test_version1():
    """
    display the version
    """
    exit_status = os.system('python -m gsArchivPDFDownloader --version')
    assert exit_status == 0

def test_version2():
    """
    display the version
    """
    exit_status = os.system('python -m gsArchivPDFDownloader -V')
    assert exit_status == 2

def test_version3():
    """
    fail as arg is not supported
    """
    exit_status = os.system('python -m gsArchivPDFDownloader -v')
    assert exit_status == 0



def test_blank():
    """
    Does the help get displayed
    """
    exit_status = os.system('python -m gsArchivPDFDownloader')
    assert exit_status == 0

def test_range_1_invalid1(testrange='1996:01-2013:13'):
    """
    no run on invalid range
    """
    exit_status = os.system(f'python -m gsArchivPDFDownloader  -e -r {testrange}')
    assert exit_status == 95
def test_range_2_invalid2(testrange='1997:01-2013:13'):
    """
    no run on invalid range
    """
    exit_status = os.system(f'python -m gsArchivPDFDownloader  -e -r {testrange}')
    assert exit_status == 95
def test_range_3_invalid3(testrange='1997:01-2013:14'):
    """
    no run on invalid range
    """
    exit_status = os.system(f'python -m gsArchivPDFDownloader  -e -r {testrange}')
    assert exit_status == 95
def test_range_4_invalid4(testrange='1997:01-2013:02'):
    """
    no run on invalid range
    """
    exit_status = os.system(f'python -m gsArchivPDFDownloader  -e -r {testrange}')
    assert exit_status == 95
def test_range_5_valid1(testrange='2020:01-2020:02'):
    """
    no run on invalid range
    """
    exit_status = os.system(f'python -m gsArchivPDFDownloader  -e -r {testrange}')
    assert exit_status == 0
def test_range_6_invalid5(testrange='2997:01-2013:02'):
    """
    no run on invalid range
    """
    exit_status = os.system(f'python -m gsArchivPDFDownloader  -e -r {testrange}')
    assert exit_status == 95
def test_range_7_invalid6(testrange='2997:31-2013:02'):
    """
    no run on invalid range
    """
    exit_status = os.system(f'python -m gsArchivPDFDownloader  -e -r {testrange}')
    assert exit_status == 95
def test_range_8_invalid7(testrange='2997:01-2013:02'):
    """
    no run on invalid range
    """
    exit_status = os.system(f'python -m gsArchivPDFDownloader  -e -r {testrange}')
    assert exit_status == 95

def test_full():
    """
    full run test
    """
    exit_status = os.system(f'python -m gsArchivPDFDownloader -e -f')
    assert exit_status == 0

def test_year_1():
    """
    year 2020
    """
    exit_status = os.system(f'python -m gsArchivPDFDownloader -e -y 2020')
    assert exit_status == 0

def test_year_2():
    """
    year 2021
    """
    exit_status = os.system(f'python -m gsArchivPDFDownloader  -e -y 2021')
    assert exit_status == 0
