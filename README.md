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
>>> for b in s.get_broadcast_by_title("Shipping Forecast", multi=True): b
00:48 on 17/03/2021 — Shipping Forecast
05:20 on 17/03/2021 — Shipping Forecast
12:03 on 17/03/2021 — Shipping Forecast
```

<details><summary>Click here for more complex examples</summary>

<p>

```py
>>> for b in s.get_broadcast_by_title(r".*\bNews\b", regex=True, multi=True): b
... 
00:00 on 17/03/2021 — Midnight News
05:30 on 17/03/2021 — News Briefing
12:00 on 17/03/2021 — News Summary
18:00 on 17/03/2021 — Six O'Clock News
>>> for b in s.get_broadcast_by_title(r".*\bnews\b", multi=True,
... case_insensitive=True, regex=True, synopsis=True): print(b)
... 
00:00 on 17/03/2021 — Midnight News
05:30 on 17/03/2021 — News Briefing
06:00 on 17/03/2021 — Today
12:00 on 17/03/2021 — News Summary
13:00 on 17/03/2021 — World at One
17:00 on 17/03/2021 — PM
18:00 on 17/03/2021 — Six O'Clock News
20:00 on 17/03/2021 — Moral Maze
22:00 on 17/03/2021 — The World Tonight
23:30 on 17/03/2021 — Today in Parliament
>>> for b in s.get_broadcast_by_title(
... r".*\b(pandemic|virus|coronavirus|Covid|vaccines?|vaccinations?|health|healthcare|NHS)\b",
... multi=True, case_insensitive=True, regex=True, synopsis=True): print(b)
... 
10:00 on 17/03/2021 — Woman's Hour
15:00 on 17/03/2021 — Money Box
15:30 on 17/03/2021 — Inside Health
```

</p>

</details>


## Description

_beeb_ centres around the `Schedule`, which is not limited to a single day's listings:

- ≥1 channels (national, local, regional; indicate by ID or name)
- ≥1 dates (only today by default, or past N days, or from particular date to another date)
- ≥1 times of day ('early', 'morning', 'afternoon', 'evening', 'late')
