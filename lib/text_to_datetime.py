import os
import sys
import datetime
import re

DATE_PATTERNS = [
                    r'(?P<year>(?:20|19)\d{2})[\._\-]?(?P<month>\d{2})[\._\-]?(?P<day>\d{2})',
                    r'(?P<day>\d{2})[\._\-]?(?P<month>\d{2})[\._\-]?(?P<year>(?:20|19)\d{2})'
                ]
TIME_PATTERNS = [
                    r'(?P<hour>[012]\d)[:\._\-]?(?P<min>[0-5]\d)[:\._\-]?(?P<sec>[0-5]\d)?[:\._\-]?(?P<msec>\d{2})?'
                ]



def text_to_datetime(text: str):
    return __get_datetime_from_text(text)


def __get_datetime_from_text(text: str):
    for date_pattern in DATE_PATTERNS:
        for time_pattern in TIME_PATTERNS:
            combined_pattern = date_pattern + r'[_\.\- ]?' + time_pattern
            match = re.search(combined_pattern, text)
            dtime = __get_datetime_from_match(match)
            if dtime:
                return dtime
        match = re.search(date_pattern, text)
        dtime = __get_datetime_from_match(match)
        if dtime:
            return dtime
    return None


def __get_datetime_from_match(match: re.Match):
    year, month, day = __get_date_from_match(match)
    hour, minutes, seconds, milliseconds = __get_time_from_match(match)
    return datetime.datetime(year, month, day, hour, minutes, seconds, milliseconds)


def __get_date_from_match(match: re.Match):
    year = match.group('year')
    month = match.group('month')
    day = match.group('day')
    return year, month, day

def __get_time_from_match(match: re.Match):
    hour = match.group('hour')
    minutes = match.group('min')
    seconds = match.group('sec')
    milliseconds = match.group('msec')
    return hour, minutes, seconds, milliseconds
