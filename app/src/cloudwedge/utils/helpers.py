'''
Helpers
'''

from datetime import datetime

from pytz import timezone
import pytz


def get_local_time(local_timezone='US/Mountain'):
    '''Get todays local time'''

    # UTC timezone
    utc = pytz.utc

    local_tz = timezone(local_timezone)

    # Get current time for utc with timezone as UTC
    utc_dt = utc.localize(datetime.utcnow())

    # From utc time, get time as if it was local timezone
    local_datetime = utc_dt.astimezone(local_tz)

    return local_datetime
