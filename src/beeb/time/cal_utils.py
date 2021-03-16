from pathlib import Path
import datetime as DT
from datetime import date as cal_date  # , datetime as dt
from dateutil.relativedelta import relativedelta as rd
from functools import partial

__all__ = [
    "cal_y", "cal_m", "cal_d",
    "cal_path",
    "y_shift", "m_shift", "d_shift",
    "cal_shift", "cal_date",
    "parse_abs_from_rel_date",
]

def cal_y(date=cal_date.today(), full_y=True):
    """
    Month, optionally full e.g. '2021' or abbreviated e.g. '21' (default: full)
    """
    year_num = "Y" if full_y else "y"
    return date.strftime(f"%{year_num}")


def cal_m(date=cal_date.today(), zf=True, with_name=False):
    """
    Month, optionally left-padded with zeroes (default: pad),
    optionally suffixed with [lower case] abbreviated month name
    (default: suffixed)
    """
    month_num = "m" if zf else "-m" # optionally zero fill
    month_str = "%b" if with_name else ""
    return date.strftime(f"%{month_num}{month_str}").lower()


def cal_d(date=cal_date.today(), zf=True):
    """
    Month, optionally left-padded with zeroes (default: pad)
    """
    day_num = "d" if zf else "-d" # optionally zero fill
    return date.strftime(f"%{day_num}")


def cal_path(date=cal_date.today(), as_tuple=False, full_y=True, zf=True, month_names=False):
    cal_y_func = partial(cal_y, full_y=full_y)
    cal_m_func = partial(cal_m, zf=zf, with_name=month_names)
    cal_d_func = partial(cal_d, zf=zf)
    y, m, d = [f(date) for f in (cal_y_func, cal_m_func, cal_d_func)]
    if as_tuple:
        return (y, m, d)
    else:
        return Path(y) / m / d


def y_shift(y=0, date=cal_date.today()):
    return date + rd(years=y) if y != 0 else date


def m_shift(m=0, date=cal_date.today()):
    return date + rd(years=m) if m != 0 else date


def d_shift(d=0, date=cal_date.today()):
    return date + rd(days=d) if d != 0 else date


def cal_shift(y=0, m=0, d=0, date=cal_date.today()):
    return date + rd(years=y, months=m, days=d) if any([y, m, d]) else date

def parse_abs_from_rel_date(ymd=None, ymd_ago=None):
    if ymd is ymd_ago is None:
        ymd = cal_date.today()
    else:
        # If ymd was supplied, do type conversion if passed as int tuple
        if isinstance(ymd, tuple):
            if all(map(lambda i: isinstance(i, int), ymd)):
                ymd = cal_date(*ymd)
            else:
                raise TypeError(f"{ymd=} is neither a datetime.date nor integer tuple")
        if all([ymd, ymd_ago]):
            # both ymd and ymd_ago are not None (i.e. are supplied) so shift accordingly
            ymd = cal_shift(*ymd_ago, date=ymd)
        elif ymd_ago:
            ymd = cal_shift(*ymd_ago)
        # else implies ymd was supplied
    # In each of the above cases `ymd` is now a `datetime.date` object
    return ymd
