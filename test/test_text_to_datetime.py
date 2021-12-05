
import pytest
import datetime
import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from lib.text_to_datetime import text_to_datetime

DATES = [
                {"year": 2020, "month": 3, "day": 1},
                {"year": 2001, "month": 12, "day": 31},
                {"year": 1920, "month": 7, "day": 12},
                {"year": 1988, "month": 10, "day": 25}
            ]

def test_positive_date_only():
    for date in DATES:
        expected = datetime.datetime(date["year"], date["month"], date["day"])
        assert text_to_datetime(f'{date["year"]}{date["month"]:02d}{date["day"]:02d}') == expected
        assert text_to_datetime(f'{date["year"]}_{date["month"]:02d}_{date["day"]:02d}') == expected
        assert text_to_datetime(f'{date["year"]}-{date["month"]:02d}-{date["day"]:02d}') == expected

        assert text_to_datetime(f'{date["day"]:02d}{date["month"]:02d}{date["year"]}') == expected
        assert text_to_datetime(f'{date["day"]:02d}.{date["month"]:02d}.{date["year"]}') == expected
        assert text_to_datetime(f'{date["day"]:02d}_{date["month"]:02d}_{date["year"]}') == expected
        assert text_to_datetime(f'{date["day"]:02d}-{date["month"]:02d}-{date["year"]}') == expected
