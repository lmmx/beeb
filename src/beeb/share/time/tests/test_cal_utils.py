import pytest

from beeb.share.time.cal_utils import cal_y, cal_m, cal_d, cal_path
from beeb.share.time.cal_utils import y_shift, m_shift, d_shift, cal_shift
from beeb.share.time.cal_utils import parse_abs_from_rel_date, parse_date_range

@pytest.fixture
def its_the_nineties_baby():
    return cal_date(1999, 1, 20)

@pytest.fixture
def april_fools():
    return cal_date(2021, 4, 1)

def check_alnum(alnum_str):
    return s.isalnum() and not s.isnumeric() and not s.isalpha()

def check_n_digits(digit_str, n=4, alphanumeric=False):
    is_num = check_alnum(digit_str) if alphanumeric else digit_str.isnumeric()
    return len(digit_str) == n and digit_str.isnumeric()

def test_cal_y_full(april_fools):
    y_str = cal_y(date=april_fools, full_y=True)
    assert y_str == "2021"

def test_cal_y_abbrev():
    "Post-2020, year will never start with '20'. Should be 4 digits."
    y_str = cal_y(full_y=False)
    assert not y_str.startswith("20") and check_n_digits(y_str, n=2)

def test_cal_m():
    "Just check month is numeric string e.g. '01'."
    m_str = cal_m()
    assert check_n_digits(m_str, n=4)

def test_cal_m_named():
    "Just length check to compare '01' with '01jan' (actual date will vary)"
    m_str = cal_m(with_name=True)
    assert check_n_digits(m_str, n=5, alphanumeric=True)


