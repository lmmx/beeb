import pytest

from beeb.share.time.cal_utils import cal_y, cal_m, cal_d, cal_path, cal_date
from beeb.share.time.cal_utils import y_shift, m_shift, d_shift, cal_shift
from beeb.share.time.cal_utils import parse_abs_from_rel_date, parse_date_range


@pytest.mark.parametrize("y,expected", [(1999, "1999"), (2021, "2021")])
def test_cal_y_full(y, expected):
    y_str = cal_y(date=cal_date(y, 1, 15), full_y=True)
    assert y_str == expected


@pytest.mark.parametrize("y,expected", [(1999, "99"), (2021, "21")])
def test_cal_y_abbrev(y, expected):
    y_str = cal_y(date=cal_date(y, 1, 15), full_y=False)
    assert y_str == expected


@pytest.mark.parametrize(
    "m,zf,expected",
    [(1, True, "01"), (1, False, "1"), (12, True, "12"), (12, False, "12")],
)
def test_cal_m(m, zf, expected):
    m_str = cal_m(date=cal_date(2021, m, 15), zf=zf)
    assert m_str == expected


@pytest.mark.parametrize(
    "m,zf,expected",
    [(1, True, "01jan"), (1, False, "1jan"), (12, True, "12dec"), (12, False, "12dec")],
)
def test_cal_m_named(m, zf, expected):
    "Just length check to compare '01' with '01jan' (actual date will vary)"
    m_str = cal_m(date=cal_date(2021, m, 15), zf=zf, with_name=True)
    assert m_str == expected
