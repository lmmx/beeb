# beeb

![](https://raw.githubusercontent.com/lmmx/beeb/master/beeb_logo.png)

A modern interface to the BBC Sounds radio catalogue.

## Usage

- Create a schedule for BBC R4, defaulting to today's date:

```py
from beeb.nav import Schedule
Schedule.from_channel_name("r4")
```
⇣
```
Schedule for BBC Radio 4 on 2021-03-16
```

These Schedule objects can be used to find programmes:

```py
>>> from beeb.nav import Schedule
>>> s = Schedule.from_channel_name("r4")
>>> s.get_broadcast_by_title("Today", True)
'm000t476'
>>> s.get_broadcast_by_title("Midnight News")
00:00 on 17/03/2021 — Midnight News
>>> s.get_broadcast_by_title("Midnight News", multi=True)
[00:00 on 17/03/2021 — Midnight News, 00:00 on 18/03/2021 — Midnight News]
```


## Description

_beeb_ centres around the `Schedule`, which is not limited to a single day's listings:

- ≥1 channels (national, local, regional; indicate by ID or name)
- ≥1 dates (only today by default, or past N days, or from particular date to another date)
- ≥1 times of day ('early', 'morning', 'afternoon', 'evening', 'late')
